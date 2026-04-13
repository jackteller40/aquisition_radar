import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import anthropic
from config import ANTHROPIC_API_KEY, MODEL, MAX_TOKENS

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SCENARIO_PROMPT = """
You are a private equity analysts evaluating e-commerce acquisition targets.
Given the following data about a target business, generate three acquisition scenarios

Target Data:
{target_data}

Generate exactly three scenarios in this format with no preamble:

BASE CASE:
[2-3 sentences describing conservative post-acquisition outcome]

UPSIDE CASE:
[2-3 sentences describing realistic outperformance if key value creation levers execute well]

DOWNSIDE CASE:
[2-3 sentences describing risk scenario and what happens if execution falters]

ACQUISITION THESIS:
[1-2 sentances summarizing why this is an interesting target]

Keep each scenario consise, specific to the data provided, and grounded in realistic PE assumptions.
"""

def generate_scenarios(target: dict) -> dict:
    '''generates base/upside/downside case scenarios for a target using claude API'''
    
    target_summary = f"""
Domain: {target.get('domain')}
Platform: {target.get('platform')}
Domain Age: {target.get('domain_age')} years
Composite Score: {target.get('composite_score')}
Indexed Pages: {target.get('indexed_pages')}
Organic Results: {target.get('organic_results')}
Has Klaviyo: {target.get('has_klaviyo')}
Has Review App: {target.get('has_review_app')}
Has Abandoned Cart: {target.get('has_abandoned_cart')}
Has Live Chat: {target.get('has_live_chat')}
Is Archaic Platform: {target.get('is_archaic')}
Traffic Score: {target.get('score_traffic_and_seo')}
Operational Gaps Score: {target.get('score_owner_fatigue')}
Platform Score: {target.get('score_platform_signals')}'
    """
    
    try:
        response = client.messages.create(
            model = MODEL,
            max_tokens = MAX_TOKENS,
            messages = [
                {
                    "role": "user",
                    "content": SCENARIO_PROMPT.format(target_data = target_summary)
                }
            ]
        )
        
        raw = response.content[0].text.strip()
        print("\nRAW RESPONSE:\n", raw)  
        
        sections = {
            "base_case": _extract_section(raw, "BASE CASE:"),
            "upside_case": _extract_section(raw, "UPSIDE CASE:"),
            "downside_case": _extract_section(raw, "DOWNSIDE CASE:"),
            "acquisition_thesis": _extract_section(raw, "ACQUISITION THESIS")
        }
        
        target.update(sections)
        return target
    
    except Exception as e:
        print(f"Scenario generation failed for {target.get('domain')}: {e}")
        target.update({
            "base_case": None,
            "upside_case": None,
            "downside_case": None,
            "acquisition_thesis": None
        })
        return target
    
def _extract_section(text: str, header: str) -> str:
    '''extracts text between each header'''
    
    headers = ["BASE CASE:", "UPSIDE CASE:", "DOWNSIDE CASE:", "ACQUISITION THESIS:"]
    
    if header not in text:
        return None
    
    start = text.index(header) + len(header)
    
    next_starts = [
        text.index(h) for h in headers
        if h in text and text.index(h) > start
    ]
    
    end = min(next_starts) if next_starts else len(text)
    return text[start:end].strip().lstrip(":")

def generate_all_scenarios(targets: list[dict]) -> list[dict]:
    '''generates scenarios for all targets'''
    results = []
    for i, target in enumerate(targets):
        domain = target.get("domain")
        print(f"Generating scenarios ({i+1}/{len(targets)}): {domain}")
        result = generate_scenarios(target)
        results.append(result)
    return results

if __name__ == "__main__":
    test_target = {
        "domain": "lessemf.com",
        "platform": "woocommerce",
        "domain_age": 29.7,
        "composite_score": 66.6,
        "indexed_pages": 751,
        "organic_results": 10,
        "has_klaviyo": False,
        "has_review_app": False,
        "has_abandoned_cart": False,
        "has_live_chat": False,
        "is_archaic": True,
        "score_traffic_and_seo": 30.0,
        "score_operational_gaps": 100.0,
        "score_owner_fatigue": 100.0,
        "score_platform_signals": 100.0
    }
    
    result = generate_scenarios(test_target)
    print("\nRAW KEYS:", result.keys())
    print("\nBASE CASE:", result.get("base_case"))
    print("\UPSIDE CASE:", result.get("upside_case"))
    print("\nDOWNSIDE CASE:", result.get("downside_case"))
    print("\nACQUISITION THESIS:", result.get("acquisition_thesis"))