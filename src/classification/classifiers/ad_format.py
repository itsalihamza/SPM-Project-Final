"""Ad format classifier"""

from typing import Dict
from src.classification.models.model_cache import ModelCache


class AdFormatClassifier:
    """Classify ad format based on media presence and content structure"""
    
    def __init__(self, model_cache: ModelCache):
        self.model_cache = model_cache
    
    def classify(self, ad_data: Dict) -> Dict:
        """Determine ad format"""
        media = ad_data.get('content', {}).get('media', {})
        images = media.get('images', [])
        videos = media.get('videos', [])
        
        if videos:
            return {
                'label': 'video',
                'confidence': 0.95,
                'alternatives': [],
                'reasoning': f"Contains {len(videos)} video(s)"
            }
        
        if len(images) > 3:
            return {
                'label': 'carousel',
                'confidence': 0.90,
                'alternatives': [{'label': 'image_static', 'confidence': 0.10}],
                'reasoning': f"Contains {len(images)} images"
            }
        
        if len(images) == 1:
            img = images[0]
            if 'dimensions' in img:
                width, height = img['dimensions']
                aspect_ratio = height / width if width > 0 else 1
                
                if aspect_ratio > 1.5:
                    return {
                        'label': 'stories',
                        'confidence': 0.85,
                        'alternatives': [{'label': 'image_static', 'confidence': 0.15}],
                        'reasoning': f"Vertical aspect ratio: {aspect_ratio:.2f}"
                    }
            
            return {
                'label': 'image_static',
                'confidence': 0.90,
                'alternatives': [],
                'reasoning': "Single static image"
            }
        
        if not images and not videos:
            return {
                'label': 'text_only',
                'confidence': 0.85,
                'alternatives': [],
                'reasoning': "No media detected"
            }
        
        return {
            'label': 'image_static',
            'confidence': 0.70,
            'alternatives': [],
            'reasoning': "Default classification"
        }
