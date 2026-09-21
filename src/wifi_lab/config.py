from __future__ import annotations

import tomllib
from pathlib import Path

from .errors import ConfigurationError
from .models import Settings, Target


def _relative(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (base / path).resolve()


def load_settings(path: Path) -> Settings:
    path = path.expanduser().resolve()
    try:
        with path.open("rb") as handle:
            raw = tomllib.load(handle)
    except FileNotFoundError as exc:
        raise ConfigurationError(
            f"Configurazione non trovata: {path}. Per la prima scansione usare "
            "'--config config/discovery.toml discover'; per il laboratorio copiare "
            "config/lab.example.toml in config/lab.toml."
        ) from exc
    except PermissionError as exc:
        raise ConfigurationError(f"Permesso negato leggendo {path}.") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigurationError(f"TOML non valido in {path}: {exc}") from exc
    except OSError as exc:
        raise ConfigurationError(f"Impossibile leggere {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigurationError(f"La radice di {path} deve essere una tabella TOML.")

    lab = raw.get("lab", {})
    if not isinstance(lab, dict):
        raise ConfigurationError("La sezione [lab] deve essere una tabella TOML.")
    target_rows = raw.get("targets", [])
    if not isinstance(target_rows, list):
        raise ConfigurationError("[[targets]] deve essere una lista di tabelle TOML.")

    targets_list: list[Target] = []
    for index, row in enumerate(target_rows, 1):
        if not isinstance(row, dict):
            raise ConfigurationError(f"Target {index}: attesa una tabella TOML.")
        missing = [field for field in ("label", "bssid", "channel") if field not in row]
        if missing:
            raise ConfigurationError(
                f"Target {index}: campi obbligatori mancanti: {', '.join(missing)}."
            )
        for flag in ("authorized", "deauth_enabled"):
            if flag in row and not isinstance(row[flag], bool):
                raise ConfigurationError(
                    f"Target {index}: {flag} deve essere true oppure false, senza virgolette."
                )
        try:
            target = Target(
                label=str(row["label"]),
                essid=str(row.get("essid", "")),
                bssid=str(row["bssid"]),
                channel=int(row["channel"]),
                client_mac=str(row["client_mac"]) if row.get("client_mac") else None,
                authorized=row.get("authorized", False),
                deauth_enabled=row.get("deauth_enabled", False),
            )
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(f"Target {index}: {exc}") from exc
        targets_list.append(target)
    targets = tuple(targets_list)

    bssids = [target.bssid for target in targets]
    if len(bssids) != len(set(bssids)):
        raise ConfigurationError("La configurazione contiene BSSID duplicati.")
    labels = [target.label for target in targets]
    if len(labels) != len(set(labels)):
        raise ConfigurationError("La configurazione contiene label duplicate.")

    interface = str(lab.get("monitor_interface", "wlan0mon")).strip()
    if not interface or any(char.isspace() for char in interface):
        raise ConfigurationError("monitor_interface è vuota o contiene spazi.")

    def integer(name: str, default: int, minimum: int, maximum: int) -> int:
        try:
            value = int(lab.get(name, default))
        except (TypeError, ValueError) as exc:
            raise ConfigurationError(f"[lab].{name} deve essere un numero intero.") from exc
        if not minimum <= value <= maximum:
            raise ConfigurationError(
                f"[lab].{name} deve essere compreso tra {minimum} e {maximum}; trovato {value}."
            )
        return value

    return Settings(
        monitor_interface=interface,
        output_dir=_relative(path.parent, str(lab.get("output_dir", "../captures"))),
        scan_seconds=integer("scan_seconds", 20, 5, 3600),
        capture_timeout_seconds=integer("capture_timeout_seconds", 900, 15, 900),
        deauth_delay_seconds=integer("deauth_delay_seconds", 5, 2, 300),
        poll_seconds=integer("poll_seconds", 5, 3, 60),
        wordlist=_relative(
            path.parent, str(lab.get("wordlist", "/usr/share/wordlists/rockyou.txt"))
        ),
        targets=targets,
    )
