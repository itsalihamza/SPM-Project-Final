"""Test preprocessing pipeline"""

import pytest
from src.preprocessing.pipeline import PreprocessingPipeline


def test_preprocessing_single_ad():
    """Test preprocessing a single ad"""
    pipeline = PreprocessingPipeline()
    
    raw_ad = {
        'ad_id': 'test_001',
        'platform': 'test',
        'source_url': 'https://example.com',
        'collected_at': '2024-01-01T00:00:00Z',
        'headline': '  Test   Headline  ',
        'body_text': '<p>Test body</p>',
        'call_to_action': 'CLICK NOW!!!',
        'brand_name': 'Test Brand Inc.',
        'media_urls': []
    }
    
    result = pipeline.preprocess_single(raw_ad)
    
    assert result['ad_id'] == 'test_001'
    assert result['content']['headline'] == 'Test Headline'
    assert '<p>' not in result['content']['body_text']
    assert result['quality']['preprocessing_status'] == 'success'


def test_text_cleaning():
    """Test text cleaning utilities"""
    from src.preprocessing.text_processing.cleaner import TextCleaner
    
    cleaner = TextCleaner()
    
    # Test whitespace removal
    assert cleaner.remove_extra_whitespace('  test   text  ') == 'test text'
    
    # Test HTML removal
    assert cleaner.remove_html_tags('<p>Hello</p>') == 'Hello'
    
    # Test full clean
    dirty = '  <b>Test</b>   Text  '
    clean = cleaner.clean(dirty)
    assert clean == 'Test Text'


def test_brand_normalization():
    """Test brand name normalization"""
    from src.preprocessing.text_processing.cleaner import TextNormalizer
    
    normalizer = TextNormalizer()
    
    assert normalizer.normalize_brand_name('Test Corp.') == 'test'
    assert normalizer.normalize_brand_name('Test Inc.') == 'test'
    assert normalizer.normalize_brand_name('Test™') == 'test'
