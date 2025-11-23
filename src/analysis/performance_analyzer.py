"""
Performance Analysis Module
Calculates ROI, performance scores, and identifies high/low performers
"""

from typing import List, Dict, Any
import statistics
from datetime import datetime


class PerformanceAnalyzer:
    """Analyzes ad performance and generates insights"""
    
    def __init__(self):
        self.thresholds = {
            "high_performance": 0.75,  # Top 25%
            "low_performance": 0.25,   # Bottom 25%
            "min_impressions": 1000,   # Minimum impressions to be considered
        }
    
    def calculate_roi(self, ad: Dict[str, Any]) -> float:
        """
        Calculate ROI for an ad
        ROI = (Impressions / Spend) * 100
        """
        try:
            impressions = ad.get('impressions', 0)
            spend_range = ad.get('spend_range', {})
            
            if not impressions or not spend_range:
                return 0.0
            
            # Use average of spend range
            lower = spend_range.get('lower', 0)
            upper = spend_range.get('upper', 0)
            
            if lower == 0 and upper == 0:
                return 0.0
            
            avg_spend = (lower + upper) / 2 if upper > 0 else lower
            
            if avg_spend == 0:
                return 0.0
            
            roi = (impressions / avg_spend) * 100
            return round(roi, 2)
            
        except Exception:
            return 0.0
    
    def calculate_performance_score(self, ad: Dict[str, Any]) -> float:
        """
        Calculate overall performance score (0-100)
        Based on: ROI, impressions, engagement signals
        """
        score = 0.0
        
        # ROI component (40%)
        roi = self.calculate_roi(ad)
        if roi > 0:
            # Normalize ROI (cap at 1000 for scoring)
            roi_score = min(roi / 1000, 1.0) * 40
            score += roi_score
        
        # Impressions component (30%)
        impressions = ad.get('impressions', 0)
        if impressions > 0:
            # Normalize impressions (cap at 100k for scoring)
            imp_score = min(impressions / 100000, 1.0) * 30
            score += imp_score
        
        # Content quality component (30%)
        # Based on presence of key elements
        has_headline = bool(ad.get('headline'))
        has_body = bool(ad.get('body_text'))
        has_cta = bool(ad.get('call_to_action'))
        has_media = bool(ad.get('media_urls'))
        
        content_score = (
            (10 if has_headline else 0) +
            (10 if has_body else 0) +
            (5 if has_cta else 0) +
            (5 if has_media else 0)
        )
        score += content_score
        
        return round(min(score, 100), 2)
    
    def analyze_batch(self, ads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a batch of ads and generate insights
        """
        if not ads:
            return {
                "total_ads": 0,
                "analyzed_ads": [],
                "insights": {},
                "summary": {}
            }
        
        # Calculate metrics for each ad
        analyzed_ads = []
        for ad in ads:
            roi = self.calculate_roi(ad)
            performance_score = self.calculate_performance_score(ad)
            
            analyzed_ad = {
                **ad,
                "roi": roi,
                "performance_score": performance_score,
                "analyzed_at": datetime.utcnow().isoformat()
            }
            analyzed_ads.append(analyzed_ad)
        
        # Sort by performance score
        analyzed_ads.sort(key=lambda x: x['performance_score'], reverse=True)
        
        # Calculate statistics
        scores = [ad['performance_score'] for ad in analyzed_ads]
        rois = [ad['roi'] for ad in analyzed_ads if ad['roi'] > 0]
        
        avg_score = statistics.mean(scores) if scores else 0
        median_score = statistics.median(scores) if scores else 0
        avg_roi = statistics.mean(rois) if rois else 0
        
        # Identify high and low performers
        high_performers = [
            ad for ad in analyzed_ads 
            if ad['performance_score'] >= avg_score * 1.5
        ]
        
        low_performers = [
            ad for ad in analyzed_ads 
            if ad['performance_score'] <= avg_score * 0.5
        ]
        
        # Generate insights
        insights = self._generate_insights(
            analyzed_ads, 
            high_performers, 
            low_performers,
            avg_score,
            avg_roi
        )
        
        # Summary statistics
        summary = {
            "total_ads": len(analyzed_ads),
            "average_performance_score": round(avg_score, 2),
            "median_performance_score": round(median_score, 2),
            "average_roi": round(avg_roi, 2),
            "high_performers_count": len(high_performers),
            "low_performers_count": len(low_performers),
            "top_performing_ad": analyzed_ads[0]['ad_id'] if analyzed_ads else None,
            "worst_performing_ad": analyzed_ads[-1]['ad_id'] if analyzed_ads else None
        }
        
        return {
            "total_ads": len(analyzed_ads),
            "analyzed_ads": analyzed_ads,
            "high_performers": high_performers,
            "low_performers": low_performers,
            "insights": insights,
            "summary": summary,
            "analyzed_at": datetime.utcnow().isoformat()
        }
    
    def _generate_insights(
        self, 
        all_ads: List[Dict], 
        high_performers: List[Dict],
        low_performers: List[Dict],
        avg_score: float,
        avg_roi: float
    ) -> Dict[str, Any]:
        """Generate actionable insights from the analysis"""
        
        insights = {
            "alerts": [],
            "recommendations": [],
            "trends": {}
        }
        
        # Alerts for low performers
        if low_performers:
            insights["alerts"].append({
                "type": "warning",
                "severity": "high",
                "message": f"{len(low_performers)} ads are significantly underperforming",
                "affected_ads": [ad['ad_id'] for ad in low_performers[:5]],
                "recommendation": "Consider pausing or optimizing these campaigns"
            })
        
        # Alerts for high performers
        if high_performers:
            insights["alerts"].append({
                "type": "success",
                "severity": "info",
                "message": f"{len(high_performers)} ads are performing exceptionally well",
                "affected_ads": [ad['ad_id'] for ad in high_performers[:5]],
                "recommendation": "Consider increasing budget for these campaigns"
            })
        
        # Platform analysis
        platform_performance = {}
        for ad in all_ads:
            platform = ad.get('platform', 'unknown')
            if platform not in platform_performance:
                platform_performance[platform] = []
            platform_performance[platform].append(ad['performance_score'])
        
        best_platform = max(
            platform_performance.items(),
            key=lambda x: statistics.mean(x[1]) if x[1] else 0
        )[0] if platform_performance else None
        
        if best_platform:
            insights["trends"]["best_platform"] = {
                "platform": best_platform,
                "avg_score": round(statistics.mean(platform_performance[best_platform]), 2),
                "recommendation": f"Focus more budget on {best_platform} platform"
            }
        
        # Brand analysis
        brand_performance = {}
        for ad in all_ads:
            brand = ad.get('brand_name', 'Unknown')
            if brand not in brand_performance:
                brand_performance[brand] = []
            brand_performance[brand].append(ad['performance_score'])
        
        if brand_performance:
            top_brand = max(
                brand_performance.items(),
                key=lambda x: statistics.mean(x[1]) if x[1] else 0
            )
            
            insights["trends"]["top_performing_brand"] = {
                "brand": top_brand[0],
                "avg_score": round(statistics.mean(top_brand[1]), 2),
                "ad_count": len(top_brand[1])
            }
        
        # ROI insights
        if avg_roi > 0:
            high_roi_ads = [ad for ad in all_ads if ad['roi'] > avg_roi * 1.5]
            if high_roi_ads:
                insights["recommendations"].append({
                    "type": "roi_optimization",
                    "message": f"{len(high_roi_ads)} ads have exceptional ROI",
                    "action": "Analyze these ads for successful patterns to replicate",
                    "example_ads": [ad['ad_id'] for ad in high_roi_ads[:3]]
                })
        
        return insights
