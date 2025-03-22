# backend/models/document_processor.py
import os
import uuid
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from PIL import Image
import io
from typing import Dict, Any, List, Tuple
import sys

# Fix imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.config import settings

class DocumentProcessor:
    """Process legal documents including PDFs and images"""
    
    def __init__(self):
        """Initialize the document processor"""
        self.upload_dir = settings.UPLOAD_DIR
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save an uploaded file to disk
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        # Create a unique filename to prevent collisions
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save the file
        with open(file_path, "wb") as f:
            f.write(file_content)
            
        return file_path
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, List[str]]:
        """
        Extract text from a PDF file using PyPDF2 and OCR if needed
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Tuple of (extracted text, list of image paths)
        """
        extracted_text = ""
        image_paths = []
        
        # First try to extract text directly using PyPDF2
        try:
            reader = PdfReader(pdf_path)
            pdf_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    pdf_text += page_text + "\n\n"
                    
            extracted_text = pdf_text
        except Exception as e:
            print(f"Error extracting text with PyPDF2: {e}")
        
        # If direct extraction yielded little text, try OCR
        if len(extracted_text.strip()) < 100:
            try:
                # Convert PDF to images
                images = convert_from_path(pdf_path)
                ocr_text = ""
                
                # Process each page with OCR
                for i, img in enumerate(images):
                    # Save image for potential multimodal input
                    img_path = os.path.join(self.upload_dir, f"page_{i}_{uuid.uuid4()}.png")
                    img.save(img_path)
                    image_paths.append(img_path)
                    
                    # Extract text with OCR
                    page_text = pytesseract.image_to_string(img)
                    ocr_text += page_text + "\n\n"
                
                # If OCR yielded more text, use it
                if len(ocr_text.strip()) > len(extracted_text.strip()):
                    extracted_text = ocr_text
            except Exception as e:
                print(f"Error with OCR processing: {e}")
        
        return extracted_text, image_paths
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            print(f"Error with image OCR: {e}")
            return ""
    
    async def process_document(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process a document (PDF or image) and extract text and metadata
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            Dictionary with processing results
        """
        result = {
            "success": False,
            "filename": filename,
            "text": "",
            "image_paths": [],
            "file_path": "",
            "file_type": ""
        }
        
        try:
            # Save the uploaded file
            file_path = self.save_uploaded_file(file_content, filename)
            result["file_path"] = file_path
            
            # Determine file type
            file_ext = os.path.splitext(filename)[1].lower()
            result["file_type"] = file_ext
            
            # Process based on file type
            if file_ext in ['.pdf']:
                text, image_paths = self.extract_text_from_pdf(file_path)
                result["text"] = text
                result["image_paths"] = image_paths
                
            elif file_ext in ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']:
                # For images, both extract text and keep the path
                text = self.extract_text_from_image(file_path)
                result["text"] = text
                result["image_paths"] = [file_path]
                
            else:
                result["error"] = f"Unsupported file type: {file_ext}"
                return result
                
            result["success"] = True
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result
    
    def cleanup_files(self, file_paths: List[str]) -> None:
        """
        Clean up temporary files
        
        Args:
            file_paths: List of file paths to remove
        """
        for path in file_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"Error removing file {path}: {e}")