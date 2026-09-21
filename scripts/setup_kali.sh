#!/usr/bin/env bash
set -euo pipefail

usage() {
  printf '%s\n' \
    'Uso: scripts/setup_kali.sh [--check|--install|--repair-key]' \
    '  --check       Controlla release, repository e pacchetti senza modifiche' \
    '  --install     Installa i pacchetti richiesti dai repository Kali' \
    '  --repair-key  Scarica il keyring ufficiale Kali 2025 e verifica SHA1'
}

mode="${1:---check}"
packages=(aircrack-ng hcxtools hashcat tshark python3 python3-venv git)

if [[ ! -f /etc/os-release ]] || ! grep -qi '^ID=kali' /etc/os-release; then
  echo 'Errore: questo script supporta soltanto Kali Linux.' >&2
  exit 2
fi

case "$mode" in
  --check)
    cat /etc/os-release
    if [[ -f /etc/apt/sources.list.d/kali.sources ]]; then
      cat /etc/apt/sources.list.d/kali.sources
    else
      cat /etc/apt/sources.list
    fi
    for package in "${packages[@]}"; do
      dpkg-query -W -f='${binary:Package}\t${Version}\n' "$package" 2>/dev/null || \
        printf 'MISSING\t%s\n' "$package"
    done
    ;;
  --repair-key)
    tmp="$(mktemp)"
    trap 'rm -f "$tmp"' EXIT
    wget https://archive.kali.org/archive-keyring.gpg -O "$tmp"
    expected='603374c107a90a69d983dbcb4d31e0d6eedfc325'
    actual="$(sha1sum "$tmp" | awk '{print $1}')"
    if [[ "$actual" != "$expected" ]]; then
      echo "Errore: checksum keyring inatteso: $actual" >&2
      exit 3
    fi
    sudo install -m 0644 "$tmp" /usr/share/keyrings/kali-archive-keyring.gpg
    echo 'Keyring Kali installato e verificato.'
    ;;
  --install)
    sudo apt update
    sudo apt install -y "${packages[@]}"
    python3 -m venv .venv
    .venv/bin/python -m pip install --upgrade pip
    .venv/bin/python -m pip install -e .
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac

