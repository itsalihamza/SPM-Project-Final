"""Collectors for various ad platforms"""

from src.collection.collectors.base_collector import BaseCollector, CollectionConfig
from src.collection.collectors.meta_ad_library import MetaAdLibraryCollector
from src.collection.collectors.web_scraper import WebScraperCollector

__all__ = ['BaseCollector', 'CollectionConfig', 'MetaAdLibraryCollector', 'WebScraperCollector']
