from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_BREAK
from pathlib import Path

OUT = Path(r"C:\Users\Utente\Documents\GIOVANNI\GITHUB\WIFI_EXPERIMENT\Sicurezza_delle_reti_WiFi_e_verifica_WPA.docx")

NAVY = "18324A"
LIGHT_BLUE = "EAF2F8"
PALE = "F6F8FA"
GRAY = "D9D9D9"
TEXT = RGBColor(31, 41, 55)


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{tag}"))
        if node is None:
            node = OxmlElement(f"w:{tag}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = borders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            borders.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "6")
        el.set(qn("w:color"), GRAY)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    rel_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rel_id)
    run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "245A7A")
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_pr.extend([color, underline])
    run.append(r_pr)
    text_el = OxmlElement("w:t")
    text_el.text = text
    run.append(text_el)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)


def set_keep_with_next(paragraph, value=True):
    paragraph.paragraph_format.keep_with_next = value


def add_code(doc, lines):
    for line in lines.strip("\n").splitlines():
        p = doc.add_paragraph(style="Codice")
        p.add_run(line if line else " ")
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def add_bullet(doc, text, level=0):
    style = "List Bullet" if level == 0 else "List Bullet 2"
    p = doc.add_paragraph(text, style=style)
    p.paragraph_format.space_after = Pt(3)
    return p


