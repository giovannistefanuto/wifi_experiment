from __future__ import annotations

import shlex
import signal
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO


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
    ) -> CommandResult:
        print(f"$ {self.display(command)}")
        if self.dry_run:
            return CommandResult(0, "", "")
        completed = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        if check and completed.returncode != 0:
            raise RuntimeError(
                f"Comando fallito ({completed.returncode}): {self.display(command)}\n"
                f"{completed.stderr.strip()}"
            )
        return CommandResult(completed.returncode, completed.stdout, completed.stderr)

    def start(self, command: list[str], log_path: Path) -> subprocess.Popen[str] | None:
        print(f"$ {self.display(command)}")
        if self.dry_run:
            return None
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log: TextIO = log_path.open("w", encoding="utf-8")
        process = subprocess.Popen(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )
        process._wifi_lab_log = log  # type: ignore[attr-defined]
        return process

    @staticmethod
    def stop(process: subprocess.Popen[str] | None) -> None:
        if process is None:
            return
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
                    process.wait(timeout=4)
        log = getattr(process, "_wifi_lab_log", None)
        if log is not None:
            log.close()
