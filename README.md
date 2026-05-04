# Jarvis Core

Deterministic Runtime Intelligence Infrastructure

Jarvis Core ist eine lokale Runtime Engine für deterministische AI-Ausführung.

Fokus:

* Stabilität
* Observability
* deterministische Entscheidungen
* kontrollierte Automation
* klare Zustandsverantwortung

Jarvis ist kein Chatbot.
Jarvis ist kein Agent.
Jarvis ist ein Runtime-System.

---

# Current Status

Jarvis ist aktuell produktiv:

* Signal-driven ✔
* Decision-based ✔
* Action-controlled ✔
* Outcome-aware ✔
* Learning-enabled (controlled) ✔
* Observable ✔
* Deterministic ✔
* Backbone-hardened ✔
* Runtime live-verified ✔

---

# What Jarvis Does

Jarvis verarbeitet Runtime-Zustände als kontrollierten Ausführungszyklus:

* Runtime-Verhalten beobachten
* Signale erkennen und bestätigen
* Zustände bewerten
* strukturierte Entscheidungen treffen
* kontrollierte Actions ausführen
* Ergebnisse bewerten
* Verhalten begrenzt adaptiv verbessern

Jarvis bleibt dabei deterministisch, beobachtbar und kontrollierbar.

---

# Runtime Backbone

Jarvis läuft auf einem gehärteten Runtime-Backbone.

Produktiv abgesichert:

* Single Source of Truth Runtime
* harte State Ownership
* Write Ownership nur über `RUNTIME_ACCESS`
* deterministische Write-Validierung
* kontrollierte State Transitions
* Cycle / Snapshot Guards
* Snapshot Commit Protection
* Runtime Consistency Validation
* Runtime-Hotpath Guarding

Das Runtime-System akzeptiert keine stillen Mutationen außerhalb des kontrollierten Zugriffspfads.

---

# Runtime Flow

Jarvis arbeitet als kontrollierter Laufzeitkreislauf:

Request
→ Queue
→ Worker
→ Runtime Update
→ Signal Generation
→ Decision Engine
→ Action System
→ Outcome Evaluation
→ Learning Update

---

# Core Modules

### Runtime Intelligence

* Signal-basierte Zustandsanalyse
* Stability Layer
* Signal Decay
* deterministische Runtime-Klassifikation

### Decision Engine

* Confidence / Priority-basierte Entscheidungen
* Score-basierte Trigger-Logik
* kontrollierte Entscheidungsfilter
* deterministische Bewertungslogik

### Action System

* Scale Up
* Scale Down
* Worker Restart
* Cooldown-Schutzmechanismen
* kontrollierte Action-Gates

### Outcome System

* Action-Bewertung
* Success / Failure Tracking
* Queue Impact
* Stability Impact
* Outcome-Rückkopplung

### Learning System

* kontrollierte adaptive Gewichtung
* GOOD / BAD / NEUTRAL Tracking
* kontextbasierte Bewertung

Learning unterstützt Entscheidungen.
Learning ersetzt Entscheidungen nicht.

---

# Runtime Validation

Jarvis validiert aktiv:

* State Transitions
* Write Ownership
* Worker Consistency
* Cycle Integrity
* Snapshot Reihenfolge
* Runtime Invariants
* Guard Violations

Ziel:

deterministisches Laufzeitverhalten ohne stille Inkonsistenzen.

---

# Live Verification

Der Runtime-Core wurde gegen reales Laufzeitverhalten geprüft.

Bestätigt:

* keine stillen Write-Bypässe
* keine State-Corruption
* keine Guard-Bypässe
* keine Snapshot/Cycle-Regression
* keine stillen Inkonsistenzen
* keine Runtime-Hotpath-Regression

Status:

**Live Verification PASS** ✔

---

# Dashboard

![Jarvis Dashboard](docs/dashboard.png)

Zeigt:

* Runtime Status
* Worker Verhalten
* Signal History
* Decision Ergebnisse
* Performance
* Learning State
* Runtime Health

---

# Safety Model

Jarvis bleibt kontrolliert:

* keine Action ohne validiertes Signal
* keine Action ohne Stabilität
* keine Action ohne Thresholds
* keine Action ohne Cooldown
* keine Mutation ohne Write-Gate
* keine Runtime-Änderung ohne Ownership

Learning darf:

* analysieren
* unterstützen
* gewichten

Learning darf NICHT:

* direkt entscheiden
* Runtime überschreiben
* Guards umgehen

---

# Start

bash
docker compose up -d


#Status:

curl localhost:8002/status

#Dashboard:

http://localhost:8002/dashboard/status.html

---

## Usage Notice

This repository is source-available for educational, research, and architectural reference purposes only.

No open-source license is currently granted.
See NOTICE.md and LICENSE for usage restrictions and rights.

---

# Next Step

Nächster technischer Schritt:

struktureller Split des Runtime-Core

* runtime_state.py
* runtime_access.py
* `runtime_snapshot.py`
* `runtime_validation.py`

Ziel:

* kleinere Verantwortungsbereiche
* bessere Wartbarkeit
* bessere Testbarkeit
* identisches Laufzeitverhalten bei sauberer Trennung

---

# Status Summary

Jarvis Core ist ein stabiler, deterministischer Runtime-Control-Systemkern
mit gehärtetem Backbone, kontrollierter Adaptivität und live verifiziertem Runtime-Core.
