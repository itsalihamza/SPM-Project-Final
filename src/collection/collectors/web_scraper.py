"""Web scraper for competitor websites"""

import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import time
from typing import List, Dict
from datetime import datetime
from src.collection.collectors.base_collector import BaseCollector, CollectionConfig


class CompetitorAdSpider(scrapy.Spider):
    """
    Scrapes competitor websites for ad-related content
    Respects robots.txt and implements polite crawling
    """
    
    name = 'competitor_ads'
    custom_settings = {
        'ROBOTSTXT_OBEY': True,
        'DOWNLOAD_DELAY': 3,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'USER_AGENT': 'AdIntelligenceBot/1.0 (Research; +http://yoursite.com/bot)'
    }
    
    def __init__(self, competitor_urls: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = competitor_urls
        self.collected_ads = []
    
    def parse(self, response):
        """Extract ad content from competitor pages"""
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        ad_selectors = [
            'div[class*="promo"]',
            'div[class*="banner"]',
            'div[class*="advertisement"]',
            'div[id*="ad-"]',
            'section[class*="campaign"]'
        ]
        
        for selector in ad_selectors:
            elements = soup.select(selector)
            for element in elements:
                ad_data = {
                    'headline': element.find(['h1', 'h2', 'h3']).get_text(strip=True) if element.find(['h1', 'h2', 'h3']) else None,
                    'body_text': element.get_text(strip=True),
                    'images': [img.get('src') for img in element.find_all('img') if img.get('src')],
                    'links': [a.get('href') for a in element.find_all('a') if a.get('href')],
                    'source_url': response.url
                }
                self.collected_ads.append(ad_data)
                yield ad_data


class WebScraperCollector(BaseCollector):
    """Wrapper for Scrapy-based web scraping"""
    
    def __init__(self, config: CollectionConfig):
        super().__init__(config)
        self.results = []
    
    def collect(self) -> List[Dict]:
        """Run Scrapy spider and return results"""
        
        process = CrawlerProcess({
            'LOG_LEVEL': 'INFO'
        })
        
        spider = CompetitorAdSpider(competitor_urls=self.config.keywords)
        process.crawl(spider)
        process.start()
        
        return spider.collected_ads
    
    def normalize(self, raw_data: Dict) -> Dict:
        """Transform scraped web data to standard schema"""
        
        return {
            "ad_id": f"web_{hash(raw_data.get('source_url'))}_{int(time.time())}",
            "platform": "web",
            "source_url": raw_data.get('source_url'),
            "collected_at": datetime.utcnow().isoformat(),
            "raw_data": raw_data,
            
            "headline": raw_data.get('headline'),
            "body_text": raw_data.get('body_text'),
            "media_urls": raw_data.get('images', []),
            "landing_page": raw_data.get('links', [None])[0],
            
            "collection_status": "success",
            "validation_errors": [],
            "retry_count": 0
        }
