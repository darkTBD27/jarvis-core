## Language
This document is written in:
EN (public understanding)
DE (architecture precision)


# ENGLISH VERSION

# JARVIS CORE PRINCIPLES

Jarvis Runtime Engineering Rules

These rules define how Jarvis must be built and evolved.
They are architectural constraints, not suggestions.

Every new component must respect these principles.

---

# CORE RULES

## Rule 1 — Runtime State has exactly one owner

RuntimeState is the Single Source of Truth.

No service may store runtime state.
No worker may maintain global runtime logic.
No duplicated state is allowed.

All runtime truth must flow through RuntimeState.

Reason:

Prevent hidden behavior.
Prevent state drift.
Ensure observability.

---

## Rule 2 — Observability is mandatory

If Jarvis cannot explain its behavior,
the design is incomplete.

Every critical runtime action must be observable.

Runtime must expose:

State
Health
Errors
Events
Performance

No hidden execution.

Reason:

Invisible systems cannot be stabilized.

---

## Rule 3 — Stability before capability

New features must never reduce runtime stability.

If a feature risks:

Determinism
State clarity
Runtime safety

It must not be implemented.

Jarvis evolves only when foundation is stable.

Reason:

Unstable intelligence is failure amplification.

---

## Rule 4 — No hidden state allowed

All runtime relevant state must be:

Explicit
Traceable
Owned

Forbidden:

Implicit state
Side effects
Hidden global logic

Allowed:

Explicit ownership
Controlled state transitions
Observable changes

Reason:

Hidden state destroys predictability.

---

## Rule 5 — Errors are signals, not failures

Errors are runtime intelligence input.

Jarvis must:

Track errors
Classify errors
Understand patterns
Detect instability

Jarvis must never ignore errors.

Reason:

Unobserved failure becomes systemic failure.

---

## Rule 6 — Health is computed, never declared

Health must always be derived from:

Runtime behavior
Error patterns
Queue pressure
Worker performance

Health must never be manually set.

Reason:

Declared health is fiction.
Measured health is reality.

---

## Rule 7 — Determinism before automation

Jarvis must remain predictable.

Automation may only exist if behavior remains explainable.

Forbidden:

Uncontrolled decision loops
Self modifying logic
Hidden AI behavior

Allowed:

Controlled adaptation
Measured adjustments
Observable decision rules

Reason:

Control must exist before autonomy.

---

## Rule 8 — Architecture before features

No feature may violate architecture rules.

When conflict exists:

Architecture wins.

Features must adapt.
Architecture must not.

Reason:

Architecture defines system lifespan.

---

# RUNTIME SAFETY RULES

## Safety Rule — No component may bypass Runtime

All execution must pass through runtime control flow.

Forbidden:

Service → Worker shortcuts
Dashboard → Runtime mutations
Tool → Runtime state changes

Reason:

Control must remain centralized.

---

## Safety Rule — No duplicated ownership

If two components own the same data:

Architecture is broken.

Every runtime structure must have:

One owner
Clear responsibility
Defined access layer

---

## Safety Rule — Intelligence must remain controlled

Jarvis may become intelligent.

Jarvis must never become uncontrollable.

All intelligence must be:

Observable
Deterministic
Bounded
Auditable

---

# EVOLUTION RULES

Jarvis evolves in this order:

1 Stability
2 Observability
3 Intelligence
4 Automation

Never:

Automation before stability.

---

# DEVELOPMENT PHILOSOPHY

Jarvis is built like:

A runtime kernel
A scheduler
A database engine
An observability system

Not like:

A chatbot
An AI experiment
A feature collection

---

# FINAL RULE

Jarvis must remain:

Predictable
Explainable
Stable

If a change violates these:

The change is wrong.

Not the rule.

---

Jarvis Core Engineering Law.

---

# LEARNING CONTROL LAW

Learning is a strictly passive system layer.

Learning must never execute, control, or override runtime behavior.

---

## ALLOWED

Learning may:

* Analyze historical outcomes
* Derive statistical patterns
* Produce action performance scores

Learning exists only to support decision evaluation.

