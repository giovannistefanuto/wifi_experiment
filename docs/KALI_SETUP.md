# Preparazione di Kali Linux

## Installazioni molto vecchie

Una chiavetta creata circa cinque anni fa può avere repository, keyring, kernel e firmware troppo vecchi per gli strumenti attuali. Prima di modificare il sistema, salvare i file personali. Se l'upgrade richiede rimozioni estese o produce conflitti, una nuova immagine Kali verificata è spesso più affidabile di una lunga migrazione in-place.

Kali è una rolling release. La documentazione ufficiale raccomanda `apt update` seguito da `apt full-upgrade`, controllando con attenzione l'elenco dei pacchetti rimossi.

## Controllo iniziale

```bash
cat /etc/os-release
cat /etc/apt/sources.list.d/kali.sources 2>/dev/null || cat /etc/apt/sources.list
./scripts/setup_kali.sh --check
```

La configurazione moderna dei repository usa:

```text
Types: deb
URIs: http://http.kali.org/kali/
Suites: kali-rolling
Components: main contrib non-free non-free-firmware
Signed-By: /usr/share/keyrings/kali-archive-keyring.gpg
```

Non aggiungere repository Ubuntu a Kali. La “chiave Ubuntu” ricordata era probabilmente il keyring Kali cercato tramite il keyserver Ubuntu.

## Errore Missing key o EXPKEYSIG

Nel 2025 Kali ha ruotato la chiave dell'archivio. Lo script offre una riparazione esplicita basata sul file ufficiale e sul checksum pubblicato:

```bash
./scripts/setup_kali.sh --repair-key
sudo apt update
```

Impronta della chiave del 2025:

```text
827C 8569 F251 8CC6 77FE CA1A ED65 462E C8D5 E4C5
```

## Aggiornamento del sistema

```bash
sudo apt update
sudo apt full-upgrade
```

Prima di confermare, controllare le rimozioni proposte. Riavviare se richiesto. Su un supporto vecchio è consigliabile eseguire prima un backup e verificare lo spazio libero.

## Installazione del progetto

```bash
git clone URL_DELLA_REPOSITORY
cd WIFI_EXPERIMENT
chmod +x scripts/setup_kali.sh
./scripts/setup_kali.sh --install
cp config/lab.example.toml config/lab.toml
```

Modificare `config/lab.toml` inserendo solo BSSID e client autorizzati. Il file locale è escluso da Git.

## Avvio rapido

```bash
source .venv/bin/activate
sudo .venv/bin/wifi-lab --config config/lab.toml doctor
sudo .venv/bin/wifi-lab --config config/lab.toml monitor-start wlan0
sudo .venv/bin/wifi-lab --config config/lab.toml scan
sudo .venv/bin/wifi-lab --config config/lab.toml wizard --audit
sudo .venv/bin/wifi-lab --config config/lab.toml monitor-stop wlan0mon --restore-network
```

Provare prima senza trasmissioni:

```bash
wifi-lab --config config/lab.toml --dry-run wizard --selection 1
```

Se NetworkManager o `wpa_supplicant` impediscono di mantenere il canale, usare esplicitamente:

```bash
sudo .venv/bin/wifi-lab --config config/lab.toml \
  monitor-start wlan0 --stop-conflicts
```

L'opzione arresta processi di rete e interrompe la normale connessione WiFi del computer. Al termine usare `monitor-stop --restore-network`.

## Conversione e Hashcat

`hcxpcapngtool` converte capture `pcapng`, `pcap` o `cap` nel formato testuale HC22000. Hashcat usa il mode `22000` per WPA PBKDF2 PMKID ed EAPOL:

```bash
hcxpcapngtool -o capture.hc22000 capture.cap
hashcat -m 22000 capture.hc22000 /usr/share/wordlists/rockyou.txt
```

Il wizard esegue questa conversione automaticamente. Se `rockyou.txt` manca ma esiste `rockyou.txt.gz`, decomprime una copia nella directory locale `captures/wordlists/`, senza modificare `/usr/share`.

## Fonti

- [Updating Kali](https://www.kali.org/docs/general-use/updating-kali/)
- [Kali archive signing key](https://www.kali.org/docs/general-use/gpgkey-expiry/)
- [Kali 2026.2 repository format](https://www.kali.org/blog/kali-linux-2026-2-release/)
- [hcxtools](https://github.com/ZerBea/hcxtools)
- [Hashcat WPA mode 22000](https://hashcat.net/wiki/doku.php?id=cracking_wpawpa2)
