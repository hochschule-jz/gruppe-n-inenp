# Drive & Decide — offene Punkte

**Erledigt:**
- **Implementierung steht und ist getestet:** Backend als IaC-Template
  (`backend/template.yaml`, inkl. S3-Web-Hosting und Loadgen-Lambda), ESP32-Firmware
  (TCRT5000), Web-View und die Virtualisierung (Load Generator + Ampelsystem, 49 Tests).
  Der physische Demo-Prototyp (vier Stellplätze, ESP32 + Sensoren) wurde end-to-end mit
  der Web-App verifiziert.
- **Kostenmodell-Gerüst:** `cost-model/` ist ein getestetes Python-Paket
  (CAPEX/OPEX/TCO/ROI/Break-Even + Sensitivität für 200/400/500, 22 Tests) — **aber alle
  Eingabewerte sind noch Platzhalter** (`assumptions.toml`, jeweils „VERIFY").
- **Deployment automatisiert:** `deploy.sh` (frisches Lab) sowie Update-/Reset-Wege in
  `backend/DEPLOY.md`. Die API-URL wird aus dem Stack-Output erzeugt (gitignoriertes
  `web/.env.production`), nicht mehr hartkodiert.

**Offen:**

1. **Kostenmodell mit echten Daten füllen** — der Engpass, der fast alles andere freischaltet:
   - **CAPEX:** reale Stückpreise (TCRT5000, ESP32, Verkabelung, Installationssatz, Cloud-Setup).
   - **OPEX:** *gemessene* AWS-Nutzung aus einem Load-Generator-Lauf (Run-Manifest — existiert
     noch nicht) + AWS-Pricing-Calculator-Preise; Wartung, Sensor-Lebensdauer, Strom.
   - **Nutzen:** realer Wiener Tarif, Basisauslastung, Auslastungssteigerung (Literatur).
   - Danach Modell laufen lassen → Kennzahlen, Sensitivität, Diagramme + Annahmen-Tabelle.

2. **Final Paper – Kapitel „Evaluierung"** — auf `main` nur ein leerer Stub; der Entwurf liegt
   auf dem ungemergten Branch `origin/evaluation`. Zu tun: mergen, „Ergebnisse",
   „Berechnung der Kennzahlen" und „Probleme" füllen; offene Review-Punkte beheben
   (Nutzen-Einheit €/belegte-Stunde statt „pro Parkvorgang", Read-Side-/API-Gateway-OPEX,
   fehlende Tabelle `tab:assumptions`).

3. **Abstract & Conclusion angleichen** — der Abstract behauptet bereits Ergebnisse, die noch
   nicht existieren; die Conclusion ist noch der **Position-Paper**-Text („Ausblick auf das
   Final Paper … wird umgesetzt") und muss für das Final Paper neu geschrieben werden.

4. **Präsentation (PPTX) erstellen** — bisher nur das Briefing
   (`presentation/presentation-brief.md`), keine Folien. Ergebnisfolien 11–14 brauchen die
   Zahlen aus Punkt 1. Noch zu erstellen: Foto(s) des Prototyps, Demo-Fallback-Video,
   Ergebnis-Diagramme (CAPEX/OPEX, KPIs, Sensitivität).

5. **Aufräumen / Logistik** — Branches `esp32`/`methodik` prüfen und mergen oder löschen;
   Präsentationstermin/-format und ggf. FH-Foliendesign klären.
