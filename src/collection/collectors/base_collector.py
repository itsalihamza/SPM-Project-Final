"""Base collector class for all platform collectors"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from dataclasses import dataclass
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential
import time

logger = structlog.get_logger()


@dataclass
class CollectionConfig:
    """Configuration for a data collection job"""
    platform: str
    keywords: List[str]
    max_results: int = 100
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    rate_limit_per_second: float = 0.5


class BaseCollector(ABC):
    """Abstract base class for all platform collectors"""
    
    def __init__(self, config: CollectionConfig):
        self.config = config
        self.logger = logger.bind(platform=config.platform)
        self._last_request_time = 0
    
    @abstractmethod
    def collect(self) -> List[Dict]:
        """
        Main collection method - must be implemented by subclasses
        Returns: List of raw ad data dictionaries
        """
        pass
    
    @abstractmethod
    def normalize(self, raw_data: Dict) -> Dict:
        """
        Transform platform-specific data to standardized schema
        Returns: Normalized ad data dictionary
        """
        pass
    
    def _apply_rate_limit(self):
        """Apply rate limiting between requests"""
        if self.config.rate_limit_per_second > 0:
            min_interval = 1.0 / self.config.rate_limit_per_second
            elapsed = time.time() - self._last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        self._last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _make_request(self, url: str, **kwargs) -> Dict:
        """
        HTTP request wrapper with retry logic
        Implement rate limiting and error handling here
        """
        import requests
        
        self._apply_rate_limit()
        
        try:
            response = requests.get(url, timeout=10, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error("Request failed", url=url, error=str(e))
            raise
    
    def run(self) -> List[Dict]:
        """
        Execute full collection pipeline:
        1. Collect raw data
        2. Normalize to standard schema
        3. Validate
        4. Return processed data
        """
        try:
            self.logger.info("Starting collection", keywords=self.config.keywords)
            raw_data = self.collect()
            
            normalized_data = []
            for item in raw_data:
                try:
                    normalized = self.normalize(item)
                    normalized_data.append(normalized)
                except Exception as e:
                    self.logger.error("Normalization failed", 
                                    item_id=item.get('id'), 
                                    error=str(e))
            
            self.logger.info("Collection complete", 
                           total_collected=len(raw_data),
                           successfully_normalized=len(normalized_data))
            
            return normalized_data
            
        except Exception as e:
            self.logger.error("Collection failed", error=str(e))
            raise
