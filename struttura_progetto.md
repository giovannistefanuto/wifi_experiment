# Struttura del progetto

Questa mappa descrive responsabilità e punti di ingresso. Non sostituisce un elenco completo dei file.

## Root

`AGENTS.md`  
Regole globali per coding agent. Consultare all'inizio di ogni task.

`README.md`  
Introduzione per lettori umani, requisiti e comandi essenziali.

`stato_progetto.md`  
Snapshot compatto e mutabile dello stato attuale. È il primo documento operativo da leggere dopo `AGENTS.md`.

`struttura_progetto.md`  
Mappa semantica del repository. Aggiornare quando cambiano componenti o responsabilità.

`decisioni_di_progetto.md`  
Registro storico append-only. Non leggere automaticamente e non modificare direttamente.

`backlog.md`  
Lavoro futuro non immediato. Consultare per pianificazione, non come descrizione dello stato corrente.

`.gitignore`  
Esclude segreti, cache, capture radio, dizionari, output temporanei e artefatti di rendering.

`requirements.txt`  
Dipendenza Python necessaria al generatore DOCX.

`pyproject.toml`  
Definisce il pacchetto Python e il comando `wifi-lab`.

## Documentazione tecnica

`Sicurezza_delle_reti_WiFi_e_verifica_WPA.md`  
Fonte tecnica più aggiornata su protocolli e procedure di laboratorio. Consultare quando si modificano contenuti, comandi o metodologia.

`Sicurezza_delle_reti_WiFi_e_verifica_WPA.docx`  
Artefatto Word destinato alla lettura. Non usarlo come fonte primaria quando esiste il Markdown corrispondente.

## Generazione documentale

`build_wifi_security_doc.py`  
Genera e impagina il DOCX con `python-docx`. Consultare per layout Word, tabelle, stili e bibliografia. Attualmente incorpora parte del testo nel codice e usa un percorso assoluto.

`.docx_render/`  
Output temporaneo del controllo visivo. È materiale generato e ignorato dal versionamento.

## Utility

`scripts/append_decision.py`  
Unico strumento autorizzato ad aggiungere voci a `decisioni_di_progetto.md`. Non contiene logica di laboratorio WiFi.

`scripts/setup_kali.sh`  
Controlla Kali, ripara esplicitamente il keyring ufficiale e installa i pacchetti richiesti. Consultare insieme a `docs/KALI_SETUP.md`.

## Applicazione CLI

`src/wifi_lab/`  
Pacchetto Python dell'MVP. Separa configurazione, modelli validati, costruzione dei comandi, esecuzione dei processi, errori applicativi, parsing della scansione e workflow. `errors.py` definisce gli errori leggibili dalla CLI; `runner.py` traduce i guasti dei processi esterni e `workflow.py` gestisce log, cleanup e recuperi localizzati. Le azioni attive richiedono allowlist, client MAC e un singolo gruppo deauthentication.

`config/lab.example.toml`  
Schema di configurazione senza target reali. Copiare in `config/lab.toml`, che è ignorato da Git.

`config/discovery.toml`  
Configurazione pubblica senza target, usata dal comando `discover` per la prima scansione passiva.

`tests/`  
Test senza hardware per configurazione, selezione, parsing CSV, process runner, wordlist/HC22000 e guardrail di sicurezza.

`docs/KALI_SETUP.md`  
Procedura aggiornata per Kali, chiave archivio, dipendenze, installazione e avvio.

`docs/GUIDA_DA_TELEFONO.md`  
Checklist operativa autonoma e lineare per preparare Kali, configurare il laboratorio, usare il wizard e risolvere problemi comuni. È il documento da consultare durante una sessione pratica.

## Materiale fornito manualmente

`GIOVANNI_INBOX/`  
Area per documenti, immagini, dataset, mockup e ricerche forniti dal proprietario. Consultare solo quando il task lo richiede esplicitamente.

## Dati locali generati

`captures/` è creata dalla CLI e ignorata da Git. Contiene scansioni, capture, file HC22000, log e risultati Hashcat. Non pubblicarla senza anonimizzazione.
