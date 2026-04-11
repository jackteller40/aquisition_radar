import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import requests
from bs4 import BeautifulSoup

PLATFORM_SIGNALS = {
    "shopify": ["shopify", "myshopify", "cdn.shopify"],
    "woocommerce": ["woocommerce", "wp-content"],
    "magento": ["magento", "mage"],
    "bigcommerce": ["bigcommerce", "bigcommerce.com"],
    "squarespace": ["squarespace"],
    "wix": ["wix.com", "wixsite"]
}

TECH_SIGNALS = {
    "has_klaviyo": ["klaviyo"],
    "has_review_app": ["yotpo", "okendo", "stamped", "judge.me", "trustpilot", "reviews.io"],
    "has_abandoned_cart": ["klaviyo", "omnisend", "drip", "cartstack"],
    "has_live_chat": ["intercom", "drift", "tidio", "gorgias", "zendesk"],
}

def detect_platform(html: str) -> str:
    html_lower = html.lower()
    for platform, signals in PLATFORM_SIGNALS.items():
        if any(s in html_lower for s in signals):
            return platform
    return "unknown"
    
def detect_tech(html: str) -> dict:
    html_lower = html.lower()
    result = {}
    for key, signals in TECH_SIGNALS.items():
        result[key] = any(s in html_lower for s in signals)
    return result

def enrich_builtwith(domain: str) -> dict:
    result = {"domain": domain, "platform": "unknown"}
    for key in TECH_SIGNALS:
        result[key] = False
        
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh, Intel Mac OS X 10_15_7)"}
        response = requests.get(
            f"https://{domain}",
            headers = headers,
            timeout = 25
        )
        response.raise_for_status()
        html = response.text
        
        result["platform"] = detect_platform(html)
        result.update(detect_tech(html))
        
    except Exception as e:
        print(f"BuiltWith failed for {domain}: {e}")
        
    return result

if __name__ == "__main__":
    test = enrich_builtwith("toolsforwellness.com")
    print(test)