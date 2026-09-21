from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .commands import deauth_command
from .config import load_settings
from .runner import CommandRunner
from .selection import parse_selection
from .workflow import (
    audit_hash,
    authorized_target,
    capture_target,
    display_networks,
    doctor,
    scan_networks,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="wifi-lab")
    result.add_argument("--config", type=Path, default=Path("config/lab.toml"))
    result.add_argument("--dry-run", action="store_true")
    sub = result.add_subparsers(dest="command", required=True)

    sub.add_parser("doctor", help="Controlla sistema, strumenti e configurazione")

    monitor_start = sub.add_parser("monitor-start", help="Abilita monitor mode")
    monitor_start.add_argument("interface", help="Interfaccia gestita, per esempio wlan0")
    monitor_start.add_argument(
        "--stop-conflicts",
        action="store_true",
        help="Esegue airmon-ng check kill prima di attivare monitor mode",
    )
    monitor_stop = sub.add_parser("monitor-stop", help="Disabilita monitor mode")
    monitor_stop.add_argument("interface", help="Interfaccia monitor, per esempio wlan0mon")
    monitor_stop.add_argument(
        "--restore-network",
        action="store_true",
        help="Riavvia NetworkManager dopo lo stop",
    )

    scan = sub.add_parser("scan", help="Esegue una scansione passiva")
    scan.add_argument("--seconds", type=int)

    wizard = sub.add_parser("wizard", help="Scansiona, seleziona e processa target autorizzati")
    wizard.add_argument("--seconds", type=int)
    wizard.add_argument("--audit", action="store_true", help="Esegue Hashcat dopo la conversione")
    wizard.add_argument("--selection", help="Selezione non interattiva, per esempio 1,2,7 o 1-5")

    convert = sub.add_parser("audit", help="Esegue Hashcat su un file HC22000 esistente")
    convert.add_argument("hash_file", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        settings = load_settings(args.config)
        runner = CommandRunner(dry_run=args.dry_run)

        if args.command == "doctor":
            return 0 if doctor(runner, settings) else 1
        if args.command == "monitor-start":
            if args.stop_conflicts:
                code = runner.run(["airmon-ng", "check", "kill"]).returncode
                if code != 0:
                    return code
            return runner.run(["airmon-ng", "start", args.interface]).returncode
        if args.command == "monitor-stop":
            code = runner.run(["airmon-ng", "stop", args.interface]).returncode
            if code == 0 and args.restore_network:
                code = runner.run(["systemctl", "restart", "NetworkManager"]).returncode
            return code
        if args.command == "audit":
            return audit_hash(runner, settings, args.hash_file.resolve())

        seconds = args.seconds or settings.scan_seconds
        aps = scan_networks(runner, settings, seconds)
        if args.command == "scan":
            display_networks(aps, settings)
            return 0

        display_networks(aps, settings)
        if not aps:
            print("Nessuna rete rilevata.", file=sys.stderr)
            return 2
        raw_selection = args.selection or input("Selezione (es. 1,2,7 oppure 1-5): ")
        indexes = parse_selection(raw_selection, len(aps))
        targets = []
        for index in indexes:
            ap = aps[index - 1]
            target = authorized_target(ap, settings)
            if target is None or not target.authorized:
                print(f"[RIFIUTATO] {index}: {ap.bssid} non è nell'allowlist autorizzata.")
                continue
            if target.channel != ap.channel:
                print(
                    f"[RIFIUTATO] {target.label}: canale rilevato {ap.channel}, "
                    f"configurato {target.channel}. Aggiornare la configurazione."
                )
                continue
            targets.append(target)

        if not targets:
            print("Nessun target autorizzato selezionato.", file=sys.stderr)
            return 2

        failures = 0
        for target in targets:
            print(f"\n=== Target {target.label} {target.bssid} ===")
            hash_file = capture_target(runner, settings, target)
            if not hash_file:
                failures += 1
                continue
            if args.audit:
                code = audit_hash(runner, settings, hash_file)
                if code not in (0, 1):
                    failures += 1
        return 1 if failures else 0
    except KeyboardInterrupt:
        print("Interrotto dall'utente.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
