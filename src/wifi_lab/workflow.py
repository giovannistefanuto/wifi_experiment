from __future__ import annotations

import gzip
import json
import os
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from .commands import (
    capture_command,
    convert_command,
    deauth_command,
    hashcat_command,
    scan_command,
)
from .errors import CommandExecutionError, ProcessExitedError, WifiLabError
from .models import AssociatedClient, AccessPoint, ScanResult, Settings, Target
from .runner import CommandRunner
from .scan import parse_airodump_csv


CORE_TOOLS = (
    "iw",
    "airmon-ng",
    "airodump-ng",
    "hcxpcapngtool",
)
OPTIONAL_TOOLS = ("aireplay-ng", "hashcat", "tshark")


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def _log_tail(path: Path, limit: int = 20) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return f"Impossibile leggere il log {path}: {exc}"
    return "\n".join(lines[-limit:]).strip() or "Il processo non ha scritto dettagli nel log."


def _ensure_process_alive(
    process: subprocess.Popen[str] | None,
    log_path: Path,
    description: str,
) -> None:
    if process is None:
        return
    code = process.poll()
    if code is None:
        return
    CommandRunner.stop(process)
    raise ProcessExitedError(
        f"{description} è terminato prima del previsto con codice {code}.\n"
        f"Log: {log_path}\n{_log_tail(log_path)}"
    )


def _create_directory(path: Path, description: str) -> None:
    try:
        path.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise WifiLabError(
            f"La directory {description} esiste già: {path}. "
            "Riprova; ogni sessione deve avere un percorso univoco."
        ) from exc
    except PermissionError as exc:
        raise WifiLabError(
            f"Permesso negato creando {description} in {path}. "
            "Controllare output_dir e i permessi della directory."
        ) from exc
    except OSError as exc:
        raise WifiLabError(f"Impossibile creare {description} {path}: {exc}") from exc


def doctor(runner: CommandRunner, settings: Settings) -> bool:
    ok = True
    print("Controllo ambiente")
    if os.name != "posix":
        print("[WARN] Esecuzione reale supportata su Kali Linux; usare --dry-run altrove.")
        ok = False
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        print("[MISSING] privilegi root: le operazioni radio richiedono sudo.")
        ok = False
    for tool in CORE_TOOLS:
        location = shutil.which(tool)
        print(f"[{'OK' if location else 'MISSING'}] {tool}: {location or '-'}")
        ok = ok and bool(location)
    for tool in OPTIONAL_TOOLS:
        location = shutil.which(tool)
        required = (
            tool == "aireplay-ng" and any(target.deauth_enabled for target in settings.targets)
        )
        state = "OK" if location else ("MISSING" if required else "WARN")
        print(f"[{state}] {tool}: {location or '-'}")
        if required and not location:
            ok = False
    wordlist_gz = Path(f"{settings.wordlist}.gz")
    wordlist_ok = settings.wordlist.exists() or wordlist_gz.exists()
    print(
        f"[{'OK' if wordlist_ok else 'WARN'}] wordlist: "
        f"{settings.wordlist} (oppure {wordlist_gz.name})"
    )
    probe_path: Path | None = None
    try:
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=".wifi-lab-doctor-",
            dir=settings.output_dir,
            delete=False,
        ) as probe:
            probe_path = Path(probe.name)
            probe.write(b"ok")
            probe.flush()
            os.fsync(probe.fileno())
        probe_path.unlink()
        probe_path = None
        print(f"[OK] output_dir: {settings.output_dir}")
    except OSError as exc:
        print(f"[MISSING] output_dir non scrivibile: {settings.output_dir}: {exc}")
        ok = False
    finally:
        if probe_path is not None:
            try:
                probe_path.unlink(missing_ok=True)
            except OSError as exc:
                print(f"[WARN] Impossibile eliminare il file di prova {probe_path}: {exc}")
    print(f"[INFO] target configurati: {len(settings.targets)}")
    return ok


