"""Model manager and cache for ML models"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
import torch
from typing import Dict, Optional, Tuple
import structlog
from pathlib import Path

logger = structlog.get_logger()


class ModelCache:
    """
    Manages loading and caching of pre-trained models
    Ensures models are loaded once and reused
    """
    
    def __init__(self, cache_dir: str = './model_cache'):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self._loaded_models = {}
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self._device}")
    
    def load_text_model(
        self, 
        model_name: str,
        task: str = 'classification'
    ) -> Tuple:
        """Load text model and tokenizer"""
        cache_key = f"text_{model_name}"
        
        if cache_key in self._loaded_models:
            logger.info("Using cached model", model=model_name)
            return self._loaded_models[cache_key]
        
        logger.info("Loading model", model=model_name, task=task)
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                cache_dir=str(self.cache_dir)
            )
            
            if task == 'embedding':
                model = AutoModel.from_pretrained(
                    model_name,
                    cache_dir=str(self.cache_dir)
                )
            else:
                model = AutoModelForSequenceClassification.from_pretrained(
                    model_name,
                    cache_dir=str(self.cache_dir)
                )
            
            model.to(self._device)
            model.eval()
            
            self._loaded_models[cache_key] = (model, tokenizer)
            logger.info("Model loaded successfully", model=model_name)
            
            return model, tokenizer
            
        except Exception as e:
            logger.error("Failed to load model", model=model_name, error=str(e))
            raise
    
    def clear_cache(self):
        """Clear all loaded models from memory"""
        self._loaded_models.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    
    @property
    def device(self):
        return self._device


# Global model cache instance
model_cache = ModelCache()
