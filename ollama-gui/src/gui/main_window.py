from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QComboBox, QPushButton, QTextBrowser, QLineEdit,
                           QLabel, QFrame, QSplitter, QScrollArea, QFileDialog, QPlainTextEdit, 
                           QGroupBox, QTextEdit, QListWidget, QListWidgetItem, QGraphicsOpacityEffect,
                           QApplication, QToolButton)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtGui import QFont, QColor, QPalette, QClipboard
import markdown2
import requests
import json
import os
import shutil
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

        # Add copy button
        copy_button = QToolButton()
        copy_button.setText("📋")
        copy_button.setStyleSheet("""
            QToolButton {
                background-color: transparent;
                border: none;
                color: #8e8ea0;
                font-size: 14px;
            }
            QToolButton:hover {
                color: #ffffff;
            }
        """)
        copy_button.clicked.connect(lambda: self.copy_to_clipboard(text))
        layout.addWidget(copy_button, alignment=Qt.AlignRight)

        # Add animation effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(500)  # 0.5 seconds
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.animation.start()

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

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
            QTextEdit {
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
            QListWidget {
                background-color: #3c3c3c;
                color: white;
                border: 1px solid #4d4d4d;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #4d4d4d;
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
        
        # New Conversation button
        self.new_convo_btn = QPushButton("New Conversation")
        self.new_convo_btn.clicked.connect(self.new_conversation)
        sidebar_layout.addWidget(self.new_convo_btn)
        
        # File interaction section in sidebar
        file_group = QGroupBox("Uploaded Files")
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
        
        # List of uploaded files
        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.select_file)
        file_layout.addWidget(self.file_list)
        
        # Add to sidebar
        sidebar_layout.addWidget(file_group)
        sidebar_layout.addStretch()
        
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
        
        # Input area at the bottom
        input_widget = QWidget()
        input_layout = QHBoxLayout(input_widget)
        
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Send a message...")
        self.input_field.setMaximumHeight(100)
        self.input_field.textChanged.connect(self.adjust_input_height)
        
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
        self.uploaded_files = {}  # Dictionary to store file paths and their content
        self.current_file = None  # Currently selected file

        # Timer for file deletion
        self.file_deletion_timer = QTimer()
        self.file_deletion_timer.timeout.connect(self.delete_uploaded_file)
        self.file_deletion_timer.setInterval(300000)  # 5 minutes

    def adjust_input_height(self):
        doc_height = self.input_field.document().size().height()
        self.input_field.setFixedHeight(min(int(doc_height) + 20, 100))

    def get_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags")
            models = [model["name"] for model in response.json()["models"]]
            self.model_selector.clear()
            self.model_selector.addItems(models)
        except Exception as e:
            self.add_message(f"Error loading models: {str(e)}", is_user=False)

    def add_message(self, text, is_user=True):
        message = ChatMessage(text, is_user)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, message)
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
                self.uploaded_files[file_path] = self.file_handler.current_file_content
                self.file_list.addItem(os.path.basename(file_path))
                self.add_message(
                    f"File loaded: {os.path.basename(file_path)}. You can now ask questions about it.",
                    is_user=False
                )
                # Start the file deletion timer
                self.file_deletion_timer.start()

    def select_file(self, item):
        file_name = item.text()
        for file_path in self.uploaded_files:
            if os.path.basename(file_path) == file_name:
                self.current_file = file_path
                self.file_handler.current_file_content = self.uploaded_files[file_path]
                self.file_handler.file_path = file_path
                self.add_message(f"Selected file: {file_name}", is_user=False)
                break

    def delete_uploaded_file(self):
        if self.current_file:
            try:
                os.remove(self.current_file)
                self.uploaded_files.pop(self.current_file)
                self.file_list.clear()
                for file_path in self.uploaded_files:
                    self.file_list.addItem(os.path.basename(file_path))
                self.current_file = None
                self.file_handler.current_file_content = None
                self.file_handler.file_path = None
                self.add_message("Uploaded file has been deleted due to inactivity.", is_user=False)
            except Exception as e:
                self.add_message(f"Error deleting file: {str(e)}", is_user=False)
        self.file_deletion_timer.stop()

    def new_conversation(self):
        self.messages_container.deleteLater()
        self.messages_container = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.addStretch()
        self.messages_layout.setSpacing(20)
        self.scroll_area.setWidget(self.messages_container)
        self.add_message("Started a new conversation.", is_user=False)

    def send_message(self):
        message = self.input_field.toPlainText()
        if not message.strip():
            return
            
        # Handle file context in all prompts
        if self.file_handler.current_file_content:
            prompt = f"""This is my file name {os.path.basename(self.file_handler.file_path)}, 
it having content are:
{self.file_handler.current_file_content}

User question: {message}"""
        else:
            prompt = message
        
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