---

## FORBIDDEN

Learning must NEVER:

* Trigger actions
* Override decisions
* Modify runtime state
* Inject hidden logic
* Bypass decision thresholds

Any violation is considered architecture breakage.

---

## CONTROLLED INFLUENCE

Learning influence is strictly limited to:

* Bounded confidence adjustment
* Bounded priority adjustment

Constraints:

* Must remain within defined min/max limits
* Must be incremental (no jumps)
* Must respect cooldown mechanisms
* Must remain fully observable

Learning may influence decisions.

Learning must never control them.

---

## ENFORCEMENT RULE

If learning behavior becomes:

* Non-deterministic
* Non-observable
* Unbounded

Then:

Learning must be disabled immediately.

---

## REASON

Uncontrolled learning introduces:

Hidden behavior
State instability
Non-deterministic execution

This violates core system principles.

---

## FINAL LAW

Runtime is the authority.

Learning is advisory.

Control is absolute.


# DEUTSCHE VERSION

# JARVIS CORE GESETZBUCH

Jarvis Runtime Engineering Regeln

Diese Regeln definieren, wie Jarvis gebaut und weiterentwickelt werden muss.
Es sind architektonische Rahmenbedingungen – keine Vorschläge.

Jede neue Komponente muss diese Regeln respektieren.

---

# KERNREGELN

## Regel 1 — Runtime State hat genau einen Besitzer

RuntimeState ist die einzige Quelle der Wahrheit (Single Source of Truth).

Kein Service darf Runtime State besitzen.
Kein Worker darf globale Runtime Logik speichern.
Doppelte Zustände sind nicht erlaubt.

Alle Runtime Wahrheit muss über RuntimeState laufen.

Grund:

Verhindert verstecktes Verhalten.
Verhindert State Drift.
Garantiert Observability.

---

## Regel 2 — Observability ist Pflicht

Wenn Jarvis sein Verhalten nicht erklären kann,
ist das Design unvollständig.

Jede kritische Runtime Aktion muss sichtbar sein.

Die Runtime muss sichtbar machen:

State
Health
Errors
Events
Performance

Keine versteckte Execution.

Grund:

Unsichtbare Systeme können nicht stabilisiert werden.

---

## Regel 3 — Stabilität vor Fähigkeit

Neue Features dürfen niemals Runtime Stabilität gefährden.

Wenn ein Feature Risiken erzeugt für:

Determinismus
State Klarheit
Runtime Sicherheit

Dann darf es nicht implementiert werden.

Jarvis entwickelt sich nur auf stabiler Basis weiter.

Grund:

Instabile Intelligenz verstärkt Fehler.

---

## Regel 4 — Kein versteckter Zustand

Jeder runtime-relevante Zustand muss sein:

Explizit
Nachvollziehbar
Klar zugeordnet

Verboten:

Impliziter State
Side Effects
Versteckte globale Logik

Erlaubt:

Klare Ownership
Kontrollierte State Änderungen
Nachvollziehbare Updates

Grund:

Versteckter State zerstört Vorhersagbarkeit.

---

## Regel 5 — Fehler sind Signale, keine Störungen

Fehler sind Runtime Intelligence Input.

Jarvis muss:

Fehler speichern
Fehler klassifizieren
Fehlermuster erkennen
Instabilität erkennen

Jarvis darf Fehler niemals ignorieren.

Grund:

Nicht beobachtete Fehler werden zu Systemproblemen.

---

## Regel 6 — Health wird berechnet, nicht gesetzt

Health muss immer basieren auf:

Runtime Verhalten
Error Patterns
Queue Druck
Worker Performance

Health darf niemals manuell gesetzt werden.

Grund:

Deklarierte Gesundheit ist Illusion.
Gemessene Gesundheit ist Realität.

---

## Regel 7 — Determinismus vor Automation

Jarvis muss vorhersagbar bleiben.

Automation ist nur erlaubt wenn Verhalten erklärbar bleibt.

Verboten:

Unkontrollierte Entscheidungsloops
Selbstmodifizierende Logik
Verstecktes AI Verhalten

