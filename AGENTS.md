# Istruzioni per gli agenti

## Missione del progetto

Questo repository supporta uno studio universitario riproducibile sulla sicurezza delle reti WiFi di proprietà dell'autore o formalmente autorizzate. Raccoglie documentazione tecnica, procedure di laboratorio e, in futuro, piccoli strumenti per organizzare esperimenti, validare catture e produrre risultati anonimizzati.

Utente principale: studente e ricercatore di sicurezza informatica. Obiettivo di lungo periodo: trasformare gli appunti attuali in un laboratorio controllato, documentato e riproducibile per confrontare WEP, WPA, WPA2 e WPA3 senza operare su reti o dispositivi di terzi.

Vincoli permanenti:

- lavorare solo su reti, hotspot e client propri o con autorizzazione esplicita;
- preferire acquisizioni passive quando sufficienti;
- limitare eventuali azioni attive al BSSID e al client autorizzati;
- non usare deauthentication continua o broadcast come comportamento predefinito;
- non committare credenziali, capture reali, MAC personali o dataset sensibili;
- anonimizzare gli identificatori prima di pubblicare risultati o esempi.

## Principi di sviluppo

- Preferire soluzioni semplici, modulari e verificabili.
- Separare acquisizione, analisi, reporting e configurazione.
- Mantenere funzioni e file con responsabilità limitate; evitare file monolitici e duplicazione.
- Usare interfacce chiare e naming coerente.
- Tenere configurazione e percorsi fuori dalla logica quando si interviene sul codice esistente.
- Centralizzare errori e logging solo quando il numero di componenti lo giustifica.
- Progettare per testabilità senza introdurre astrazioni premature.
- Preservare documenti e codice esistenti; evitare refactoring collaterali.

## Esplorazione e context budget

Prima di modificare qualcosa:

1. leggere `stato_progetto.md`;
2. leggere `struttura_progetto.md`;
3. cercare per filename, simbolo o testo e aprire solo i file pertinenti;
4. consultare `decisioni_di_progetto.md` soltanto per ricostruire una decisione, un esperimento o un problema storico.

Non scandire automaticamente `GIOVANNI_INBOX/`, capture, artefatti generati o documenti estesi. Usare subagent soltanto per attività indipendenti e ben delimitate; fornire loro il minimo contesto necessario.

## Regola sulle modifiche

Prima di una modifica significativa, identificare il componente e le dipendenze immediate. Mantenere la modifica localizzata e non introdurre funzionalità non richieste. Dopo la modifica eseguire il controllo più mirato sufficiente; usare verifiche più ampie solo per modifiche trasversali.

Comandi attualmente disponibili:

```bash
python -m py_compile build_wifi_security_doc.py scripts/append_decision.py
python build_wifi_security_doc.py
python scripts/append_decision.py percorso/file_temporaneo.md
python -m unittest discover -s tests -v
wifi-lab --config config/lab.example.toml --dry-run wizard --selection 1
```

I test automatici coprono configurazione, selezione, parsing, guardrail, errori dei processi esterni e recupero da artefatti corrotti senza usare hardware. La generazione DOCX richiede `python-docx`; il risultato deve essere aperto o renderizzato e controllato visivamente.

## Memoria tecnica

`stato_progetto.md` e `struttura_progetto.md` sono mutabili e devono descrivere soltanto la realtà corrente. Aggiornarli quando cambia in modo rilevante lo stato o la mappa del repository.

`decisioni_di_progetto.md` è append-only. È vietato modificarlo direttamente con editor, replace, patch o riscritture. Per aggiungere una voce:

1. creare un breve file Markdown temporaneo;
2. inserire il log nel formato seguente;
3. eseguire `python scripts/append_decision.py <file_temporaneo.md>`;
4. verificare il successo e che il file temporaneo sia stato eliminato.

Registrare decisioni architetturali, modifiche significative, bug con causa, esperimenti, test rilevanti, benchmark, cambi di librerie o API, soluzioni rifiutate, ricerche utili e problemi aperti. Non registrare correzioni sintattiche minori. Il log deve essere conciso e non deve contenere ragionamenti interni o trascrizioni del lavoro.

### YYYY-MM-DD — Titolo sintetico

**Obiettivo**  
Cosa si voleva ottenere.

**Contesto**  
Informazioni necessarie per capire la modifica.

**Analisi / decisione**  
Cosa è stato deciso e perché.

**Modifiche**  
File o componenti modificati e descrizione sintetica.

**File consultati**  
Solo quelli realmente importanti.

**Test eseguiti**  
Comandi, test, benchmark o verifiche effettuate.

**Risultati**  
Esito concreto.

**Problemi / limiti**  
Eventuali problemi rimasti.

**Prossimi passi**  
Solo azioni future concrete.

**Fonti / ricerca**  
Solo documentazione esterna, paper, repository o ricerche realmente usati.
