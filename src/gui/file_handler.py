import os
from utils.document_parser import DocumentParser

class FileContextManager:
    def __init__(self):
        self.current_file_content = None
        self.file_path = None
    
    def load_file(self, file_path):
        try:
            content = DocumentParser.parse_document(file_path)
            if isinstance(content, str) and not content.startswith("Error"):
                self.current_file_content = content
                self.file_path = file_path
                return True
            return content
        except Exception as e:
            return str(e)
    
    def get_context_prompt(self, user_message):
        if not self.current_file_content:
            return user_message
            
        return f"""Context from file '{os.path.basename(self.file_path)}':
User question: {user_message}"""