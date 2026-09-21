# Guida pratica da telefono per WiFi Experiment

Questa è la checklist breve da usare accanto a Kali Linux. Tutte le operazioni devono riguardare soltanto hotspot, access point e client propri o formalmente autorizzati.

## Prima volta su Kali

### 1 Scarica il progetto

```bash
git clone https://github.com/giovannistefanuto/wifi_experiment.git
cd wifi_experiment
chmod +x scripts/setup_kali.sh
```

### 2 Controlla Kali

```bash
./scripts/setup_kali.sh --check
```

Se Kali è molto vecchia, prima fai un backup dei file personali. Poi controlla che i repository puntino a `kali-rolling` e aggiorna:

```bash
sudo apt update
sudo apt full-upgrade
```

Leggi la lista delle rimozioni prima di confermare. Riavvia se viene richiesto.

### 3 Se apt segnala una chiave mancante

Errore tipico:

```text
Missing key 827C8569F2518CC677FECA1AED65462EC8D5E4C5
```

Usa lo script del progetto:

```bash
./scripts/setup_kali.sh --repair-key
sudo apt update
```

Non aggiungere repository Ubuntu a Kali. La chiave da aggiornare è quella ufficiale di Kali.

### 4 Installa gli strumenti e la CLI

```bash
./scripts/setup_kali.sh --install
```

Lo script installa Aircrack-ng, hcxtools, Hashcat, TShark, Python e Git. Crea anche `.venv` e installa il comando `wifi-lab` al suo interno.

## Configurazione del laboratorio

### 5 Scopri prima le tue reti

Non devi conoscere in anticipo BSSID, canale o MAC dei client. Il progetto contiene già una configurazione senza target per la prima scoperta:

```bash
sudo .venv/bin/wifi-lab \
  --config config/discovery.toml \
  discover
```

Il programma elenca ESSID, BSSID, canale e client associati osservati. Alla richiesta di selezione inserisci, per esempio, `1,2,7`; stampa una bozza TOML senza autorizzare automaticamente nessuna rete.

### 6 Crea la configurazione privata dopo la scoperta

```bash
cp config/lab.example.toml config/lab.toml
nano config/lab.toml
```

```bash
cp config/lab.example.toml config/lab.toml
nano config/lab.toml
```

`config/lab.toml` non viene inviato su GitHub. Inserisci soltanto dati di laboratorio reali:

```toml
[lab]
monitor_interface = "wlan0mon"
capture_timeout_seconds = 900
wordlist = "/usr/share/wordlists/rockyou.txt"

[[targets]]
label = "mio_hotspot"
essid = "NOME_DEL_MIO_HOTSPOT"
bssid = "AA:BB:CC:DD:EE:FF"
channel = 6
client_mac = "11:22:33:44:55:66"
authorized = true
deauth_enabled = true
```

Significato importante:

- `bssid`: MAC dell'hotspot, non il suo nome.
- `channel`: canale rilevato durante la scansione.
- `client_mac`: MAC di un tuo dispositivo già collegato all'hotspot.
- `authorized = true`: abilita il target nel workflow.
- `deauth_enabled = true`: permette un solo impulso di deauthentication diretto al client indicato.

Non inserire una rete di terzi. Non omettere `client_mac`: l'applicativo non usa broadcast.

La bozza contiene `authorized = false` e `deauth_enabled = false` proprio perché devi verificare personalmente che BSSID e client MAC siano dei tuoi dispositivi. Solo dopo aggiorna tali campi per il workflow attivo. Se non conosci o non vuoi indicare il tuo client MAC, lascia `deauth_enabled = false`: il programma effettuerà una cattura passiva fino al timeout.

## Verifica prima di trasmettere

### 7 Controlla strumenti e configurazione

```bash
sudo .venv/bin/wifi-lab --config config/lab.toml doctor
```

Devi vedere `OK` per `iw`, `airmon-ng`, `airodump-ng`, `aireplay-ng`, `hcxpcapngtool`, `hashcat` e `tshark`.

### 8 Simula tutto senza usare la scheda WiFi

```bash
.venv/bin/wifi-lab \
  --config config/lab.toml \
  --dry-run wizard --selection 1
```

Il dry-run stampa i comandi che sarebbero eseguiti ma non cattura e non trasmette frame.

## Sessione pratica

### 9 Attiva monitor mode

```bash
sudo .venv/bin/wifi-lab \
  --config config/lab.toml \
  monitor-start wlan0
```

Sostituisci `wlan0` con la tua interfaccia gestita. Controlla il nome dell'interfaccia creata con:

```bash
iw dev
```

Di solito è `wlan0mon`; se ha un nome diverso, aggiorna `monitor_interface` in `config/lab.toml`.

Se il canale continua a cambiare o Airodump non cattura bene, usa solo se accetti che il PC perda temporaneamente la normale connettività WiFi:

```bash
sudo .venv/bin/wifi-lab \
  --config config/lab.toml \
  monitor-start wlan0 --stop-conflicts
```

### 10 Scansiona passivamente

```bash
sudo .venv/bin/wifi-lab \
  --config config/lab.toml \
  scan
```

L'output mostra l'ID temporaneo, il canale, il BSSID, l'ESSID e se la rete è autorizzata (`AUT = SI`).

Se il canale reale differisce da quello nel file TOML, aggiorna prima `config/lab.toml`. Il programma rifiuta un target con canale diverso per evitare di agire sulla rete sbagliata.

### 11 Esegui il wizard

