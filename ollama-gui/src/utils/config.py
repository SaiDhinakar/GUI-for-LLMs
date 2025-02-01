def load_config(file_path):
    """Load configuration settings from a JSON file."""
    import json
    try:
        with open(file_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def save_config(file_path, config_data):
    """Save configuration settings to a JSON file."""
    import json
    with open(file_path, 'w') as config_file:
        json.dump(config_data, config_file, indent=4)

def get_default_config():
    """Return a default configuration dictionary."""
    return {
        "selected_model": "default_model",
        "user_preferences": {
            "theme": "light",
            "font_size": 12
        }
    }