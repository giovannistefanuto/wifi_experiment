"""Append a UTF-8 Markdown entry to the project decision log safely."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DECISION_LOG = PROJECT_ROOT / "decisioni_di_progetto.md"
SEPARATOR = "\n\n---\n\n"


def append_entry(source: Path) -> None:
    source = source.resolve()

    if source == DECISION_LOG.resolve():
        raise ValueError("Il file temporaneo non può essere il registro decisioni.")
    if not source.exists() or not source.is_file():
        raise FileNotFoundError(f"File temporaneo non trovato: {source}")
    if not DECISION_LOG.exists() or not DECISION_LOG.is_file():
        raise FileNotFoundError(f"Registro decisioni non trovato: {DECISION_LOG}")

    content = source.read_text(encoding="utf-8")
    if not content.strip():
        raise ValueError("Il file temporaneo è vuoto.")

    payload = SEPARATOR + content
    if not payload.endswith("\n"):
        payload += "\n"

    previous_size = DECISION_LOG.stat().st_size
    with DECISION_LOG.open("a", encoding="utf-8", newline="") as log:
        log.write(payload)
        log.flush()
        os.fsync(log.fileno())

    expected_size = previous_size + len(payload.encode("utf-8"))
    actual_size = DECISION_LOG.stat().st_size
    if actual_size != expected_size:
        raise OSError(
            "Dimensione inattesa dopo l'append: "
            f"attesi {expected_size} byte, trovati {actual_size}."
        )

    with DECISION_LOG.open("rb") as log:
        log.seek(previous_size)
        written = log.read()
    if written != payload.encode("utf-8"):
        raise OSError("La verifica del contenuto appena scritto non è riuscita.")

    source.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Aggiunge una voce Markdown al registro decisioni append-only."
    )
    parser.add_argument("file", type=Path, help="File Markdown temporaneo in UTF-8")
    args = parser.parse_args()

    try:
        append_entry(args.file)
    except Exception as exc:
        print(f"Errore: {exc}", file=sys.stderr)
        return 1

    print(f"Voce aggiunta a {DECISION_LOG}")
    print(f"File temporaneo eliminato: {args.file.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

