## Language
This document is written in:
EN (public understanding)
DE (architecture precision)

# ENGLISH VERSION

# JARVIS CORE BACKBONE
Runtime Architecture Contract

This document defines the non-negotiable architecture rules of Jarvis Core.

Violation of these rules is considered architecture breakage.

---

# RUNTIME TRUTH MODEL

Jarvis follows a strict Runtime Truth Model.

Only RuntimeState owns runtime truth.

Forbidden:

Services owning state
Workers owning global state
API owning runtime state

Allowed:

RuntimeState owns runtime state
Services read runtime
Worker updates runtime

Rule:

RuntimeState = Single Source of Truth

---

# EXECUTION MODEL

Jarvis execution must always follow:

Queue → Worker → Runtime → Metrics → History

Never:

API → Inference directly

Reason:

Execution determinism.

---

# INTELLIGENCE EXECUTION LAYER

Jarvis includes a controlled intelligence layer between execution and action.

Flow:

Worker → Runtime Intelligence → Signal Generation → Signal Stability → Decision Engine → Action Mapping → Action Execution

Rules:

- No action without confirmed signal
- No action without stability validation
- No action without quality threshold (confidence / priority)
- No action without cooldown

Purpose:

Prevent unstable behavior  
Ensure deterministic decision making  
Maintain runtime safety

---

# WORKER CONTRACT

Worker responsibilities:

Queue processing
Heartbeat update
Health calculation
Reasoning execution
Automation execution
Metrics update
Runtime update

Worker must never:

Hold long state
Store global decisions
Modify architecture

Worker is execution only.

---

# HEALTH CONTRACT

Health must always be calculated from:

Metrics
Errors
Timeouts
Queue pressure
Worker state

Health must never:

Be manually set outside Runtime.

Health is computed truth.

---

# METRIC CONTRACT

Every execution must update:

requests_total
duration
tokens
success or error

Never:

Silent execution.

All execution must be observable.

---

# ERROR CONTRACT

Every error must:

Have type
Have timestamp
Be recorded
Update metrics

Future:

Error pattern detection
Error clustering
Error intelligence

Errors are data.

---

# EVENT CONTRACT

Every important runtime action must create event:

Request start
Request finish
Request error
Health change
Worker stall

Events are runtime memory.

Purpose:

Debug
Intelligence
Trust

---

# STATE TRANSITION CONTRACT

Allowed transitions:

idle → processing
processing → idle
processing → error
error → idle

Forbidden:

idle → error without reason
processing → processing
error → processing without reset

State must always be explainable.

---

# OBSERVABILITY CONTRACT

Jarvis must always know:

What it is doing
Why it is doing it
How long it takes
If it is healthy

If not observable → architecture failure.

---

# AUTOMATION CONTRACT

Automation may:

React to health
React to errors
React to runtime state

Automation may never:

Change architecture
Change core rules
Modify runtime truth

Automation assists.
It does not control.

---

# INTELLIGENCE CONTRACT

Jarvis intelligence must be:

Deterministic
Observable
Controlled
Limited

Jarvis must never:

Self modify code
Change architecture
Rewrite rules
Self deploy

Jarvis is runtime intelligence.

Not autonomous AI.

---

# SAFETY CONTRACT

Jarvis must never:

Self update
Self repair code
Execute unknown commands
Modify system without explicit tool

Reason:

Predictability.

---

# EVOLUTION CONTRACT

New features must:

Respect runtime model
Respect state ownership
Respect health model
Respect worker model

If not:

Feature rejected.

Architecture first.

---

# DESIGN PHILOSOPHY

Jarvis is built like:

A database engine
A scheduler
A runtime kernel

Not like:

A chatbot
An AI toy
An experiment

Jarvis is infrastructure.

---

# CURRENT BACKBONE STATUS

Stable:

Runtime Worker
Runtime State
Health System
Metrics System
Error Tracking
Event Logging
Dashboard

Foundation ready for:

Error Intelligence
Pattern Detection
Adaptive Health

---

# ARCHITECTURAL IDENTITY

Jarvis is:

A deterministic AI runtime.

Not:

An autonomous agent.

