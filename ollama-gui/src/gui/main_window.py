from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QComboBox, QPushButton, QTextBrowser, QLineEdit,
                           QLabel, QFrame, QSplitter, QScrollArea, QFileDialog, QPlainTextEdit, 
                           QGroupBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette
import markdown2
import requests
import json
import os
from .message_widget import MessageWidget
from .file_handler import FileContextManager

class ChatMessage(QFrame):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.setObjectName("userMessage" if is_user else "assistantMessage")
        
        layout = QVBoxLayout(self)
        
        # Convert markdown to HTML
        html = markdown2.markdown(
            text,
            extras=['fenced-code-blocks', 'tables', 'break-on-newline']
        )
        
        # Create text browser for rendered markdown
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        content.setHtml(html)
        content.setReadOnly(True)
        content.setFont(QFont("Inter", 10))
        layout.addWidget(content)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_handler = FileContextManager()
        self.setWindowTitle("Ollama Chat")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            #sidebar {
                background-color: #252526;
                min-width: 260px;
                max-width: 260px;
                padding: 10px;
            }
            QComboBox, QPushButton {
                background-color: #3c3c3c;
                color: white;
                padding: 8px;
                border-radius: 5px;
                border: 1px solid #4d4d4d;
            }
            QComboBox:hover, QPushButton:hover {
                background-color: #4d4d4d;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: white;
                padding: 12px;
                border: 1px solid #4d4d4d;
                border-radius: 5px;
                font-size: 14px;
            }
            QTextBrowser {
                background-color: #252526;
                color: #fff;
                border: none;
            }
            QScrollArea {
                border: none;
                background-color: #1e1e1e;
            }
            QLabel {
                color: #000;
            }
        """)

        # Main layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        sidebar = QWidget()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Model selector
        model_label = QLabel("Select Model")
        model_label.setStyleSheet("color: white;")
        sidebar_layout.addWidget(model_label)
        
        self.model_selector = QComboBox()
        sidebar_layout.addWidget(self.model_selector)
        
        # Refresh button
        self.refresh_btn = QPushButton("Refresh Models")
        sidebar_layout.addWidget(self.refresh_btn)
        sidebar_layout.addStretch()
        
        # File interaction section in sidebar
        file_group = QGroupBox("File Interaction")
        file_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #4d4d4d;
                padding: 10px;
            }
        """)
        file_layout = QVBoxLayout(file_group)
        
        # File upload button
        self.upload_btn = QPushButton("Upload File")
        self.upload_btn.clicked.connect(self.handle_file_upload)
        file_layout.addWidget(self.upload_btn)
        
        # Add to sidebar
        sidebar_layout.insertWidget(sidebar_layout.count()-1, file_group)
        
        # Chat area
        chat_widget = QWidget()
        chat_widget.setObjectName("chatArea")
        chat_layout = QVBoxLayout(chat_widget)
        
        # Messages container
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.addStretch()
        self.messages_layout.setSpacing(20)
        
        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.messages_container)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: white;
            }
        """)
        chat_layout.addWidget(self.scroll_area)
        
        # Input area
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Send a message...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        chat_layout.addWidget(input_widget)
        
        # Add to main layout
        layout.addWidget(sidebar)
        layout.addWidget(chat_widget)
        
        # Connect signals
        self.refresh_btn.clicked.connect(self.get_models)
        
        # Initialize
        self.get_models()
        self.first_prompt_after_upload = True

    def get_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags")
            models = [model["name"] for model in response.json()["models"]]
            self.model_selector.clear()
            self.model_selector.addItems(models)
        except Exception as e:
            self.add_message(f"Error loading models: {str(e)}", is_user=False)

    def add_message(self, text, is_user=True):
        message = MessageWidget(text, is_user)
        self.messages_layout.insertWidget(self.messages_layout.count()-1, message)
        # Auto scroll to bottom
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def handle_file_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select File",
            "",
            "All Files (*);;PDF Files (*.pdf);;Word Files (*.docx);;Text Files (*.txt)"
        )
        if file_path:
            result = self.file_handler.load_file(file_path)
            if isinstance(result, str):
                self.add_message(f"Error loading file: {result}", is_user=False)
            else:
                self.first_prompt_after_upload = True
                self.add_message(
                    f"File loaded: {os.path.basename(file_path)}. You can now ask questions about it.",
                    is_user=False
                )

    def send_message(self):
        message = self.input_field.text()
        if not message.strip():
            return
            
        # Handle file context in first prompt
        if self.file_handler.current_file_content and self.first_prompt_after_upload:
            prompt = f"""This is my file name {os.path.basename(self.file_handler.file_path)}, 
it having content are:
{self.file_handler.current_file_content}

User question: {message}"""
            self.first_prompt_after_upload = False
        else:
            prompt = self.file_handler.get_context_prompt(message)
        
        self.add_message(message, is_user=True)
        self.input_field.clear()
        
        try:
            model = self.model_selector.currentText()
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": model, "prompt": prompt},
                stream=True
            )
            
            response_text = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode())
                    response_text += data.get("response", "")
            
            self.add_message(response_text, is_user=False)
        except Exception as e:
            self.add_message(f"Error: {str(e)}", is_user=False)