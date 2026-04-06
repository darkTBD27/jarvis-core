from inference.inference import run_inference, inference_status, ai_ready

class AIService:

```
def __init__(self):
    self.service_name = "jarvis-ai-core"

def infer(self, prompt:str):
    return run_inference(prompt)

def status(self):
    return inference_status()

def ready(self):
    return ai_ready()
```

ai_service = AIService()
