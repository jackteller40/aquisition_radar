# Acquisition Radar

An automated deal sourcing pipeline that finds, filters, and ranks small e-commerce businesses as acquisition targets, then uses Claude to generate an investment thesis for each one.

Press run, get a ranked list of targets with a composite score, a signal-by-signal breakdown, and three acquisition scenarios per company.

**Live demo:** [add Streamlit URL]

---

## Why This Exists

Small online brands often stall for predictable reasons. The founder has run the store for a decade, the site still runs on WooCommerce or Magento, organic traffic has been sliding for years, and paid ads are covering the gap. To an owner, that looks like a tired business. To a buyer with modern operations, it looks like an underpriced asset with obvious fixes.

Finding these companies manually means hours of searching, checking tech stacks, and estimating traffic one domain at a time. Acquisition Radar automates that sourcing workflow. It looks for **operational decay that a buyer can reverse**: aging platforms, declining organic reach, and signs of owner fatigue in a niche that fits an existing catalog.

The current configuration targets the alternative health and wellness device space (PEMF, red light therapy, biofeedback, grounding, and similar categories). Changing the seed keywords in `config.py` points the pipeline at a different vertical.

---

## How It Works

```
Seed keywords
     │
     ▼
1. Discovery ─────────── SerpAPI search returns competing store domains
     │
     ▼
2. Platform Detection ── Scrapes each site to identify its e-commerce platform and tech stack
     │
     ▼
3. Platform Gate ─────── Filters or flags archaic platforms (WooCommerce, Magento, WordPress)
     │
     ▼
4. Traffic Analysis ──── Organic search visibility, indexed pages, paid ad detection
     │
     ▼
5. Owner Fatigue ─────── WHOIS domain age as a proxy for seller motivation
     │
     ▼
6. Decline Scoring ───── Weighted model produces a composite score per target
     │
     ▼
7. Scenario Generation ─ Claude writes base, optimal, and best case scenarios
     │
     ▼
8. Ranked Output ─────── CSV + terminal summary + Streamlit dashboard
```

### 1. Discovery
Each seed keyword is run through SerpAPI. The domains that come back are candidate competitors in the target niche. Major retailers and marketplaces (Amazon, Walmart, Target, CVS, and so on) are removed by a domain blacklist so only independent brands move forward.

### 2. Platform Detection
Each candidate site is fetched and inspected for platform fingerprints to identify what it runs on. Sites that consistently time out are dropped.

### 3. Platform Gate
Configurable through `PLATFORM_GATE_MODE`:
- **`strict`** passes only archaic platforms (WooCommerce, Magento, WordPress, or undetectable) to the next stage. Use this to save API credits and focus on the strongest targets.
- **`soft`** flags archaic platforms but lets everything through. Use this for a wider view of the market.

### 4. Traffic Analysis
Configurable through `TRAFFIC_SOURCE`:
- **`serpapi`** (default) estimates organic visibility from search results, indexed page counts, and paid ad presence.
- **`semrush`** pulls traffic data from the SEMrush API for more accurate trend data.

Targets outside the traffic band in `config.py` (default 5,000 to 500,000 monthly visits) are excluded, which removes both hobby sites and businesses too large to be realistic targets.

### 5. Owner Fatigue
A WHOIS lookup returns the domain registration date. Domains older than the fatigue threshold (default 8 years) score higher on the theory that long-tenured owners are more likely to be open to a sale.