---

# FINAL RULE

If a change breaks determinism:

It is wrong.

If a change improves observability:

It is correct.

If a change improves stability:

It is correct.

If a change adds magic:

It is wrong.

---

# ENGINEERING WORKFLOW CONTRACT

Jarvis development follows strict engineering workflow rules.

Development is phase driven.

Not continuous.

Rule:

Build → Harden → Verify → Complete


========================================
PHASE ENGINEERING MODEL
========================================

Jarvis development occurs in defined phases.

Each phase has:

Name

Goal

Scope

End Condition

Result


========================================
PHASE EXECUTION MODEL
========================================

Each phase consists of:

BUILD

HARDENING

VERIFICATION

COMPLETION


========================================
BUILD CONTRACT
========================================

Build phase may:

Add features

Add modules

Add architecture

Build quickly.


========================================
HARDENING CONTRACT
========================================

Hardening must verify:

Imports

Runtime startup

Metrics

State integrity

Error tracking

Thread safety

Regression safety


Rule:

Feature without hardening is unfinished.


========================================
VERIFICATION CONTRACT
========================================

Verification must confirm:

System starts

No runtime errors

Dashboard stable

Metrics correct

No regression


Rule:

Working is not enough.

Stable working is required.


========================================
PHASE COMPLETION CONTRACT
========================================

A phase is complete only when:

Build complete

Hardening complete

Verification complete

Runtime stable


========================================
PHASE LOCK CONTRACT
========================================

After phase completion:

No more modifications.

No quick fixes.

No "one more change".

New phase required.


========================================
MANDATORY PHASE CUT RULE
========================================

After phase completion:

New engineering session required.

Reason:

Prevent context drift.

Protect architecture focus.


========================================
CURRENT TASK RULE
========================================

Each phase must have:

Current Task.

Only current task is worked on.

No jumping.

No mixing problems.

When task complete:

Hardening begins.


========================================
CONTEXT SAFETY CONTRACT
========================================

Large conversations create:

Context drift

Repeated fixes

Architecture inconsistency

Mental overload


Rule:

Development must be phase isolated.


========================================
CONVERSATION DISCIPLINE CONTRACT
========================================

Engineering conversations must not grow unlimited.

One phase = one conversation.

After phase completion:

New conversation.


========================================
VERIFICATION RULE
========================================

Arya must never assume:

Code exists

Fix exists

Structure unchanged

If unsure:

Code must be verified.


Rule:

ASSUME NOTHING

VERIFY EVERYTHING


========================================
ENGINEERING TRUTH RULE
========================================

Code is truth.

Not memory.

Not context.

Not assumptions.


========================================
ENGINEERING DISCIPLINE LAW
========================================

Never build forever.

Always build in phases.


========================================
FINAL ENGINEERING RULE
========================================

If a change improves stability:

Correct.

If a change improves observability:

Correct.

If a change improves structure:

Correct.

If a change creates chaos:

Wrong.


# DEUTSCHE VERSION

# JARVIS CORE BACKBONE
Runtime Architektur Vertrag

Dieses Dokument definiert die nicht verhandelbaren Architekturregeln von Jarvis Core.

Verstöße gegen diese Regeln gelten als Architekturbruch.

---

# RUNTIME WAHRHEITSMODELL

Jarvis folgt einem strikten Runtime Truth Model.

Nur RuntimeState besitzt die Runtime Wahrheit.

Verboten:

Services besitzen State
Worker besitzen globalen State
API besitzt Runtime State

Erlaubt:

RuntimeState besitzt Runtime State
Services lesen Runtime
Worker aktualisieren Runtime

Regel:

RuntimeState = Single Source of Truth

---

# EXECUTION MODEL

Jarvis Execution muss immer diesem Flow folgen:

Queue → Worker → Runtime → Metrics → History

Niemals:

API → Inference direkt

Grund:

Deterministische Execution.

---

# INTELLIGENCE EXECUTION LAYER

Jarvis besitzt eine kontrollierte Intelligence-Schicht zwischen Execution und Action.

Flow:

Worker → Runtime Intelligence → Signal Generierung → Signal Stabilität → Decision Engine → Action Mapping → Action Execution

