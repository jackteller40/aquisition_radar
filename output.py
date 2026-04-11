import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import csv
import json
from config import OUTPUT_PATH

def save_ranked_csv(targets: list[dict]):
    '''saves ranked targets csv'''
    
    if not targets:
        print("No targets to save")
        return
    
    OUTPUT_PATH.parent.mkdir(exist_ok = True)
    
    flattened = []
    for t in targets:
        row = {}
        for k, v in t.items():
            if isinstance(v, list):
                row[k] = ", ".join(str(i) for i in v)
            else:
                row[k] = v
        flattened.append(row)
    
    keys = flattened[0].keys()
    with open(OUTPUT_PATH, "w", newline = "") as f:
        writer = csv.DictWriter(f, fieldnames = keys)
        writer.writeheader()
        writer.writerows(flattened)
        
    print(f"Saved ranked targets to {OUTPUT_PATH}")
    
def print_summary(targets: list[dict]):
    #prints clean summary of ranked targets to terminal
    
    print("\n" + "="*60)
    print("ACQUISITION RADER: RANKED TARGETS")
    print("="*60)
    
    for i, t in enumerate(targets):
        print(f"\n#{i+1} {t.get('domain').upper()}")
        print(f" Composite Score: {t.get('composite_score')}")
        print(f" Platform: {t.get('platform')} | Archaic: {t.get('is_archaic')}")
        print(f" Domain Age: {t.get('domain_age')} years")
        print(f" Indexed Pages: {t.get('indexed_pages')}")
        print(f" Klaviyo: {t.get('has_klaviyo')} | Review app: {t.get('has_review_app')}")
        print(f" Traffic Score: {t.get('score_traffic_and_seo')}")
        print(f" Ops Gap Score: {t.get('score_operational_gaps')}")
        print(f" Fatigure Score: {t.get('score_owner_fatigue')}")
        print(f" Platform Score: {t.get('score_platform_signals')}")
        
        if t.get('acquisition_thesis'):
            print(f"\n THESIS: {t.get('acquisition_thesis')}")
            
        if t.get('base_case'):
            print(f"\n BASE: {t.get('base_case')}")
            
        if t.get('optimal_case'):
            print(f"\n OPTIMAL: {t.get('optimal_case')}")
        
        if t.get('best_case'):
            print(f"\n BEST: {t.get('best_case')}")
            
        print("\n" + "-"*60)
        
if __name__ == '__main__':
    test = [{
        "domain": "lessemf.com",
        "platform": "woocommerce",
        "is_archaic": True,
        "domain_age": 29.7,
        "indexed_pages": 751,
        "has_klaviyo": False,
        "has_review_app": False,
        "has_abandoned_cart": False,
        "composite_sscore": 66.5,
        "score_traffic_and_ceo": 30.0,
        "score_operational_gaps": 100.0,
        "score_owner_fatigue": 100.0,
        "score_platform_signals": 100.0,
        "acquisition_thesis": "LessEMF.com is a compelling niche target.",
        "base_case": "Stabalize platform and implement retention tools.",
        "optimal_case": "Full Shopify migration with Klaviyo deployment.",
        "best_case": "Category leader with 2-3x revenue in 36 months."
    }]
    
    print_summary(test)
    save_ranked_csv(test)