```bash
sudo .venv/bin/wifi-lab \
  --config config/lab.toml \
  wizard
```

Il wizard esegue una nuova scansione e chiede una selezione:

```text
1
1,2,7
1-5
all
```

`all` prova soltanto le reti incluse nell'allowlist autorizzata. I target selezionati vengono elaborati uno alla volta.

Per ogni target autorizzato, il programma:

1. avvia Airodump sul canale e BSSID indicati;
2. dopo pochi secondi invia, se abilitato, un solo gruppo di deauthentication diretto al tuo client;
3. controlla periodicamente se la capture è convertibile in HC22000;
4. passa al target successivo se trova un handshake convertibile o se scade il timeout.

I file vengono salvati in `captures/sessions/`. Non caricarli su GitHub.

### 12 Audit opzionale con RockYou

Per avviare Hashcat automaticamente dopo una conversione riuscita:

```bash
sudo .venv/bin/wifi-lab \
  --config config/lab.toml \
  wizard --audit
```

Il programma usa Hashcat mode `22000`. Se `/usr/share/wordlists/rockyou.txt` non esiste ma esiste il file `.gz`, crea una copia decompressa in `captures/wordlists/`.

Un risultato negativo significa solo che la password non era nel dizionario usato; non dimostra che la rete sia invulnerabile.

## Alla fine

### 13 Arresta monitor mode e ripristina la rete

```bash
sudo .venv/bin/wifi-lab \
  --config config/lab.toml \
  monitor-stop wlan0mon --restore-network
```

Sostituisci `wlan0mon` con il nome effettivo della tua interfaccia monitor.

## Problemi comuni

| Sintomo | Controllo o soluzione |
|---|---|
| `doctor` mostra uno strumento mancante | Esegui `./scripts/setup_kali.sh --install`. |
| `apt update` segnala `Missing key` o `EXPKEYSIG` | Esegui `./scripts/setup_kali.sh --repair-key`, poi `sudo apt update`. |
| Nessuna rete appare | Controlla con `iw dev`, prova una scheda WiFi USB compatibile con monitor mode, verifica regione e segnale. |
| Il canale cambia | Riavvia monitor mode con `--stop-conflicts`; al termine ripristina NetworkManager. |
| Il target viene rifiutato | Controlla BSSID, canale e `authorized = true` in `config/lab.toml`. |
| Non avviene deauthentication | Controlla `client_mac`, `deauth_enabled = true`, driver/injection, PMF e distanza. Non aumentare automaticamente il numero di frame. |
| Nessun HC22000 viene creato | Verifica che il client si sia riconnesso, che la capture contenga EAPOL e che `hcxpcapngtool` sia installato. |
| Hashcat non trova nulla | La password potrebbe non essere nel dizionario; non è un errore della conversione. |

## Come leggere gli errori

- `Errore:` indica un problema previsto e correggibile, per esempio configurazione mancante, selezione non valida, file vuoto, permessi o tool assente. Il testo indica il file o il comando coinvolto.
- `[ERRORE TARGET]` riguarda una sola rete: il wizard la salta e continua con le altre selezionate. Il riepilogo finale mostra quanti target non sono stati completati.
- `Errore inatteso (...)` indica un caso non previsto. Ripeti lo stesso comando aggiungendo l'opzione globale `--debug` prima del sottocomando e conserva il traceback.
- Se Airodump termina in anticipo, il messaggio mostra il percorso di `airodump.log` e le ultime righe utili. I log sono dentro `captures/scans/` o `captures/sessions/`.
- Un exit code `0` indica successo; `1` può indicare un batch incompleto o, per Hashcat, dizionario esaurito; `2` indica input/configurazione non valida; `70` è riservato agli errori inattesi; `130` indica interruzione con Ctrl+C.

Esempio diagnostico:

```bash
sudo .venv/bin/wifi-lab \
  --config config/lab.toml \
  --debug \
  wizard --selection 1,2
```

La decompressione di RockYou usa un file temporaneo: se l'archivio è corrotto o la scrittura fallisce, il programma non lascia una wordlist parziale utilizzabile. Non cancellare i log prima di aver letto l'errore.

## Comandi da ricordare

```bash
# Stato del progetto
git status

# Aggiorna il progetto dopo modifiche pubblicate su GitHub
git pull

# Controlla Kali e gli strumenti
sudo .venv/bin/wifi-lab --config config/lab.toml doctor

# Simulazione sicura
.venv/bin/wifi-lab --config config/lab.toml --dry-run wizard --selection 1

# Scansione passiva
sudo .venv/bin/wifi-lab --config config/lab.toml scan

# Workflow con audit opzionale
sudo .venv/bin/wifi-lab --config config/lab.toml wizard --audit

# Ripristino della rete
sudo .venv/bin/wifi-lab --config config/lab.toml monitor-stop wlan0mon --restore-network
```

## Limiti del progetto oggi

- Il programma è stato testato in dry-run e con unit test, non ancora su una scheda WiFi reale con Kali.
- WPA3 con PMF obbligatorio può ignorare frame di deauthentication contraffatti; questo è un comportamento atteso.
- Il programma non autorizza automaticamente reti soltanto perché hanno lo stesso ESSID.
- Le capture contengono metadati sensibili: trattale come dati di laboratorio privati.

Per approfondire la teoria, leggi `Sicurezza_delle_reti_WiFi_e_verifica_WPA.md`. Per i dettagli sulle fonti Kali e HC22000, leggi `docs/KALI_SETUP.md`.
