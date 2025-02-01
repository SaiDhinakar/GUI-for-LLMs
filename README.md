# ollama-gui

## Overview
The `ollama-gui` project is a modern and user-friendly graphical user interface (GUI) designed to interact with Ollama's local LLMs (Language Learning Models). This application allows users to easily retrieve available models and switch between them for a seamless experience.

## Features
- User-friendly interface for interacting with local LLMs.
- Options to automatically retrieve and switch between models.
- Chat interface for real-time interaction with the selected model.

## Project Structure
```
ollama-gui
├── src
│   ├── main.py                # Entry point of the application
│   ├── api                    # Contains API-related functionality
│   │   ├── __init__.py
│   │   └── ollama_client.py   # Handles communication with local LLMs
│   ├── gui                    # Contains GUI components
│   │   ├── __init__.py
│   │   ├── main_window.py      # Main application window layout
│   │   ├── model_selector.py    # Model selection functionality
│   │   └── chat_window.py      # Chat interface for interaction
│   └── utils                  # Utility functions
│       ├── __init__.py
│       └── config.py          # Configuration settings management
├── requirements.txt           # Project dependencies
├── .gitignore                 # Files and directories to ignore by Git
└── README.md                  # Project documentation
```

## Installation
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd ollama-gui
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
To run the application, execute the following command:
```
python src/main.py
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.
