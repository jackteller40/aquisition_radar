import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import requests
import re
from urllib.parse import urlparse
from config import SERP_API_KEY, SEED_KEYWORDS

def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    return domain

def is_valid_target(domain: str) -> bool:
    blacklist = {
        "amazon.com", "ebay.com", "walmart.com", "target.com", "facebook.com", "instagram.com",
        "youtube.com", "pinterest.com", "google.com", "bing.com", "yahoo.com", "reddit.com",
        "healthline.com", "webmd.com", "mayoclinic.org", "toolsforwellness.com",
        "walmart-toolsforwellness.com"
    }
    return domain not in blacklist and domain != ""

def search_google_shopping(keyword: str) -> list[str]:
    """search google shopping for keyword and return list of domains
    that appear in the results"""
    
    params ={
        "engine": "google_shopping",
        "q": keyword,
        "api_key": SERP_API_KEY,
        "num": 20
    }
    
    try:
        response = requests.get(
            "https://serpapi.com/search",
            params = params,
            timeout = 10
        )
        response.raise_for_status()
        data = response.json()
        
        domains = []
        for result in data.get("shopping_results", []):
            source = result.get("source", "")
            link = result.get("link", "")
            
            if link:
                domain = extract_domain(link)
            elif source:
                domain = source.lower().replace(" ", "") + ".com"
            else:
                continue
            
            if is_valid_target(domain):
                domains.append(domain)
                
        return domains
    
    except requests.RequestException as e:
        print(f"Error Searching '{keyword}': {e}")
        return []
    
def discover_targets(max_per_keyword: int = 10) -> list[str]:
    """run discovery across seed keywords and return a deduplicated list of target domains"""
    all_domains = set()
    
    for keyword in SEED_KEYWORDS:
        print(f"Searching: {keyword}")
        domains = search_google_shopping(keyword)
        for domain in domains[:max_per_keyword]:
            all_domains.add(domain)
        print(f" Found {len(domains)} domains")
        
    print(f"\nTotal unique targets discovered: {len(all_domains)}")
    return list(all_domains)

if __name__ == "__main__":
    targets = discover_targets()
    for t in targets:
        print(t)
        