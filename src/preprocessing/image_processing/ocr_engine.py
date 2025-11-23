"""OCR engine for extracting text from images"""

import pytesseract
import easyocr
from PIL import Image
import requests
from io import BytesIO
import cv2
import numpy as np
from typing import Optional, Dict
import structlog

logger = structlog.get_logger()


class OCREngine:
    """
    OCR engine supporting both Tesseract (fast, local) and EasyOCR (accurate, deep learning)
    Both are FREE and require NO authentication
    """
    
    def __init__(self, primary_engine: str = 'tesseract', fallback: bool = True):
        """
        Initialize OCR engine
        
        Args:
            primary_engine: 'tesseract' or 'easyocr'
            fallback: If True, try alternate engine if primary fails
        """
        self.primary_engine = primary_engine
        self.fallback = fallback
        self._easyocr_reader = None
        self.tesseract_config = '--oem 3 --psm 6'
    
    @property
    def easyocr_reader(self):
        """Lazy initialize EasyOCR to save memory"""
        if self._easyocr_reader is None:
            self._easyocr_reader = easyocr.Reader(['en'], gpu=False)
        return self._easyocr_reader
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        denoised = cv2.fastNlMeansDenoising(thresh)
        return denoised
    
    def extract_text_tesseract(self, image_url: str) -> Dict:
        """Extract text using Tesseract OCR"""
        try:
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content))
            
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            preprocessed = self.preprocess_image(cv_image)
            
            text = pytesseract.image_to_string(
                Image.fromarray(preprocessed),
                config=self.tesseract_config
            )
            
            data = pytesseract.image_to_data(
                Image.fromarray(preprocessed),
                output_type=pytesseract.Output.DICT,
                config=self.tesseract_config
            )
            
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence / 100,
                'engine': 'tesseract',
                'success': True
            }
            
        except Exception as e:
            logger.error("Tesseract OCR failed", url=image_url, error=str(e))
            return {
                'text': '',
                'confidence': 0,
                'engine': 'tesseract',
                'success': False,
                'error': str(e)
            }
    
    def extract_text_easyocr(self, image_url: str) -> Dict:
        """Extract text using EasyOCR"""
        try:
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content))
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            results = self.easyocr_reader.readtext(cv_image)
            
            text_parts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                text_parts.append(text)
                confidences.append(confidence)
            
            combined_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': combined_text.strip(),
                'confidence': avg_confidence,
                'engine': 'easyocr',
                'success': True,
                'detected_regions': len(results)
            }
            
        except Exception as e:
            logger.error("EasyOCR failed", url=image_url, error=str(e))
            return {
                'text': '',
                'confidence': 0,
                'engine': 'easyocr',
                'success': False,
                'error': str(e)
            }
    
    def extract_text(self, image_url: str) -> Dict:
        """Extract text from image using configured OCR engine(s)"""
        if self.primary_engine == 'tesseract':
            result = self.extract_text_tesseract(image_url)
        else:
            result = self.extract_text_easyocr(image_url)
        
        if not result['success'] and self.fallback:
            logger.info("Primary OCR failed, trying fallback", url=image_url)
            
            if self.primary_engine == 'tesseract':
                result = self.extract_text_easyocr(image_url)
            else:
                result = self.extract_text_tesseract(image_url)
        
        return result
    
    def batch_extract(self, image_urls: list) -> list:
        """Extract text from multiple images in parallel"""
        from joblib import Parallel, delayed
        
        results = Parallel(n_jobs=4)(
            delayed(self.extract_text)(url) for url in image_urls
        )
        
        return results