### 6. Decline Scoring
Each target is scored across five signals and combined into a weighted composite (see [Scoring Model](#scoring-model)).

### 7. Scenario Generation
For each scored target, the pipeline sends Claude the company's enrichment data and signal breakdown: platform, traffic profile, paid vs. organic mix, domain age, and catalog fit. Claude returns three acquisition scenarios:

| Scenario | What it describes |
|---|---|
| **Base case** | Acquire and stabilize. Modest gains from basic operational cleanup. |
| **Optimal case** | Replatform, fix SEO, and rebalance the paid/organic mix. Realistic upside with focused execution. |
| **Best case** | Full integration into an existing catalog with cross-selling and shared fulfillment. |

Each scenario names the specific levers that drive it, so the output reads as an investment thesis rather than a generic summary.

### 8. Ranked Output
Targets are sorted by composite score and written to `data/ranked_targets.csv`, printed as a terminal summary, and displayed in the Streamlit dashboard.

---

## Scoring Model

| Signal | Weight | What it measures |
|---|---|---|
| Traffic & SEO decay | 30% | Declining organic visibility, heavy reliance on paid traffic |
| Catalog fit | 25% | How well the product line fits an acquirer's catalog (similar, adjacent, or complementary) |
| Owner fatigue | 20% | Domain age as a proxy for founder tenure |
| Operational gaps | 15% | Missing or outdated site infrastructure a buyer could fix |
| Platform signals | 10% | Running on an archaic e-commerce platform |

Weights live in `config.py` and must sum to 1.0.

**Signal thresholds (defaults):**

| Threshold | Value | Meaning |
|---|---|---|
| `DOMAIN_AGE_FATIGUE` | 8 years | Fatigue likely beyond this age |
| `REVIEW_STALE_MONTHS` | 6 months | No new reviews signals decay |
| `PAID_TRAFFIC_WARNING` | 40% | Paid share above this is a warning sign |
| `ORGANIC_DECAY_HIGH` | -5% | High decay signal |
| `ORGANIC_DECAY_VERY_HIGH` | -20% | Very high decay signal |

---

## Project Structure

```
aquisition_radar/
├── main.py                  # entry point, runs the full pipeline
├── config.py                # API keys, weights, thresholds, seed keywords
├── pipeline.py              # orchestrates discovery, platform gate, traffic, fatigue
├── scoring.py               # weighted scoring model
├── scenarios.py             # Claude API scenario generation
├── output.py                # CSV export and terminal summary
├── app.py                   # Streamlit dashboard
├── discovery/
│   └── google_shopping.py   # SerpAPI domain discovery
├── enrichment/
│   ├── builtwith.py         # platform and tech stack detection
│   ├── whois_lookup.py      # domain age lookup
│   └── traffic.py           # traffic analysis (SerpAPI or SEMrush)
└── data/
    ├── targets.csv          # raw pipeline output
    └── ranked_targets.csv   # final scored and ranked output
```

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/jackteller40/aquisition_radar.git
cd aquisition_radar
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API keys**

Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your-key
SERP_API_KEY=your-key
SEMRUSH_API_KEY=your-key
```
No spaces around `=` and no quotes. `SEMRUSH_API_KEY` can be a placeholder if `TRAFFIC_SOURCE` is set to `serpapi`.

**5. Run**
```bash
# Full pipeline in the terminal
python main.py

# Streamlit dashboard
streamlit run app.py
```

---

## Configuration

All settings live in `config.py`.

| Setting | Default | Description |
|---|---|---|
| `MODEL` | `claude-sonnet-4-6` | Claude model used for scenario generation |
| `PLATFORM_GATE_MODE` | `strict` | `strict` passes archaic platforms only; `soft` flags them and passes everything |
| `ARCHAIC_PLATFORMS` | WooCommerce, Magento, WordPress, unknown | Platforms treated as archaic |
| `TRAFFIC_SOURCE` | `serpapi` | `serpapi` (cheaper) or `semrush` (more accurate) |
| `MIN_MONTHLY_TRAFFIC` | 5,000 | Lower bound of the target universe |
| `MAX_MONTHLY_TRAFFIC` | 500,000 | Upper bound of the target universe |
| `SEED_KEYWORDS` | 10 wellness device terms | Search terms used for discovery |
| `WEIGHTS` | see Scoring Model | Signal weights, must sum to 1.0 |

---

## API Usage

A full run with the default 10 seed keywords and 10 domains uses about **20 SerpAPI credits**:
- 10 for discovery (1 per seed keyword)
- 10 for traffic analysis (1 per domain)

SerpAPI's free tier includes 100 searches, enough for several full runs. Claude is called once per scored target for scenario generation.

---

## Limitations

This is a sourcing tool, not a valuation tool. Its output is a shortlist for human diligence.

- **Traffic is estimated.** In `serpapi` mode, traffic comes from search visibility proxies rather than measured visits. SEMrush mode is more accurate but requires a paid key.
- **Domain age is not owner age.** WHOIS registration date is a rough stand-in for founder tenure. A domain can change hands without the date changing.
- **Platform detection is fingerprint-based.** Heavily customized or headless sites may be misclassified or labeled unknown.
- **Discovery can surface large brands.** The blacklist catches the common ones, but new large retailers occasionally slip through and need to be added.
- **Scenarios are generated, not modeled.** Claude's scenarios are grounded in the target's signals but are not financial projections.

## Next Steps

- Pull multi-year organic traffic trends to measure decay directly instead of from a snapshot
- Add review recency as a live signal (the threshold already exists in config)
- Score catalog fit automatically against a defined acquirer product list
- Add revenue estimation to bring rough valuation ranges into the scenarios
- Cache enrichment results to avoid re-spending API credits on known domains

---

## Built With

Python · Anthropic Claude API · SerpAPI · SEMrush API · python-whois · Streamlit · pandas