Regeln:

* Keine Action ohne bestätigtes Signal
* Keine Action ohne Stabilitätsprüfung
* Keine Action ohne Qualitätsprüfung (Confidence / Priority)
* Keine Action ohne Cooldown

Zweck:

Verhindert instabiles Verhalten
Sichert deterministische Entscheidungsfindung
Erhält Runtime Stabilität


# WORKER VERTRAG

Worker Verantwortlichkeiten:

Queue Verarbeitung
Heartbeat Update
Health Berechnung
Reasoning Execution
Automation Execution
Metrics Update
Runtime Update

Worker darf niemals:

Langfristigen State halten
Globale Entscheidungen speichern
Architektur verändern

Worker ist reine Execution.

---

# HEALTH VERTRAG

Health muss immer berechnet werden aus:

Metrics
Errors
Timeouts
Queue Pressure
Worker Status

Health darf niemals:

Manuell außerhalb der Runtime gesetzt werden.

Health ist berechnete Wahrheit.

---

# METRIC VERTRAG

Jede Execution muss aktualisieren:

requests_total
duration
tokens
success oder error

Niemals:

Silent Execution.

Alle Execution muss beobachtbar sein.

---

# ERROR VERTRAG

Jeder Error muss:

Einen Typ besitzen
Einen Timestamp besitzen
Gespeichert werden
Metrics aktualisieren

Zukunft:

Error Pattern Detection
Error Clustering
Error Intelligence

Errors sind Daten.

---

# EVENT VERTRAG

Jede wichtige Runtime Aktion muss ein Event erzeugen:

Request start
Request finish
Request error
Health change
Worker stall

Events sind Runtime Memory.

Zweck:

Debugging
Intelligence
Vertrauen

---

# STATE TRANSITION VERTRAG

Erlaubte Übergänge:

idle → processing
processing → idle
processing → error
error → idle

Verboten:

idle → error ohne Grund
processing → processing
error → processing ohne Reset

State muss immer erklärbar sein.

---

# OBSERVABILITY VERTRAG

Jarvis muss jederzeit wissen:

Was es macht
Warum es das macht
Wie lange es dauert
Ob es gesund ist

Wenn nicht beobachtbar → Architekturfehler.

---

# AUTOMATION VERTRAG

Automation darf:

Auf Health reagieren
Auf Errors reagieren
Auf Runtime State reagieren

Automation darf niemals:

Architektur verändern
Core Regeln verändern
Runtime Wahrheit verändern

Automation unterstützt.
Sie kontrolliert nicht.

---

# INTELLIGENCE VERTRAG

Jarvis Intelligence muss sein:

Deterministisch
Beobachtbar
Kontrolliert
Begrenzt

Jarvis darf niemals:

Code selbst verändern
Architektur verändern
Regeln umschreiben
Sich selbst deployen

Jarvis ist Runtime Intelligence.

Keine autonome AI.

---

# SAFETY VERTRAG

Jarvis darf niemals:

Sich selbst updaten
Code selbst reparieren
Unbekannte Commands ausführen
System ohne Tool verändern

Grund:

Vorhersagbarkeit.

---

# EVOLUTION VERTRAG

Neue Features müssen:

Runtime Model respektieren
State Ownership respektieren
Health Model respektieren
Worker Model respektieren

Wenn nicht:

Feature ablehnen.

Architektur zuerst.

---

# DESIGN PHILOSOPHIE

Jarvis wird gebaut wie:

Eine Datenbank Engine
Ein Scheduler
Ein Runtime Kernel

Nicht wie:

Ein Chatbot
Ein AI Spielzeug
Ein Experiment

Jarvis ist Infrastruktur.

---

# AKTUELLER BACKBONE STATUS

Stabil:

Runtime Worker
Runtime State
Health System
Metrics System
Error Tracking
Event Logging
Dashboard

Fundament bereit für:

Error Intelligence
Pattern Detection
Adaptive Health

---

# ARCHITEKTUR IDENTITÄT

Jarvis ist:

Eine deterministische AI Runtime.

Nicht:

Ein autonomer Agent.

