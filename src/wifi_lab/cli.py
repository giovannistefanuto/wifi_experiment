from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

from .config import load_settings
from .errors import WifiLabError
from .runner import CommandRunner
from .selection import parse_selection
from .workflow import (
    audit_hash,
    authorized_target,
    capture_target,
    display_networks,
    doctor,
    print_target_draft,
    scan_networks,
)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="wifi-lab")
    result.add_argument("--config", type=Path, default=Path("config/lab.toml"))
    result.add_argument("--dry-run", action="store_true")
    result.add_argument(
        "--debug",
        action="store_true",
        help="Mostra il traceback completo per errori inattesi",
    )
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

    discover = sub.add_parser(
        "discover",
        help="Mostra reti e client associati e genera bozze TOML non autorizzate",
    )
    discover.add_argument("--seconds", type=int)
    discover.add_argument(
        "--selection", help="Reti per cui stampare la bozza, per esempio 1,2 o 1-3"
    )

    wizard = sub.add_parser("wizard", help="Scansiona, seleziona e processa target autorizzati")
    wizard.add_argument("--seconds", type=int)
    wizard.add_argument("--audit", action="store_true", help="Esegue Hashcat dopo la conversione")
    wizard.add_argument("--selection", help="Selezione non interattiva, per esempio 1,2,7 o 1-5")

    convert = sub.add_parser("audit", help="Esegue Hashcat su un file HC22000 esistente")
    convert.add_argument("hash_file", type=Path)
    return result


def _read_selection(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError as exc:
        raise WifiLabError(
            "Input interattivo non disponibile. Usare --selection, per esempio "
            "--selection 1,2 oppure --selection all."
        ) from exc


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        settings = load_settings(args.config)
        runner = CommandRunner(dry_run=args.dry_run)

        if args.command == "doctor":
            return 0 if doctor(runner, settings) else 1
        if args.command == "monitor-start":
            if args.stop_conflicts:
                runner.run(["airmon-ng", "check", "kill"], check=True, stream=True)
            runner.run(["airmon-ng", "start", args.interface], check=True, stream=True)
            return 0
        if args.command == "monitor-stop":
            runner.run(["airmon-ng", "stop", args.interface], check=True, stream=True)
            if args.restore_network:
                runner.run(
                    ["systemctl", "restart", "NetworkManager"],
                    check=True,
                    stream=True,
                )
            return 0
        if args.command == "audit":
            return audit_hash(runner, settings, args.hash_file.resolve())

        seconds = args.seconds or settings.scan_seconds
        scan_result = scan_networks(runner, settings, seconds)
        if args.command == "scan":
            display_networks(scan_result, settings)
            return 0

        if args.command == "discover":
            display_networks(scan_result, settings)
            if not scan_result.access_points:
                print("Nessuna rete rilevata.", file=sys.stderr)
                return 2
            raw_selection = args.selection or _read_selection(
                "Bozza per quali reti (es. 1,2,7 oppure 1-5): "
            )
            indexes = parse_selection(raw_selection, len(scan_result.access_points))
            print_target_draft(scan_result, indexes)
            return 0

        display_networks(scan_result, settings)
        if not scan_result.access_points:
            print("Nessuna rete rilevata.", file=sys.stderr)
            return 2
        raw_selection = args.selection or _read_selection(
            "Selezione (es. 1,2,7 oppure 1-5): "
        )
        indexes = parse_selection(raw_selection, len(scan_result.access_points))
        targets = []
        for index in indexes:
            ap = scan_result.access_points[index - 1]
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
            try:
                hash_file = capture_target(runner, settings, target)
                if not hash_file:
                    failures += 1
                    continue
                if args.audit:
                    code = audit_hash(runner, settings, hash_file)
                    if code not in (0, 1):
                        failures += 1
            except (WifiLabError, ValueError) as exc:
                failures += 1
                print(
                    f"[ERRORE TARGET] {target.label}: {exc}\n"
                    "Il target viene saltato; il wizard prosegue con il successivo.",
                    file=sys.stderr,
                )
        print(
            f"\nRiepilogo: {len(targets) - failures} completati, "
            f"{failures} non completati su {len(targets)} target."
        )
        return 1 if failures else 0
    except KeyboardInterrupt:
        print("Interrotto dall'utente.", file=sys.stderr)
        return 130
    except (WifiLabError, ValueError) as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(
            f"Errore inatteso ({type(exc).__name__}): {exc}\n"
            "Rieseguire con --debug e conservare il traceback e i log della sessione.",
            file=sys.stderr,
        )
        if getattr(args, "debug", False):
            traceback.print_exc()
        return 70


if __name__ == "__main__":
    raise SystemExit(main())
