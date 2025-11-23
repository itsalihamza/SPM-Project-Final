"""Main application entry point"""

import argparse
import structlog
from pathlib import Path
from src.collection.collectors.meta_ad_library import MetaAdLibraryCollector
from src.collection.collectors.mock_collector import MockAdCollector
from src.collection.collectors.bigspy_collector import BigSpyCollector
from src.collection.collectors.google_ads_collector import GoogleAdsCollector
from src.collection.collectors.meta_web_scraper import MetaWebScraper
from src.collection.collectors.base_collector import CollectionConfig
from src.preprocessing.pipeline import PreprocessingPipeline
from src.classification.pipeline import ClassificationPipeline

logger = structlog.get_logger()


def main():
    parser = argparse.ArgumentParser(
        description='Autonomous Competitor Ad Intelligence Agent'
    )
    parser.add_argument(
        '--keywords',
        nargs='+',
        required=True,
        help='Keywords to search for'
    )
    parser.add_argument(
        '--platform',
        default='mock',
        choices=['meta', 'metaweb', 'web', 'mock', 'bigspy', 'google'],
        help='Platform to collect from (mock=testing, metaweb=free scraper, meta=requires token)'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=100,
        help='Maximum number of ads to collect'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='./data/output.json',
        help='Output file path'
    )
    
    args = parser.parse_args()
    
    logger.info("Starting Ad Intelligence Agent",
                platform=args.platform,
                keywords=args.keywords,
                max_results=args.max_results)
    
    # 1. Data Collection
    logger.info("STEP 1: Data Collection")
    config = CollectionConfig(
        platform=args.platform,
        keywords=args.keywords,
        max_results=args.max_results,
        rate_limit_per_second=0.5
    )
    
    if args.platform == 'meta':
        collector = MetaAdLibraryCollector(config)
    elif args.platform == 'metaweb':
        collector = MetaWebScraper(config)
    elif args.platform == 'mock':
        collector = MockAdCollector(config)
    elif args.platform == 'bigspy':
        collector = BigSpyCollector(config)
    elif args.platform == 'google':
        collector = GoogleAdsCollector(config)
    else:
        logger.error("Platform not yet implemented", platform=args.platform)
        return
    
    raw_ads = collector.run()
    logger.info(f"Collected {len(raw_ads)} ads")
    
    # 2. Preprocessing
    logger.info("STEP 2: Preprocessing & Normalization")
    preprocessing = PreprocessingPipeline()
    preprocessed_ads = preprocessing.preprocess_batch(raw_ads, max_workers=4)
    logger.info(f"Preprocessed {len(preprocessed_ads)} ads")
    
    # 3. Classification
    logger.info("STEP 3: Classification & Tagging")
    classification = ClassificationPipeline()
    classified_ads = classification.classify_batch(preprocessed_ads, max_workers=4)
    logger.info(f"Classified {len(classified_ads)} ads")
    
    # 4. Save results
    import json
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(classified_ads, f, indent=2, ensure_ascii=False)
    
    logger.info("Pipeline complete", output=str(output_path.absolute()))


if __name__ == '__main__':
    main()