def scan_networks(runner: CommandRunner, settings: Settings, seconds: int) -> ScanResult:
    if not 5 <= seconds <= 3600:
        raise WifiLabError(
            f"La durata della scansione deve essere tra 5 e 3600 secondi; ricevuto {seconds}."
        )
    scan_dir = settings.output_dir / "scans" / _stamp()
    prefix = scan_dir / "scan"
    _create_directory(scan_dir, "della scansione")
    log_path = scan_dir / "airodump.log"
    process = runner.start(scan_command(settings.monitor_interface, prefix), log_path)
    if runner.dry_run:
        return ScanResult(
            access_points=tuple(
                AccessPoint(
                    bssid=target.bssid,
                    channel=target.channel,
                    privacy="LAB-DRY-RUN",
                    power=None,
                    essid=target.essid,
                )
                for target in settings.targets
            ),
            clients=tuple(
                AssociatedClient(
                    mac=target.client_mac,
                    bssid=target.bssid,
                    power=None,
                )
                for target in settings.targets
                if target.client_mac
            ),
        )
    try:
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            _ensure_process_alive(process, log_path, "Airodump durante la scansione")
            time.sleep(min(0.5, max(0.0, deadline - time.monotonic())))
    finally:
        runner.stop(process)
    csv_path = scan_dir / "scan-01.csv"
    if not csv_path.exists():
        raise WifiLabError(
            f"Airodump non ha prodotto il CSV atteso: {csv_path}.\n"
            f"Controllare monitor mode, interfaccia e log: {log_path}\n{_log_tail(log_path)}"
        )
    try:
        result = parse_airodump_csv(csv_path)
    except OSError as exc:
        raise WifiLabError(f"Impossibile leggere il CSV {csv_path}: {exc}") from exc
    if not result.access_points:
        print(
            f"[WARN] Nessun access point valido nel CSV. Controllare {log_path}, "
            "segnale, interfaccia monitor e durata della scansione."
        )
    return result


def authorized_target(ap: AccessPoint, settings: Settings) -> Target | None:
    return next((target for target in settings.targets if target.bssid == ap.bssid), None)


def display_networks(scan: ScanResult, settings: Settings) -> None:
    print("\nReti rilevate")
    print("ID  AUT  CH   PWR   SICUREZZA        BSSID              ESSID")
    for index, ap in enumerate(scan.access_points, 1):
        target = authorized_target(ap, settings)
        auth = "SI" if target and target.authorized else "NO"
        power = str(ap.power) if ap.power is not None else "?"
        print(
            f"{index:<3} {auth:<4} {ap.channel:<4} {power:<5} "
            f"{ap.privacy[:16]:<16} {ap.bssid:<18} {ap.essid}"
        )
    if scan.clients:
        print("\nClient associati rilevati passivamente")
        print("BSSID              CLIENT MAC         PWR")
        for client in scan.clients:
            power = str(client.power) if client.power is not None else "?"
            print(f"{client.bssid:<18} {client.mac:<18} {power}")


def print_target_draft(scan: ScanResult, indexes: list[int]) -> None:
    """Print a review-only configuration draft; never marks discovered targets authorized."""
    clients_by_bssid: dict[str, list[AssociatedClient]] = {}
    for client in scan.clients:
        clients_by_bssid.setdefault(client.bssid, []).append(client)

    print("\nBozza da rivedere prima di copiarla in config/lab.toml")
    for index in indexes:
        ap = scan.access_points[index - 1]
        suffix = index
        print("\n[[targets]]")
        print(f'label = "da_rinominare_{suffix}"')
        print(f"essid = {json.dumps(ap.essid, ensure_ascii=False)}")
        print(f'bssid = "{ap.bssid}"')
        print(f"channel = {ap.channel}")
        matching = clients_by_bssid.get(ap.bssid, [])
        if matching:
            print(f'# Client osservato: {matching[0].mac}. Verifica che sia un tuo device.')
            print(f'client_mac = "{matching[0].mac}"')
        else:
            print('# Nessun client associato osservato. Aggiungilo solo dopo averlo verificato.')
            print('client_mac = "AA:BB:CC:DD:EE:FF"')
        print("authorized = false")
        print("deauth_enabled = false")


def _capture_file(prefix: Path) -> Path | None:
    try:
        candidates = sorted(prefix.parent.glob(f"{prefix.name}-*.cap"))
    except OSError as exc:
        raise WifiLabError(
            f"Impossibile cercare la capture nella sessione {prefix.parent}: {exc}"
        ) from exc
    return candidates[0] if candidates else None


def _try_convert(
    runner: CommandRunner, capture: Path, output: Path
) -> tuple[bool, str | None]:
    snapshot = output.parent / ".capture_snapshot.cap"
    try:
        if not capture.exists() or capture.stat().st_size == 0:
            return False, None
        output.unlink(missing_ok=True)
        shutil.copy2(capture, snapshot)
        result = runner.run(convert_command(snapshot, output))
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip() or "nessun dettaglio"
            return False, f"hcxpcapngtool rc={result.returncode}: {detail}"
        return output.exists() and output.stat().st_size > 0, None
    except PermissionError as exc:
        raise WifiLabError(
            f"Permesso negato preparando la conversione in {output.parent}: {exc}"
        ) from exc
    except OSError as exc:
        raise WifiLabError(f"Errore preparando la conversione di {capture}: {exc}") from exc
    finally:
        try:
            snapshot.unlink(missing_ok=True)
        except OSError:
            print(f"[WARN] Impossibile eliminare il file temporaneo {snapshot}.")


