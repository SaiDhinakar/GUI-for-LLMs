from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QTextOption
import markdown2
import re

class MessageWidget(QWidget):
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Role indicator
        role = QLabel("You" if is_user else "Assistant")
        role.setStyleSheet("""
            QLabel {
                color: #8e8ea0;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        layout.addWidget(role)
        
        # Message content
        content = QTextBrowser()
        content.setOpenExternalLinks(True)
        content.setFont(QFont("Inter", 11))
        content.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        
        # Dynamic sizing
        content.document().documentLayout().documentSizeChanged.connect(
            lambda: content.setFixedHeight(
                min(400, int(content.document().size().height()) + 20)
            )
        )
        
        # Set content
        if any(marker in text for marker in ['```', '**', '#', '`', '>', '-', '*', '|']):
            html = markdown2.markdown(text, extras=['fenced-code-blocks', 'tables'])
            content.setHtml(html)
        else:
            content.setPlainText(text)
            
        content.setStyleSheet(f"""
            QTextBrowser {{
                background-color: {'#343541' if is_user else '#444654'};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        layout.addWidget(content)