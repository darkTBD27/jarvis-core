import logging
logger = logging.getLogger("jarvis")

class LearningController:

    def __init__(self):
        self.step_size = 0.005

    def adjust_confidence(self, current, success: bool, context: dict = None):
        return current
