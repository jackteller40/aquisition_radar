import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from pipeline import run_pipeline
from scoring import score_all
from scenarios import generate_all_scenarios
from output import save_ranked_csv, print_summary

def main(max_domains: int = 10):
    """
    full aquisition pipeline
    1. discover/enrich radar pipeline
    2. score each target
    3. generate aquisition scenarios via claude
    4. output ranked list
    """
    
    print("\nStarting Aquisition Radar Pipeline")
    targets = run_pipeline(max_domains = max_domains)
    
    if not targets:
        print("No targets survived the pipeline. Exiting")
        return
    
    print("\n" + "="*60)
    print("STEP 5: SCORING TARGETS")
    print("="*60)
    scored = score_all(targets)
    print(f"Scored{len(scored)} targets")
    
    print("\n" + "="*60)
    print("STEP 6: GENERATING ACQUISITION SCENARIOS")
    print("="*60)
    final = generate_all_scenarios(scored)
    
    print_summary(final)
    save_ranked_csv(final)
    
    print("\nAcquisition Radar complete")
    return final   

if __name__ == '__main__':
    main(max_domains = 10)