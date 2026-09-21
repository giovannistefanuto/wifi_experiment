# Sicurezza delle reti WiFi e verifica delle credenziali WPA

## Panoramica dei protocolli cattura del 4 way handshake e analisi con Aircrack ng

Questa dispensa riassume i concetti necessari per comprendere la sicurezza delle reti IEEE 802.11 e per verificare, in un laboratorio autorizzato, la resistenza di una rete WPA o WPA2 Personal a un attacco a dizionario offline.

> **Ambito etico e legale.** Le procedure operative devono essere eseguite esclusivamente su hotspot, access point e client propri, oppure con autorizzazione scritta del titolare. La trasmissione di frame di deautenticazione interrompe temporaneamente una connessione ed è un'azione attiva, non una semplice osservazione passiva.

## 1 Concetti fondamentali

Una rete WiFi usa lo standard IEEE 802.11. L'access point trasmette frame di gestione che descrivono la rete e coordina l'associazione dei client. Una scheda in modalità gestita riceve normalmente il traffico necessario alla propria connessione; in **monitor mode** espone al sistema i frame 802.11 osservati sul canale selezionato.

| Termine | Significato |
|---|---|
| ESSID o SSID | Nome logico della rete visualizzato dagli utenti. |
| BSSID | Indirizzo MAC che identifica una specifica radio o istanza dell'access point. |
| Canale | Porzione dello spettro radio su cui avviene la comunicazione. |
| Station | Dispositivo client osservato o associato a un access point. |
| EAPOL | Formato usato nello scambio di autenticazione che include il 4 way handshake. |
| PSK | Segreto condiviso usato nelle reti Personal; nella pratica deriva dalla passphrase. |
| PMF | Protected Management Frames, protezione per determinati frame di gestione. |

## 2 Evoluzione da WEP a WPA3

| Protocollo | Meccanismo | Valutazione |
|---|---|---|
| WEP | RC4 e IV corto | Protocollo compromesso; il recupero statistico della chiave è praticabile. |
| WPA | TKIP e RC4 | Soluzione transitoria ormai obsoleta. |
| WPA2 Personal | PSK e AES CCMP | Ancora valido con una passphrase robusta; consente la verifica offline di password candidate. |
| WPA2 Enterprise | 802.1X, EAP e RADIUS | Adatto alle organizzazioni se metodo EAP e certificati sono configurati correttamente. |
| WPA3 Personal | SAE e PMF | Preferibile sui dispositivi moderni; resiste meglio agli attacchi a dizionario offline. |
| WPA3 Enterprise | 802.1X e suite moderne | Include una modalità di sicurezza a 192 bit per ambienti sensibili. |
| Enhanced Open | OWE | Cifra reti senza password, ma non autentica l'identità dell'access point. |

### WEP

WEP impiega RC4 con vettori di inizializzazione troppo corti e una costruzione crittografica debole. Il riutilizzo degli IV consente di ricavare statisticamente la chiave dopo aver raccolto traffico sufficiente. Una password lunga non corregge il difetto strutturale del protocollo.

### WPA e TKIP

WPA fu progettato come misura transitoria per hardware nato con WEP. TKIP introdusse contatori, mixing delle chiavi e controlli di integrità, ma conservò RC4 e oggi è considerato obsoleto.

### WPA2

WPA2 con AES CCMP offre una cifratura solida. Nella modalità Personal, tutti i dispositivi condividono una passphrase. La cattura di un'autenticazione permette di provare offline password candidate. La modalità Enterprise usa invece 802.1X ed EAP, normalmente con un server RADIUS e credenziali individuali.

### WPA3

WPA3 Personal sostituisce il tradizionale scambio PSK con **Simultaneous Authentication of Equals**, un Password Authenticated Key Exchange. Una registrazione passiva non offre lo stesso controllo offline economico disponibile con WPA2 PSK. WPA3 richiede inoltre Protected Management Frames. Restano importanti gli aggiornamenti, le vulnerabilità di implementazione e i rischi introdotti dalla modalità mista WPA2 WPA3.

### WPS

