class ModelSelector:
    def __init__(self, available_models):
        self.available_models = available_models
        self.selected_model = None

    def display_models(self):
        print("Available Models:")
        for index, model in enumerate(self.available_models):
            print(f"{index + 1}: {model}")

    def select_model(self, model_index):
        if 0 <= model_index < len(self.available_models):
            self.selected_model = self.available_models[model_index]
            print(f"Selected Model: {self.selected_model}")
        else:
            print("Invalid model selection.")

    def get_selected_model(self):
        return self.selected_model if self.selected_model else "No model selected."