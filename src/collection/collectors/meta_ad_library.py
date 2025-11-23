"""Meta Ad Library collector implementation"""

import requests
import os
from typing import List, Dict
from datetime import datetime
from ratelimit import limits, sleep_and_retry
from src.collection.collectors.base_collector import BaseCollector, CollectionConfig


class MetaAdLibraryCollector(BaseCollector):
    """
    Collector for Meta Ad Library using official Graph API
    Requires access token from Meta for Developers
    Get token at: https://developers.facebook.com/
    """
    
    BASE_URL = "https://graph.facebook.com/v18.0/ads_archive"
    
    def __init__(self, config: CollectionConfig):
        super().__init__(config)
        self.session = requests.Session()
        
        # Get access token from environment variable
        self.access_token = os.getenv('META_ACCESS_TOKEN')
        if not self.access_token:
            self.logger.warning(
                "META_ACCESS_TOKEN not set. Using demo mode with limited functionality. "
                "Get your token at: https://developers.facebook.com/"
            )
        
        self.session.headers.update({
            'User-Agent': 'AdIntelligence/1.0',
            'Accept': 'application/json'
        })
    
    @sleep_and_retry
    @limits(calls=200, period=3600)  # 200 requests per hour
    def _fetch_ads_page(self, keyword: str, after: str = None) -> Dict:
        """Fetch one page of ads from Meta Ad Library using Graph API"""
        
        params = {
            'search_terms': keyword,
            'ad_reached_countries': "['US']",
            'ad_active_status': 'ALL',
            'limit': 30,
            'fields': 'id,ad_creative_bodies,ad_creative_link_captions,ad_creative_link_descriptions,ad_creative_link_titles,ad_delivery_start_time,ad_delivery_stop_time,ad_snapshot_url,currency,funding_entity,page_name,impressions,spend'
        }
        
        # Add access token if available
        if self.access_token:
            params['access_token'] = self.access_token
        
        # Add pagination cursor if provided
        if after:
            params['after'] = after
        
        try:
            self._apply_rate_limit()
            response = self.session.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error("API request failed", keyword=keyword, error=str(e))
            raise
    
    def collect(self) -> List[Dict]:
        """Collect ads for all configured keywords"""
        all_ads = []
        
        for keyword in self.config.keywords:
            self.logger.info("Collecting ads", keyword=keyword, platform="meta")
            after_cursor = None
            
            while len(all_ads) < self.config.max_results:
                try:
                    response = self._fetch_ads_page(keyword, after_cursor)
                    
                    # Graph API returns data in 'data' field
                    ads = response.get('data', [])
                    if not ads:
                        self.logger.info("No more ads found", keyword=keyword)
                        break
                    
                    all_ads.extend(ads)
                    
                    self.logger.info("Fetched page", 
                                   keyword=keyword, 
                                   ads_count=len(ads),
                                   total_so_far=len(all_ads))
                    
                    # Check for pagination cursor
                    paging = response.get('paging', {})
                    after_cursor = paging.get('cursors', {}).get('after')
                    
                    if not after_cursor:
                        self.logger.info("No more pages available", keyword=keyword)
                        break
                    
                except Exception as e:
                    self.logger.error("Failed to fetch page", 
                                    keyword=keyword, 
                                    error=str(e))
                    break
        
        return all_ads[:self.config.max_results]
    
    def normalize(self, raw_data: Dict) -> Dict:
        """Transform Meta Ad Library Graph API data to standard schema"""
        
        # Extract text from ad creative bodies
        ad_bodies = raw_data.get('ad_creative_bodies', [])
        headline = ad_bodies[0] if ad_bodies else None
        
        # Extract link descriptions
        link_descriptions = raw_data.get('ad_creative_link_descriptions', [])
        body_text = link_descriptions[0] if link_descriptions else None
        
        # Extract link captions (CTA)
        link_captions = raw_data.get('ad_creative_link_captions', [])
        call_to_action = link_captions[0] if link_captions else None
        
        # Extract link titles
        link_titles = raw_data.get('ad_creative_link_titles', [])
        
        # Parse impressions
        impressions_data = raw_data.get('impressions')
        impressions = None
        if impressions_data and 'lower_bound' in impressions_data:
            impressions = impressions_data['lower_bound']
        
        # Parse spend
        spend_data = raw_data.get('spend')
        spend_range = None
        if spend_data:
            spend_range = {
                "lower": spend_data.get('lower_bound'),
                "upper": spend_data.get('upper_bound'),
                "currency": raw_data.get('currency', 'USD')
            }
        
        return {
            "ad_id": f"meta_{raw_data.get('id')}",
            "platform": "meta",
            "source_url": raw_data.get('ad_snapshot_url'),
            "collected_at": datetime.utcnow().isoformat(),
            "raw_data": raw_data,
            
            # Content
            "headline": headline,
            "body_text": body_text,
            "call_to_action": call_to_action,
            "media_urls": [],  # Graph API doesn't directly provide image URLs in basic response
            "landing_page": None,  # Not in basic fields
            
            # Metadata
            "brand_name": raw_data.get('page_name'),
            "page_name": raw_data.get('page_name'),
            "funding_entity": raw_data.get('funding_entity'),
            "detected_keywords": self.config.keywords,
            "start_date": raw_data.get('ad_delivery_start_time'),
            "end_date": raw_data.get('ad_delivery_stop_time'),
            
            # Engagement
            "impressions": impressions,
            "spend_range": spend_range,
            
            # System
            "collection_status": "success",
            "validation_errors": [],
            "retry_count": 0
        }