WiFi Protected Setup non è una versione di WPA. È una procedura di configurazione semplificata. Le implementazioni basate sul vecchio PIN possono indebolire una rete anche quando la passphrase WPA2 è robusta; se non necessario, WPS dovrebbe essere disabilitato.

## 3 Il 4 way handshake WPA2

Nel caso WPA2 Personal, la passphrase non viene trasmessa via radio. La passphrase e l'SSID vengono elaborati per derivare la Pairwise Master Key. Durante l'handshake, access point e client scambiano nonce e altre informazioni e derivano una Pairwise Transient Key. I codici di integrità dei messaggi consentono di verificare che entrambi conoscano il segreto corretto.

1. L'access point invia un nonce e avvia lo scambio.
2. Il client genera il proprio nonce, deriva le chiavi temporanee e restituisce un messaggio protetto da MIC.
3. L'access point verifica il MIC e comunica i parametri della chiave di gruppo.
4. Il client conferma l'installazione delle chiavi e la connessione può proseguire.

La verifica a dizionario ricostruisce localmente la derivazione per ogni password candidata e confronta il risultato con il materiale catturato. Il file non contiene quindi un semplice hash statico della password.

## 4 Procedura di laboratorio con Aircrack ng

Negli esempi:

- `wlan0` è l'interfaccia WiFi iniziale;
- `wlan0mon` è l'interfaccia in monitor mode;
- `CH` è il canale dell'hotspot;
- `AA:BB:CC:DD:EE:FF` è il BSSID dell'hotspot;
- `11:22:33:44:55:66` è il MAC di un client proprio e associato.

### Preparazione dell'interfaccia

```bash
iw dev
sudo airmon-ng
sudo airmon-ng check
sudo airmon-ng start wlan0
```

Se NetworkManager o `wpa_supplicant` interferiscono con il canale:

```bash
sudo airmon-ng check kill
```

Questo comando interrompe temporaneamente la normale connettività WiFi del computer.

### Ricognizione passiva

```bash
sudo airodump-ng wlan0mon
```

Si annotano il BSSID dell'hotspot, il canale, l'ESSID e la modalità di sicurezza. `PWR` rappresenta la potenza ricevuta, non una distanza precisa. Nella sezione `STATION` si individua il MAC del client autorizzato.

### Cattura mirata

La cattura deve rimanere attiva durante la riconnessione del client:

```bash
sudo airodump-ng \
  --channel CH \
  --bssid AA:BB:CC:DD:EE:FF \
  --write hotspot \
  wlan0mon
```

Airodump ng genera file come `hotspot-01.cap` e `hotspot-01.csv`.

## 5 Riconnessione manuale e deautenticazione controllata

### Riconnessione manuale

Il metodo meno invasivo consiste nel lasciare attiva la cattura, disattivare e riattivare il WiFi di un proprio client e riconnetterlo all'hotspot. La nuova autenticazione produce i messaggi EAPOL necessari.

### Che cosa fa realmente Aireplay ng

Il comando ricordato come “logout” è normalmente l'attacco di **deauthentication** di Aireplay ng. Non effettua il logout a livello IP e non comunica con un servizio applicativo. Trasmette frame di gestione IEEE 802.11 che dichiarano terminata l'associazione tra client e access point.

Nelle reti legacy questi frame non erano autenticati. Un trasmettitore poteva quindi contraffarli usando gli indirizzi dell'AP e del client. Dopo averli ricevuti, il client:

1. considera non più valida l'associazione corrente;
2. avvia una nuova scansione o tenta di associarsi nuovamente allo stesso AP;
3. ripete autenticazione e associazione;
4. in WPA o WPA2 completa un nuovo 4 way handshake, che Airodump ng può catturare.

La riconnessione non è garantita: dipende dal sistema operativo, dal risparmio energetico, dalla qualità del segnale e dalle politiche del client. Alcuni dispositivi applicano un ritardo, chiedono un intervento dell'utente oppure scelgono un'altra rete.

### Controlli preliminari

La scheda deve supportare l'iniezione e deve trovarsi sullo stesso canale dell'AP. Per verificarlo:

```bash
iw dev wlan0mon info
sudo aireplay-ng --test \
  -e "NOME_HOTSPOT" \
  -a AA:BB:CC:DD:EE:FF \
  wlan0mon
```

