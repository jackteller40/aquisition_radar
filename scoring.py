import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from config import WEIGHTS, DOMAIN_AGE_FATIGUE, ARCHAIC_PLATFORMS

def score_traffic_and_seo(target: dict) -> float:
    #scores based on organc presence signals
    #lower indexed pages and organic results = higher distress = higher score
    
    score = 0.0
    indexed = target.get("indexed_pages") or 0
    organic = target.get("organic_results") or 0
    
    if indexed == 0:
        score += 40
    elif indexed < 100:
        score += 30
    elif indexed < 1000:
        score += 20
    elif indexed < 1000:
        score += 10
    else: 
        score += 0
        
    if organic == 0:
        score += 40
    elif organic < 5:
        score += 25
    elif organic < 10:
        score += 10
    else:
        score += 10
        
    if target.get("has_paid_ads"):
        score += 20
    
    return min(score, 100)

def score_operational_gaps(target: dict) -> float:
    '''scores based on missing tools and infrastructure
    more gaps = higher oppurtunity = higher score'''
    
    score = 0.0
    
    if not target.get("has_klaviyo"): 
        score += 35
    if not target.get("has_review_app"):
        score += 25
    if not target.get("has_abandoned_cart"):
        score += 25
    if not target.get("has_live_chat"):
        score += 15
    
    return min(score, 100)

def score_owner_fatigue(target: dict) -> float:
    '''scores based on domain age as proxy for owner fatigure
    older domain = more likely owner fatigue'''
    
    score = 0.0
    age = target.get("domain_age") or 0
    
    if age >= 20:
        score = 100
    elif age >= 15:
        score = 80
    elif age >= DOMAIN_AGE_FATIGUE:
        score = 60
    elif age >= 5:
        score = 30
    else:
        score = 10
        
    return score

def score_platform_signals(target: dict) -> float:
    #scores based on platform, archaic platforms scoring higher
    
    platform = (target.get("platform") or "unknown").lower()
    
    if platform == "woocommerce": 
        return 100
    elif platform == "magento":
        return 90
    elif platform == "wordpress":
        return 80
    elif platform == "unknown":
        return 10
    elif platform == "shopify":
        return 10
    else:
        return 20

def score_catalog_fit(target: dict) -> float:
    #placeholder, catalog fit requires manual or LLM assessment.
    #Defaults to 50 until Claude enrichment adds this signal
    return 50.0

def score_target(target: dict) -> dict:
    # runs all scoring functions and returns composite score
    
    scores = {
        "traffic_and_seo": score_traffic_and_seo(target),
        "operational_gaps": score_operational_gaps(target),
        "owner_fatigue": score_owner_fatigue(target),
        "platform_signals": score_platform_signals(target),
        "catalog_fit": score_catalog_fit(target)
    }
    
    composite = sum(
        scores[k] * WEIGHTS[k]
        for k in scores
    )
    
    target["score_traffic_and_seo"] = round(scores["traffic_and_seo"], 1)
    target["score_operational_gaps"] = round(scores["operational_gaps"], 1)
    target["score_owner_fatigue"] = round(scores["owner_fatigue"], 1)
    target["score_platform_signals"] = round(scores["platform_signals"], 1)
    target["score_catalog_fit"] = round(scores["catalog_fit"], 1)
    target["composite_score"] = round(composite, 1)
    
    return target

def score_all(targets: list[dict]) -> list[dict]:
    # scores all targets and returns sorted by composite sort descending
    
    scored = [score_target(t) for t in targets]
    scored.sort(key = lambda x: x["composite_score"], reverse = True)
    return scored

if __name__ == "__main__":
    test_targets = [
        {
            "domain": "lessemf.com",
            "platform": "woocommerce",
            "has_klaviyo": False,
            "has_review_app": False,
            "has_abandoned_cart": False,
            "has_live_chat": False,
            "is_archaic": True,
            "indexed_pages": 751,
            "organic_results": 10,
            "has_paid_ads": False,
            "domain_age": 29.7
        },
        {
            "domain": "boncharge.com",
            "platform": "shopify",
            "has_klaviyo": True,
            "has_review_app": True,
            "has_abandoned_cart": True,
            "has_live_chat": False,
            "is_archaic": False,
            "indexed_pages": 1860,
            "organic_results": 10,
            "has_paid_ads": False,
            "domain_age": 4.6
        },
        {
            "domain": "calmigo.com",
            "platform": "magento",
            "has_klaviyo": True,
            "has_review_app": False,
            "has_abandoned_cart": True,
            "has_live_chat": True,
            "is_archaic": True,
            "indexed_pages": 309,
            "organic_results": 10,
            "has_paid_ads": False,
            "domain_age": 7.8
        }
    ]
    
    results = score_all(test_targets)
    for r in results:
        print(f"\n{r['domain']}")
        print(f" Composite Score: {r['composite_score']}")
        print(f" Traffic and SEO: {r['score_traffic_and_seo']}")
        print(f" Operational Gaps: {r['score_operational_gaps']}")
        print(f" Owner Fatigue: {r['score_owner_fatigue']}")
        print(f" Platform Signals: {r['score_platform_signals']}")
        print(f" Catalog Fit: {r['score_catalog_fit']}")
        
        