# WiFi Experiment

Laboratorio documentale per uno studio universitario sulla sicurezza WiFi svolto esclusivamente su reti e dispositivi propri o formalmente autorizzati.

Il repository contiene una dispensa sui protocolli WEP, WPA, WPA2 e WPA3, una procedura controllata basata sulla suite Aircrack ng e uno script Python per generare una versione DOCX.

## Stato

Il progetto include ora un MVP CLI per Kali Linux. La CLI effettua controlli dell'ambiente, scansione passiva, selezione di reti allowlisted, cattura sequenziale, singola deauthentication diretta opzionale, conversione HC22000 e audit Hashcat opzionale.

## Requisiti documentali

- Python 3.12 o compatibile;
- dipendenze elencate in `requirements.txt`;
- Kali Linux con Aircrack ng, hcxtools, Hashcat e TShark per le operazioni radio;
- Microsoft Word o un renderer DOCX per la verifica visiva del documento generato.

Installazione della dipendenza:

```bash
python -m pip install -r requirements.txt
python -m pip install -e .
```

Generazione del DOCX:

```bash
python build_wifi_security_doc.py
```

Il generatore contiene attualmente un percorso Windows assoluto; consultare `stato_progetto.md` prima di usarlo su un altro computer.

## CLI di laboratorio

Consultare [docs/KALI_SETUP.md](docs/KALI_SETUP.md) per aggiornamento della distribuzione, keyring, installazione degli strumenti e configurazione.

Per una checklist completa e leggibile da telefono: [docs/GUIDA_DA_TELEFONO.md](docs/GUIDA_DA_TELEFONO.md).

```bash
cp config/lab.example.toml config/lab.toml
wifi-lab --config config/lab.toml --dry-run wizard --selection 1
sudo .venv/bin/wifi-lab --config config/lab.toml doctor
sudo .venv/bin/wifi-lab --config config/lab.toml wizard --audit
```

La CLI mostra anche reti non autorizzate durante la scansione, ma esegue workflow attivi solo per BSSID presenti in `config/lab.toml` con `authorized=true`. Le reti vengono processate in sequenza.

## Uso sicuro

Le procedure radio descritte sono destinate a un laboratorio autorizzato. Non usare il materiale per interferire con reti, access point o client di terzi. Capture, password, indirizzi MAC reali e dizionari non devono essere aggiunti al repository.

## Orientamento

- `Sicurezza_delle_reti_WiFi_e_verifica_WPA.md`: contenuto tecnico principale.
- `AGENTS.md`: regole per coding agent.
- `stato_progetto.md`: situazione corrente.
- `struttura_progetto.md`: mappa semantica.