Il test di iniezione controlla se la scheda riesce a trasmettere frame e a ricevere risposte dall'AP. Deve essere eseguito soltanto sull'access point del laboratorio.

### Deautenticazione diretta di un solo client

Con Airodump ng già in esecuzione in un altro terminale:

```bash
sudo aireplay-ng --deauth 1 \
  -a AA:BB:CC:DD:EE:FF \
  -c 11:22:33:44:55:66 \
  wlan0mon
```

La forma abbreviata equivalente è:

```bash
sudo aireplay-ng -0 1 \
  -a AA:BB:CC:DD:EE:FF \
  -c 11:22:33:44:55:66 \
  wlan0mon
```

Significato dei parametri:

| Parametro | Funzione |
|---|---|
| `--deauth 1` o `-0 1` | Invia un singolo gruppo di frame di deautenticazione. |
| `-a BSSID` | Indica l'indirizzo dell'access point. |
| `-c CLIENT` | Limita la trasmissione a uno specifico client autorizzato. |
| `wlan0mon` | Interfaccia in monitor mode usata per l'iniezione. |

La documentazione Aircrack ng specifica che, nella deautenticazione diretta, Aireplay ng trasmette frame sia verso l'AP sia verso il client. Nell'output, valori ACK provenienti da entrambi indicano che i due dispositivi hanno ricevuto le trasmissioni.

### Perché usare un solo tentativo

Per una prova controllata, un solo gruppo è normalmente sufficiente. Se il client non reagisce, si controllano prima:

- canale dell'interfaccia;
- correttezza di BSSID e MAC del client;
- distanza e qualità del segnale;
- supporto all'iniezione del chipset;
- presenza di PMF;
- eventuale cambio casuale del MAC del client.

Il valore `0` dopo `--deauth` indica trasmissione continua. Non è appropriato per la cattura ordinaria di un singolo handshake e può trasformare la prova in una persistente negazione del servizio. Anche omettere `-c` indirizza l'azione a tutti i client dell'AP; nel laboratorio è preferibile mantenere sempre il filtro sul proprio dispositivo.

### Verifica della riconnessione

Airodump ng dovrebbe mostrare `WPA handshake: <BSSID>`. In Wireshark si applica il filtro:

```text
eapol
```

Da terminale:

```bash
tshark -r hotspot-01.cap -Y eapol
```

Per osservare deautenticazione, nuova associazione ed EAPOL in Wireshark si può usare:

```text
wlan.fc.type_subtype == 0x000c ||
wlan.fc.type_subtype == 0x0000 ||
wlan.fc.type_subtype == 0x0001 ||
eapol
```

La sola presenza di quattro frame EAPOL non garantisce una cattura valida: i messaggi devono appartenere allo stesso scambio e avere contatori di replay e nonce coerenti.

### Effetto di PMF e WPA3

Protected Management Frames protegge diversi frame di gestione, compresi quelli di deauthentication e disassociation, dopo l'instaurazione delle chiavi. Un client che usa PMF in modalità obbligatoria dovrebbe ignorare frame contraffatti non protetti.

WPA3 richiede PMF. In modalità WPA2 WPA3 mista, però, il comportamento dipende dalle capacità negoziate dal singolo client. Il fallimento della deautenticazione non dimostra da solo che PMF sia attivo: possono intervenire anche canale errato, mancanza di ACK, driver incompatibile o segnale insufficiente.

## 6 Verifica a dizionario

```bash
aircrack-ng \
  -w /usr/share/wordlists/rockyou.txt \
  -b AA:BB:CC:DD:EE:FF \
  hotspot-01.cap
```

Se RockYou è compresso:

```bash
ls -lh /usr/share/wordlists/rockyou*
sudo gzip -dk /usr/share/wordlists/rockyou.txt.gz
```

Aircrack ng trova la password soltanto se la candidata corretta è presente nel dizionario o nello spazio di ricerca configurato. Un risultato negativo non dimostra che la rete sia invulnerabile.

## 7 Ripristino della rete

```bash
sudo airmon-ng stop wlan0mon
sudo systemctl restart NetworkManager
```

