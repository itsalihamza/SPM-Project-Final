"""Text cleaning and normalization utilities"""

import re
import ftfy
from unidecode import unidecode
import emoji
from typing import Optional


class TextCleaner:
    """Clean and normalize text from various sources"""
    
    @staticmethod
    def fix_encoding(text: str) -> str:
        """Fix common encoding issues"""
        return ftfy.fix_text(text)
    
    @staticmethod
    def remove_extra_whitespace(text: str) -> str:
        """Remove extra whitespace and normalize line breaks"""
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    @staticmethod
    def normalize_unicode(text: str, preserve_emojis: bool = True) -> str:
        """Normalize unicode characters"""
        if not preserve_emojis:
            text = emoji.demojize(text)
        return text
    
    @staticmethod
    def remove_urls(text: str) -> str:
        """Remove URLs from text"""
        url_pattern = r'https?://\S+|www\.\S+'
        return re.sub(url_pattern, '', text)
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags"""
        clean_pattern = re.compile('<.*?>')
        return re.sub(clean_pattern, '', text)
    
    @staticmethod
    def standardize_quotes(text: str) -> str:
        """Convert smart quotes to standard quotes"""
        replacements = {
            '"': '"', '"': '"',
            ''': "'", ''': "'",
            '„': '"', '‟': '"',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = '...') -> str:
        """Truncate text to max length"""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    def clean(self, text: Optional[str], max_length: Optional[int] = None) -> str:
        """Apply all cleaning steps"""
        if not text:
            return ''
        
        text = self.fix_encoding(text)
        text = self.remove_html_tags(text)
        text = self.standardize_quotes(text)
        text = self.remove_extra_whitespace(text)
        
        if max_length:
            text = self.truncate(text, max_length)
        
        return text


class TextNormalizer:
    """Normalize text for consistent comparison and analysis"""
    
    @staticmethod
    def normalize_brand_name(brand: str) -> str:
        """Normalize brand name for consistent matching"""
        normalized = brand.lower()
        normalized = re.sub(r'[™®©]', '', normalized)
        normalized = re.sub(r'[^a-z0-9\s]', '', normalized)
        
        suffixes = ['inc', 'llc', 'ltd', 'corp', 'corporation', 'company', 'co']
        for suffix in suffixes:
            normalized = re.sub(rf'\b{suffix}\b', '', normalized)
        
        normalized = re.sub(r'\s+', '', normalized)
        return normalized.strip()
    
    @staticmethod
    def normalize_call_to_action(cta: str) -> str:
        """Standardize CTA text"""
        cta = cta.lower().strip()
        cta = re.sub(r'[!?.]{2,}', '', cta)
        cta = re.sub(r'\s+', ' ', cta)
        return cta.strip()
    
    @staticmethod
    def detect_emojis(text: str) -> dict:
        """Detect and count emojis in text"""
        emoji_list = emoji.emoji_list(text)
        return {
            'contains_emojis': len(emoji_list) > 0,
            'emoji_count': len(emoji_list),
            'emojis': [e['emoji'] for e in emoji_list]
        }
