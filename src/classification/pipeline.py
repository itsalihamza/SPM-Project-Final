"""Main classification pipeline orchestrator"""

import time
from typing import Dict, List
import structlog
from src.classification.models.model_cache import ModelCache
from src.classification.classifiers.ad_format import AdFormatClassifier

logger = structlog.get_logger()


class ClassificationPipeline:
    """Main orchestrator for ad classification"""
    
    def __init__(self):
        self.model_cache = ModelCache()
        self.format_classifier = AdFormatClassifier(self.model_cache)
    
    def classify(self, ad_data: Dict) -> Dict:
        """Run complete classification pipeline on a single ad"""
        start_time = time.time()
        models_used = []
        
        logger.info("Starting classification", ad_id=ad_data.get('ad_id'))
        
        try:
            # Ad format classification
            ad_format = self.format_classifier.classify(ad_data)
            models_used.append('rule_based_format')
            
            # Build result
            result = {
                'ad_id': ad_data.get('ad_id'),
                'classifications': {
                    'ad_format': ad_format,
                },
                'extracted_features': {
                    'keywords': [],
                    'entities': [],
                    'call_to_action_type': 'other',
                    'has_urgency_indicators': False,
                    'has_pricing': False,
                    'has_social_proof': False
                },
                'classification_metadata': {
                    'models_used': models_used,
                    'total_inference_time_ms': int((time.time() - start_time) * 1000),
                    'requires_review': False,
                    'review_reason': None
                }
            }
            
            logger.info("Classification complete",
                       ad_id=ad_data.get('ad_id'),
                       duration_ms=result['classification_metadata']['total_inference_time_ms'])
            
            return result
            
        except Exception as e:
            logger.error("Classification failed",
                        ad_id=ad_data.get('ad_id'),
                        error=str(e))
            raise
    
    def classify_batch(self, ads: List[Dict], max_workers: int = 4) -> List[Dict]:
        """Classify multiple ads in parallel"""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ad = {
                executor.submit(self.classify, ad): ad
                for ad in ads
            }
            
            for future in as_completed(future_to_ad):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    ad = future_to_ad[future]
                    logger.error("Batch classification failed",
                                ad_id=ad.get('ad_id'),
                                error=str(e))
        
        return results
