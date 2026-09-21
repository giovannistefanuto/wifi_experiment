# Decisioni di progetto

Registro storico append-only delle decisioni, modifiche significative, prove e risultati del progetto.

Ogni nuova voce deve essere aggiunta esclusivamente con `python scripts/append_decision.py <file_temporaneo.md>`. Non correggere o riscrivere manualmente le voci già presenti; eventuali rettifiche devono essere registrate in una nuova voce.



---

### 2026-09-21 — Bootstrap dell harness per agenti

**Obiettivo**  
Preparare il laboratorio WiFi per uno sviluppo progressivo da parte di coding agent con contesto ridotto e memoria tecnica affidabile.

**Contesto**  
La cartella conteneva una dispensa Markdown, un DOCX, il relativo generatore Python e output temporanei di rendering. Non era presente un repository Git né un harness per agenti.

**Analisi / decisione**  
Il progetto è stato classificato come laboratorio documentale Python in fase iniziale. Non sono state create strutture applicative premature. Sono state aggiunte regole specifiche per autorizzazione, minimizzazione delle azioni radio e protezione di capture e identificatori.

**Modifiche**  
Creati `AGENTS.md`, `stato_progetto.md`, `struttura_progetto.md`, `README.md`, `backlog.md`, `.gitignore`, `requirements.txt`, `GIOVANNI_INBOX/README.md` e `scripts/append_decision.py`. Inizializzato il registro append-only.

**File consultati**  
`Sicurezza_delle_reti_WiFi_e_verifica_WPA.md`, `build_wifi_security_doc.py` e contenuto della root.

**Test eseguiti**  
Compilazione sintattica degli script Python; append di questa voce tramite `scripts/append_decision.py`; verifica automatica dei byte scritti e rimozione del file temporaneo.

**Risultati**  
Un nuovo agente può orientarsi usando tre documenti brevi e consultare la cronologia soltanto quando necessario.

**Problemi / limiti**  
Il generatore DOCX usa ancora un percorso assoluto; Markdown e DOCX non sono completamente sincronizzati; manca una suite di test.

**Prossimi passi**  
Rendere portatile la generazione documentale e progettare un harness sperimentale con dry run, target espliciti e fixture sintetiche.

**Fonti / ricerca**  
Nessuna nuova ricerca esterna per il bootstrap.



---

### 2026-09-21 — MVP CLI per laboratorio WiFi autorizzato

**Obiettivo**  
Creare un applicativo Python installabile su Kali che orchestri scansione, selezione, cattura, conversione HC22000 e audit offline.

**Contesto**  
Il proprietario vuole eseguire esperimenti su più hotspot propri partendo da una vecchia installazione Kali. Servivano aggiornamento del sistema, gestione del keyring, installazione degli strumenti e automazione riproducibile.

**Analisi / decisione**  
L'MVP elabora i target in sequenza. La cattura resta attiva mentre viene inviato al massimo un singolo gruppo deauthentication a un client esplicito. Solo BSSID con `authorized=true` nell'allowlist possono essere processati. Broadcast e modalità continua non sono esposti.

**Modifiche**  
Creati pacchetto `src/wifi_lab`, configurazione TOML di esempio, test, `pyproject.toml`, guida Kali e script di setup. Aggiornati harness, README, backlog e gitignore. Inizializzato Git locale su `main`.

**File consultati**  
`AGENTS.md`, `stato_progetto.md`, `struttura_progetto.md`, documentazione Aircrack ng e documentazione ufficiale Kali, hcxtools e Hashcat.

**Test eseguiti**  
Compilazione con `py_compile`; 6 unit test; simulazione completa `--dry-run wizard --selection 1`; controllo `git status`.

**Risultati**  
La CLI costruisce senza shell interpolation comandi mirati per Airodump ng, Aireplay ng, hcxpcapngtool e Hashcat. Selezioni singole, liste, intervalli e `all` sono supportate, ma i target non allowlisted vengono rifiutati.

**Problemi / limiti**  
Il workflow non è ancora stato validato su Kali e hardware radio reali. Il parser CSV richiede fixture aggiuntive. Il repository non ha ancora commit o remote GitHub.

**Prossimi passi**  
Provare `doctor` e scansione su Kali aggiornato, poi una cattura su un singolo hotspot di laboratorio prima di usare selezioni multiple.

**Fonti / ricerca**  
Kali Updating, Kali archive signing key, Kali 2026.2 repository format, repository hcxtools e documentazione Hashcat mode 22000.



---

### 2026-09-21 — Guida pratica da telefono per Kali

**Obiettivo**  
Creare un unico documento operativo consultabile da telefono durante una sessione su Kali Linux.

**Contesto**  
Le istruzioni erano distribuite tra README, guida Kali, configurazione e documentazione tecnica. Il primo utilizzo richiede una sequenza lineare e una sezione di troubleshooting.

**Analisi / decisione**  
È stata aggiunta una checklist separata dalla teoria, con comandi ordinati, punti di controllo, limiti del workflow e protezione dei target autorizzati.

**Modifiche**  
Creati `docs/GUIDA_DA_TELEFONO.md`; aggiornati README, stato e mappa del repository.

**File consultati**  
`README.md`, `docs/KALI_SETUP.md`, `config/lab.example.toml`, `stato_progetto.md`, `struttura_progetto.md`.

**Test eseguiti**  
Verifica delle sezioni, dei comandi principali e del collegamento dal README.

**Risultati**  
Il progetto dispone di una guida autonoma per preparazione, configurazione, esecuzione e ripristino.

**Problemi / limiti**  
I comandi radio richiedono ancora validazione su Kali e hardware compatibile.

**Prossimi passi**  
Seguire la checklist su Kali e registrare eventuali differenze nei nomi delle interfacce o nei pacchetti disponibili.

**Fonti / ricerca**  
Nessuna nuova ricerca esterna; sono state consolidate le fonti già archiviate nel progetto.



---

### 2026-09-21 — Scoperta passiva prima dell allowlist

**Obiettivo**  
Permettere di rilevare BSSID, canale, ESSID e client associati prima di configurare i target di laboratorio.

**Contesto**  
L'allowlist iniziale richiedeva informazioni che l'utente può non conoscere prima di una scansione.

**Analisi / decisione**  
È stata introdotta una fase passiva `discover` e una configurazione senza target. La fase stampa una bozza TOML con `authorized=false` e `deauth_enabled=false`; non rende attive automaticamente reti o client osservati.

**Modifiche**  
Estesi parser CSV, modelli, workflow e CLI; creato `config/discovery.toml`; aggiornate guida, README, stato e mappa; aggiunto test della configurazione senza target.

**File consultati**  
`src/wifi_lab/scan.py`, `src/wifi_lab/workflow.py`, `src/wifi_lab/cli.py`, guida pratica e configurazione di esempio.

**Test eseguiti**  
Unit test del parser Airodump, selezione, guardrail e configurazione senza target; dry-run del comando `discover`.

**Risultati**  
L'utente può individuare passivamente i parametri della propria rete e copiare una bozza controllabile senza conoscerli in anticipo.

**Problemi / limiti**  
Un MAC osservato non prova la proprietà del dispositivo; la conferma resta manuale prima di qualunque azione attiva.

**Prossimi passi**  
Verificare la forma CSV prodotta dall'adattatore e dalla versione Airodump effettivi su Kali.

**Fonti / ricerca**  
Nessuna nuova ricerca esterna; il parser segue la struttura CSV di Airodump ng già usata dal progetto.

