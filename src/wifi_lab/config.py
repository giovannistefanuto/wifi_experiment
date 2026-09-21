from __future__ import annotations

import tomllib
from pathlib import Path

from .models import Settings, Target


def _relative(base: Path, value: str) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else (base / path).resolve()


def load_settings(path: Path) -> Settings:
    path = path.expanduser().resolve()
    with path.open("rb") as handle:
        raw = tomllib.load(handle)

    lab = raw.get("lab", {})
    target_rows = raw.get("targets", [])
    if not target_rows:
        raise ValueError("La configurazione non contiene target autorizzati.")

    targets = tuple(
        Target(
            label=str(row["label"]),
            essid=str(row.get("essid", "")),
            bssid=str(row["bssid"]),
            channel=int(row["channel"]),
            client_mac=str(row["client_mac"]) if row.get("client_mac") else None,
            authorized=bool(row.get("authorized", False)),
            deauth_enabled=bool(row.get("deauth_enabled", False)),
        )
        for row in target_rows
    )

    bssids = [target.bssid for target in targets]
    if len(bssids) != len(set(bssids)):
        raise ValueError("La configurazione contiene BSSID duplicati.")

    return Settings(
        monitor_interface=str(lab.get("monitor_interface", "wlan0mon")),
        output_dir=_relative(path.parent, str(lab.get("output_dir", "../captures"))),
        scan_seconds=max(5, int(lab.get("scan_seconds", 20))),
        capture_timeout_seconds=min(
            900, max(15, int(lab.get("capture_timeout_seconds", 900)))
        ),
        deauth_delay_seconds=max(2, int(lab.get("deauth_delay_seconds", 5))),
        poll_seconds=max(3, int(lab.get("poll_seconds", 5))),
        wordlist=_relative(
            path.parent, str(lab.get("wordlist", "/usr/share/wordlists/rockyou.txt"))
        ),
        targets=targets,
    )

