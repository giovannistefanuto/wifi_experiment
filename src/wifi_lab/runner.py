from __future__ import annotations

import shlex
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from .errors import CommandExecutionError


@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class CommandRunner:
    def __init__(self, dry_run: bool = False) -> None:
        self.dry_run = dry_run

    @staticmethod
    def display(command: list[str]) -> str:
        return shlex.join(command)

    def run(
        self,
        command: list[str],
        *,
        timeout: int | None = None,
        check: bool = False,
        stream: bool = False,
    ) -> CommandResult:
        if not command or not command[0].strip():
            raise CommandExecutionError("Comando esterno vuoto o non valido.")
        print(f"$ {self.display(command)}")
        if self.dry_run:
            return CommandResult(0, "", "")
        try:
            completed = subprocess.run(
                command,
                text=True,
                capture_output=not stream,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError as exc:
            raise CommandExecutionError(
                f"Strumento non trovato: {command[0]!r}. "
                "Eseguire './scripts/setup_kali.sh --install' e poi 'wifi-lab doctor'."
            ) from exc
        except PermissionError as exc:
            raise CommandExecutionError(
                f"Permesso negato avviando {command[0]!r}. "
                "Per le operazioni radio eseguire la CLI con sudo."
            ) from exc
        except subprocess.TimeoutExpired as exc:
            partial = exc.stderr or exc.stdout
            if isinstance(partial, bytes):
                partial = partial.decode(errors="replace")
            suffix = f"\nOutput parziale: {partial.strip()}" if partial else ""
            raise CommandExecutionError(
                f"Timeout dopo {timeout}s: {self.display(command)}{suffix}"
            ) from exc
        except OSError as exc:
            raise CommandExecutionError(
                f"Impossibile avviare {command[0]!r}: {exc}"
            ) from exc

        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        if check and completed.returncode != 0:
            detail = stderr.strip() or stdout.strip()
            if not detail:
                detail = "vedere l'output mostrato sopra" if stream else "nessun dettaglio prodotto"
            raise CommandExecutionError(
                f"Comando fallito ({completed.returncode}): {self.display(command)}\n"
                f"{detail}"
            )
        return CommandResult(completed.returncode, stdout, stderr)

    def start(self, command: list[str], log_path: Path) -> subprocess.Popen[str] | None:
        if not command or not command[0].strip():
            raise CommandExecutionError("Comando esterno vuoto o non valido.")
        print(f"$ {self.display(command)}")
        if self.dry_run:
            return None
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            log: TextIO = log_path.open("w", encoding="utf-8")
        except OSError as exc:
            raise CommandExecutionError(
                f"Impossibile creare il log {log_path}: {exc}"
            ) from exc
        try:
            process = subprocess.Popen(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
            )
        except FileNotFoundError as exc:
            log.close()
            raise CommandExecutionError(
                f"Strumento non trovato: {command[0]!r}. "
                "Eseguire './scripts/setup_kali.sh --install'."
            ) from exc
        except PermissionError as exc:
            log.close()
            raise CommandExecutionError(
                f"Permesso negato avviando {command[0]!r}; riprovare con sudo."
            ) from exc
        except OSError as exc:
            log.close()
            raise CommandExecutionError(
                f"Impossibile avviare {command[0]!r}: {exc}"
            ) from exc
        process._wifi_lab_log = log  # type: ignore[attr-defined]
        return process

    @staticmethod
    def stop(process: subprocess.Popen[str] | None) -> None:
        if process is None:
            return
        try:
            if process.poll() is None:
                process.send_signal(signal.SIGINT)
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    try:
                        process.wait(timeout=4)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        try:
                            process.wait(timeout=4)
                        except subprocess.TimeoutExpired:
                            print(
                                f"[WARN] Il processo PID {process.pid} non è terminato "
                                "neppure dopo kill; verificarlo manualmente.",
                                file=sys.stderr,
                            )
        except ProcessLookupError:
            # Il processo potrebbe essere già terminato tra poll e signal.
            pass
        except OSError as exc:
            print(
                f"[WARN] Impossibile arrestare correttamente il processo "
                f"PID {process.pid}: {exc}",
                file=sys.stderr,
            )
        finally:
            log = getattr(process, "_wifi_lab_log", None)
            if log is not None and not log.closed:
                log.close()
