"""
Document parsing module supporting multiple formats:
- PDF (PyMuPDF/fitz)
- HTML (BeautifulSoup)
- JSON
- Markdown
- Plain text
"""
from typing import Dict
import json
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import markdown
from pathlib import Path
import re


class DocumentParser:
    """Parse documents from various formats into clean text with metadata."""
    
    def parse_pdf(self, file_path: str) -> Dict:
        """
        Parse PDF file using PyMuPDF.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with text and metadata
        """
        doc = fitz.open(file_path)
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(page_text)
        
        doc.close()
        
        # Combine all pages
        full_text = "\n\n".join(text_parts)
        full_text = self._clean_text(full_text)
        
        filename = Path(file_path).name
        
        return {
            "text": full_text,
            "metadata": {
                "source": filename,
                "type": "pdf"
            }
        }
    
    def parse_html(self, file_path: str) -> Dict:
        """
        Parse HTML file using BeautifulSoup.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            Dictionary with text and metadata
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text(separator='\n', strip=True)
        text = self._clean_text(text)
        
        filename = Path(file_path).name
        
        return {
            "text": text,
            "metadata": {
                "source": filename,
                "type": "html"
            }
        }
    
    def parse_json(self, file_path: str) -> Dict:
        """
        Parse JSON file and extract text content.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with text and metadata
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON to readable text
        json_text = json.dumps(data, indent=2, ensure_ascii=False)
        json_text = self._clean_text(json_text)
        
        filename = Path(file_path).name
        
        return {
            "text": json_text,
            "metadata": {
                "source": filename,
                "type": "json"
            }
        }
    
    def parse_txt(self, file_path: str) -> Dict:
        """
        Parse plain text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dictionary with text and metadata
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
        
        text = self._clean_text(text)
        filename = Path(file_path).name
        
        return {
            "text": text,
            "metadata": {
                "source": filename,
                "type": "txt"
            }
        }
    
    def parse_md(self, file_path: str) -> Dict:
        """
        Parse Markdown file.
        
        Args:
            file_path: Path to Markdown file
            
        Returns:
            Dictionary with text and metadata
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML first, then extract text
        html = markdown.markdown(md_content)
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)
        text = self._clean_text(text)
        
        filename = Path(file_path).name
        
        return {
            "text": text,
            "metadata": {
                "source": filename,
                "type": "md"
            }
        }
    
    def parse_file(self, file_path: str) -> Dict:
        """
        Parse a file based on its extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with text and metadata
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self.parse_pdf(file_path)
        elif extension in ['.html', '.htm']:
            return self.parse_html(file_path)
        elif extension == '.json':
            return self.parse_json(file_path)
        elif extension in ['.md', '.markdown']:
            return self.parse_md(file_path)
        elif extension == '.txt':
            return self.parse_txt(file_path)
        else:
            # Try as text file
            return self.parse_txt(file_path)
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text by removing excessive whitespace and normalizing.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple blank lines to double
        text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces to single
        text = re.sub(r' +\n', '\n', text)  # Trailing spaces
        text = re.sub(r'\n +', '\n', text)  # Leading spaces after newline
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
