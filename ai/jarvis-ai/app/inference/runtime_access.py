# inference/runtime_access.py
# REDIRECT TO SOURCE OF TRUTH

from inference.runtime_object import RUNTIME_ACCESS

# Falls jemand versucht, das alte Modul zu nutzen, leiten wir ihn einfach um
def get_runtime():
    return RUNTIME_ACCESS

# Wir loggen eine Warnung, damit du weißt, welche Datei noch den alten Pfad nutzt
import logging
logger = logging.getLogger("jarvis")
logger.warning("[DEPRECATION] A module is still using runtime_access.py - Please update to runtime_object.py")
