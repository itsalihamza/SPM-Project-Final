"""Test classification pipeline"""

import pytest
from src.classification.pipeline import ClassificationPipeline


def test_ad_format_classification():
    """Test ad format classification"""
    from src.classification.classifiers.ad_format import AdFormatClassifier
    from src.classification.models.model_cache import ModelCache
    
    cache = ModelCache()
    classifier = AdFormatClassifier(cache)
    
    # Test video detection
    ad_with_video = {
        'content': {
            'media': {
                'images': [],
                'videos': ['video1.mp4']
            }
        }
    }
    result = classifier.classify(ad_with_video)
    assert result['label'] == 'video'
    assert result['confidence'] > 0.9
    
    # Test carousel detection
    ad_with_many_images = {
        'content': {
            'media': {
                'images': [f'img{i}.jpg' for i in range(5)],
                'videos': []
            }
        }
    }
    result = classifier.classify(ad_with_many_images)
    assert result['label'] == 'carousel'
    
    # Test text-only
    text_only_ad = {
        'content': {
            'media': {
                'images': [],
                'videos': []
            }
        }
    }
    result = classifier.classify(text_only_ad)
    assert result['label'] == 'text_only'


def test_classification_pipeline():
    """Test full classification pipeline"""
    pipeline = ClassificationPipeline()
    
    ad_data = {
        'ad_id': 'test_001',
        'content': {
            'headline': 'Test Ad',
            'body_text': 'This is a test advertisement',
            'media': {
                'images': ['image1.jpg'],
                'videos': []
            }
        }
    }
    
    result = pipeline.classify(ad_data)
    
    assert result['ad_id'] == 'test_001'
    assert 'classifications' in result
    assert 'ad_format' in result['classifications']
    assert result['classification_metadata']['total_inference_time_ms'] > 0
