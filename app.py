import sys
import json
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import streamlit as st
import pandas as pd

DEMO_PATH = Path(__file__).parent / "demo" / "demo_targets.json"

st.set_page_config(
    page_title = "Acquisition Radar",
    layout = "wide"
)

st.title("Acquisition Radar")
st.caption("Automated e-commerce acquisition target discovery and scoring")


def _text(value) -> str:
    return value if value else "N/A"


def load_demo_results() -> list[dict]:
    """loads fictional enrichment data and sample scenarios, then scores them
    with the real scoring model so the ranking reflects current weights"""
    import config
    from scoring import score_all
    with open(DEMO_PATH) as f:
        targets = json.load(f)["targets"]
    for t in targets:
        t["is_archaic"] = t["platform"].lower() in config.ARCHAIC_PLATFORMS
    return score_all(targets)


def run_live_pipeline(max_domains: int, gate_mode: str) -> list[dict]:
    import config
    config.PLATFORM_GATE_MODE = gate_mode

    status = st.empty()
    progress = st.progress(0)

    status.text("Step 1: Discovering targets...")
    from discovery.google_shopping import discover_targets
    from pipeline import is_legitimate_domain, in_traffic_band
    domains = discover_targets(max_per_keyword=5)
    domains = [d for d in domains if is_legitimate_domain(d)]
    domains = domains[:max_domains]
    progress.progress(15)

    status.text(f"Step 2: Detecting platforms for {len(domains)} domains...")
    from enrichment.builtwith import enrich_builtwith
    platform_results = []
    for domain in domains:
        result = enrich_builtwith(domain)
        platform = result.get("platform", "unknown").lower()
        result["is_archaic"] = platform in config.ARCHAIC_PLATFORMS
        platform_results.append(result)
        time.sleep(1)

    if config.PLATFORM_GATE_MODE == "strict":
        gated = [r for r in platform_results if r["is_archaic"]]
    else:
        gated = platform_results
    progress.progress(35)

    status.text(f"Step 3: Analyzing traffic for {len(gated)} targets...")
    from enrichment.traffic import enrich_traffic
    enriched = []
    for result in gated:
        result.update(enrich_traffic(result["domain"]))
        enriched.append(result)
        time.sleep(1)
    enriched = [r for r in enriched if in_traffic_band(r)]
    progress.progress(55)

    status.text("Step 4: Checking owner fatigue...")
    from enrichment.whois_lookup import enrich_whois
    for result in enriched:
        result.update(enrich_whois(result["domain"]))
        time.sleep(0.5)
    progress.progress(65)

    status.text("Step 5: Scoring targets...")
    from scoring import score_all
    scored = score_all(enriched)
    progress.progress(75)

    status.text("Step 6: Generating acquisition scenarios with Claude...")
    from scenarios import generate_all_scenarios
    results = generate_all_scenarios(scored)
    progress.progress(90)

    from output import save_ranked_csv
    save_ranked_csv(results)
    progress.progress(100)
    status.text("Pipeline complete.")
    return results


def render_results(results: list[dict]):
    st.subheader("Ranked Acquisition Targets")
    table_data = []
    for i, r in enumerate(results):
        table_data.append({
            "Rank":           i + 1,
            "Domain":         r.get("domain"),
            "Score":          r.get("composite_score"),
            "Platform":       r.get("platform"),
            "Archaic":        r.get("is_archaic"),
            "Domain Age":     r.get("domain_age"),
            "Traffic Score":  r.get("score_traffic_and_seo"),
            "Ops Gap Score":  r.get("score_operational_gaps"),
            "Fatigue Score":  r.get("score_owner_fatigue"),
            "Platform Score": r.get("score_platform_signals"),
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, width="stretch", hide_index=True)

    st.subheader("Acquisition Briefs")
    for i, r in enumerate(results):
        with st.expander(f"#{i+1} {r.get('domain').upper()} — Score: {r.get('composite_score')}"):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Composite Score", r.get("composite_score"))
            col2.metric("Domain Age", f"{r.get('domain_age')} yrs")
            col3.metric("Platform", r.get("platform"))
            col4.metric("Indexed Pages", r.get("indexed_pages"))

            st.divider()

            if r.get("acquisition_thesis"):
                st.markdown("**Acquisition Thesis**")
                st.info(r.get("acquisition_thesis"))

            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown("**Base Case**")
                st.write(_text(r.get("base_case")))
            with col_b:
                st.markdown("**Upside Case**")
                st.write(_text(r.get("upside_case")))
            with col_c:
                st.markdown("**Downside Case**")
                st.write(_text(r.get("downside_case")))

            st.divider()
            st.markdown("**Signal Breakdown**")
            sig1, sig2 = st.columns(2)
            with sig1:
                st.write(f"Klaviyo: {r.get('has_klaviyo')}")
                st.write(f"Review App: {r.get('has_review_app')}")
                st.write(f"Abandoned Cart: {r.get('has_abandoned_cart')}")
                st.write(f"Live Chat: {r.get('has_live_chat')}")
            with sig2:
                st.write(f"Organic Results: {r.get('organic_results')}")
                st.write(f"Indexed Pages: {r.get('indexed_pages')}")
                st.write(f"Has Paid Ads: {r.get('has_paid_ads')}")
                st.write(f"Is Archaic: {r.get('is_archaic')}")

    st.divider()
    st.download_button(
        label="📥 Download Ranked Targets CSV",
        data=df.to_csv(index=False),
        file_name="acquisition_radar_results.csv",
        mime="text/csv",
        width="stretch",
    )


with st.sidebar:
    st.header("Pipeline Settings")

    demo_mode = st.toggle(
        "Demo mode",
        value = True,
        help = "Loads fictional sample targets instantly and scores them with the "
               "live scoring model. Uses no API credits."
    )

    max_domains = st.slider(
        "Max Domains to analyze",
        min_value = 5,
        max_value = 30,
        value = 10,
        step = 5,
        disabled = demo_mode
    )

    gate_mode = st.radio(
        "Platform gate mode",
        options = ["soft", "strict"],
        index = 0,
        help = "Strict only passes archaic platforms. Soft flags, but passes all.",
        disabled = demo_mode
    )

    st.divider()
    run_button = st.button("Run Pipeline", width = "stretch")
    if demo_mode:
        st.caption("Demo mode: no API credits used")
    else:
        st.caption(f"Each run uses ≈{max_domains + 10} SerpAPI credits")

if run_button:
    try:
        if demo_mode:
            results = load_demo_results()
            st.warning("Demo data: these companies and their enrichment values are "
                       "fictional. Scores are computed by the live scoring model.")
        else:
            results = run_live_pipeline(max_domains, gate_mode)

        if not results:
            st.warning("No targets survived the pipeline.")
        else:
            st.success(f"Pipeline complete — {len(results)} targets analyzed")
            render_results(results)

    except Exception as e:
        st.error(f"Pipeline failed: {e}")
        st.exception(e)

else:
    st.info("Configure your settings in the sidebar and click **Run Pipeline** to start.")
    st.markdown("""
    **How it Works:**
    1. SerpAPI discovers wellness e-commerce domains matching the seed keywords
    2. Platform detection identifies archaic tech stacks
    3. Traffic analysis scores organic presence
    4. WHOIS lookup estimates owner fatigue
    5. Weighted scoring model ranks all the targets
    6. Claude generates base, upside, and downside case acquisition scenarios per target
    """)
