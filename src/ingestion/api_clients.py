import random
from typing import Dict, List, Any

# Mock databases of review templates for sync simulation
MOCK_APP_STORE_REVIEWS = [
    ("Love this app! It has completely solved our team tracking problems.", 5),
    ("The latest update crashes on launch on my iPhone 14. Please fix ASAP!", 1),
    ("It's decent but missing iPad multitasking support. Please add it.", 3),
    ("Extremely slow loading times when syncing large files. Disappointed.", 2),
    ("A clean and elegant interface. Highly recommended for designers.", 5),
    ("Can you please add support for dark mode? The white screen hurts my eyes.", 4)
]

MOCK_GOOGLE_PLAY_REVIEWS = [
    ("Battery drain is insane after the last security update. Uninstalled.", 1),
    ("Works flawlessly on my Pixel 8. Best investment I've made this year.", 5),
    ("Too expensive for the basic features. Subscription cost is too high.", 2),
    ("Great customer service! They resolved my account lockout in 10 minutes.", 5),
    ("Very confusing layout. Buttons are overlapping on smaller screens.", 2)
]

MOCK_G2_REVIEWS = [
    ("Excellent enterprise-grade tool. Scalability is unmatched. However, pricing is steep.", 4),
    ("Jira integration is broken. We cannot sync our support tickets. Critical blocker for our developers.", 1),
    ("Feature-rich platform, but the learning curve is quite steep. Support docs need improvement.", 3),
    ("The ROI we've seen since implementing this has been outstanding. +30% productivity.", 5),
    ("Frequent database connection errors during peak hours. High latency.", 2)
]

class AppStoreClient:
    """Mock client to simulate pulling review data from the Apple App Store."""
    def __init__(self, app_id: str):
        self.app_id = app_id

    def fetch_latest_reviews(self) -> List[Dict[str, Any]]:
        reviews = []
        # Generate 2 to 4 random reviews
        samples = random.sample(MOCK_APP_STORE_REVIEWS, random.randint(2, 4))
        for text, rating in samples:
            reviews.append({
                "text": text,
                "rating": rating,
                "source": "api_appstore",
                "metadata_json": {
                    "app_id": self.app_id,
                    "reviewer": f"iOS_User_{random.randint(100, 999)}",
                    "device": "iPhone"
                }
            })
        return reviews

class GooglePlayClient:
    """Mock client to simulate pulling reviews from the Google Play Store."""
    def __init__(self, package_name: str):
        self.package_name = package_name

    def fetch_latest_reviews(self) -> List[Dict[str, Any]]:
        reviews = []
        samples = random.sample(MOCK_GOOGLE_PLAY_REVIEWS, random.randint(2, 4))
        for text, rating in samples:
            reviews.append({
                "text": text,
                "rating": rating,
                "source": "api_googleplay",
                "metadata_json": {
                    "package_name": self.package_name,
                    "reviewer": f"Android_User_{random.randint(100, 999)}",
                    "version": "v3.1.2"
                }
            })
        return reviews

class G2Client:
    """Mock client to simulate pulling enterprise reviews from G2 Crowd."""
    def __init__(self, product_slug: str):
        self.product_slug = product_slug

    def fetch_latest_reviews(self) -> List[Dict[str, Any]]:
        reviews = []
        samples = random.sample(MOCK_G2_REVIEWS, random.randint(2, 3))
        for text, rating in samples:
            # G2 reviews represent enterprise accounts
            reviews.append({
                "text": text,
                "rating": rating,
                "source": "api_g2",
                "metadata_json": {
                    "product_slug": self.product_slug,
                    "segment": "Enterprise",
                    "company_size": "500-1000 employees"
                }
            })
        return reviews
