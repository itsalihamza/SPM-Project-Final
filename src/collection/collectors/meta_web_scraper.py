"""Meta Ad Library web scraper - No authentication required"""

import time
import json
from typing import List, Dict
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from src.collection.collectors.base_collector import BaseCollector, CollectionConfig


class MetaWebScraper(BaseCollector):
    """
    Web scraper for Meta Ad Library
    No authentication required - scrapes public website
    Uses Selenium for dynamic content
    """
    
    BASE_URL = "https://www.facebook.com/ads/library/"
    
    def __init__(self, config: CollectionConfig):
        super().__init__(config)
        self.driver = None
        self.logger.info("Using MetaWebScraper - scraping public Meta Ad Library website")
    
    def _init_driver(self):
        """Initialize Selenium WebDriver with automatic driver management"""
        if self.driver:
            return
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run in background
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            # Use webdriver-manager to automatically download and manage ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome WebDriver: {e}")
            self.logger.info("Make sure Chrome browser is installed on your system")
            raise Exception("Could not initialize WebDriver. Please install Chrome browser.")
    
    def _search_ads(self, keyword: str, max_scroll: int = 5) -> List[Dict]:
        """Search for ads on Meta Ad Library website"""
        
        self._init_driver()
        ads = []
        
        try:
            # Build search URL
            search_url = f"{self.BASE_URL}?active_status=all&ad_type=all&country=US&q={keyword}&search_type=keyword_unordered"
            
            self.logger.info(f"Navigating to Meta Ad Library: {keyword}")
            self.driver.get(search_url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Scroll to load more ads
            for scroll in range(max_scroll):
                self.logger.info(f"Scrolling to load more ads... ({scroll + 1}/{max_scroll})")
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)
            
            # Extract ad elements
            self.logger.info("Extracting ad data from page...")
            
            # Try to find ad containers (Meta's structure may vary)
            ad_containers = self.driver.find_elements(By.CSS_SELECTOR, '[role="article"]')
            
            if not ad_containers:
                # Try alternative selectors
                ad_containers = self.driver.find_elements(By.CSS_SELECTOR, 'div[data-testid]')
            
            self.logger.info(f"Found {len(ad_containers)} potential ad containers")
            
            for idx, container in enumerate(ad_containers[:self.config.max_results]):
                try:
                    ad_data = self._extract_ad_data(container, idx)
                    if ad_data:
                        ads.append(ad_data)
                except Exception as e:
                    self.logger.warning(f"Failed to extract ad {idx}: {e}")
                    continue
            
            self.logger.info(f"Successfully extracted {len(ads)} ads")
            
        except Exception as e:
            self.logger.error(f"Error during web scraping: {e}")
        
        return ads
    
    def _extract_ad_data(self, container, idx: int) -> Dict:
        """Extract data from a single ad container"""
        
        ad_data = {
            'id': f'web_scraped_{idx}_{int(time.time())}',
            'scraped_at': datetime.utcnow().isoformat(),
        }
        
        try:
            # Extract text content
            text_elements = container.find_elements(By.TAG_NAME, 'span')
            all_text = ' '.join([elem.text for elem in text_elements if elem.text])
            
            # Try to identify different parts
            paragraphs = container.find_elements(By.TAG_NAME, 'p')
            if paragraphs:
                ad_data['ad_creative_bodies'] = [p.text for p in paragraphs if p.text]
            
            # Extract links
            links = container.find_elements(By.TAG_NAME, 'a')
            if links:
                ad_data['ad_snapshot_url'] = links[0].get_attribute('href') if links else ''
            
            # Extract images
            images = container.find_elements(By.TAG_NAME, 'img')
            if images:
                ad_data['images'] = [img.get_attribute('src') for img in images if img.get_attribute('src')]
            
            # Store all text for processing
            ad_data['full_text'] = all_text
            
            # Try to find page name / advertiser
            try:
                page_name_elem = container.find_element(By.CSS_SELECTOR, 'a[role="link"]')
                ad_data['page_name'] = page_name_elem.text
            except:
                ad_data['page_name'] = 'Unknown'
            
            return ad_data
            
        except Exception as e:
            self.logger.warning(f"Error extracting ad data: {e}")
            return None
    
    def collect(self) -> List[Dict]:
        """Collect ads for all configured keywords"""
        all_ads = []
        
        try:
            for keyword in self.config.keywords:
                self.logger.info(f"Searching for ads with keyword: {keyword}")
                
                ads = self._search_ads(keyword, max_scroll=3)
                all_ads.extend(ads)
                
                self.logger.info(f"Collected {len(ads)} ads for keyword: {keyword}")
                
                if len(all_ads) >= self.config.max_results:
                    break
                
                time.sleep(2)  # Be respectful
            
        finally:
            # Clean up
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver closed")
        
        return all_ads[:self.config.max_results]
    
    def normalize(self, raw_data: Dict) -> Dict:
        """Transform scraped data to standard schema"""
        
        # Extract text content
        bodies = raw_data.get('ad_creative_bodies', [])
        headline = bodies[0] if bodies else raw_data.get('full_text', '')[:100]
        body_text = raw_data.get('full_text', '')
        
        return {
            "ad_id": f"meta_web_{raw_data.get('id')}",
            "platform": "meta_web",
            "source_url": raw_data.get('ad_snapshot_url', ''),
            "collected_at": datetime.utcnow().isoformat(),
            "raw_data": raw_data,
            
            # Content
            "headline": headline,
            "body_text": body_text,
            "call_to_action": '',
            "media_urls": raw_data.get('images', []),
            "landing_page": '',
            
            # Metadata
            "brand_name": raw_data.get('page_name', 'Unknown'),
            "page_name": raw_data.get('page_name', 'Unknown'),
            "detected_keywords": self.config.keywords,
            
            # System
            "collection_status": "success",
            "validation_errors": [],
            "retry_count": 0
        }
