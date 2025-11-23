"""
Demo script showing all analytics and reporting features
"""

import requests
import json
import time

API_URL = "http://localhost:8000"

print("="*80)
print("AD INTELLIGENCE AGENT - ANALYTICS & REPORTING DEMO")
print("="*80)

print("\n📊 Collecting ads with full analysis and reporting...\n")

# Make request with analysis
response = requests.post(
    f"{API_URL}/api/v1/collect",
    json={
        "keywords": ["Nike", "Adidas"],
        "platform": "mock",
        "max_results": 20
    },
    timeout=60
)

if response.status_code == 200:
    data = response.json()
    
    print("✅ SUCCESS!\n")
    
    # Collection Summary
    print("="*80)
    print("📦 COLLECTION SUMMARY")
    print("="*80)
    print(f"Total Collected: {data['total_collected']}")
    print(f"Total Preprocessed: {data['total_preprocessed']}")
    print(f"Total Classified: {data['total_classified']}")
    print(f"Execution Time: {data['execution_time_seconds']:.2f}s")
    
    # Performance Analysis Summary
    if 'analysis' in data:
        analysis = data['analysis']
        summary = analysis['summary']
        
        print("\n" + "="*80)
        print("📈 PERFORMANCE ANALYSIS")
        print("="*80)
        print(f"Average Performance Score: {summary['average_performance_score']}")
        print(f"Median Performance Score: {summary['median_performance_score']}")
        print(f"Average ROI: {summary['average_roi']}")
        print(f"High Performers: {summary['high_performers_count']}")
        print(f"Low Performers: {summary['low_performers_count']}")
        
        # Insights & Alerts
        insights = analysis['insights']
        
        print("\n" + "="*80)
        print("🚨 ALERTS & INSIGHTS")
        print("="*80)
        
        if insights.get('alerts'):
            for i, alert in enumerate(insights['alerts'], 1):
                print(f"\n{i}. [{alert['type'].upper()}] {alert['message']}")
                print(f"   Recommendation: {alert['recommendation']}")
        
        # Trends
        if insights.get('trends'):
            print("\n" + "="*80)
            print("📊 TRENDS")
            print("="*80)
            
            if 'best_platform' in insights['trends']:
                bp = insights['trends']['best_platform']
                print(f"\nBest Platform: {bp['platform']}")
                print(f"  Average Score: {bp['avg_score']}")
                print(f"  Recommendation: {bp['recommendation']}")
            
            if 'top_performing_brand' in insights['trends']:
                tb = insights['trends']['top_performing_brand']
                print(f"\nTop Performing Brand: {tb['brand']}")
                print(f"  Average Score: {tb['avg_score']}")
                print(f"  Ad Count: {tb['ad_count']}")
        
        # High Performers
        print("\n" + "="*80)
        print("🌟 TOP 5 HIGH PERFORMERS")
        print("="*80)
        
        for i, ad in enumerate(analysis['high_performers'][:5], 1):
            print(f"\n{i}. {ad.get('brand_name', 'Unknown')}")
            print(f"   Performance Score: {ad['performance_score']}")
            print(f"   ROI: {ad['roi']}")
            print(f"   Impressions: {ad.get('impressions', 'N/A')}")
        
        # Low Performers
        if analysis['low_performers']:
            print("\n" + "="*80)
            print("⚠️  BOTTOM 5 LOW PERFORMERS")
            print("="*80)
            
            for i, ad in enumerate(analysis['low_performers'][:5], 1):
                print(f"\n{i}. {ad.get('brand_name', 'Unknown')}")
                print(f"   Performance Score: {ad['performance_score']}")
                print(f"   ROI: {ad['roi']}")
    
    # Generated Reports
    if 'reports' in data:
        reports = data['reports']
        
        print("\n" + "="*80)
        print("📄 GENERATED REPORTS")
        print("="*80)
        
        if 'json' in reports:
            print(f"\n✅ JSON Report: {reports['json']}")
        
        if 'csv' in reports:
            print(f"✅ CSV Report: {reports['csv']}")
        
        if 'visual' in reports:
            print(f"✅ Visual Dashboard: {reports['visual']}")
    
    print("\n" + "="*80)
    print("🎉 DEMO COMPLETE!")
    print("="*80)
    print("\nCheck the 'reports' folder for generated files:")
    print("  - JSON report with full analysis")
    print("  - CSV file for Excel/spreadsheet import")
    print("  - PNG dashboard with performance charts")
    
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
