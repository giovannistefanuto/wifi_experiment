from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


MAC_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$")
LABEL_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def normalize_mac(value: str) -> str:
    value = value.strip().upper().replace("-", ":")
    if not MAC_RE.fullmatch(value):
        raise ValueError(f"MAC non valido: {value!r}")
    return value


@dataclass(frozen=True)
class Target:
    label: str
    essid: str
    bssid: str
    channel: int
    client_mac: str | None
    authorized: bool
    deauth_enabled: bool

    def __post_init__(self) -> None:
        object.__setattr__(self, "bssid", normalize_mac(self.bssid))
        if self.client_mac:
            object.__setattr__(self, "client_mac", normalize_mac(self.client_mac))
        if not self.label.strip():
            raise ValueError("Ogni target richiede un label.")
        if not LABEL_RE.fullmatch(self.label):
            raise ValueError(
                f"Label non sicuro {self.label!r}; usare solo lettere, numeri, punto, _ e -."
            )
        if not 1 <= self.channel <= 196:
            raise ValueError(f"Canale non valido per {self.label}: {self.channel}")
        if self.deauth_enabled and not self.client_mac:
            raise ValueError(
                f"{self.label}: deauth_enabled richiede client_mac; il broadcast non è ammesso."
            )
        if self.deauth_enabled and not self.authorized:
            raise ValueError(f"{self.label}: una deauthentication richiede authorized=true.")


@dataclass(frozen=True)
class Settings:
    monitor_interface: str
    output_dir: Path
    scan_seconds: int
    capture_timeout_seconds: int
    deauth_delay_seconds: int
    poll_seconds: int
    wordlist: Path
    targets: tuple[Target, ...]


@dataclass(frozen=True)
class AccessPoint:
    bssid: str
    channel: int
    privacy: str
    power: int | None
    essid: str


@dataclass(frozen=True)
class AssociatedClient:
    mac: str
    bssid: str
    power: int | None


@dataclass(frozen=True)
class ScanResult:
    access_points: tuple[AccessPoint, ...]
    clients: tuple[AssociatedClient, ...]
