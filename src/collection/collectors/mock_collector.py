"""Mock data collector for testing without API access"""

from typing import List, Dict
from datetime import datetime, timedelta
import random
from src.collection.collectors.base_collector import BaseCollector, CollectionConfig


class MockAdCollector(BaseCollector):
    """
    Mock collector that generates fake ad data for testing
    Use this to test the preprocessing and classification pipeline
    without needing API access
    """
    
    SAMPLE_BRANDS = ["Nike", "Adidas", "Puma", "Under Armour", "Reebok"]
    SAMPLE_HEADLINES = [
        "Summer Sale - Up to 50% Off",
        "New Collection Just Dropped",
        "Limited Time Offer",
        "Free Shipping on Orders Over $50",
        "Shop the Latest Trends"
    ]
    SAMPLE_BODY_TEXT = [
        "Don't miss out on our biggest sale of the year",
        "Discover the perfect fit for your lifestyle",
        "Quality products at unbeatable prices",
        "Join millions of satisfied customers",
        "Upgrade your wardrobe today"
    ]
    SAMPLE_CTA = ["Shop Now", "Learn More", "Sign Up", "Get Started", "Buy Now"]
    
    def __init__(self, config: CollectionConfig):
        super().__init__(config)
        self.logger.info("Using MockAdCollector - generating fake data for testing")
    
    def collect(self) -> List[Dict]:
        """Generate mock ad data"""
        all_ads = []
        
        for i in range(min(self.config.max_results, 20)):
            brand = random.choice(self.SAMPLE_BRANDS)
            ad = {
                "id": f"mock_{i}_{random.randint(1000, 9999)}",
                "ad_creative_bodies": [random.choice(self.SAMPLE_HEADLINES)],
                "ad_creative_link_descriptions": [random.choice(self.SAMPLE_BODY_TEXT)],
                "ad_creative_link_captions": [random.choice(self.SAMPLE_CTA)],
                "ad_creative_link_titles": [f"{brand} - Official Store"],
                "ad_delivery_start_time": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "ad_delivery_stop_time": None,
                "ad_snapshot_url": f"https://facebook.com/ads/library/?id=mock_{i}",
                "currency": "USD",
                "funding_entity": brand,
                "page_name": brand,
                "impressions": {
                    "lower_bound": random.randint(1000, 100000),
                    "upper_bound": random.randint(100000, 500000)
                },
                "spend": {
                    "lower_bound": random.randint(100, 1000),
                    "upper_bound": random.randint(1000, 10000)
                }
            }
            all_ads.append(ad)
            
        self.logger.info(f"Generated {len(all_ads)} mock ads")
        return all_ads
    
    def normalize(self, raw_data: Dict) -> Dict:
        """Transform mock data to standard schema"""
        
        ad_bodies = raw_data.get('ad_creative_bodies', [])
        headline = ad_bodies[0] if ad_bodies else None
        
        link_descriptions = raw_data.get('ad_creative_link_descriptions', [])
        body_text = link_descriptions[0] if link_descriptions else None
        
        link_captions = raw_data.get('ad_creative_link_captions', [])
        call_to_action = link_captions[0] if link_captions else None
        
        impressions_data = raw_data.get('impressions')
        impressions = None
        if impressions_data and 'lower_bound' in impressions_data:
            impressions = impressions_data['lower_bound']
        
        spend_data = raw_data.get('spend')
        spend_range = None
        if spend_data:
            spend_range = {
                "lower": spend_data.get('lower_bound'),
                "upper": spend_data.get('upper_bound'),
                "currency": raw_data.get('currency', 'USD')
            }
        
        return {
            "ad_id": f"mock_{raw_data.get('id')}",
            "platform": "mock",
            "source_url": raw_data.get('ad_snapshot_url'),
            "collected_at": datetime.utcnow().isoformat(),
            "raw_data": raw_data,
            
            # Content
            "headline": headline,
            "body_text": body_text,
            "call_to_action": call_to_action,
            "media_urls": [],
            "landing_page": None,
            
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
