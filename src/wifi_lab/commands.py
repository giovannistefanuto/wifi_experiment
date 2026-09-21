from __future__ import annotations

from pathlib import Path

from .models import Target


def scan_command(interface: str, prefix: Path) -> list[str]:
    return [
        "airodump-ng",
        "--write-interval",
        "1",
        "--output-format",
        "csv",
        "--write",
        str(prefix),
        interface,
    ]


def capture_command(interface: str, target: Target, prefix: Path) -> list[str]:
    return [
        "airodump-ng",
        "--channel",
        str(target.channel),
        "--bssid",
        target.bssid,
        "--output-format",
        "pcap,csv",
        "--write",
        str(prefix),
        interface,
    ]


def deauth_command(interface: str, target: Target) -> list[str]:
    if not target.authorized:
        raise ValueError("Target non autorizzato.")
    if not target.deauth_enabled or not target.client_mac:
        raise ValueError("Deauthentication non abilitata o client MAC mancante.")
    return [
        "aireplay-ng",
        "--deauth",
        "1",
        "-a",
        target.bssid,
        "-c",
        target.client_mac,
        interface,
    ]


def convert_command(capture: Path, output: Path) -> list[str]:
    return ["hcxpcapngtool", "-o", str(output), str(capture)]


def hashcat_command(hash_file: Path, wordlist: Path, session_dir: Path) -> list[str]:
    return [
        "hashcat",
        "-m",
        "22000",
        str(hash_file),
        str(wordlist),
        "--session",
        session_dir.name,
        "--potfile-path",
        str(session_dir / "hashcat.potfile"),
        "--outfile",
        str(session_dir / "recovered.txt"),
        "--status",
        "--status-timer",
        "10",
    ]

