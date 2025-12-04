"""Mock data collector for testing without API access"""

from typing import List, Dict
from datetime import datetime, timedelta
import random
import time
from src.collection.collectors.base_collector import BaseCollector, CollectionConfig


class MockAdCollector(BaseCollector):
    """
    Enhanced mock collector that generates realistic ad data with delays
    Simulates real web scraping behavior for testing
    """
    
    # Extended brand database with industry categories for more realistic data
    SAMPLE_BRANDS = {
        "Sports & Fitness": ["Nike", "Adidas", "Puma", "Under Armour", "Reebok", "New Balance", 
                             "Skechers", "Asics", "Fila", "Converse", "Vans", "Jordan",
                             "Lululemon", "Gymshark", "The North Face", "Patagonia", "Columbia"],
        "Technology": ["Apple", "Samsung", "Sony", "Microsoft", "Dell", "HP", "Lenovo",
                       "Google", "Amazon", "Meta", "Netflix", "Spotify", "Adobe"],
        "Retail": ["Amazon", "eBay", "Walmart", "Target", "Best Buy", "Costco", 
                   "Home Depot", "IKEA", "Zara", "H&M", "Gap"],
        "Food & Beverage": ["McDonald's", "Starbucks", "Subway", "KFC", "Pizza Hut", "Domino's",
                            "Coca-Cola", "Pepsi", "Red Bull", "Monster", "Gatorade", "Sprite",
                            "Chipotle", "Dunkin'", "Taco Bell"],
        "Automotive": ["BMW", "Mercedes-Benz", "Toyota", "Honda", "Ford", "Tesla", "Audi",
                       "Volkswagen", "Nissan", "Chevrolet", "Hyundai"],
        "Beauty & Personal Care": ["L'Oréal", "Estée Lauder", "Dove", "Nivea", "Clinique",
                                    "Sephora", "Ulta Beauty", "MAC", "Maybelline"],
        "Finance": ["Chase", "Bank of America", "Wells Fargo", "American Express", "PayPal",
                    "Capital One", "Visa", "Mastercard"]
    }
    
    # Flatten brands for easy selection
    ALL_BRANDS = [brand for brands in SAMPLE_BRANDS.values() for brand in brands]
    
    # Realistic ad headlines by category
    SAMPLE_HEADLINES = [
        # Sales & Promotions
        "Flash Sale - Up to 70% Off Everything",
        "Summer Clearance - Save Big Today",
        "Limited Time: Buy 2 Get 1 Free",
        "Weekend Special - Extra 25% Off Sale Items",
        "Black Friday Deals Start Now - Don't Miss Out",
        "Cyber Monday Sale Live Now",
        "End of Season Sale - Huge Discounts",
        "Member Exclusive: 40% Off Your First Purchase",
        "Save up to 50% on Selected Items",
        "Clearance Event - Everything Must Go",
        "Special Discount Code Inside - SAVE20",
        
        # Product Launches
        "Introducing Our Latest Collection",
        "New Arrivals - Shop The Hottest Trends",
        "Just Dropped: The 2025 Edition",
        "Be The First To Own Our New Release",
        "Revolutionary New Product Available Now",
        "Pre-Order Now - Ships Next Week",
        "Experience Innovation Like Never Before",
        "The Wait Is Over - Available Today",
        
        # Urgency & FOMO
        "Only 3 Hours Left - Final Chance to Save",
        "Last Chance: Sale Ends Tonight at Midnight",
        "Hurry - Almost Sold Out",
        "Limited Stock Available - Act Fast",
        "Today Only: Exclusive Special Offer",
        "Don't Miss Out - Offer Expires Soon",
        "While Supplies Last - Shop Now",
        "Final Hours - Get Yours Before It's Gone",
        
        # Value Props
        "Free Shipping on All Orders Over $50",
        "Free Returns Within 30 Days",
        "Price Match Guarantee - We Won't Be Beaten",
        "0% Financing Available for 12 Months",
        "100% Money Back Guarantee",
        "Premium Quality at Affordable Prices",
        "Best Value for Your Money",
        
        # Social Proof & Trust
        "Join 10 Million Happy Customers Worldwide",
        "Rated 4.9 Stars by Thousands of Reviews",
        "Trusted By Professionals Since 2010",
        "See What Everyone's Talking About",
        "As Seen On TV - Now Available Online",
        "Award-Winning Product of the Year",
        "Recommended by Industry Experts",
        
        # Seasonal & Events
        "Perfect Holiday Gift for Everyone",
        "Back To School Special - Save Big",
        "Spring Into Savings Event",
        "Winter Collection Now Available",
        "Valentine's Day Sale - Show Your Love",
        "Mother's Day Special Offers",
        "Father's Day Gift Guide",
        
        # Product Features
        "Discover Premium Quality You Can Trust",
        "Advanced Technology Meets Style",
        "Sustainable & Eco-Friendly Products",
        "Handcrafted Excellence in Every Detail",
        "Designed for Comfort & Performance",
        "Built to Last - Lifetime Warranty",
        
        # Action-Oriented
        "Transform Your Lifestyle Today",
        "Upgrade Your Experience Right Now",
        "Start Your Journey With Us",
        "Make Every Day Better",
        "Level Up Your Game",
        "Unlock Your Full Potential"
    ]
    
    # Realistic ad body text - more detailed and varied
    SAMPLE_BODY_TEXT = [
        "Experience unmatched quality and style with our latest collection. Premium materials, expert craftsmanship, and designs that stand out. Shop now and elevate your lifestyle with products built to last.",
        "Transform the way you live, work, and play. Our innovative products are designed with you in mind, combining cutting-edge technology with user-friendly features. Free shipping on all orders over $50.",
        "Don't miss out on this limited-time opportunity to save big on your favorite products. Join millions of satisfied customers worldwide who trust us for quality, value, and exceptional service.",
        "Discover why customers rate us 4.9 out of 5 stars. From unbeatable prices to exceptional customer service, we deliver excellence every time. Shop with confidence today with our 30-day money-back guarantee.",
        "Upgrade your experience with cutting-edge technology and timeless design. Whether you're a beginner or a seasoned pro, we have something for everyone. Browse our extensive collection and find your perfect match.",
        "Quality you can trust, prices you'll love. Our commitment to excellence means you always get the best value for your money. Every product is carefully tested and backed by our satisfaction guarantee.",
        "Get ready to turn heads with our exclusive collection. Carefully curated for style, comfort, and durability. Limited quantities available - shop now before they're gone forever.",
        "Join our community of over 10 million happy customers and see the difference for yourself. 100% satisfaction guaranteed or your money back. No questions asked.",
        "Premium features at an unbeatable price. We believe everyone deserves the best, which is why we make high-quality products accessible to all. Experience luxury without breaking the bank.",
        "Your search ends here. With thousands of verified 5-star reviews and industry-leading warranties, you can shop with total peace of mind. Fast shipping, easy returns, and dedicated customer support.",
        "Sustainable, eco-friendly, and built to last a lifetime. Make a choice that's good for you and the planet. Shop consciously today and join the movement towards a better tomorrow.",
        "Fast, free delivery right to your door within 2-3 business days. Plus, hassle-free returns for up to 60 days if you're not completely satisfied. It's that simple and risk-free.",
        "Designed by industry experts, loved by millions worldwide. Our products combine innovation with practicality to bring you the ultimate experience. See why we're the #1 choice in our category.",
        "Limited edition release - once they're gone, they're gone forever. Don't let this opportunity slip through your fingers. Order now and be part of something special.",
        "Exclusive online offer you won't find anywhere else. Save up to 40% when you shop directly from us. Plus, get instant access to members-only deals and early product launches.",
        "Engineered for peak performance and maximum comfort. Our team spent years perfecting every detail so you don't have to compromise. Experience the difference quality makes.",
        "From our family to yours - 25 years of trusted service. We're not just selling products, we're building relationships. Shop with a company that truly cares about your satisfaction.",
        "Made with premium materials sourced from around the world. Each piece is inspected for quality before it reaches your hands. We never cut corners, so you get products that exceed expectations.",
        "The perfect blend of style and functionality. Our award-winning design team creates products that look as good as they perform. Upgrade your collection today.",
        "Backed by a lifetime warranty and 24/7 customer support. We stand behind every product we sell because your satisfaction is our top priority. Try it risk-free today.",
        "Discover what over 500,000 customers already know - we're the best in the business. Join our loyal community and experience world-class quality, unbeatable prices, and service that goes above and beyond.",
        "Limited time offer - save an extra 15% when you buy today. Use code SAVE15 at checkout. Plus, get free gift wrapping on all orders. Perfect for treating yourself or someone special.",
        "Certified by industry leaders and trusted by professionals worldwide. When only the best will do, choose the brand that delivers exceptional results every single time.",
        "From casual everyday use to professional applications, our versatile products adapt to your needs. One solution, endless possibilities. Find out why we're the preferred choice.",
        "Revolutionary technology meets classic design. Experience innovation that changes the game while maintaining the timeless appeal you love. Available now in multiple colors and sizes."
    ]
    
    # Call-to-action variations
    SAMPLE_CTA = [
        "Shop Now", "Learn More", "Sign Up Today", "Get Started", "Buy Now",
        "Order Now", "Claim Offer", "Join Free", "Download Now", "Try Free",
        "Get Yours", "Reserve Now", "See Details", "Explore More", "Book Now",
        "Subscribe", "View Collection", "Start Shopping", "Discover More"
    ]
    
    def __init__(self, config: CollectionConfig):
        super().__init__(config)
        self.logger.info("Using Enhanced MockAdCollector - simulating realistic web scraping")
    
    def collect(self) -> List[Dict]:
        """Generate realistic mock ad data with simulated scraping delays"""
        all_ads = []
        num_ads = min(self.config.max_results, 100)  # Support up to 100 ads
        
        self.logger.info(f"Starting simulated scraping for {num_ads} ads...")
        
        for i in range(num_ads):
            # Simulate realistic scraping delay (0.8-2.5 seconds per ad - more realistic)
            delay = random.uniform(0.8, 2.5)
            time.sleep(delay)
            
            if (i + 1) % 5 == 0:
                self.logger.info(f"Scraped {i + 1}/{num_ads} ads... ({int((i+1)/num_ads*100)}% complete)")
            
            # Select brand and determine industry
            brand = random.choice(self.ALL_BRANDS)
            industry = next((k for k, v in self.SAMPLE_BRANDS.items() if brand in v), "Other")
            
            # Generate highly realistic engagement metrics based on spend
            # Higher spend = more impressions (realistic correlation)
            spend_lower = random.randint(500, 5000)
            spend_upper = spend_lower + random.randint(2000, 15000)
            
            # Calculate impressions based on average CPM ($5-$20)
            avg_spend = (spend_lower + spend_upper) / 2
            cpm = random.uniform(5, 20)
            estimated_impressions = int((avg_spend / cpm) * 1000)
            
            impressions_lower = int(estimated_impressions * random.uniform(0.7, 0.9))
            impressions_upper = int(estimated_impressions * random.uniform(1.1, 1.5))
            
            # Randomly decide if ad is still active (70% active)
            start_date = datetime.now() - timedelta(days=random.randint(1, 90))
            is_active = random.random() < 0.70
            stop_date = None if is_active else start_date + timedelta(days=random.randint(7, 60))
            
            # Generate realistic CTR and engagement
            ctr = random.uniform(0.5, 5.0)  # Click-through rate percentage
            clicks = int((impressions_lower + impressions_upper) / 2 * ctr / 100)
            conversions = int(clicks * random.uniform(0.01, 0.15))  # 1-15% conversion rate
            
            # Make headlines and content more brand-relevant
            headline = random.choice(self.SAMPLE_HEADLINES)
            body = random.choice(self.SAMPLE_BODY_TEXT)
            
            # Add brand name naturally to some ads
            if random.random() < 0.4:
                headline = f"{brand}: {headline}"
            
            # Generate realistic ad ID based on platform format
            # Facebook/Meta: 17-19 digit numeric IDs
            # Google Ads: mix of numbers and letters
            ad_id_format = random.choice([
                f"{random.randint(100000000000000000, 999999999999999999)}",  # Facebook/Meta format (18 digits)
                f"{random.randint(10000000000000000, 99999999999999999)}",   # Facebook/Meta format (17 digits)
                f"gad_{random.randint(1000000000, 9999999999)}_{random.randint(100000, 999999)}",  # Google Ads format
                f"{random.randint(1000000000000, 9999999999999)}",  # LinkedIn/Twitter format (13 digits)
            ])
            
            ad = {
                "id": ad_id_format,
                "ad_creative_bodies": [headline],
                "ad_creative_link_descriptions": [body],
                "ad_creative_link_captions": [random.choice(self.SAMPLE_CTA)],
                "ad_creative_link_titles": [f"{brand} - Official {random.choice(['Store', 'Site', 'Shop', 'Website'])}"],
                "industry": industry,
                "ad_delivery_start_time": start_date.isoformat(),
                "ad_delivery_stop_time": stop_date.isoformat() if stop_date else None,
                "ad_snapshot_url": f"https://facebook.com/ads/library/?id={random.randint(100000000000, 999999999999)}",
                "currency": "USD",
                "funding_entity": f"{brand} {random.choice(['Inc.', 'LLC', 'Corp.', 'Ltd.'])}",
                "page_name": f"{brand} {random.choice(['Official', 'Global', 'USA', 'Store', ''])}".strip(),
                "page_id": random.randint(1000000000, 9999999999),
                "impressions": {
                    "lower_bound": impressions_lower,
                    "upper_bound": impressions_upper
                },
                "spend": {
                    "lower_bound": spend_lower,
                    "upper_bound": spend_upper
                },
                "currency": random.choice(["USD", "USD", "USD", "EUR", "GBP"]),  # 60% USD
                # Additional realistic fields
                "publisher_platforms": random.choice([
                    ["facebook"], 
                    ["instagram"], 
                    ["facebook", "instagram"],
                    ["messenger"], 
                    ["audience_network"],
                    ["facebook", "instagram", "messenger"]
                ]),
                "estimated_audience_size": {
                    "lower_bound": random.randint(500000, 2000000),
                    "upper_bound": random.randint(2000000, 15000000)
                },
                "ad_delivery_optimization": random.choice([
                    "link_clicks", "impressions", "reach", "conversions",
                    "landing_page_views", "post_engagement", "video_views"
                ]),
                "target_age": f"{random.choice([18, 25, 35, 45])}-{random.choice([24, 34, 44, 54, 65])}",
                "target_gender": random.choice(["All", "Men", "Women"]),
                "regions": random.choice([
                    ["United States"], 
                    ["United States", "Canada"],
                    ["United States", "United Kingdom", "Australia"],
                    ["Worldwide"]
                ]),
                # Realistic engagement metrics
                "clicks": clicks,
                "conversions": conversions,
                "ctr": round(ctr, 2),
                "cpc": round((spend_lower + spend_upper) / 2 / clicks if clicks > 0 else 0, 2),
                "conversion_rate": round(conversions / clicks * 100 if clicks > 0 else 0, 2)
            }
            all_ads.append(ad)
            
        self.logger.info(f"✓ Successfully scraped {len(all_ads)} ads (simulated)")
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
            "ad_id": raw_data.get('id'),  # Use realistic platform-style IDs directly
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
