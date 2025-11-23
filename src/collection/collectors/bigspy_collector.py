"""BigSpy web scraper for competitor ad intelligence"""

import requests
from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup
import time
from src.collection.collectors.base_collector import BaseCollector, CollectionConfig


class BigSpyCollector(BaseCollector):
    """
    Collector for BigSpy - free ad intelligence platform
    No authentication required for basic searches
    Covers 10+ platforms including Facebook, Instagram, Google, TikTok
    """
    
    BASE_URL = "https://bigspy.com"
    SEARCH_URL = "https://bigspy.com/api/v1/ad/search"
    
    def __init__(self, config: CollectionConfig):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Referer': 'https://bigspy.com/'
        })
    
    def _fetch_ads_page(self, keyword: str, page: int = 1) -> Dict:
        """Fetch one page of ads from BigSpy"""
        
        params = {
            'keyword': keyword,
            'page': page,
            'page_size': 20,
            'platform': 'facebook',  # Can be: facebook, instagram, google, tiktok, etc.
            'sort': 'recent'
        }
        
        try:
            self._apply_rate_limit()
            response = self.session.get(self.SEARCH_URL, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.warning(f"BigSpy returned status {response.status_code}")
                return {"data": []}
                
        except Exception as e:
            self.logger.error("BigSpy request failed", keyword=keyword, error=str(e))
            return {"data": []}
    
    def collect(self) -> List[Dict]:
        """Collect ads for all configured keywords"""
        all_ads = []
        
        for keyword in self.config.keywords:
            self.logger.info("Collecting ads from BigSpy", keyword=keyword, platform="bigspy")
            page = 1
            
            while len(all_ads) < self.config.max_results:
                response = self._fetch_ads_page(keyword, page)
                ads = response.get('data', [])
                
                if not ads:
                    self.logger.info("No more ads found", keyword=keyword, page=page)
                    break
                
                all_ads.extend(ads)
                
                self.logger.info("Fetched page", 
                               keyword=keyword, 
                               page=page,
                               ads_count=len(ads),
                               total_so_far=len(all_ads))
                
                page += 1
                time.sleep(1)  # Be respectful with rate limiting
                
                if page > 5:  # Limit to 5 pages per keyword
                    break
        
        return all_ads[:self.config.max_results]
    
    def normalize(self, raw_data: Dict) -> Dict:
        """Transform BigSpy data to standard schema"""
        
        return {
            "ad_id": f"bigspy_{raw_data.get('id', 'unknown')}",
            "platform": raw_data.get('platform', 'facebook'),
            "source_url": raw_data.get('url', ''),
            "collected_at": datetime.utcnow().isoformat(),
            "raw_data": raw_data,
            
            # Content
            "headline": raw_data.get('title', ''),
            "body_text": raw_data.get('description', ''),
            "call_to_action": raw_data.get('cta', ''),
            "media_urls": raw_data.get('images', []),
            "landing_page": raw_data.get('landing_page', ''),
            
            # Metadata
            "brand_name": raw_data.get('advertiser', ''),
            "page_name": raw_data.get('page_name', ''),
            "detected_keywords": self.config.keywords,
            "start_date": raw_data.get('first_seen', ''),
            "end_date": raw_data.get('last_seen', ''),
            
            # Engagement (if available)
            "impressions": raw_data.get('impressions'),
            "spend_range": None,
            
            # System
            "collection_status": "success",
            "validation_errors": [],
            "retry_count": 0
        }
