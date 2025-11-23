"""Main preprocessing pipeline orchestrator"""

import time
from typing import Dict, List
import structlog
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.preprocessing.image_processing.ocr_engine import OCREngine
from src.preprocessing.text_processing.cleaner import TextCleaner, TextNormalizer

logger = structlog.get_logger()


class PreprocessingPipeline:
    """
    Main orchestrator for preprocessing pipeline
    Coordinates all preprocessing steps
    """
    
    def __init__(self):
        self.ocr_engine = OCREngine(primary_engine='tesseract', fallback=True)
        self.text_cleaner = TextCleaner()
        self.text_normalizer = TextNormalizer()
    
    def preprocess_single(self, raw_ad: Dict) -> Dict:
        """Preprocess a single ad through complete pipeline"""
        start_time = time.time()
        validation_errors = []
        enrichment_applied = []
        
        try:
            # Clean text fields
            headline = self.text_cleaner.clean(
                raw_ad.get('headline'),
                max_length=500
            )
            body_text = self.text_cleaner.clean(
                raw_ad.get('body_text'),
                max_length=5000
            )
            cta = self.text_normalizer.normalize_call_to_action(
                raw_ad.get('call_to_action', '')
            )
            enrichment_applied.append('text_cleaning')
            
            # Extract text from images via OCR
            extracted_texts = []
            media_images = []
            
            if raw_ad.get('media_urls'):
                for img_url in raw_ad['media_urls'][:5]:
                    try:
                        ocr_result = self.ocr_engine.extract_text(img_url)
                        if ocr_result['success'] and ocr_result['text']:
                            extracted_texts.append(ocr_result['text'])
                        
                        media_images.append({
                            'url': img_url,
                            'extracted_text': ocr_result.get('text', ''),
                            'ocr_confidence': ocr_result.get('confidence', 0)
                        })
                    except Exception as e:
                        logger.error("Image processing failed", url=img_url, error=str(e))
                        validation_errors.append(f"OCR failed for {img_url}")
                
                enrichment_applied.append('ocr')
            
            # Normalize brand name
            brand_name = raw_ad.get('brand_name', '')
            brand_normalized = self.text_normalizer.normalize_brand_name(brand_name)
            
            # Build standardized output
            preprocessed = {
                "ad_id": raw_ad.get('ad_id'),
                "platform": raw_ad.get('platform'),
                "source_url": raw_ad.get('source_url'),
                "collected_at": raw_ad.get('collected_at'),
                
                "content": {
                    "headline": headline,
                    "body_text": body_text,
                    "call_to_action": cta,
                    "extracted_text_from_images": ' '.join(extracted_texts),
                    "media": {
                        "images": media_images,
                        "videos": []
                    },
                    "landing_page": {
                        "url": raw_ad.get('landing_page'),
                        "is_valid": bool(raw_ad.get('landing_page'))
                    }
                },
                
                "metadata": {
                    "brand_name": brand_name,
                    "brand_name_normalized": brand_normalized,
                    "timestamps": {
                        "detected_at": raw_ad.get('collected_at'),
                        "last_seen": raw_ad.get('collected_at')
                    }
                },
                
                "engagement": {
                    "impressions": raw_ad.get('impressions'),
                    "spend_range": raw_ad.get('spend_range'),
                },
                
                "quality": {
                    "preprocessing_status": 'success',
                    "validation_errors": validation_errors,
                    "enrichment_applied": enrichment_applied,
                    "processing_duration_ms": int((time.time() - start_time) * 1000)
                }
            }
            
            logger.info("Ad preprocessed successfully",
                       ad_id=preprocessed['ad_id'],
                       duration_ms=preprocessed['quality']['processing_duration_ms'])
            
            return preprocessed
            
        except Exception as e:
            logger.error("Preprocessing failed",
                        ad_id=raw_ad.get('ad_id'),
                        error=str(e))
            
            return {
                'ad_id': raw_ad.get('ad_id'),
                'platform': raw_ad.get('platform'),
                'quality': {
                    'preprocessing_status': 'failed',
                    'validation_errors': [str(e)],
                    'processing_duration_ms': int((time.time() - start_time) * 1000)
                }
            }
    
    def preprocess_batch(self, raw_ads: List[Dict], max_workers: int = 4) -> List[Dict]:
        """Preprocess multiple ads in parallel"""
        logger.info("Starting batch preprocessing",
                   total_ads=len(raw_ads),
                   workers=max_workers)
        
        preprocessed_ads = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ad = {
                executor.submit(self.preprocess_single, ad): ad
                for ad in raw_ads
            }
            
            for future in as_completed(future_to_ad):
                try:
                    result = future.result()
                    preprocessed_ads.append(result)
                except Exception as e:
                    ad = future_to_ad[future]
                    logger.error("Batch item failed",
                                ad_id=ad.get('ad_id'),
                                error=str(e))
        
        successful = sum(
            1 for ad in preprocessed_ads
            if ad.get('quality', {}).get('preprocessing_status') == 'success'
        )
        
        logger.info("Batch preprocessing complete",
                   total=len(preprocessed_ads),
                   successful=successful,
                   failed=len(preprocessed_ads) - successful)
        
        return preprocessed_ads
