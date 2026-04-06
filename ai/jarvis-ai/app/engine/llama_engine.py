import ctypes
import os

LLAMA_LIB = "/engine/llama.cpp/build/src/libllama.so"
MODEL_PATH = "/models/llama3/model.gguf"

class LlamaEngine:

    def __init__(self):

        if not os.path.exists(MODEL_PATH):
            raise Exception("Model not found")

        self.lib = ctypes.CDLL(LLAMA_LIB)

        self.model_path = MODEL_PATH

        self.model_loaded = False

        self.load_model()

    def load_model(self):

        # minimal placeholder
        # echter loader kommt gleich

        self.model_loaded = True

    def health(self):

        return {
            "engine":"loaded",
            "model":self.model_path,
            "status":self.model_loaded
        }
