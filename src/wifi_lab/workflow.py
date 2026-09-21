from __future__ import annotations

import gzip
import os
import shutil
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
from .models import AccessPoint, Settings, Target
from .runner import CommandRunner
from .scan import parse_airodump_csv


REQUIRED_TOOLS = (
    "iw",
    "airmon-ng",
    "airodump-ng",
    "aireplay-ng",
    "hcxpcapngtool",
    "hashcat",
    "tshark",
)


def doctor(runner: CommandRunner, settings: Settings) -> bool:
    ok = True
    print("Controllo ambiente")
    if os.name != "posix":
        print("[WARN] Esecuzione reale supportata su Kali Linux; usare --dry-run altrove.")
        ok = False
    if hasattr(os, "geteuid") and os.geteuid() != 0:
        print("[WARN] Le operazioni radio richiedono normalmente sudo/root.")
    for tool in REQUIRED_TOOLS:
        location = shutil.which(tool)
        print(f"[{'OK' if location else 'MISSING'}] {tool}: {location or '-'}")
        ok = ok and bool(location)
    print(f"[{'OK' if settings.wordlist.exists() else 'MISSING'}] wordlist: {settings.wordlist}")
    return ok


def scan_networks(runner: CommandRunner, settings: Settings, seconds: int) -> list[AccessPoint]:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    scan_dir = settings.output_dir / "scans" / stamp
    prefix = scan_dir / "scan"
    scan_dir.mkdir(parents=True, exist_ok=True)
    process = runner.start(scan_command(settings.monitor_interface, prefix), scan_dir / "airodump.log")
    if runner.dry_run:
        return [
            AccessPoint(
                bssid=target.bssid,
                channel=target.channel,
                privacy="LAB-DRY-RUN",
                power=None,
                essid=target.essid,
            )
            for target in settings.targets
        ]
    try:
        time.sleep(seconds)
    finally:
        runner.stop(process)
    csv_path = scan_dir / "scan-01.csv"
    if not csv_path.exists():
        raise RuntimeError(f"Airodump non ha prodotto {csv_path}")
    return parse_airodump_csv(csv_path)


def authorized_target(ap: AccessPoint, settings: Settings) -> Target | None:
    return next((target for target in settings.targets if target.bssid == ap.bssid), None)


def display_networks(aps: list[AccessPoint], settings: Settings) -> None:
    print("\nReti rilevate")
    print("ID  AUT  CH   PWR   SICUREZZA        BSSID              ESSID")
    for index, ap in enumerate(aps, 1):
        target = authorized_target(ap, settings)
        auth = "SI" if target and target.authorized else "NO"
        power = str(ap.power) if ap.power is not None else "?"
        print(
            f"{index:<3} {auth:<4} {ap.channel:<4} {power:<5} "
            f"{ap.privacy[:16]:<16} {ap.bssid:<18} {ap.essid}"
        )


def _capture_file(prefix: Path) -> Path | None:
    candidates = sorted(prefix.parent.glob(f"{prefix.name}-*.cap"))
    return candidates[0] if candidates else None


def _try_convert(runner: CommandRunner, capture: Path, output: Path) -> bool:
    output.unlink(missing_ok=True)
    result = runner.run(convert_command(capture, output))
    return result.returncode == 0 and output.exists() and output.stat().st_size > 0


def capture_target(runner: CommandRunner, settings: Settings, target: Target) -> Path | None:
    if not target.authorized:
        raise ValueError(f"Target non autorizzato: {target.label}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    session = settings.output_dir / "sessions" / f"{stamp}_{target.label}"
    session.mkdir(parents=True, exist_ok=True)
    prefix = session / "capture"
    hash_file = session / "capture.hc22000"
    process = runner.start(
        capture_command(settings.monitor_interface, target, prefix),
        session / "airodump.log",
    )
    if runner.dry_run:
        if target.deauth_enabled:
            runner.run(deauth_command(settings.monitor_interface, target))
        runner.run(convert_command(prefix.with_name("capture-01.cap"), hash_file))
        return hash_file

    started = time.monotonic()
    deauth_sent = False
    print(
        f"Cattura {target.label} avviata; timeout {settings.capture_timeout_seconds}s."
    )
    try:
        while time.monotonic() - started < settings.capture_timeout_seconds:
            elapsed = time.monotonic() - started
            if target.deauth_enabled and not deauth_sent and elapsed >= settings.deauth_delay_seconds:
                print("Invio di un singolo gruppo deauthentication al client autorizzato.")
                runner.run(deauth_command(settings.monitor_interface, target), check=True)
                deauth_sent = True

            capture = _capture_file(prefix)
            if capture and _try_convert(runner, capture, hash_file):
                print(f"Handshake convertibile rilevato: {hash_file}")
                return hash_file
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
        raise FileNotFoundError(
            f"Wordlist non trovata: {settings.wordlist} oppure {compressed}"
        )
    destination = settings.output_dir / "wordlists" / settings.wordlist.name
    destination.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(compressed, "rb") as source, destination.open("wb") as target:
        shutil.copyfileobj(source, target)
    return destination


def audit_hash(runner: CommandRunner, settings: Settings, hash_file: Path) -> int:
    wordlist = ensure_wordlist(settings)
    session_dir = hash_file.parent
    result = runner.run(hashcat_command(hash_file, wordlist, session_dir))
    return result.returncode
