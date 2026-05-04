# VERIFY MARKER: y}q.B#qg

from engine.logger import logger

def process_signal(worker_output, snapshot=None):

    """
    Pipeline Entry Point

    dies ist das einzige legitime Eintrittsgate in den Signal-Kontrollpfad
    jeder produktive Signalfluss muss hier durch
    ab hier beginnt der validierte Backbone-kontrollierte Signalpfad
    kein Signal darf den Entscheidungsfluss außerhalb dieses Gates erreichen
    """

    signals = list(worker_output) if isinstance(worker_output, list) else worker_output

    signals = _stage_normalize(signals, snapshot)
    signals = _stage_derive(signals, snapshot)
    signals = _stage_deduplicate(signals, snapshot)
    signals = _stage_evaluate(signals, snapshot)

    return signals


def _stage_normalize(signals, snapshot=None):
    """
    Stage 1: Normalisierung (minimal)

    Ziel:
    - immer Liste
    - jedes Element ist dict

    KEINE:
    - Bewertung
    - Ableitung
    - Mutation von Inhalten
    """

    if signals is None:
        return []

    if not isinstance(signals, list):
        signals = [signals]

    normalized = []

    for s in signals:
        if isinstance(s, dict):
            normalized.append(s)
        else:
            # alles andere wird in dict gehüllt
            normalized.append({
                "type": "unknown",
                "source": "intelligence",
                "severity": "info",
                "payload": {"value": s},
                "metadata": {}
            })

    return normalized


def _stage_derive(signals, snapshot=None):
    return signals


def _stage_deduplicate(signals, snapshot=None):
    """
    Stage 3: Deduplication (light, stateless)

    Ziel:
    - doppelte Signals innerhalb eines Calls entfernen

    KEINE:
    - Runtime-Abhängigkeit
    - Speicherung zwischen Calls
    - komplexe Logik
    """

    seen = set()
    deduped = []

    for s in signals:
        if not isinstance(s, dict):
            # Safety – sollte durch Stage 1 bereits passen
            continue

        # stabiler, deterministischer Schlüssel
        key = (
            s.get("type"),
            s.get("source"),
            s.get("severity"),
            str(s.get("payload"))
        )

        if key in seen:
            continue

        seen.add(key)
        deduped.append(s)

    return deduped


def _stage_evaluate(signals, snapshot=None):
    """
    Stage 4: Bewertung (nur Contract Check – minimal)

    KEINE Bewertung!
    Nur:
    - Struktur prüfen
    - Fehler sichtbar machen
    """

    validated = []

    for s in signals:
        if not isinstance(s, dict):
            logger.warning(f"[PIPELINE] signal not dict: {s}")
            continue

        # minimale Pflichtfelder prüfen (noch nicht vollständig)
        required = ["type", "source", "severity"]

        missing = [k for k in required if k not in s]

        if missing:
            logger.warning(f"[PIPELINE] missing keys {missing} in signal: {s}")

        validated.append(s)

    return validated
