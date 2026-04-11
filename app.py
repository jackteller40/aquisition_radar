import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import streamlit as st
import pandas as pd
from main import main

st.set_page_config(
    page_title = "Acquisition Radar",
    layout = "wide"
)

st.title("Acquisition Radar")
st.caption("Automated e-commerce acquisition target discovery and scoring")

with st.sidebar:
    st.header("Pipeline Settings")

    max_domains = st.slider(
        "Max Domains to analyze",
        min_value = 5,
        max_value = 30,
        value = 10,
        step = 5
    )
    
    gate_mode = st.radio(
        "Platform gate mode",
        options = ["soft", "strict"],
        index = 0,
        help = "Strict only passes archaic platofrms. Soft flags, but passes all."
    )
    
    st.divider()
    run_button = st.button("Run Pipeline", use_container_width = True)
    st.caption(f"Each run uses ≈{max_domains + 10} SerpAPI credits")
    
if run_button:
    import config
    config.PLATFORM_GATE_MODE = gate_mode

    status = st.empty()
    progress = st.progress(0)

    try:
        status.text("Step 1: Discovering targets...")
        from discovery.google_shopping import discover_targets
        from pipeline import is_legitimate_domain
        domains = discover_targets(max_per_keyword=5)
        domains = [d for d in domains if is_legitimate_domain(d)]
        domains = domains[:max_domains]
        progress.progress(15)
        status.text(f"Step 1 complete — {len(domains)} targets discovered")

        status.text("Step 2: Detecting platforms...")
        from enrichment.builtwith import enrich_builtwith
        import time
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
        status.text(f"Step 2 complete — {len(gated)} targets passed gate")
        
        status.text("Step 3: Analyzing traffic...")
        from enrichment.traffic import enrich_traffic
        enriched = []
        for result in gated:
            traffic = enrich_traffic(result["domain"])
            result.update(traffic)
            enriched.append(result)
            time.sleep(1)
        progress.progress(55)
        status.text(f"Step 3 complete — traffic data pulled")

        status.text("Step 4: Checking owner fatigue...")
        from enrichment.whois_lookup import enrich_whois
        final = []
        for result in enriched:
            whois_data = enrich_whois(result["domain"])
            result.update(whois_data)
            final.append(result)
            time.sleep(0.5)
        progress.progress(65)
        status.text(f"Step 4 complete — owner data pulled")

        status.text("Step 5: Scoring targets...")
        from scoring import score_all
        scored = score_all(final)
        progress.progress(75)
        status.text(f"Step 5 complete — targets scored")

        status.text("Step 6: Generating acquisition scenarios...")
        from scenarios import generate_all_scenarios
        results = generate_all_scenarios(scored)
        progress.progress(90)
        status.text(f"Step 6 complete — scenarios generated")

        from output import save_ranked_csv
        save_ranked_csv(results)
        progress.progress(100)
        status.text("Pipeline complete.")

        st.success(f"Pipeline complete — {len(results)} targets analyzed")

        st.subheader("Ranked Acquisition Targets")
        table_data = []
        for r in results:
            table_data.append({
                "Rank":           results.index(r) + 1,
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
        st.dataframe(df, use_container_width=True, hide_index=True)

        # --- TARGET CARDS ---
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
                    st.write(r.get("base_case", "N/A"))
                with col_b:
                    st.markdown("**Optimal Case**")
                    st.write(r.get("optimal_case", "N/A"))
                with col_c:
                    st.markdown("**Best Case**")
                    st.write(r.get("best_case", "N/A"))

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

        # --- DOWNLOAD ---
        st.divider()
        output_path = Path(__file__).parent / "data" / "ranked_targets.csv"
        if output_path.exists():
            with open(output_path, "r") as f:
                csv_data = f.read()
            st.download_button(
                label="📥 Download Ranked Targets CSV",
                data=csv_data,
                file_name="acquisition_radar_results.csv",
                mime="text/csv",
                use_container_width=True
            )

    except Exception as e:
        progress.progress(0)
        st.error(f"Pipeline failed: {e}")
        st.exception(e)
            
else:
    st.info("Configure your settings in the sidebar and click **Run Pipeline** to start.")
    st.markdown("""
    **How it Works:**
    1. SerpAPI discovers wellness e-commerce domains matching tfw criteria
    2. Platform detection identifies orachaic tech stacks
    3. Traffic analysis scores organic presence
    4. WhoIs lookup estimes owner fatigue
    5. Weighted scoring model ranks all the targets
    6. Claude generates base, optimal, and best case aquisition scenarios per target
    """)
                                
                                     
                                   