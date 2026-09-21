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

