import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    dotenv_path = Path(__file__).parent/  ".env"
    load_dotenv(dotenv_path = dotenv_path)
except Exception:
    pass

try:
    import streamlit as st
    ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    SERP_API_KEY = st.secrets.get("SERP_API_KEY") or os.getenv("SERP_API_KEY")
    SEMRUSH_API_KEY = st.secrets.get("SEMRUSH_API_KEY") or os.getenv("SEMRUSH_API_KEY")
except Exception:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    SERP_API_KEY = os.getenv("SERP_API_KEY")
    SEMRUSH_API_KEY = os.getenv("SEMRUSH_API_KEY")

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1000

PLATFORM_GATE_MODE = "soft" #or "strict"

ARCHAIC_PLATFORMS = {"woocommerce", "magento", "wordpress", "unknown"}

TRAFFIC_SOURCE = "serpapi" # or "semrush"
WEIGHTS = {
    "traffic_and_seo" : 0.30,
    "catalog_fit":      0.25,
    "owner_fatigue":    0.20,
    "operational_gaps": 0.15,
    "platform_signals": 0.10
}

MIN_MONTHLY_TRAFFIC = 5000
MAX_MONTHLY_TRAFFIC = 500000

DOMAIN_AGE_FATIGUE = 8
REVIEW_STALE_MONTHS = 6
PAID_TRAFFIC_WARNING = 0.40
ORGANIC_DECAY_HIGH = -0.05
ORGANIC_DEAY_VERY_HIGH = -0.20

CATALOG_FIT_SIMILAR = "similar"
CATALOG_FIT_ADJACENT = "adjacent"
CATALOG_FIT_COMPLEMENTARY = "complementary"

SEED_KEYWORDS = [
    "neuropathy relief device",
    "PEMF therapy device",
    "red light therapy device",
    "EMF protection products",
    "biofeedback device",
    "sound therapy device",
    "grounding products wellness",
    "air purification wellness",
    "alternative health devices",
    "hoilistic wellness devices"
]

DATA_PATH = Path(__file__).parent / "data" / "targets.csv"
OUTPUT_PATH = Path(__file__).parent / "data" / "ranked_targets.csv"