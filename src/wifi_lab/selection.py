from __future__ import annotations


def parse_selection(value: str, maximum: int) -> list[int]:
    value = value.strip().lower()
    if not value:
        raise ValueError("Selezione vuota.")
    if maximum < 1:
        return []
    if value == "all":
        return list(range(1, maximum + 1))

    selected: set[int] = set()
    for token in value.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            left, right = token.split("-", 1)
            start, end = int(left), int(right)
            if start > end:
                raise ValueError(f"Intervallo inverso: {token}")
            selected.update(range(start, end + 1))
        else:
            selected.add(int(token))

    invalid = sorted(item for item in selected if item < 1 or item > maximum)
    if invalid:
        raise ValueError(f"Indici fuori intervallo: {invalid}")
    return sorted(selected)

