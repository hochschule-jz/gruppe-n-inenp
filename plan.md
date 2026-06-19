# Drive & Decide — offene Punkte

**Stand:** Implementierung, Kostenmodell, Final Paper und Präsentationsdeck sind fertig.
Offen sind im Wesentlichen nur noch die Demo-Assets (Foto/Video), der finale Build und etwas
Logistik.

**Erledigt:**
- **Implementierung steht und ist getestet:** Backend als IaC-Template
  (`backend/template.yaml`, inkl. S3-Web-Hosting und Loadgen-Lambda), ESP32-Firmware
  (TCRT5000), Web-View und Virtualisierung (Load Generator + Ampelsystem). Der physische
  Demo-Prototyp (vier Stellplätze, ESP32 + Sensoren) wurde end-to-end mit der Web-App verifiziert.
- **Kostenmodell mit echten Daten gefüllt:** `cost-model/` rechnet CAPEX/OPEX/TCO/ROI/Break-Even
  + Sensitivität für 200/400/500 mit real recherchierten, in `assumptions.toml` belegten Werten
  (AWS-Listenpreise, WIPARK-Tarif, österreichische Handwerker-/Strompreise, Vendor-Hardwarepreise,
  Smart-Parking-Literatur). Ergebnisfiguren sind generiert. Headline-Kennzahl:
  Break-Even ~0,03–0,04 pp; CAPEX 7.616–13.784 €, OPEX 468–891 €/Jahr.
- **Final Paper fertig:** Evaluierungskapitel komplett (PoC, Probleme, Methodik, Ergebnisse +
  Tabellen + Figuren), Abstract & Conclusion an die Ergebnisse angeglichen, Einleitungs-Roadmap
  verweist auf das Evaluierungskapitel. Das Paper kompiliert (15 Seiten).
- **Präsentation erstellt:** `presentation/Drive-and-Decide.pptx` (16 Folien, native Diagramme
  mit den echten Zahlen, Sprechernotizen). Platzhalter für Prototyp-Foto (Folie 8) und
  Demo-Fallback-Video (Folie 9).
- **Deployment automatisiert:** `deploy.sh` (Bash) und `deploy.ps1` (PowerShell; GarageSpots-
  Quoting-Bug via `params.json` + `file://` behoben). Die API-URL kommt aus dem Stack-Output
  (gitignoriertes `web/.env.production`), nicht hartkodiert.
- **AWS lauffähig:** Backend läuft im Free-Account (Julian) und im Lab des Kollegen; die
  fehlende DynamoDB-Berechtigung der LabRole wurde behoben.
- **Aufräumen/Konsistenz:** Branches `esp32`/`methodik`/`windows-deploy-script` gemergt
  (`evaluation` obsolet); garage2 durchgehend auf 400 Stellplätze vereinheitlicht; Terminologie
  auf „serverless" vereinheitlicht (Vorgabe Lehrender); veraltete Docs (cost-model-README,
  Haupt-READMEs, Präsentations-Briefing) aktualisiert.

**Offen:**

1. **Demo-Assets:** Foto des physischen Prototyps und vertontes Demo-Fallback-Video erstellen
   und in die Deck-Platzhalter (Folien 8, 9) einsetzen. (Kollege nimmt auf.)

2. **Finaler Build & Korrektur:** Paper final kompilieren (Overleaf/VS Code), Seitenzahl gegen
   die Kurs-Vorgabe prüfen, Korrekturlesen.

3. **Git:** Offene Working-Tree-Änderungen committen (Paper-Edits, `deploy.ps1`, `.gitignore`,
   Deck, Konsistenz-Edits); obsoleten Remote-Branch `evaluation` löschen.

4. **Optionale Verfeinerung:** Reale eu-central-1-AWS-Preise und gemessene Lambda-Laufzeit über
   die jetzt funktionierende CLI ziehen; für einen plausiblen ROI einen realistischen
   Nutzen-Erfassungsanteil ansetzen (aktuell wird bewusst der Break-Even berichtet).

5. **Logistik:** Präsentationstermin/-format klären, Sprecheraufteilung, ggf. FH-Foliendesign;
   AWS-Stack nach Abgabe abbauen (Free-Account-Credits schonen).
