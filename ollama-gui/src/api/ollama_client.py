class OllamaClient:
    def __init__(self):
        self.models = self.retrieve_available_models()
        self.current_model = None

    def retrieve_available_models(self):
        # Logic to retrieve available models from the local system
        return ["model1", "model2", "model3"]  # Example model names

    def switch_model(self, model_name):
        if model_name in self.models:
            self.current_model = model_name
            return f"Switched to model: {model_name}"
        else:
            return "Model not found."