Erlaubt:

Kontrollierte Anpassung
Messbare Optimierungen
Beobachtbare Entscheidungsregeln

Grund:

Kontrolle muss vor Autonomie existieren.

---

## Regel 8 — Architektur vor Features

Kein Feature darf Architekturregeln verletzen.

Bei Konflikt gilt:

Architektur gewinnt.

Features müssen sich anpassen.
Architektur nicht.

Grund:

Architektur bestimmt die Lebensdauer eines Systems.

---

# RUNTIME SICHERHEITSREGELN

## Sicherheitsregel — Keine Komponente darf Runtime umgehen

Alle Execution muss durch den Runtime Flow gehen.

Verboten:

Service → Worker Direktzugriff
Dashboard → Runtime Änderungen
Tool → Runtime State Änderungen

Grund:

Kontrolle muss zentral bleiben.

---

## Sicherheitsregel — Keine doppelte Ownership

Wenn zwei Komponenten dieselben Daten besitzen:

Ist die Architektur beschädigt.

Jede Runtime Struktur braucht:

Genau einen Besitzer
Klare Verantwortung
Definierten Zugriff

---

## Sicherheitsregel — Intelligenz muss kontrolliert bleiben

Jarvis darf intelligent werden.

Jarvis darf niemals unkontrollierbar werden.

Alle Intelligence muss sein:

Beobachtbar
Deterministisch
Begrenzt
Nachvollziehbar

---

# EVOLUTIONSREGELN

Jarvis entwickelt sich in dieser Reihenfolge:

1 Stabilität
2 Observability
3 Intelligence
4 Automation

Niemals:

Automation vor Stabilität.

---

# ENTWICKLUNGSPHILOSOPHIE

Jarvis wird gebaut wie:

Ein Runtime Kernel
Ein Scheduler
Eine Datenbank Engine
Ein Observability System

Nicht wie:

Ein Chatbot
Ein AI Experiment
Eine Feature Sammlung

---

# ABSCHLUSSREGEL

Jarvis muss bleiben:

Vorhersagbar
Erklärbar
Stabil

Wenn eine Änderung diese Regeln verletzt:

Ist die Änderung falsch.

Nicht die Regel.

---

Jarvis Core Engineering Gesetzbuch.

---

# LEARNING CONTROL GESETZ

Learning ist eine strikt passive Systemschicht.

Learning darf niemals Runtime Verhalten ausführen, steuern oder überschreiben.

---

## ERLAUBT

Learning darf:

* Vergangene Outcomes analysieren
* Statistische Muster ableiten
* Action Performance bewerten

Learning existiert ausschließlich zur Unterstützung von Entscheidungen.

---

## VERBOTEN

Learning darf NIEMALS:

* Actions auslösen
* Entscheidungen überschreiben
* Runtime State verändern
* Versteckte Logik einbringen
* Decision Thresholds umgehen

Jeder Verstoß gilt als Architekturbruch.

---

## KONTROLLIERTER EINFLUSS

Der Einfluss von Learning ist strikt begrenzt auf:

* Begrenzte Anpassung von Confidence
* Begrenzte Anpassung von Priority

Einschränkungen:

* Innerhalb definierter Min/Max Grenzen
* Schrittweise Anpassung (keine Sprünge)
* Cooldown muss eingehalten werden
* Vollständig beobachtbar

Learning darf Entscheidungen beeinflussen.

Learning darf sie niemals steuern.

---

## DURCHSETZUNGSREGEL

Wenn Learning:

* Nicht-deterministisch wird
* Nicht beobachtbar wird
* Unkontrolliert wächst

Dann gilt:

Learning muss sofort deaktiviert werden.

---

## BEGRÜNDUNG

Unkontrolliertes Learning führt zu:

Verstecktem Verhalten
State Instabilität
Nicht-deterministischem Systemverhalten

Das verletzt die Kernprinzipien.

---

## ABSOLUTES GESETZ

Runtime hat die Kontrolle.

Learning ist beratend.

Kontrolle ist nicht verhandelbar.

