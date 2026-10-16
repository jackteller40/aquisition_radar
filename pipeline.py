import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import csv
import time
from config import (PLATFORM_GATE_MODE, ARCHAIC_PLATFORMS,
                    MIN_MONTHLY_TRAFFIC, MAX_MONTHLY_TRAFFIC,
                    DATA_PATH)

from discovery.google_shopping import discover_targets
from enrichment.builtwith import enrich_builtwith
from enrichment.whois_lookup import enrich_whois
from enrichment.traffic import enrich_traffic

def run_pipeline(max_domains: int = 20) -> list[dict]:
    '''runs full aquisition radar pipeline
    
        1: discover domains w/ serp api
        2: platform gate (filter or flag archaic platforms)
        3: traffic enrichment
        4: owner fatigure enrichment
        
        returns list of enriched domain dicts ready for scoring
        '''
    #step 1
    print("\n" + "="* 60)
    print("STEP 1: DISCOVERING TARGETS")
    print("="*60)
    domains = discover_targets(max_per_keyword = 5)
    domains = [d for d in domains if is_legitimate_domain(d)]
    print(f"After quality filter: {len(domains)} legitimate domains")
    domains = domains[:max_domains]
    print(f"Proceeding with {len(domains)} domains")
    
    #step 2
    print("\n" + "="* 60)
    print("STEP 2: PLATFORM DETECTION")
    print("="*60)
    
    platform_results = []
    for domain in domains:
        print(f"Checking platform: {domain}")
        result = enrich_builtwith(domain)
        platform = result.get("platform","unknown").lower()
        result["is_archaic"] = platform in ARCHAIC_PLATFORMS
        platform_results.append(result)
        time.sleep(1)
    
    #gate
    if PLATFORM_GATE_MODE == "strict":
        gated = [ r for r in platform_results if r["is_archaic"]]
        print(f"\nStrict gate : {len(gated)}/{len(platform_results)} passed")
    else:
        gated = platform_results
        archaic_count = sum(1 for r in gated if r["is_archaic"])
        print(f"\nSoft gate: all {len(gated)} passed, {archaic_count} flagged archaic")
    
    #step 3
    print("\n" + "="* 60)
    print("STEP 3: TRAFFIC ANALYSIS")
    print("="*60)
    
    enriched = []
    for result in gated:
        domain = result["domain"]
        print(f"Pulling traffic: {domain}")
        traffic = enrich_traffic(domain)
        result.update(traffic)
        enriched.append(result)
        time.sleep(1)

    before = len(enriched)
    enriched = [r for r in enriched if in_traffic_band(r)]
    if len(enriched) < before:
        print(f"Traffic band filter: dropped {before - len(enriched)} outside "
              f"{MIN_MONTHLY_TRAFFIC:,}-{MAX_MONTHLY_TRAFFIC:,} monthly visits")
    
    # step 4
    print("\n" + "="* 60)
    print("STEP 4: OWNER FATIGUE")
    print("="*60)
    
    final = []
    for result in enriched:
        domain = result["domain"]
        print(f"WhoIs lookup: {domain}")
        whois_data = enrich_whois(domain)
        result.update(whois_data)
        final.append(result)
        time.sleep(0.5)
        
    save_to_csv(final)
    print(f"\nPipeline complete, {len(final)} targets enriched")
    return final

def in_traffic_band(result: dict) -> bool:
    """keeps targets inside the configured monthly traffic band.
    only SEMrush returns a visit estimate; SerpAPI mode has no visit count,
    so targets without one pass through rather than being dropped."""
    traffic = result.get("organic_traffic")
    if traffic is None:
        return True
    total = traffic + (result.get("paid_traffic") or 0)
    return MIN_MONTHLY_TRAFFIC <= total <= MAX_MONTHLY_TRAFFIC

def is_legitimate_domain(domain: str) -> bool:
    blacklist_keywords = ["walmart-", "amazon-", ".com.com", ".ltd.com", "ebay-"]
    blacklist_domains = {
        "bestbuy.com", "ultabeauty.com", "iqair.com", "walmart.com",
        "amazon.com", "amazon.com", "target.com", "costco.com", 
        "homedepot.com", "cvspharmacy.com", "dickssportinggoods.com",
        "walgreens.com", "kroger.com"
    }
    if any(kw in domain.lower() for kw in blacklist_keywords):
        return False
    if domain in blacklist_domains:
        return False
    if domain.count(".") != 1:
        return False
    if len(domain) > 50:
        return False
    return True

def save_to_csv(targets: list[dict]):
    if not targets:
        return
    
    DATA_PATH.parent.mkdir(exist_ok = True)
    keys = targets[0].keys()
    
    with open(DATA_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames = keys)
        writer.writeheader()
        writer.writerows(targets)
        
    print(f"\nSaved to {DATA_PATH}")
    
if __name__ == ("__main__"):
    results = run_pipeline(max_domains=10)
    for r in results:
        print(r)  