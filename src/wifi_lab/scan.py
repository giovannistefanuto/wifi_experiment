from __future__ import annotations

import csv
from pathlib import Path

from .models import AssociatedClient, AccessPoint, ScanResult, normalize_mac


def parse_airodump_csv(path: Path) -> ScanResult:
    access_points: list[AccessPoint] = []
    clients: list[AssociatedClient] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        rows = csv.reader(handle, skipinitialspace=True)
        section = ""
        for row in rows:
            if not row:
                continue
            first = row[0].strip()
            if first == "BSSID":
                section = "access_points"
                continue
            if first == "Station MAC":
                section = "stations"
                continue
            if section == "access_points" and len(row) >= 14:
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
            if section == "stations" and len(row) >= 6:
                try:
                    mac = normalize_mac(first)
                    bssid = normalize_mac(row[5].strip())
                    power_raw = row[3].strip()
                    power = int(power_raw) if power_raw else None
                except (ValueError, IndexError):
                    continue
                clients.append(AssociatedClient(mac=mac, bssid=bssid, power=power))
    return ScanResult(tuple(access_points), tuple(clients))
