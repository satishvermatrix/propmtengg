"""
Document processing functions for extracting text from various file formats.
"""
import os
import PyPDF2
import docx
import pandas as pd
from utils import count_tokens


def extract_text_from_file(file_path):
    """Extract text content from various file formats"""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        
        elif file_extension == '.docx':
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        elif file_extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        
        elif file_extension in ['.csv']:
            df = pd.read_csv(file_path)
            return df.to_string()
        
        elif file_extension in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
            return df.to_string()
        
        else:
            return f"Unsupported file format: {file_extension}"
    
    except Exception as e:
        return f"Error reading file: {str(e)}"
