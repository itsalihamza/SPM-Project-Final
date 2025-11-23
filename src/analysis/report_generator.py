"""
Report Generator
Creates JSON, CSV, and visual reports
"""

import json
import csv
from typing import List, Dict, Any
from pathlib import Path
from datetime import datetime
import structlog

logger = structlog.get_logger()

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False


class ReportGenerator:
    """Generates various report formats"""
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
    
    def generate_json_report(
        self, 
        analysis_results: Dict[str, Any],
        filename: str = None
    ) -> str:
        """Generate JSON report"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ad_analysis_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        return str(filepath.absolute())
    
    def generate_csv_report(
        self,
        ads: List[Dict[str, Any]],
        filename: str = None
    ) -> str:
        """Generate CSV report with key metrics"""
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ad_analysis_report_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # Define CSV columns
        columns = [
            'ad_id',
            'platform',
            'brand_name',
            'headline',
            'impressions',
            'spend_lower',
            'spend_upper',
            'roi',
            'performance_score',
            'collected_at'
        ]
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            
            for ad in ads:
                spend_range = ad.get('spend_range', {})
                row = {
                    'ad_id': ad.get('ad_id', ''),
                    'platform': ad.get('platform', ''),
                    'brand_name': ad.get('brand_name', ''),
                    'headline': ad.get('headline', '')[:100],  # Truncate
                    'impressions': ad.get('impressions', 0),
                    'spend_lower': spend_range.get('lower', 0) if spend_range else 0,
                    'spend_upper': spend_range.get('upper', 0) if spend_range else 0,
                    'roi': ad.get('roi', 0),
                    'performance_score': ad.get('performance_score', 0),
                    'collected_at': ad.get('collected_at', '')
                }
                writer.writerow(row)
        
        return str(filepath.absolute())
    
    def generate_visual_summary(
        self,
        analysis_results: Dict[str, Any],
        filename: str = None
    ) -> str:
        """Generate visual summary with charts"""
        
        if not MATPLOTLIB_AVAILABLE:
            logger.warning("Matplotlib not available. Skipping visual report.")
            return None
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ad_analysis_visual_{timestamp}.png"
        
        filepath = self.output_dir / filename
        
        ads = analysis_results.get('analyzed_ads', [])
        if not ads:
            return None
        
        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Ad Performance Analysis Dashboard', fontsize=16, fontweight='bold')
        
        # 1. Performance Score Distribution
        scores = [ad['performance_score'] for ad in ads]
        axes[0, 0].hist(scores, bins=20, color='skyblue', edgecolor='black')
        axes[0, 0].set_title('Performance Score Distribution')
        axes[0, 0].set_xlabel('Performance Score')
        axes[0, 0].set_ylabel('Number of Ads')
        axes[0, 0].axvline(
            analysis_results['summary']['average_performance_score'],
            color='red',
            linestyle='--',
            label='Average'
        )
        axes[0, 0].legend()
        
        # 2. Top 10 Performers
        top_10 = sorted(ads, key=lambda x: x['performance_score'], reverse=True)[:10]
        ad_labels = [f"{ad.get('brand_name', 'Unknown')[:15]}" for ad in top_10]
        scores_top = [ad['performance_score'] for ad in top_10]
        
        axes[0, 1].barh(ad_labels, scores_top, color='green')
        axes[0, 1].set_title('Top 10 Performing Ads')
        axes[0, 1].set_xlabel('Performance Score')
        axes[0, 1].invert_yaxis()
        
        # 3. Platform Performance
        platform_data = {}
        for ad in ads:
            platform = ad.get('platform', 'unknown')
            if platform not in platform_data:
                platform_data[platform] = []
            platform_data[platform].append(ad['performance_score'])
        
        platforms = list(platform_data.keys())
        avg_scores = [sum(scores)/len(scores) if scores else 0 
                     for scores in platform_data.values()]
        
        axes[1, 0].bar(platforms, avg_scores, color='orange')
        axes[1, 0].set_title('Average Performance by Platform')
        axes[1, 0].set_xlabel('Platform')
        axes[1, 0].set_ylabel('Average Performance Score')
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 4. ROI vs Impressions Scatter
        rois = [ad.get('roi', 0) for ad in ads if ad.get('roi', 0) > 0]
        impressions = [ad.get('impressions', 0) for ad in ads if ad.get('roi', 0) > 0]
        
        if rois and impressions:
            axes[1, 1].scatter(impressions, rois, alpha=0.6, color='purple')
            axes[1, 1].set_title('ROI vs Impressions')
            axes[1, 1].set_xlabel('Impressions')
            axes[1, 1].set_ylabel('ROI')
            axes[1, 1].set_xscale('log')
        else:
            axes[1, 1].text(0.5, 0.5, 'Insufficient ROI data', 
                          ha='center', va='center', fontsize=12)
            axes[1, 1].set_title('ROI vs Impressions')
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath.absolute())
    
    def generate_all_reports(
        self,
        analysis_results: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate all report types"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        reports = {}
        
        # JSON report
        json_path = self.generate_json_report(
            analysis_results,
            f"report_{timestamp}.json"
        )
        reports['json'] = json_path
        
        # CSV report
        if analysis_results.get('analyzed_ads'):
            csv_path = self.generate_csv_report(
                analysis_results['analyzed_ads'],
                f"report_{timestamp}.csv"
            )
            reports['csv'] = csv_path
        
        # Visual summary
        visual_path = self.generate_visual_summary(
            analysis_results,
            f"report_{timestamp}.png"
        )
        if visual_path:
            reports['visual'] = visual_path
        
        return reports
