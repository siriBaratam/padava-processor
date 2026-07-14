# create_training_data.py
# Run this ONCE to build your labeled dataset
# After this you never need Gemini again

import requests, json, time, os
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    genai = None

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWSAPI_KEY = os.getenv("NEWS_API_KEY")
USE_SAMPLE_DATA = os.getenv("USE_SAMPLE_DATA", "true").lower() in {"1", "true", "yes", "on"}

if genai and GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini = genai.GenerativeModel(GEMINI_MODEL)
else:
    gemini = None

SAMPLE_ARTICLES = [
    {"headline": "Oil tanker traffic resumes through Red Sea corridor after ceasefire", "summary": "Shipping lanes reopen and prices ease after a temporary truce."},
    {"headline": "Houthi attacks disrupt crude shipments through Bab el-Mandeb", "summary": "Operators warn of higher freight costs and supply delays."},
    {"headline": "India signs new energy deal with UAE to expand oil imports", "summary": "The agreement strengthens supply security for Indian refiners."},
    {"headline": "OPEC+ extends output cuts to support global crude prices", "summary": "Markets react as producers maintain tighter supply."},
    {"headline": "Local football tournament draws record crowds in Mumbai", "summary": "Sports event unrelated to energy or shipping."},
]

# ── fetch a large batch of headlines ──────────
def fetch_headlines(pages=5):
    if USE_SAMPLE_DATA or not NEWSAPI_KEY:
        print("Using built-in sample headlines for test data")
        return SAMPLE_ARTICLES.copy()

    keywords = (
        "oil tanker OR shipping lanes OR Strait of Hormuz "
        "OR Red Sea OR Houthi OR sanctions OR crude oil "
        "OR OPEC OR Persian Gulf OR energy supply"
    )
    all_articles = []
    for page in range(1, pages + 1):
        try:
            resp = requests.get("https://newsapi.org/v2/everything", params={
                "q":        keywords,
                "sortBy":   "publishedAt",
                "language": "en",
                "pageSize": 20,
                "page":     page,
                "apiKey":   NEWSAPI_KEY,
            }, timeout=10)
            data = resp.json()
            if data.get("status") == "ok":
                for a in data.get("articles", []):
                    all_articles.append({
                        "headline": a.get("title", ""),
                        "summary":  (a.get("description") or "")[:200],
                    })
            time.sleep(1)
        except Exception as e:
            print(f"  NewsAPI error: {e}")
            break
    if all_articles:
        print(f"Fetched {len(all_articles)} headlines total")
        return all_articles

    print("NewsAPI returned no usable articles; using built-in sample headlines")
    return SAMPLE_ARTICLES.copy()


def heuristic_label(item):
    text = f"{item['headline']} {item['summary']}".lower()
    if any(word in text for word in ["attack", "disrupt", "block", "sanction", "war", "conflict", "closure", "risk", "houthi", "tanker", "crude", "supply", "price"]):
        return "BAD"
    if any(word in text for word in ["reopen", "deal", "agreement", "stabil", "ease", "resume", "support", "increase"]):
        return "GOOD"
    return "NEUTRAL"

# ── label each headline using Gemini or a fallback ──────────
def label(item):
    if not gemini:
        return heuristic_label(item)

    prompt = f"""
You are a risk analyst for India's oil supply chain.
Classify this headline.

BAD     = threatens supply, blocks routes, raises prices
GOOD    = stabilises supply, new deals, routes reopening
NEUTRAL = unrelated to oil, energy, or shipping

Headline: {item['headline']}
Summary : {item['summary']}

Reply ONLY with one word: BAD or GOOD or NEUTRAL
"""
    try:
        resp = gemini.generate_content(prompt)
        label = resp.text.strip().upper()
        if label not in ["BAD", "GOOD", "NEUTRAL"]:
            label = "NEUTRAL"
        return label
    except Exception as e:
        print(f"  Gemini error: {e}")
        return heuristic_label(item)

# ── run labeling ──────────────────────────────
articles = fetch_headlines(pages=5)   # gets ~100 headlines

labeled = []
for i, item in enumerate(articles):
    if not item["headline"].strip():
        continue
    tag = label(item)
    labeled.append({
        "text":  item["headline"] + " " + item["summary"],
        "label": tag
    })
    print(f"  [{i+1}/{len(articles)}] {tag}  —  {item['headline'][:60]}")
    time.sleep(1.5)   # respect Gemini rate limit

# ── save to file ──────────────────────────────
import pandas as pd
df = pd.DataFrame(labeled)
df.to_csv("Scout-agent/training_data.csv", index=False)
print(f"\nSaved {len(df)} labeled examples to training_data.csv")
print(df["label"].value_counts())  