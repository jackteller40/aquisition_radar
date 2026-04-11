import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import requests
from config import SERP_API_KEY, SEMRUSH_API_KEY, TRAFFIC_SOURCE

def get_traffic_serpapi(domain: str) -> dict:
    '''uses serpAPI to estimate organic search presence by pulling google
    search results for the domain'''
    
    try:
        params = {
            "engine": "google",
            "q": f"site:{domain}",
            "api_key": SERP_API_KEY,
            "num": 10
        }
        
        response = requests.get(
            "https://serpapi.com/search",
            params = params,
            timeout = 10
        )
        response.raise_for_status()
        data = response.json()
        
        #google estimate of indexed pages
        total_results = data.get("search_information", {}).get("total_results", None)
        
        #proxy for domain authority
        organic_results = data.get("organic_results", [])
        organic_count = len(organic_results)
        
        ads = data.get("ads", [])
        has_paid_ads = len(ads) > 0
        
        return{
            "indexed_pages": total_results,
            "organic_results": organic_count,
            "has_paid_ads": has_paid_ads,
            "traffic_source": "serpapi"
        }
    
    except Exception as e:
        print(f"SerpAPI traffic failed for {domain}: {e}")
        return {
            "indexed_pages": None,
            "organic_results": None,
            "has_paid_ads": None,
            "traffic_source": "serpapi"
        }
        
def get_traffic_semrush(domain: str) -> dict:
    '''uses semrush api to pull traffic estimate and trend over time'''
    
    try:
        params = {
            "type": "domain_ranks",
            "key": SEMRUSH_API_KEY,
            "domain": domain,
            "database": "us",
            "export_columns": "or, Ot, Oc, Ad, At"
        }
        
        response = requests.get(
            "https://api.semrush.com/",
            params = params,
            timeout = 10
        )
        response.raise_for_status()
        
        lines = response.text.strip().split("\n")
        if len(lines) < 2:
            return {
                "organic_keywords": None,
                "organic_traffic": None,
                "paid_keywords": None,
                "paid_traffic": None,
                "traffic_source": "semrush"
            }
            
        headers = lines[0].split(";")
        values = lines[1].split(";")
        data = dict(zip(headers, values))
        
        return {
            "organic_kaywords": int(data.get("Organic Keywords", 0) or 0),
            "organic_traffic": int(data.get("Organic Traffic", 0) or 0),
            "paid_keywords": int(data.get("Adwords Keywords", 0) or 0),
            "paid_traffic": int(data.get("Adwords Traffic", 0) or 0),
            "traffic_source": "semrush"
        }
        
    except Exception as e:
        print(f"SEMrush traffic failed for {domain}: {e}")
        return {
            "organic_keywords": None,
            "organic_traffic": None,
            "paid_traffic": None,
            "traffic_source": "semrush"
        }
        
def enrich_traffic(domain: str) -> str:
    result = {"domain": domain}
    
    if TRAFFIC_SOURCE == "semrush":
        result.update(get_traffic_semrush(domain))
    else:
        result.update(get_traffic_serpapi(domain))
    
    return result

if __name__ == '__main__':
    test = enrich_traffic("toolsforwellness.com")
    print(test)