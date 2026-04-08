from inference.runtime_errors import get_recent_error_count
from inference.runtime_errors import get_last_error


def analyze_error_patterns():
    """
    Analysiert aktuelle Error Trends.
    Noch keine komplexe Logik – nur Grundlage.
    """

    errors_last_minute = get_recent_error_count(60)
    errors_last_5min = get_recent_error_count(300)

    return {
        "last_minute": errors_last_minute,
        "last_5_minutes": errors_last_5min
    }


def calculate_stability_score():
    """
    Einfacher Stability Score als Startpunkt.
    100 = stabil
    """

    errors = get_recent_error_count(60)

    if errors == 0:
        return 100

    if errors < 3:
        return 85

    if errors < 6:
        return 70

    if errors < 10:
        return 50

    return 25


def detect_runtime_risk():
    """
    Erkennt einfache Risiko Zustände.
    """

    errors = get_recent_error_count(60)

    if errors > 8:
        return "high"

    if errors > 3:
        return "medium"

    return "low"


def get_runtime_intelligence():

    return {
        "error_patterns": analyze_error_patterns(),
        "stability_score": calculate_stability_score(),
        "risk_level": detect_runtime_risk(),
        "error_trend": detect_error_trend(),
        "instability": detect_instability()
    }


def detect_error_trend():
    """
    Erkennt ob Fehler steigen oder fallen.
    """

    last_min = get_recent_error_count(60)
    last_5min = get_recent_error_count(300)

    # einfache Trend Logik
    if last_min > last_5min / 5:
        return "increasing"

    if last_min < last_5min / 10:
        return "decreasing"

    return "stable"


def detect_instability():
    """
    Bewertet Runtime Stabilität.
    """

    errors = get_recent_error_count(60)
    trend = detect_error_trend()

    if errors > 8:
        return "critical"

    if trend == "increasing" and errors > 3:
        return "warning"

    return "stable"
