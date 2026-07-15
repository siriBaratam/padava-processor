# scout.py — updated to use your own model
import os, json, time, requests, joblib
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from datetime import date

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")
NEWSAPI_KEY = os.getenv("NEWS_API_KEY")
STATE_FILE = BASE_DIR / "scout_output.json"

# ── load YOUR model (no Gemini needed) ────────
model_path = BASE_DIR / "scout_model.pkl"
model = joblib.load(model_path)
print(f"Your model loaded successfully from {model_path}")

# ── risk score map ────────────────────────────
# our classifier is an SVM, so we use decision scores instead of probabilities

def confidence_to_risk(label, score):
    if label == "BAD":
        return round(max(2.0, min(9.5, 5.0 + score * 1.5)), 1)
    elif label == "GOOD":
        return round(max(1.0, min(5.0, 3.0 - score * 0.8)), 1)
    else:
        return 2.0
def fetchTime():
    today = date.today()
    print(type(today.isoformat()))
    return today.isoformat()
    
# ── fetch (unchanged) ─────────────────────────
def fetch_news(max_articles=20):
    """
    NewsAPI free tier — keyword search on headlines
    Covers ships, sanctions, wars, oil, energy
    """
    keywords = (
        "oil tanker OR shipping lanes OR Strait of Hormuz "
        "OR Red Sea OR Houthi OR sanctions OR crude oil "
        "OR OPEC OR Persian Gulf OR energy supply"
    )
    try:
        resp = requests.get("https://newsapi.org/v2/everything", params={
            "q":        keywords,
            "sortBy":   "publishedAt",
            "language": "en",
            "pageSize": max_articles,
            "apiKey":   NEWSAPI_KEY,
        }, timeout=10)
        data = resp.json()
        if data.get("status") != "ok":
            print(f"  NewsAPI error: {data.get('message')}")
            return []
        articles = []
        for a in data.get("articles", []):
            articles.append({
                "headline": a.get("title", ""),
                "summary":  (a.get("description") or "")[:300],
                "source":   a.get("source", {}).get("name", "unknown"),
                "link":     a.get("url", ""),
                "published_at": a.get("publishedAt", ""),
            })
        print(f"  Fetched {len(articles)} articles")
        return articles
    except Exception as e:
        print(f"  Fetch error: {e}")
        return []

# ── classify with YOUR model ──────────────────
# ── corridor → Indian stations mapping ────────
# domain knowledge hardcoded — this is intentional
CORRIDOR_MAP = {
    "Red Sea":       {
        "corridors": ["Red Sea", "Bab el-Mandeb", "Suez Canal"],
        "stations":  ["Kochi Refinery", "Paradip Refinery", "Haldia Port"]
    },
    "Hormuz":        {
        "corridors": ["Strait of Hormuz", "Persian Gulf", "Gulf of Oman"],
        "stations":  ["Jamnagar Refinery", "Vadinar Port", "Mumbai JNPT"]
    },
    "Persian Gulf":  {
        "corridors": ["Persian Gulf", "Kuwait", "Saudi Arabia", "UAE"],
        "stations":  ["Jamnagar Refinery", "Mundra Port", "Vadinar Port"]
    },
    "Russia":        {
        "corridors": ["Baltic Sea", "Arctic Route", "Black Sea"],
        "stations":  ["Nayara Energy Vadinar", "HPCL Vizag"]
    },
    "OPEC":          {
        "corridors": ["Global supply"],
        "stations":  ["All major Indian refineries"]
    },
}

def detect_areas(headline: str, summary: str):
    """
    Scan headline + summary for known corridor keywords.
    Returns which areas and stations are at risk.
    """
    text = (headline + " " + summary).lower()

    areas_affected    = []
    stations_at_risk  = []
    corridors_at_risk = []

    keyword_map = {
        "Red Sea":      ["red sea", "bab el-mandeb", "bab-el-mandeb",
                         "aden", "houthi", "yemen"],
        "Hormuz":       ["hormuz", "strait of hormuz", "gulf of oman",
                         "iran", "persian gulf"],
        "Persian Gulf": ["persian gulf", "kuwait", "saudi", "uae",
                         "abu dhabi", "qatar", "opec"],
        "Russia":       ["russia", "russian", "urals", "baltic",
                         "black sea", "sanctions"],
        "OPEC":         ["opec", "opec+", "production cut",
                         "oil output", "crude supply"],
    }

    for area, keywords in keyword_map.items():
        if any(kw in text for kw in keywords):
            areas_affected.append(area)
            corridors_at_risk += CORRIDOR_MAP[area]["corridors"]
            stations_at_risk  += CORRIDOR_MAP[area]["stations"]

    # deduplicate
    return (
        areas_affected,
        list(set(corridors_at_risk)),
        list(set(stations_at_risk))
    )