def add_number(doc, number, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.add_run(f"{number}.  ")
    p.add_run(text)
    p.paragraph_format.space_after = Pt(3)
    return p


def add_para(doc, text, bold_lead=None):
    p = doc.add_paragraph()
    if bold_lead and text.startswith(bold_lead):
        p.add_run(bold_lead).bold = True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p


doc = Document()
sec = doc.sections[0]
sec.page_width = Inches(8.5)
sec.page_height = Inches(11)
sec.top_margin = Inches(0.82)
sec.bottom_margin = Inches(0.75)
sec.left_margin = Inches(0.9)
sec.right_margin = Inches(0.9)

styles = doc.styles
normal = styles["Normal"]
normal.font.name = "Aptos"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
normal.font.size = Pt(10.8)
normal.font.color.rgb = TEXT
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.12

for name, size, before, after in (("Title", 25, 0, 12), ("Heading 1", 17, 16, 7), ("Heading 2", 13, 11, 5), ("Heading 3", 11, 8, 4)):
    st = styles[name]
    st.font.name = "Aptos Display" if name in ("Title", "Heading 1") else "Aptos"
    st._element.rPr.rFonts.set(qn("w:ascii"), st.font.name)
    st._element.rPr.rFonts.set(qn("w:hAnsi"), st.font.name)
    st.font.size = Pt(size)
    st.font.bold = name != "Title"
    st.font.color.rgb = RGBColor(0, 0, 0)
    st.paragraph_format.space_before = Pt(before)
    st.paragraph_format.space_after = Pt(after)
    st.paragraph_format.keep_with_next = True

title_ppr = styles["Title"]._element.get_or_add_pPr()
title_border = title_ppr.find(qn("w:pBdr"))
if title_border is not None:
    title_ppr.remove(title_border)

if "Codice" not in styles:
    code_style = styles.add_style("Codice", WD_STYLE_TYPE.PARAGRAPH)
else:
    code_style = styles["Codice"]
code_style.font.name = "Cascadia Mono"
code_style._element.rPr.rFonts.set(qn("w:ascii"), "Cascadia Mono")
code_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Cascadia Mono")
code_style.font.size = Pt(8.8)
code_style.font.color.rgb = RGBColor(30, 41, 59)
code_style.paragraph_format.left_indent = Inches(0.22)
code_style.paragraph_format.right_indent = Inches(0.12)
code_style.paragraph_format.space_before = Pt(0)
code_style.paragraph_format.space_after = Pt(0)
code_style.paragraph_format.line_spacing = 1.0

# Footer with page field
footer = sec.footer
fp = footer.paragraphs[0]
fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
fr = fp.add_run("Sicurezza delle reti WiFi   |   ")
fr.font.size = Pt(8)
fr.font.color.rgb = RGBColor(90, 100, 110)
fld = OxmlElement("w:fldSimple")
fld.set(qn("w:instr"), "PAGE")
fp._p.append(fld)

# Cover
p = doc.add_paragraph(style="Title")
p.add_run("Sicurezza delle reti WiFi e verifica delle credenziali WPA")
p.alignment = WD_ALIGN_PARAGRAPH.LEFT
# Remove any border inherited from the built-in Title style.
p_pr = p._p.get_or_add_pPr()
p_bdr = p_pr.find(qn("w:pBdr"))
if p_bdr is not None:
    p_pr.remove(p_bdr)
sub = doc.add_paragraph()
sub.add_run("Panoramica dei protocolli, cattura del 4 way handshake e analisi con Aircrack ng").bold = True
sub.runs[0].font.size = Pt(13)
sub.runs[0].font.color.rgb = RGBColor(55, 65, 81)
sub.paragraph_format.space_after = Pt(20)

intro = doc.add_paragraph()
intro.add_run("Scopo").bold = True
intro.add_run("  Questa dispensa riassume i concetti tecnici necessari per comprendere la sicurezza delle reti IEEE 802.11 e per verificare, in un laboratorio autorizzato, la resistenza di una rete WPA o WPA2 Personal a un attacco a dizionario offline.")

scope = doc.add_paragraph()
scope.add_run("Ambito etico e legale").bold = True
scope.add_run("  Le procedure operative devono essere eseguite esclusivamente su hotspot, access point e client propri, oppure con autorizzazione scritta del titolare. La cattura passiva può comunque raccogliere metadati di reti vicine; la trasmissione di frame di deautenticazione può interrompere connessioni e non è inclusa nella procedura consigliata.")

doc.add_paragraph("Versione aggiornata al 21 settembre 2026", style="Subtitle")
doc.add_page_break()

doc.add_heading("Indice", level=1)
for item in [
    "1  Concetti fondamentali delle reti WiFi",
    "2  Evoluzione da WEP a WPA3",
    "3  Il 4 way handshake WPA2",
    "4  Procedura di laboratorio con Aircrack ng",
    "5  Principali categorie di attacco",
    "6  Limiti della verifica a dizionario",
    "7  Configurazione consigliata per un hotspot",
    "8  Proposta di metodologia sperimentale",
    "9  Riferimenti",
]:
    p = doc.add_paragraph(item)
    p.paragraph_format.left_indent = Inches(0.18)
    p.paragraph_format.space_after = Pt(4)

doc.add_heading("Sintesi", level=1)
add_para(doc, "WEP e WPA con TKIP sono protocolli superati. WPA2 con AES CCMP rimane adeguato quando la passphrase è lunga e imprevedibile, ma il suo 4 way handshake consente di verificare password candidate offline. WPA3 Personal usa SAE e riduce sostanzialmente questa possibilità, purché dispositivi, firmware e modalità di transizione siano configurati correttamente. In un audit reale, la qualità della password, gli aggiornamenti, WPS, Protected Management Frames e la validazione dei certificati nelle reti Enterprise incidono quanto il nome del protocollo.")

doc.add_heading("1  Fondamenti delle reti WiFi", level=1)
add_para(doc, "Una rete WiFi usa lo standard IEEE 802.11. L'access point trasmette frame di gestione che descrivono la rete e coordina l'associazione dei client. Una scheda in modalità gestita riceve normalmente il traffico necessario alla propria connessione; in monitor mode espone invece al sistema i frame 802.11 osservati sul canale selezionato.")

terms = [
    ("ESSID o SSID", "Nome logico della rete visualizzato dagli utenti."),
    ("BSSID", "Indirizzo MAC che identifica una specifica radio o istanza dell'access point."),
    ("Canale", "Porzione dello spettro radio su cui avviene la comunicazione."),
    ("Station", "Dispositivo client osservato o associato a un access point."),
    ("EAPOL", "Formato usato nello scambio di autenticazione che include il 4 way handshake."),
    ("PSK", "Segreto condiviso usato nelle reti Personal; nella pratica deriva dalla passphrase."),
    ("PMF", "Protected Management Frames, protezione per determinati frame di gestione."),
]
t = doc.add_table(rows=1, cols=2)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
t.autofit = False
t.columns[0].width = Inches(1.65)
t.columns[1].width = Inches(4.95)
hdr = t.rows[0].cells
hdr[0].text, hdr[1].text = "Termine", "Significato"
set_repeat_table_header(t.rows[0])
for c in hdr:
    set_cell_shading(c, NAVY)
    c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    for r in c.paragraphs[0].runs:
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
for idx, (a, b) in enumerate(terms):
    cells = t.add_row().cells
    cells[0].text, cells[1].text = a, b
    if idx % 2:
        for c in cells:
            set_cell_shading(c, PALE)
    for c in cells:
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(c)
set_table_borders(t)

doc.add_heading("2  Evoluzione da WEP a WPA3", level=1)
add_para(doc, "I nomi WEP, WPA, WPA2 e WPA3 descrivono generazioni differenti di protezione. La sicurezza effettiva dipende anche dalla modalità Personal o Enterprise, dal cifrario negoziato, dalla qualità delle credenziali e dall'implementazione dei dispositivi.")

protocols = [
    ("WEP", "RC4 e IV corto", "Protocollo compromesso; il recupero statistico della chiave è praticabile."),
    ("WPA", "TKIP e RC4", "Soluzione transitoria ormai obsoleta; non deve essere usata."),
    ("WPA2 Personal", "PSK e AES CCMP", "Ancora valido con passphrase robusta; espone la verifica offline delle candidate."),
    ("WPA2 Enterprise", "802.1X EAP e RADIUS", "Adatto alle organizzazioni se il metodo EAP e i certificati sono configurati correttamente."),
    ("WPA3 Personal", "SAE e PMF", "Preferibile sui dispositivi moderni; resiste meglio agli attacchi a dizionario offline."),
    ("WPA3 Enterprise", "802.1X e suite moderne", "Include una modalità di sicurezza a 192 bit per ambienti sensibili."),
    ("Enhanced Open", "OWE", "Cifra reti senza password, ma non autentica l'identità dell'access point."),
]
t = doc.add_table(rows=1, cols=3)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
t.autofit = False
widths = [1.38, 1.6, 3.55]
for i, w in enumerate(widths):
    t.columns[i].width = Inches(w)
for i, val in enumerate(("Protocollo", "Meccanismo", "Valutazione")):
    t.rows[0].cells[i].text = val
    set_cell_shading(t.rows[0].cells[i], NAVY)
    for r in t.rows[0].cells[i].paragraphs[0].runs:
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
set_repeat_table_header(t.rows[0])
for idx, row in enumerate(protocols):
    cells = t.add_row().cells
    for i, val in enumerate(row):
        cells[i].text = val
    if idx % 2:
        for c in cells:
            set_cell_shading(c, PALE)
    for c in cells:
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(c)
set_table_borders(t)

doc.add_heading("WEP", level=2)
add_para(doc, "WEP impiega RC4 con vettori di inizializzazione troppo corti e una costruzione crittografica debole. Il riutilizzo degli IV consente di ricavare statisticamente la chiave dopo aver raccolto traffico sufficiente. Una password lunga non corregge il difetto strutturale del protocollo.")

doc.add_heading("WPA e TKIP", level=2)
add_para(doc, "WPA fu progettato come misura transitoria per hardware nato con WEP. TKIP introdusse contatori, mixing delle chiavi e controlli di integrità, ma conservò RC4 e oggi è considerato obsoleto.")

doc.add_heading("WPA2", level=2)
add_para(doc, "WPA2 con AES CCMP offre una cifratura solida. Nella modalità Personal, tutti i dispositivi condividono una passphrase. La cattura di un'autenticazione permette di provare offline password candidate. La modalità Enterprise usa invece 802.1X ed EAP, normalmente con un server RADIUS e credenziali individuali.")

doc.add_heading("WPA3", level=2)
add_para(doc, "WPA3 Personal sostituisce il tradizionale scambio PSK con Simultaneous Authentication of Equals, un Password Authenticated Key Exchange. Una registrazione passiva non offre lo stesso controllo offline economico disponibile con WPA2 PSK. WPA3 richiede inoltre Protected Management Frames. Restano rilevanti gli aggiornamenti, le vulnerabilità di implementazione e i rischi introdotti dalla modalità mista WPA2 WPA3.")

doc.add_heading("WPS", level=2)
add_para(doc, "WiFi Protected Setup non è una versione di WPA. È una procedura di configurazione semplificata. Le implementazioni basate sul vecchio PIN possono indebolire una rete anche quando la passphrase WPA2 è robusta; se non necessario, WPS dovrebbe essere disabilitato.")

doc.add_heading("3  Il 4 way handshake WPA2", level=1)
add_para(doc, "Nel caso WPA2 Personal, la passphrase non viene trasmessa via radio. La passphrase e l'SSID vengono elaborati per derivare la Pairwise Master Key. Durante l'handshake, access point e client scambiano nonce e altre informazioni e derivano una Pairwise Transient Key. I codici di integrità dei messaggi consentono di verificare che entrambi conoscano il segreto corretto.")
for idx, text in enumerate([
    "L'access point invia un nonce e avvia lo scambio.",
    "Il client genera il proprio nonce, deriva le chiavi temporanee e restituisce un messaggio protetto da MIC.",
    "L'access point verifica il MIC e comunica i parametri della chiave di gruppo.",
    "Il client conferma l'installazione delle chiavi e la connessione può proseguire.",
], 1):
    add_number(doc, idx, text)
add_para(doc, "La verifica a dizionario ricostruisce localmente la derivazione per ogni password candidata e confronta il risultato con il materiale catturato. Il file non contiene quindi un hash semplice della password e Aircrack ng non decifra direttamente il segreto.")

doc.add_heading("4  Procedura di laboratorio con Aircrack ng", level=1)
add_para(doc, "La procedura seguente usa una scheda WiFi compatibile con monitor mode e si limita alla cattura passiva. I nomi delle interfacce possono variare. Nell'esempio, wlan0 è l'interfaccia gestita e wlan0mon è quella creata da Airmon ng.")

doc.add_heading("Preparazione dell'interfaccia", level=2)
add_code(doc, """
iw dev
sudo airmon-ng
sudo airmon-ng check
sudo airmon-ng start wlan0
""")
add_para(doc, "Se NetworkManager o wpa supplicant cambiano continuamente canale, Airmon ng può arrestare i processi interferenti. Il comando successivo interrompe temporaneamente la normale connettività WiFi del computer:")
add_code(doc, "sudo airmon-ng check kill")

doc.add_heading("Ricognizione passiva", level=2)
add_code(doc, "sudo airodump-ng wlan0mon")
add_para(doc, "Nell'output si annotano il BSSID dell'hotspot, il canale, l'ESSID e la modalità di sicurezza. PWR rappresenta la potenza ricevuta e non fornisce una distanza affidabile. La sezione STATION elenca i client osservati.")

doc.add_heading("Cattura mirata", level=2)
add_code(doc, """
sudo airodump-ng --channel CH \\
  --bssid AA:BB:CC:DD:EE:FF \\
  --write hotspot wlan0mon
""")
add_para(doc, "Airodump ng genera file come hotspot 01 cap e hotspot 01 csv. Per produrre un nuovo handshake senza trasmettere frame di disturbo, si può disattivare e riattivare il WiFi di un proprio client e ricollegarlo all'hotspot. Quando la cattura è valida, Airodump ng mostra l'indicazione WPA handshake associata al BSSID.")

doc.add_heading("Verifica dei frame EAPOL", level=2)
add_para(doc, "In Wireshark si applica il filtro di visualizzazione eapol. Da terminale si può usare:")
add_code(doc, "tshark -r hotspot-01.cap -Y eapol")
add_para(doc, "Il numero di frame non basta a dimostrare che la cattura sia utilizzabile: i messaggi devono appartenere allo stesso scambio e presentare contatori di replay e nonce coerenti.")

doc.add_heading("Verifica a dizionario", level=2)
add_code(doc, """
aircrack-ng -w /usr/share/wordlists/rockyou.txt \\
  -b AA:BB:CC:DD:EE:FF hotspot-01.cap
""")
add_para(doc, "Se RockYou è distribuito in forma compressa, è possibile verificarne la presenza e decomprimerlo una sola volta:")
add_code(doc, """
ls -lh /usr/share/wordlists/rockyou*
sudo gzip -dk /usr/share/wordlists/rockyou.txt.gz
""")

doc.add_heading("Ripristino della rete", level=2)
add_code(doc, """
sudo airmon-ng stop wlan0mon
sudo systemctl restart NetworkManager
""")

h5 = doc.add_heading("5  Principali categorie di attacco", level=1)
h5.paragraph_format.page_break_before = True
attacks = [
    ("Dizionario su WPA e WPA2", "Cattura di materiale di autenticazione e prova offline di password prevedibili.", "Passphrase casuale e lunga."),
    ("PMKID", "Alcune configurazioni espongono materiale utilizzabile per una verifica offline senza handshake completo.", "Password robusta, firmware aggiornato, WPA3 quando possibile."),
    ("WEP statistico", "Recupero della chiave sfruttando IV e debolezze di RC4.", "Eliminare WEP."),
    ("Deautenticazione", "Frame contraffatti provocano disconnessioni o riconnessioni.", "PMF, WPA3, monitoraggio."),
    ("Evil twin", "Un AP falso imita l'ESSID per attirare client o credenziali.", "Validazione dei certificati, consapevolezza, profili gestiti."),
    ("Rogue AP", "Un access point non autorizzato viene collegato alla rete interna.", "Inventario, NAC e rilevamento wireless."),
    ("WPS PIN", "Ricerca del PIN o sfruttamento di implementazioni vulnerabili.", "Disabilitare WPS PIN."),
    ("Downgrade", "Un dispositivo viene indotto a usare una modalità compatibile meno forte.", "WPA3 only e Transition Disable quando supportato."),
    ("KRACK", "Reinstallazione delle chiavi in implementazioni WPA2 vulnerabili.", "Aggiornare client e access point."),
    ("Dragonblood", "Problemi nelle prime implementazioni SAE e nella mappatura verso gruppi crittografici.", "Firmware recente e SAE Hash to Element."),
    ("Jamming", "Interferenza intenzionale contro la disponibilità del canale radio.", "Rilevamento radio e procedure operative; la cifratura non lo impedisce."),
]
t = doc.add_table(rows=1, cols=3)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
t.autofit = False
for i, w in enumerate([1.28, 3.05, 2.15]):
    t.columns[i].width = Inches(w)
for i, val in enumerate(("Categoria", "Meccanismo", "Difesa principale")):
    c = t.rows[0].cells[i]
    c.text = val
    set_cell_shading(c, NAVY)
    for r in c.paragraphs[0].runs:
        r.font.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
set_repeat_table_header(t.rows[0])
for idx, row in enumerate(attacks):
    cells = t.add_row().cells
    for i, val in enumerate(row):
        cells[i].text = val
    if idx % 2:
        for c in cells:
            set_cell_shading(c, PALE)
    for c in cells:
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_margins(c, top=85, bottom=85)
set_table_borders(t)

doc.add_heading("6  Limiti della verifica a dizionario", level=1)
add_bullet(doc, "Aircrack ng trova la password soltanto se una candidata corretta è presente nel dizionario o nello spazio di ricerca configurato.")
add_bullet(doc, "Un esito negativo non dimostra che la rete sia invulnerabile; dimostra soltanto che il tentativo eseguito non ha individuato la credenziale.")
add_bullet(doc, "Una passphrase casuale di 16 o più caratteri rende impraticabili molti attacchi a dizionario e forza bruta.")
add_bullet(doc, "L'SSID partecipa alla derivazione della chiave in WPA e WPA2; tabelle precalcolate per un SSID non si trasferiscono automaticamente a un altro.")
add_bullet(doc, "Le prestazioni dipendono dall'hardware, dal formato di cattura, dall'algoritmo e dalla qualità delle candidate, ma la velocità non compensa uno spazio di ricerca con elevata entropia.")

doc.add_heading("7  Configurazione consigliata per un hotspot", level=1)
for text in [
    "Preferire WPA3 Personal quando tutti i dispositivi lo supportano.",
    "In alternativa usare WPA2 Personal con AES CCMP, senza TKIP.",
    "Usare una password casuale di almeno 16 o 20 caratteri e non riutilizzata altrove.",
    "Disabilitare WEP, WPA legacy e WPS PIN.",
    "Aggiornare regolarmente il sistema operativo del telefono e i dispositivi client.",
    "Evitare la modalità WPA2 WPA3 mista se non serve per compatibilità.",
    "Impostare PMF come obbligatorio quando il dispositivo lo consente.",
    "Controllare periodicamente l'elenco dei client associati all'hotspot.",
]:
    add_bullet(doc, text)

doc.add_heading("8  Proposta di metodologia sperimentale", level=1)
add_para(doc, "Per una tesi, l'esperimento può confrontare la resistenza di diverse classi di password senza tentare intrusioni su reti esterne. Si configura un access point di laboratorio, si registrano handshake prodotti da client controllati e si misura il comportamento degli strumenti su insiemi di candidate predefiniti.")
for idx, text in enumerate([
    "Definire tre classi: password umana prevedibile, passphrase composta da parole casuali e password generata casualmente.",
    "Usare lo stesso SSID, lo stesso hardware e lo stesso file di cattura per mantenere costanti le condizioni.",
    "Registrare dimensione del dizionario, numero di candidate provate, tempo, hardware e versione del software.",
    "Distinguere tra password trovata, spazio di ricerca esaurito e test interrotto per limite temporale.",
    "Ripetere le misure e riportare mediana, variabilità e limiti sperimentali.",
    "Confrontare i risultati WPA2 PSK con il diverso modello di attacco di WPA3 SAE, senza presentare SAE come immune a password deboli o implementazioni difettose.",
], 1):
    add_number(doc, idx, text)
add_para(doc, "Il dataset pubblicato non dovrebbe contenere credenziali reali, indirizzi MAC personali o catture di terzi. È preferibile usare BSSID sintetici nelle figure e conservare i file cap grezzi in un archivio di ricerca con accesso controllato.")

doc.add_heading("9  Riferimenti", level=1)
refs = [
    ("Aircrack ng  Airodump ng documentation", "https://www.aircrack-ng.org/doku.php?id=airodump-ng"),
    ("Aircrack ng  Aircrack ng documentation", "https://www.aircrack-ng.org/doku.php?id=aircrack-ng"),
    ("Aircrack ng  Cracking WPA", "https://www.aircrack-ng.org/doku.php?id=cracking_wpa"),
    ("Aircrack ng  WPA capture analysis", "https://www.aircrack-ng.org/doku.php?id=wpa_capture"),
    ("Android Open Source Project  WPA3 and WiFi Enhanced Open", "https://source.android.com/docs/core/connect/wifi-wpa3-owe"),
    ("NIST Special Publication 800 153  Guidelines for Securing Wireless Local Area Networks", "https://csrc.nist.gov/pubs/sp/800/153/final"),
]
for idx, (label, url) in enumerate(refs, 1):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.first_line_indent = Inches(-0.25)
    p.add_run(f"{idx}.  ")
    add_hyperlink(p, label, url)
    p.add_run(f". Accesso 21 settembre 2026. {url}")

doc.add_heading("Nota terminologica", level=2)
add_para(doc, "Nel linguaggio informale si parla spesso di hash da crackare. Nel caso WPA2 PSK è più preciso parlare di materiale di autenticazione che consente la verifica offline di password candidate. La distinzione evita di confondere il 4 way handshake con un database di hash statici delle password.")

# Keep headings and table intro paragraphs tidy
for p in doc.paragraphs:
    if p.style.name.startswith("Heading"):
        set_keep_with_next(p)

# Metadata
doc.core_properties.title = "Sicurezza delle reti WiFi e verifica delle credenziali WPA"
doc.core_properties.subject = "Protocolli WiFi e laboratorio Aircrack ng"
doc.core_properties.author = ""
doc.core_properties.keywords = "WiFi, WPA2, WPA3, Aircrack-ng, sicurezza informatica"

doc.save(OUT)
print(OUT)