def capture_target(runner: CommandRunner, settings: Settings, target: Target) -> Path | None:
    if not target.authorized:
        raise WifiLabError(f"Target non autorizzato: {target.label}")

    session = settings.output_dir / "sessions" / f"{_stamp()}_{target.label}"
    _create_directory(session, "della sessione")
    prefix = session / "capture"
    hash_file = session / "capture.hc22000"
    log_path = session / "airodump.log"
    process = runner.start(
        capture_command(settings.monitor_interface, target, prefix),
        log_path,
    )
    if runner.dry_run:
        if target.deauth_enabled:
            runner.run(deauth_command(settings.monitor_interface, target))
        runner.run(convert_command(prefix.with_name("capture-01.cap"), hash_file))
        return hash_file

    started = time.monotonic()
    deauth_sent = False
    conversion_failures = 0
    print(
        f"Cattura {target.label} avviata; timeout {settings.capture_timeout_seconds}s."
    )
    try:
        while time.monotonic() - started < settings.capture_timeout_seconds:
            _ensure_process_alive(process, log_path, f"Airodump per {target.label}")
            elapsed = time.monotonic() - started
            if target.deauth_enabled and not deauth_sent and elapsed >= settings.deauth_delay_seconds:
                print("Invio di un singolo gruppo deauthentication al client autorizzato.")
                runner.run(
                    deauth_command(settings.monitor_interface, target),
                    check=True,
                    stream=True,
                )
                deauth_sent = True

            capture = _capture_file(prefix)
            if capture:
                converted, warning = _try_convert(runner, capture, hash_file)
                if converted:
                    print(f"Handshake convertibile rilevato: {hash_file}")
                    return hash_file
                if warning:
                    conversion_failures += 1
                    print(
                        f"[WARN] Conversione temporaneamente fallita "
                        f"({conversion_failures}/3): {warning}"
                    )
                    if conversion_failures >= 3:
                        raise CommandExecutionError(
                            "hcxpcapngtool ha fallito tre volte consecutive. "
                            f"Capture: {capture}; log Airodump: {log_path}"
                        )
                else:
                    conversion_failures = 0
            time.sleep(settings.poll_seconds)
        print(f"Timeout senza handshake convertibile per {target.label}.")
        return None
    finally:
        runner.stop(process)


def ensure_wordlist(settings: Settings) -> Path:
    if settings.wordlist.exists():
        return settings.wordlist
    compressed = Path(f"{settings.wordlist}.gz")
    if not compressed.exists():
        raise WifiLabError(
            f"Wordlist non trovata: {settings.wordlist} oppure {compressed}"
        )
    destination = settings.output_dir / "wordlists" / settings.wordlist.name
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(compressed, "rb") as source, temporary.open("wb") as target:
            shutil.copyfileobj(source, target)
            target.flush()
            os.fsync(target.fileno())
        if temporary.stat().st_size == 0:
            raise WifiLabError(f"La wordlist decompressa da {compressed} è vuota.")
        temporary.replace(destination)
    except (gzip.BadGzipFile, EOFError) as exc:
        raise WifiLabError(
            f"Archivio wordlist corrotto o incompleto: {compressed}. "
            "Reinstallare il pacchetto wordlists oppure sostituire il file."
        ) from exc
    except PermissionError as exc:
        raise WifiLabError(
            f"Permesso negato decomprimendo la wordlist in {destination.parent}: {exc}"
        ) from exc
    except OSError as exc:
        raise WifiLabError(f"Errore decomprimendo {compressed}: {exc}") from exc
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except OSError:
            print(f"[WARN] Impossibile eliminare il temporaneo {temporary}.")
    print(f"Wordlist decompressa in modo sicuro: {destination}")
    return destination


def audit_hash(runner: CommandRunner, settings: Settings, hash_file: Path) -> int:
    if not runner.dry_run:
        try:
            if not hash_file.exists():
                raise WifiLabError(f"File HC22000 non trovato: {hash_file}")
            if hash_file.stat().st_size == 0:
                raise WifiLabError(f"File HC22000 vuoto: {hash_file}")
        except PermissionError as exc:
            raise WifiLabError(f"Permesso negato leggendo {hash_file}.") from exc
        except OSError as exc:
            raise WifiLabError(f"Impossibile controllare {hash_file}: {exc}") from exc
        wordlist = ensure_wordlist(settings)
    else:
        wordlist = settings.wordlist
    session_dir = hash_file.parent
    result = runner.run(
        hashcat_command(hash_file, wordlist, session_dir),
        stream=True,
    )
    messages = {
        0: "Hashcat ha recuperato almeno una credenziale candidata.",
        1: "Hashcat ha esaurito il dizionario senza trovare una corrispondenza.",
        2: "Hashcat è stato interrotto o ha restituito un errore.",
        3: "Hashcat si è fermato al checkpoint.",
        4: "Hashcat è stato terminato dall'utente.",
    }
    print(f"[HASHCAT] {messages.get(result.returncode, f'codice inatteso {result.returncode}.')}")
    return result.returncode