def classify(item):
    text = item["headline"] + " " + item["summary"]

    # your trained model classifies
    label = model.predict([text])[0]

    # LinearSVC does not support predict_proba, so use decision scores
    try:
        score = float(model.decision_function([text])[0])
    except Exception:
        score = 0.0

    if label == "BAD":
        confidence = round(min(99.0, max(55.0, 50.0 + abs(score) * 10.0)), 1)
        risk_score = round(min(9.5, max(2.0, 5.0 + abs(score) * 1.5)), 1)
    elif label == "GOOD":
        confidence = round(min(99.0, max(55.0, 50.0 + abs(score) * 8.0)), 1)
        risk_score = round(min(5.0, max(1.0, 3.0 - abs(score) * 0.8)), 1)
    else:
        confidence = 60.0
        risk_score = 2.0

    # detect areas and stations
    areas, corridors, stations = detect_areas(
        item["headline"], item["summary"]
    )

    # ── this is the handoff output ─────────────
    return {
        "agent":             "scout",
        "timestamp":         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        # ✅ core signal — what every agent reads first
        "classification":    label,           # BAD / GOOD / NEUTRAL
        "signal":            label,           # BAD / GOOD / NEUTRAL
        "risk_score":        risk_score,      # 1-10

        # ✅ geography — what Accountant and Strategist need
        "areas_affected":    areas,           # ["Red Sea", "Hormuz"]
        "supply_corridors":  corridors,       # ["Bab el-Mandeb", ...]
        "stations_at_risk":  stations,        # ["Kochi Refinery", ...]

        # ✅ context — what Strategist needs
        "event_type":        detect_event_type(item["headline"]),
        "who_involved":      "",              # your teammates can enrich this
        "reason":            item["headline"],
        "confidence":        confidence,

        # ✅ source info
        "headline":          item["headline"],
        "source":            item["source"],
        "link":              item["link"],
    }


def detect_event_type(headline: str) -> str:
    """Classify what kind of event this is"""
    h = headline.lower()
    if any(w in h for w in ["attack", "missile", "fire", "strike", "bomb"]):
        return "military_attack"
    elif any(w in h for w in ["sanction", "ban", "restrict", "embargo"]):
        return "sanctions"
    elif any(w in h for w in ["close", "block", "suspend", "halt", "shut"]):
        return "route_closure"
    elif any(w in h for w in ["deal", "agree", "sign", "supply", "contract"]):
        return "trade_deal"
    elif any(w in h for w in ["cut", "reduce", "opec", "output", "production"]):
        return "supply_cut"
    else:
        return "general_news"

# ── print ─────────────────────────────────────
def show(r):
    icon = {"BAD": "🚨", "GOOD": "✅", "NEUTRAL": "⚪"}.get(r["classification"], "❓")
    print(f"\n{icon}  {r['classification']}  [{r['risk_score']}/10]  confidence: {r['confidence']}%")
    print(f"    Headline : {r['headline']}")
    print(f"    Source   : {r['source']}")
    print(f"    {'─'*55}")

# ── state handling ─────────────────────────────
def save_latest_results(results):
    payload = {"entries": results}
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

# ── loop ──────────────────────────────────────
def run(interval_minutes=1):
    print("🛰️  Scout Agent running — YOUR model, no Gemini\n")

    cycle = 0
    while True:
        cycle += 1
        print(f"\n{'━'*50}")
        print(f"  Cycle {cycle}  |  {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'━'*50}")

        articles = fetch_news()
        bad_count = 0
        results = []
        for item in articles:
            result = classify(item)
            show(result)
            results.append(result)
            if result["classification"] == "BAD":
                bad_count += 1

        save_latest_results(results)
        print(f"\n  Summary: {bad_count} bad signals / {len(articles)} articles / {len(results)} items stored for this cycle")
        if bad_count >= 3:
            print("  ⚠️  HIGH ALERT")

        print(f"\n⏳ Next scan in {interval_minutes} min...")
        time.sleep(interval_minutes * 60)

run(interval_minutes=1)