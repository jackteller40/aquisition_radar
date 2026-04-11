import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import whois
from datetime import datetime

def get_domain_age(domain: str) -> float | None:
    ''' returns domain age in years / none if lookup fails'''
    
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        
        if isinstance(creation_date, list):
            creation_date = min(creation_date)
            
        if creation_date is None:
            return None
        
        if hasattr(creation_date, 'tzinfo') and creation_date.tzinfo is not None:
            creation_date = creation_date.replace(tzinfo = None)
        
        age = (datetime.now() - creation_date).days / 365
        return round(age, 1)
    
    except Exception as e:
        print(f"WhoIs failed for {domain}: {e}")
        return None
    
def get_registrant_email(domain: str) -> str | None:
    '''returns registrant email if available'''
    try:
        w = whois.whois(domain)
        return w.emails if hasattr(w, "emails") else None
    except Exception:
        return None

def enrich_whois(domain: str) -> dict:
    devnull = open(os.devnull, 'w')
    old_stderr = sys.stderr
    sys.stderr = devnull

    result = {
        "domain":        domain,
        "domain_age":    get_domain_age(domain),
        "contact_email": get_registrant_email(domain)
    }

    sys.stderr = old_stderr
    devnull.close()
    return result

if __name__ == "__main__":
    test = enrich_whois("toolsforwellness.com")
    print(test)
    