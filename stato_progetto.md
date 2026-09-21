# Stato del progetto

## Obiettivo attuale

Validare su Kali Linux l'MVP CLI per esperimenti controllati su WPA2 Personal, dalla scansione alla conversione HC22000 e all'audit offline opzionale.

## Funzionalità operative

- Dispensa tecnica in Markdown su WEP, WPA, WPA2, WPA3 e Aircrack ng.
- Procedura documentata per monitor mode, cattura mirata, verifica EAPOL e controllo a dizionario.
- Sezione Markdown sulla deauthentication diretta a un singolo client autorizzato, PMF e limiti operativi.
- Documento DOCX impaginato e relativo script di generazione.
- Memoria tecnica append-only tramite `scripts/append_decision.py`.
- CLI `wifi-lab` con doctor, monitor mode, scansione, wizard interattivo, cattura, conversione e audit.
- Allowlist obbligatoria, target sequenziali, singolo gruppo deauthentication e client MAC obbligatorio.
- Procedura Kali aggiornata e script di setup.
- Test automatici senza hardware per selezione e guardrail.

## Architettura corrente

Il repository è un laboratorio Python con due sottosistemi:

- una fonte Markdown aggiornata manualmente;
- uno script Python che costruisce il DOCX;
- il DOCX generato;
- documenti di harness per agenti;
- una CLI modulare in `src/wifi_lab/` per orchestrare strumenti Kali senza shell interpolation.

## Tecnologie effettive

- Markdown per documentazione e memoria tecnica.
- Python 3; ambiente verificato con Python 3.12.14.
- `python-docx` 1.2.0 per generare il documento Word.
- Aircrack ng, Wireshark e TShark descritti come strumenti esterni di laboratorio su Kali Linux.
- hcxtools per conversione HC22000 e Hashcat mode 22000 per audit offline.
- Ambiente di sviluppo corrente Windows; gli esperimenti radio sono destinati a Kali Linux e hardware compatibile.

## Componenti principali

- `Sicurezza_delle_reti_WiFi_e_verifica_WPA.md`: fonte tecnica più aggiornata.
- `build_wifi_security_doc.py`: generatore del DOCX.
- `Sicurezza_delle_reti_WiFi_e_verifica_WPA.docx`: artefatto leggibile e distribuibile.
- `scripts/append_decision.py`: unico percorso consentito per il registro storico.
- `src/wifi_lab/`: applicazione CLI.
- `config/lab.example.toml`: schema dell'allowlist locale.
- `docs/KALI_SETUP.md`: installazione e aggiornamento Kali.

## Problemi noti

- Il generatore DOCX contiene un percorso di output Windows assoluto e non è ancora portabile.
- Markdown e DOCX non sono sincronizzati: la sezione estesa sulla deauthentication è presente nel Markdown ma non ancora nel generatore DOCX.
- I workflow radio non sono ancora stati provati su hardware Kali reale.
- Non esiste ancora uno schema per metadati degli esperimenti o per anonimizzare capture e indirizzi MAC.
- Il repository Git locale è inizializzato sulla branch `main`, ma non ha ancora commit né remote GitHub.
- Gli artefatti in `.docx_render/` sono generati e non devono diventare fonte primaria.

## Prossime milestone

1. Rendere portabile il generatore DOCX e scegliere una singola fonte autorevole per i contenuti.
2. Sincronizzare la sezione deauthentication tra Markdown e DOCX.
3. Provare `doctor`, monitor mode e scansione su Kali aggiornato.
4. Validare su un hotspot di laboratorio la cattura anticipata tramite conversione HC22000.
5. Aggiungere fixture CSV di Airodump e test del workflow con process runner simulato.
6. Creare il primo commit e collegare un remote GitHub quando il proprietario sceglie nome e visibilità.

## Decisioni recenti da conoscere

- L'MVP usa solo la libreria standard Python; gli strumenti radio restano processi esterni.
- Capture, credenziali e identificatori reali devono restare fuori dal versionamento.
- Le azioni attive devono essere esplicite, circoscritte e rivolte a un singolo dispositivo autorizzato.
- Le reti selezionate vengono processate in sequenza; non si eseguono deauthentication parallele.
