# Drive & Decide — Presentation Brief

Everything needed to build the **final group presentation** (PPTX) for the Cloud
Computing course. This is a planning document: structural guidance is in English,
**slide titles and on-slide bullet text are pre-written in German** (the deck
language — all three papers are German) so they can be pasted straight in.

> **Status / blocker:** the *Ergebnisse* (results) and *Diskussion* slides need the
> cost-benefit numbers, which **do not exist in the repo yet** (`cost-model/` is only
> a README; the Final Paper `evaluation.tex` is a stub). Those slides are templated
> with `[TBD]` markers. See [§8 Benötigte Daten](#8-benötigte-daten--offene-punkte).

---

## 1. Eckdaten (constraints)

| Punkt | Wert |
|---|---|
| Format | Klassische PPTX, Gruppenpräsentation |
| Dauer | **20–25 Minuten** (Ziel: ~22 min Vortrag + Demo, Puffer einplanen) |
| Pflichtinhalte | Problemstellung · Methodik · Ergebnisse · **Diskussion** der Ergebnisse |
| Demo | **Pflicht** — gewählt: **Hybrid** (Live-Demo mit Video-Fallback) |
| Gruppe | Maximilian Seier · Julian Zankl (FH Burgenland) |
| Sprache | **Deutsch** (bestätigt) |
| Titel | **Drive & Decide** — *Wirtschaftlichkeit eines IoT-basierten Smart-Parking-Systems* |
| Publikum | Lehrende + Peers; technisch versiert, aber Fokus auf Methodik & Wirtschaftlichkeit |

## 2. Kernbotschaft (the one thing they should remember)

> *Drive & Decide* zeigt, wie ein **ereignisgetriebenes, IoT-basiertes Smart-Parking-System
> auf serverlosem AWS** die laufenden Cloud-Kosten **messbar** macht — und liefert
> Parkhausbetreibern damit eine **nachvollziehbare Kosten-Nutzen-Grundlage**
> (TCO, ROI, Break-Even) für die Investitionsentscheidung.

Roter Faden: *Problem → Forschungslücke (Wirtschaftlichkeit, nicht Machbarkeit) →
Prototyp (physisch + virtuell) → messbarer Datenfluss → Kostenmodell → Kennzahlen → Diskussion.*

## 3. Sprecheraufteilung

Zwei Vortragende, **~11 min je Person** — die konkrete Aufteilung übernimmt das Team selbst.
Bewährt: Wechsel nach Themenblöcken (nicht innerhalb einer Folie) und **ein gemeinsamer
Demo-Teil** (eine Person bedient, eine erklärt). Optionaler Vorschlag: eine Person
„Problem & Wirtschaftlichkeit" (Folien 3–5, 10–15), die andere „Technische Lösung" (Folien 6–9).

## 4. Zeit- & Foliengerüst (timing budget)

Target ~22 min so you land safely inside 20–25. ~16 Inhaltsfolien + Backup.

| # | Folie | Min |
|---|---|---|
| 1 | Titel | 0.5 |
| 2 | Agenda | 0.5 |
| 3 | Problemstellung & Motivation | 3.0 |
| 4 | Forschungsfrage & Stand des Wissens | 2.0 |
| 5 | Lösungsansatz & Use Case | 1.5 |
| 6 | Systemarchitektur | 2.5 |
| 7 | Datenfluss in 6 Schritten | 2.0 |
| 8 | Prototyp: physisch + virtuell | 1.5 |
| 9 | **DEMO** | 5.0 |
| 10 | Kosten-Nutzen-Modell (Aufbau) | 2.5 |
| 11 | Ergebnisse: Kosten (CAPEX/OPEX) | 1.5 |
| 12 | Ergebnisse: Kennzahlen (TCO/ROI/Break-Even) | 2.0 |
| 13 | Ergebnisse: Sensitivitätsanalyse | 1.0 |
| 14 | Diskussion & Limitationen | 2.0 |
| 15 | Fazit & Ausblick | 1.0 |
| 16 | Backup (Q&A) | — |
| | **Summe** | **~22.5** |

## 5. Folienweise Gliederung (slide-by-slide)

Each slide: on-slide German content + English guidance + visual + source.

### Folie 1 — Titel
- **Inhalt (DE):** „Drive & Decide" · Untertitel „Wirtschaftlichkeit eines IoT-basierten
  Smart-Parking-Systems auf serverlosem AWS" · Maximilian Seier & Julian Zankl ·
  FH Burgenland · Cloud Computing · Datum.
- **Visual:** Projekt-Wortmarke + dezentes Ampel-Motiv (grün/gelb/rot). Optional ein Foto
  des physischen Prototyps.

### Folie 2 — Agenda
- **Inhalt (DE):** Problem · Stand des Wissens · Lösungsansatz · Architektur & Demo ·
  Kosten-Nutzen-Modell · Ergebnisse · Diskussion · Fazit.
- **Notes:** 15 Sekunden, nur Orientierung.

### Folie 3 — Problemstellung & Motivation
- **Inhalt (DE):**
  - Steigende Motorisierung in Österreich: 2025 +54.208 Pkw, höchste Neuzulassungen seit
    2019, >7,5 Mio. Kfz; zunehmend große Fahrzeuge (SUV) → Druck auf städtische Flächen.
  - Pendler aus dem Umland nach Wien, oft mit dem Pkw → Parkplatzsuche endet in Parkhäusern
    mit nur statischer/lokaler Anzeige → wiederholtes Anfahren, Zeitverlust, **Suchverkehr**,
    Emissionen, Lärm.
  - **Betreibersicht:** Druck, Stellplätze effizient auszulasten und gegen alternative
    Mobilität zu bestehen — aber Wirtschaftlichkeit eines SPS unklar.
  - **Sicherheit:** Parkinfo-Suche während der Fahrt lenkt ab; ~⅓ der Verkehrstoten in
    Österreich durch Unachtsamkeit/Ablenkung.
- **Visual:** 2–3 Kennzahlen groß (54.208; >7,5 Mio.; ⅓), Icon Suchverkehr.
- **Quelle:** `Final Paper/section/introduction.tex`.

### Folie 4 — Forschungsfrage & Stand des Wissens
- **Inhalt (DE):**
  - Literatur deckt viele Einzelaspekte ab: Sensorik (IR, Kamera, Induktion), Edge/Fog/Cloud,
    dynamische Preis-/Routingansätze, Fahrerablenkung.
  - **Forschungslücke:** nicht die technische *Machbarkeit*, sondern ein **reproduzierbarer
    Bewertungsrahmen aus Sicht des Betreibers**.
  - **Forschungsfrage:** Rechtfertigt der erwartete Nutzen die Investitions- und Betriebskosten
    eines IoT-SPS — und ab wann (Break-Even)?
- **Visual:** Schichtenmodell (Sensor → Übertragung → Verarbeitung → Anwendung) mit markierter
  Lücke „Wirtschaftlichkeit".
- **Quelle:** `related_work.tex`.

### Folie 5 — Lösungsansatz & Use Case
- **Inhalt (DE):**
  - **Use Case:** mittelgroßer Wiener Parkhausbetreiber, **200–500 Stellplätze**, innerstädtisch,
    schwankende Auslastung.
  - Betreiber = Entscheidungsträger; Investition in Sensorik + Konnektivität + Cloud = zu
    bewertende Maßnahme.
  - **Drive & Decide** = realitätsnaher Prototyp **+** Kosten-Nutzen-Modell.
- **Visual:** Ein Satz-Claim + Use-Case-Skizze (Garage, Pfeil „lohnt sich das?").
- **Quelle:** `methodology.tex` (Use Case, Abgrenzung).

### Folie 6 — Systemarchitektur
- **Inhalt (DE):** Serverlose AWS-Architektur: **AWS IoT Core** (Geräteanbindung + MQTT-Routing)
  → **AWS Lambda** (ereignisgetriebene Verarbeitung) → **Amazon DynamoDB** (aktueller Status)
  → **API Gateway** (Ausgabe). Keine dauerhaft laufenden Server → Voraussetzung für messbare
  Kosten.
- **Visual:** **`Final Paper/fig/architecture.jpg`** (existiert bereits) — als zentrale Folie groß.
- **Quelle:** `methodology.tex` §Technische Beschreibung; `backend/template.yaml`, `backend/README.md`.

### Folie 7 — Datenfluss in 6 Schritten
- **Inhalt (DE):** (1) Sensor erkennt Statuswechsel → (2) Mikrocontroller baut MQTT-Nachricht
  (sensorId, spotId, ts, raw, status) → (3) Publish auf `parking/garage1/spot/<id>` → (4) IoT-Rule
  → Validierungs-Lambda (Schema/Wertebereich) → DynamoDB → (5) Aggregations-Lambda
  (Auslastung + Ampel) → (6) API Gateway → Web/Navigation.
- **Notes:** Betonen: **jede Nachricht = 1 IoT-Nachricht = 1 Lambda-Aufruf = 1 DynamoDB-Write**
  → genau das macht OPEX messbar. Ampelschwellen: 🟢 <0,70 · 🟡 0,70–0,90 · 🔴 >0,90.
- **Visual:** Nummerierter Fluss als Pfeilkette; ein Beispiel-JSON klein eingeblendet.
- **Quelle:** `methodology.tex` §Datenfluss; `docs/contract.md` §0.3/§0.6.

### Folie 8 — Prototyp: physisch + virtuell
- **Inhalt (DE):**
  - **Physisch (Realismus):** Box, deren Deckel eine Parkgarage mit **4 markierten Stellplätzen**
    ist; je ein **TCRT5000-IR-Sensor** unter dem Platz, ausgelesen vom **ESP32**, Publish via MQTT.
    (Matchbox-Fahrzeuge als Belegung.)
  - **Virtuell (Skalierung):** Software-Lastgenerator simuliert **bis ~250 Stellplätze** über
    **denselben** MQTT-Pfad + Einfahrts-Ampel — realistische Last & Cloud-Kosten ohne Hardware.
  - Beide nutzen identisches Topic + JSON-Schema (gemeinsamer „Contract").
- **Visual:** links Foto der Box, rechts Screenshot Großgarage-View; Pfeil „gleicher Pfad".
- **Quelle:** `firmware/`, `virtual/load_generator/`, `virtual/traffic_light/`, `docs/contract.md`.

### Folie 9 — DEMO  ⟶ siehe [§6 Demo-Plan](#6-demo-plan)
- **Inhalt (DE):** Überschrift „Live-Demo (mit Video-Fallback)" + 3 Stichpunkte, was gezeigt wird:
  physische Belegung → Web-Update; Großgarage → „Andrang simulieren" → Ampel grün→gelb→rot.
- **Notes:** Diese Folie ist nur der „Rahmen"; der Bildschirm wechselt zur App/zum Video.

### Folie 10 — Kosten-Nutzen-Modell (Aufbau)
- **Inhalt (DE):**
  - Sicht des Betreibers, **5-Jahres-Horizont** (Abschreibung IT/Sensorik).
  - **CAPEX:** Sensoren/Stellplatz, Mikrocontroller, Verkabelung, Installation, initiale Cloud-Konfig.
  - **OPEX:** nutzungsabhängige AWS-Kosten (IoT Core, Lambda, DynamoDB, Transfer, Speicher) +
    Wartung, Sensoraustausch, Strom.
  - **4 Nutzenannahmen:** (1) höhere Auslastung durch Auffindbarkeit, (2) dynamische Preise in
    Stoßzeiten, (3) weniger Fehlfahrten/Reputation, (4) Datenverwertung.
  - **4 Kennzahlen:** TCO · ROI · Amortisationsdauer · **Break-Even** (Δ Auslastung in %-Punkten).
  - **Datenquellen:** Markt-/Herstellerpreise · AWS Pricing Calculator · Literaturparameter.
- **Visual:** Waage „Kosten ⇄ Nutzen" + Kennzahlen-Leiste.
- **Quelle:** `methodology.tex` §Kosten-Nutzen-Analyse; `cost-model/README.md`.

### Folie 11 — Ergebnisse: Kosten (CAPEX/OPEX)  `[TBD]`
- **Inhalt (DE):** CAPEX-Aufschlüsselung (Tabelle) + monatliche/jährliche OPEX, abgeleitet aus
  **gemessener** AWS-Nutzung der Lastläufe (iotMessages/Lambda/DynamoDB-Writes aus dem Run-Manifest).
- **Visual:** gestapeltes Balkendiagramm CAPEX vs. OPEX(5J); kleine Tabelle.
- **Daten benötigt:** siehe §8. **Hook:** `RunStats.manifest()['awsUsageEstimate']` liefert die
  Mengengerüste für die OPEX-Hochrechnung.

### Folie 12 — Ergebnisse: Kennzahlen  `[TBD]`
- **Inhalt (DE):** TCO (5J), ROI, Amortisation (Monate), Break-Even (%-Punkte) — je als große Zahl.
- **Visual:** 4 KPI-Kacheln; optional Break-Even-Kurve (Nutzen vs. Kosten über Zeit).
- **Daten benötigt:** §8.

### Folie 13 — Ergebnisse: Sensitivitätsanalyse  `[TBD]`
- **Inhalt (DE):** Variation von **Stellplatzzahl (200/350/500)**, Sensor-Stückkosten und
  unterstellter Auslastungssteigerung → wie robust ist die Aussage?
- **Visual:** Tornado-Diagramm oder Linienschar ROI/Break-Even über Stellplatzzahl.
- **Daten benötigt:** §8.

### Folie 14 — Diskussion & Limitationen
- **Inhalt (DE):**
  - **Interpretation:** Unter welchen Bedingungen trägt sich das System? Welcher Parameter dominiert
    (i. d. R. Auslastungssteigerung & Stellplatzzahl)? Skaleneffekt: OPEX/Platz sinkt mit Größe.
  - **Enabler:** ereignisgetriebenes Serverless macht OPEX überhaupt belastbar erfassbar.
  - **Limitationen:** kein Sensor-Benchmark, keine Endnutzerstudie, Sicherheitseffekte nur
    qualitativ, Ergebnisse hängen an offen dokumentierten Modellannahmen.
- **Visual:** „Lohnt sich ab …"-Aussage + 3 Limitationen als Liste.
- **Quelle:** `methodology.tex` §Abgrenzung; `conclusion.tex`.

### Folie 15 — Fazit & Ausblick
- **Inhalt (DE):** Investitionsentscheidungen sollten auf TCO/ROI/Break-Even beruhen; Serverless
  ist Voraussetzung für belastbare OPEX. **Ausblick:** reale Messreihen, mehr Sensoren/Stellplätze,
  Navigations-Anbindung, dynamische Tarife.
- **Visual:** eine Merksatz-Zeile (= Kernbotschaft) + Mini-Roadmap.
- **Quelle:** `conclusion.tex`.

### Folie 16 — Backup (für Q&A)
- Ampel-Schwellen & Aggregationslogik · Contract (Topic + JSON-Schema) · IoT-Policy
  (nur Connect+Publish) · Lastprofil-Beispiel (`peak.json`/`offpeak.json`) · `awsUsageEstimate`-Manifest
  · Kostentabelle im Detail · Quellenverzeichnis (`references.bib`).

## 6. Demo-Plan

**⚠️ Größtes Risiko — AWS Learner Lab:** Das Backend läuft im AWS Academy Learner Lab, das
**manuell gestartet werden muss und nur 4 Stunden** läuft. Eine reine Live-Demo hängt damit
davon ab, dass das Lab während des Vortrags aktiv ist und die in der Web-App fest eingebaute
API-URL (`5akjc62zn1…`, siehe `web/.env.production`) noch stimmt. Bei einem Re-Deploy ändert
sich die API-ID. **Empfehlung: hybrid** — Live versuchen, aber ein **aufgezeichnetes Video als
Fallback** bereithalten (das Aufgabenblatt erlaubt Video ausdrücklich).

**Was gezeigt wird (zwei Teile, ~5 min):**
1. **Physisch (Realismus, „Aha-Moment"):** Modell-View (garage1, 4 Plätze, leer = grün). Ein
   Matchbox-Auto auf einen markierten Platz stellen → nach 1–2 s zeigt das Raster den Platz als
   belegt, Auslastung/Ampel aktualisieren sich. Mehrere Plätze belegen → Ampel grün→gelb→rot.
   Dabei den End-to-End-Pfad live erzählen (Sensor→MQTT→IoT Core→Lambda→DynamoDB→API→Web).
2. **Virtuell (Skalierung):** Auf **Großgarage** (garage2, ~250 Plätze) wechseln. Button
   **„Andrang simulieren"** → Loadgen-Lambda publiziert über **denselben** Pfad → Auslastung
   steigt, Heatmap füllt sich, Ampel wechselt. Aussage: so entsteht die OPEX-relevante Last
   ohne Hardware.
3. *(optional, technisch):* Terminal `python -m load_generator --profile load_generator/peak.json
   --transport dry-run --quiet` → Nachrichtenstrom + Manifest (= OPEX-Datenquelle) zeigen.

**Pre-Flight-Checkliste (vor dem Vortrag):**
- [ ] AWS Lab gestartet, Restlaufzeit deckt den Vortragsslot ab (4-h-Fenster bewusst legen).
- [ ] Stack `drive-and-decide` aktiv; API-URL stimmt mit `web/.env.production` überein
      (sonst Web neu bauen oder URL anpassen).
- [ ] Web-App offen & geladen (Modell **und** Großgarage je einmal getestet).
- [ ] ESP32 am Strom, mit **Handy-Hotspot** verbunden, Initial-Publish gesehen (Serial-Monitor).
- [ ] Matchbox-Autos bereit; ein Trockenlauf der Belegung erfolgreich.
- [ ] **Fallback-Video** lokal auf dem Vortragsrechner (nicht streamen) + in die PPTX eingebettet.
- [ ] Bildschirmauflösung/Beamer getestet; Web-Zoom so, dass Ampel & Raster gut sichtbar sind.

## 7. Verfügbare & benötigte Assets

**Vorhanden:**
- Architektur-Diagramm: `Final Paper/fig/architecture.jpg`.
- Web-UI (Screenshots ziehen): Modell- und Großgarage-View, Ampel, Heatmap, Verlauf.
- Lauffähiges Backend/Prototyp für Live-Screens.
- Lastprofile + Manifest-Struktur (`virtual/load_generator/`).

**Noch zu erstellen:**
- **Foto(s) des physischen Prototyps** (Box mit 4 Plätzen, ESP32 innen).
- **Demo-Fallback-Video** (~3–4 min, vertont).
- Diagramme der Ergebnisse (CAPEX/OPEX, KPIs, Sensitivität) — sobald Zahlen vorliegen.
- Ggf. FH-/Kurs-Foliendesign (Corporate Template), falls vorgegeben.

## 8. Benötigte Daten / offene Punkte

Die *Ergebnis-* und *Diskussionsfolien* (11–14) brauchen Zahlen, die es im Repo noch nicht gibt
(`cost-model/` ist leer). Bitte liefern — oder ich helfe beim Aufbau des Kostenmodells:

1. **CAPEX-Eingaben:** Stückkosten TCRT5000-Sensor, ESP32, Verkabelung/Platz, Installationsaufwand
   (h × Satz), initiale Cloud-Konfiguration — je Stellplatz und gesamt für 200/350/500.
2. **OPEX-Eingaben:** gemessene AWS-Nutzung aus Lastläufen (Manifest-Mengen) → Hochrechnung auf
   Monat/Jahr; AWS-Stückpreise (IoT Core, Lambda, DynamoDB, Transfer, Speicher); Wartungs-%,
   Sensor-Lebensdauer/Austauschrate, Stromkosten.
3. **Nutzenparameter:** Basis-Auslastung, angenommene Auslastungssteigerung (%-Punkte),
   Parkerlös (€/Platz·h oder €/belegte Stunde), Aufschlag dynamische Preise, Datenverwertung.
4. **Ergebnis-Kennzahlen:** TCO (5J), ROI, Amortisation, Break-Even — berechnet — + Sensitivitätsspannen.

**Entschieden:** Demo = **Hybrid** (live + Video-Fallback) · Ergebnisfolien = **vorerst
Platzhalter** · Sprecheraufteilung = **durch das Team** · Sprache = **Deutsch**.

**Noch offen:**
- **Kostenmodell-Daten (Punkte 1–4 oben):** sobald verfügbar → Ergebnisfolien 11–14 füllen.
- **Termin/Slot:** Datum; sind 20–25 min inkl. oder exkl. Q&A?
- **Template:** gibt es ein vorgegebenes FH-/Kurs-PPTX-Design?

## 9. Design & Stil

- **Marke:** „Drive & Decide", Subline „Parkleitsystem". Ampel-Motiv (🟢🟡🔴) als wiederkehrendes
  Element, konsistent mit der Web-App.
- **Wenig Text pro Folie** (Stichpunkte, große Zahlen), eine Kernaussage je Folie; Details mündlich.
- Einheitliche Farbpalette aus der Web-UI; serifenlose Schrift; Diagramme statt Textwänden.
- Folien-Fußzeile: „Drive & Decide · Seier & Zankl · FH Burgenland".

## 10. Quellen-Mapping (woher kommt der Inhalt)

| Folie(n) | Quelle im Repo |
|---|---|
| 3 | `Final Paper/section/introduction.tex` |
| 4 | `Final Paper/section/related_work.tex` |
| 5, 10, 14 | `Final Paper/section/methodology.tex` |
| 6, 7 | `methodology.tex` + `backend/template.yaml`, `backend/README.md`, `docs/contract.md` |
| 8, 9 | `firmware/`, `virtual/load_generator/`, `virtual/traffic_light/`, `web/` |
| 11–13 | `cost-model/` (zu erstellen) + Lauf-Manifeste; `evaluation.tex` (Stub) |
| 15 | `Final Paper/section/conclusion.tex` |
| 16 | `docs/contract.md`, `references.bib` |
