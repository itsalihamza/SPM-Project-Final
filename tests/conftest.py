"""Shared test fixtures and utilities"""

import pytest


@pytest.fixture
def sample_raw_ad():
    """Sample raw ad data"""
    return {
        'ad_id': 'test_001',
        'platform': 'meta',
        'source_url': 'https://facebook.com/ads/library/123',
        'collected_at': '2024-01-01T00:00:00Z',
        'headline': 'Amazing Product Sale',
        'body_text': 'Get 50% off on all items. Limited time offer!',
        'call_to_action': 'Shop Now',
        'brand_name': 'Test Brand',
        'media_urls': ['https://example.com/image1.jpg'],
        'landing_page': 'https://testbrand.com/sale',
        'impressions': 10000,
        'spend_range': {
            'lower': 100,
            'upper': 500,
            'currency': 'USD'
        }
    }


@pytest.fixture
def sample_preprocessed_ad():
    """Sample preprocessed ad data"""
    return {
        'ad_id': 'test_001',
        'platform': 'meta',
        'content': {
            'headline': 'Amazing Product Sale',
            'body_text': 'Get 50% off on all items. Limited time offer!',
            'call_to_action': 'shop now',
            'extracted_text_from_images': 'Sale 50% OFF',
            'media': {
                'images': [
                    {
                        'url': 'https://example.com/image1.jpg',
                        'extracted_text': 'Sale 50% OFF',
                        'ocr_confidence': 0.85
                    }
                ]
            }
        },
        'metadata': {
            'brand_name': 'Test Brand',
            'brand_name_normalized': 'testbrand'
        },
        'quality': {
            'preprocessing_status': 'success',
            'validation_errors': []
        }
    }