## 8 Principali categorie di attacco

| Categoria | Meccanismo | Difesa principale |
|---|---|---|
| Dizionario WPA e WPA2 | Cattura di materiale di autenticazione e prova offline di password prevedibili. | Passphrase casuale e lunga. |
| PMKID | Alcune configurazioni espongono materiale utilizzabile per una verifica offline senza handshake completo. | Password robusta, aggiornamenti e WPA3 quando possibile. |
| WEP statistico | Recupero della chiave sfruttando IV e debolezze di RC4. | Eliminare WEP. |
| Deautenticazione | Frame contraffatti provocano disconnessioni o riconnessioni. | PMF, WPA3 e monitoraggio. |
| Evil twin | Un AP falso imita l'ESSID per attirare client o credenziali. | Validazione dei certificati e profili gestiti. |
| Rogue AP | Un access point non autorizzato viene collegato alla rete interna. | Inventario, NAC e rilevamento wireless. |
| WPS PIN | Ricerca del PIN o sfruttamento di implementazioni vulnerabili. | Disabilitare WPS PIN. |
| Downgrade | Il dispositivo viene indotto a usare una modalità meno forte. | WPA3 only e Transition Disable quando supportato. |
| KRACK | Reinstallazione delle chiavi in implementazioni WPA2 vulnerabili. | Aggiornare client e access point. |
| Dragonblood | Problemi nelle prime implementazioni SAE. | Firmware recente e SAE Hash to Element. |
| Jamming | Interferenza intenzionale contro la disponibilità radio. | Rilevamento radio e procedure operative. |

## 9 Configurazione consigliata per un hotspot

- Preferire WPA3 Personal quando tutti i dispositivi lo supportano.
- In alternativa usare WPA2 Personal con AES CCMP, senza TKIP.
- Usare una password casuale di almeno 16 o 20 caratteri e non riutilizzata.
- Disabilitare WEP, WPA legacy e WPS PIN.
- Aggiornare il sistema operativo del telefono e i dispositivi client.
- Evitare la modalità WPA2 WPA3 mista se non serve per compatibilità.
- Impostare PMF come obbligatorio quando possibile.
- Controllare periodicamente i client associati all'hotspot.

## 10 Metodologia sperimentale suggerita

1. Definire tre classi di password: umana prevedibile, passphrase composta da parole casuali e password generata casualmente.
2. Usare lo stesso SSID, lo stesso hardware e lo stesso file di cattura per mantenere costanti le condizioni.
3. Registrare dimensione del dizionario, candidate provate, tempo, hardware e versione del software.
4. Distinguere tra password trovata, spazio di ricerca esaurito e test interrotto per limite temporale.
5. Ripetere le misure e riportare mediana, variabilità e limiti sperimentali.
6. Confrontare WPA2 PSK con il diverso modello di attacco di WPA3 SAE.

Il dataset pubblicato non dovrebbe contenere credenziali reali, indirizzi MAC personali o catture di terzi. È preferibile usare BSSID sintetici nelle figure e conservare i file `cap` grezzi in un archivio di ricerca ad accesso controllato.

## Riferimenti

1. [Aircrack ng Airodump ng documentation](https://www.aircrack-ng.org/doku.php?id=airodump-ng)
2. [Aircrack ng Aireplay ng documentation](https://www.aircrack-ng.org/doku.php?id=aireplay-ng)
3. [Aircrack ng Deauthentication](https://www.aircrack-ng.org/doku.php?id=deauthentication)
4. [Aircrack ng Injection test](https://www.aircrack-ng.org/doku.php?id=injection_test)
5. [Aircrack ng Aircrack ng documentation](https://www.aircrack-ng.org/doku.php?id=aircrack-ng)
6. [Aircrack ng WPA capture analysis](https://www.aircrack-ng.org/doku.php?id=wpa_capture)
7. [Android Open Source Project WPA3 and WiFi Enhanced Open](https://source.android.com/docs/core/connect/wifi-wpa3-owe)
8. [NIST SP 800 153 Guidelines for Securing Wireless Local Area Networks](https://csrc.nist.gov/pubs/sp/800/153/final)

