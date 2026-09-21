# Backlog

## Riproducibilità documentale

- Rendere configurabile e relativo il percorso di output del generatore DOCX.
- Eliminare la duplicazione dei contenuti scegliendo una fonte autorevole e generando gli altri formati.
- Sincronizzare nel DOCX la sezione sulla deauthentication già presente nel Markdown.
- Aggiungere un controllo automatico di link e blocchi di codice Markdown.

## Harness sperimentale

- Registrare versioni degli strumenti, hardware, durata e condizioni dell'esperimento in un manifest per sessione.
- Migliorare la validazione delle capture EAPOL e produrre un riepilogo anonimizzato.
- Salvare la scansione selezionata in JSON per esecuzioni ripetibili non interattive.
- Aggiungere un controllo esplicito dello stato monitor e del canale prima della cattura.

## Privacy e dati

- Definire un processo di pseudonimizzazione per BSSID e MAC dei client.
- Separare capture grezze, metadati anonimizzati e risultati pubblicabili.
- Aggiungere controlli che impediscano il versionamento accidentale di file sensibili.

## Testing

- Aggiungere unit test per utility e validatori quando vengono introdotti.
- Aggiungere test di integrazione soltanto con fixture sintetiche e senza trasmissioni radio.
- Documentare separatamente le prove hardware manuali su Kali Linux.
