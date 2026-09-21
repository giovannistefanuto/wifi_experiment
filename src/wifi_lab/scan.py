from __future__ import annotations

import csv
from pathlib import Path

from .models import AccessPoint, normalize_mac


def parse_airodump_csv(path: Path) -> list[AccessPoint]:
    access_points: list[AccessPoint] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        rows = csv.reader(handle, skipinitialspace=True)
        in_access_points = False
        for row in rows:
            if not row:
                if in_access_points:
                    break
                continue
            first = row[0].strip()
            if first == "BSSID":
                in_access_points = True
                continue
            if not in_access_points or len(row) < 14:
                continue
            try:
                bssid = normalize_mac(first)
                channel = int(row[3].strip())
                power_raw = row[8].strip()
                power = int(power_raw) if power_raw else None
            except (ValueError, IndexError):
                continue
            access_points.append(
                AccessPoint(
                    bssid=bssid,
                    channel=channel,
                    privacy=row[5].strip(),
                    power=power,
                    essid=row[13].strip(),
                )
            )
    return access_points

