import magic
import PyPDF2
from docx import Document
import chardet
import os

class DocumentParser:
    @staticmethod
    def parse_document(file_path):
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        
        try:
            if file_type == 'application/pdf':
                return DocumentParser._parse_pdf(file_path)
            elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                return DocumentParser._parse_docx(file_path)
            else:
                return DocumentParser._parse_text(file_path)
        except Exception as e:
            return f"Error parsing file: {str(e)}"

    @staticmethod
    def _parse_pdf(file_path):
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text

    @staticmethod
    def _parse_docx(file_path):
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])

    @staticmethod
    def _parse_text(file_path):
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            encoding = chardet.detect(raw_data)['encoding']
            return raw_data.decode(encoding or 'utf-8')