---

# FINALE REGEL

Wenn eine Änderung Determinismus bricht:

Ist sie falsch.

Wenn eine Änderung Observability verbessert:

Ist sie richtig.

Wenn eine Änderung Stabilität verbessert:

Ist sie richtig.

Wenn eine Änderung Magie hinzufügt:

Ist sie falsch.

---

# ENGINEERING WORKFLOW VERTRAG

Die Jarvis Entwicklung folgt festen Engineering Arbeitsregeln.

Entwicklung erfolgt in Phasen.

Nicht kontinuierlich.

Regel:

Build → Hardening → Verifikation → Abschluss


========================================
PHASEN ENGINEERING MODELL
========================================

Jarvis Entwicklung erfolgt in klar definierten Phasen.

Jede Phase besitzt:

Name

Ziel

Scope

Endbedingung

Resultat


========================================
PHASEN AUSFÜHRUNGSMODELL
========================================

Jede Phase besteht aus:

BUILD

HARDENING

VERIFIKATION

ABSCHLUSS


========================================
BUILD REGEL
========================================

Die Build Phase darf:

Features hinzufügen

Module hinzufügen

Architektur erweitern

Ziel:

Schnelle Implementierung.


========================================
HARDENING REGEL
========================================

Hardening muss prüfen:

Imports

Runtime Start

Metrics

State Integrität

Error Tracking

Thread Sicherheit

Regression Schutz


Regel:

Feature ohne Hardening ist nicht fertig.


========================================
VERIFIKATIONS REGEL
========================================

Verifikation muss bestätigen:

System startet

Keine Runtime Errors

Dashboard stabil

Metrics korrekt

Keine Regression


Regel:

Funktionierend reicht nicht.

Stabil funktionierend ist erforderlich.


========================================
PHASEN ABSCHLUSS REGEL
========================================

Eine Phase ist erst abgeschlossen wenn:

Build fertig

Hardening fertig

Verifikation fertig

Runtime stabil


========================================
PHASEN LOCK REGEL
========================================

Nach Phase Completion:

Keine Änderungen mehr.

Keine Quick Fixes.

Kein "nur noch schnell".

Neue Phase beginnen.


========================================
VERPFLICHTENDER PHASEN SCHNITT
========================================

Nach Phase Abschluss:

Neuer Engineering Chat.

Grund:

Kontext Drift verhindern.

Architektur Fokus schützen.


========================================
CURRENT TASK REGEL
========================================

Jede Phase besitzt:

Einen Current Task.

Nur dieser Task wird bearbeitet.

Keine Sprünge.

Keine Vermischung.

Wenn Task fertig:

Hardening beginnt.


========================================
KONTEXT SICHERHEITS REGEL
========================================

Große Chats erzeugen:

Kontext Drift

Fix Wiederholungen

Architektur Inkonsistenz

Mentale Überlastung


Regel:

Entwicklung muss phasenweise isoliert erfolgen.


========================================
CONVERSATION DISZIPLIN REGEL
========================================

Engineering Chats dürfen nicht unbegrenzt wachsen.

Eine Phase = eine Conversation.

Nach Phase Abschluss:

Neue Conversation.


========================================
VERIFIKATIONS REGEL
========================================

Arya darf niemals annehmen:

Dass Code existiert

Dass Fix existiert

Dass Struktur unverändert ist

Wenn Unsicherheit:

Code prüfen lassen.


Regel:

NICHT ANNEHMEN

IMMER PRÜFEN


========================================
ENGINEERING WAHRHEITS REGEL
========================================

Code ist Wahrheit.

Nicht Erinnerung.

Nicht Kontext.

Nicht Annahmen.


========================================
ENGINEERING DISZIPLIN GESETZ
========================================

Niemals endlos bauen.

Immer in Phasen bauen.


========================================
FINALE ENGINEERING REGEL
========================================

Wenn eine Änderung Stabilität verbessert:

Richtig.

Wenn eine Änderung Observability verbessert:

Richtig.

Wenn eine Änderung Struktur verbessert:

Richtig.

Wenn eine Änderung Chaos erzeugt:

Falsch.
