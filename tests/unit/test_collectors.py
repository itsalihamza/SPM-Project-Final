"""Test base collector functionality"""

import pytest
from src.collection.collectors.base_collector import BaseCollector, CollectionConfig


class MockCollector(BaseCollector):
    """Mock collector for testing"""
    
    def collect(self):
        return [
            {'id': '1', 'text': 'Test ad 1'},
            {'id': '2', 'text': 'Test ad 2'}
        ]
    
    def normalize(self, raw_data):
        return {
            'ad_id': raw_data['id'],
            'content': raw_data['text']
        }


def test_collector_initialization():
    """Test collector can be initialized"""
    config = CollectionConfig(
        platform='test',
        keywords=['test'],
        max_results=10
    )
    collector = MockCollector(config)
    assert collector.config.platform == 'test'


def test_collector_run():
    """Test collector run method"""
    config = CollectionConfig(
        platform='test',
        keywords=['test'],
        max_results=10
    )
    collector = MockCollector(config)
    results = collector.run()
    
    assert len(results) == 2
    assert results[0]['ad_id'] == '1'
    assert results[1]['ad_id'] == '2'


def test_rate_limiting():
    """Test rate limiting is applied"""
    import time
    config = CollectionConfig(
        platform='test',
        keywords=['test'],
        max_results=10,
        rate_limit_per_second=2.0  # 2 requests per second
    )
    collector = MockCollector(config)
    
    start = time.time()
    collector._apply_rate_limit()
    collector._apply_rate_limit()
    elapsed = time.time() - start
    
    # Should take at least 0.5 seconds (1/2.0)
    assert elapsed >= 0.4
