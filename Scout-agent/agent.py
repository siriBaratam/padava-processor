import os, json, re, time, requests
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

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

    url = "https://newsapi.org/v2/everything"
    params = {
        "q":        keywords,
        "sortBy":   "publishedAt",
        "language": "en",
        "pageSize": max_articles,
    }
    headers = {"X-Api-Key": NEWS_API_KEY}

    for attempt in range(2):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
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
                })
            print(f"  Fetched {len(articles)} articles from NewsAPI")
            return articles

        except requests.exceptions.Timeout:
            if attempt == 0:
                print("  NewsAPI timed out, retrying...")
                continue
            print("  NewsAPI timed out after retry; skipping this cycle")
            return []
        except requests.exceptions.RequestException as e:
            print(f"  NewsAPI request error: {e}")
            return []

    return []
    
PROMPT_TEMPLATE = """
You are a risk analyst for India's oil supply chain.
Classify this news headline for its impact on India's crude oil imports.

BAD     = threatens supply, raises prices, blocks shipping routes
GOOD    = stabilises supply, new trade deals, routes reopening
NEUTRAL = unrelated to oil, energy, or shipping

Key areas to watch:
- Red Sea / Bab el-Mandeb
- Strait of Hormuz / Persian Gulf
- Russia oil sanctions
- OPEC+ production decisions
- India bilateral energy deals (UAE, Saudi, Russia)

Headline : {headline}
Summary  : {summary}

Reply ONLY in this exact JSON format, no extra text, no markdown:
{{
  "classification": "BAD" or "GOOD" or "NEUTRAL",
  "risk_score": 1-10,
  "area_affected": "region or topic",
  "who_is_involved": "countries or organisations",
  "reason": "one clear sentence",
  "action_needed": "monitor" or "alert team" or "escalate"
}}
"""

def classify(item):
    prompt = PROMPT_TEMPLATE.format(
        headline=item["headline"],
        summary=item["summary"],
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        raw = response.text.strip()

        # strip markdown code fences if Gemini adds them
        raw = re.sub(r"```json|```", "", raw).strip()

        data = json.loads(raw)

    except json.JSONDecodeError:
        # try to extract JSON block if there's surrounding text
        match = re.search(r'\{.*?\}', raw, re.DOTALL)
        data = json.loads(match.group()) if match else {
            "classification": "NEUTRAL",
            "risk_score": 1,
            "reason": "Could not parse response"
        }
    except Exception as e:
        print(f"  Gemini error: {e}")
        error_text = str(e)
        if "RESOURCE_EXHAUSTED" in error_text or "quota" in error_text.lower():
            short_reason = "Gemini quota exceeded; classification skipped"
        else:
            short_reason = f"Gemini request failed: {error_text[:120]}"
        data = {"classification": "NEUTRAL", "risk_score": 1, "reason": short_reason}

    # attach metadata
    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data["headline"]  = item["headline"]
    data["source"]    = item["source"]
    data["link"]      = item["link"]
    data.pop("reason", None)
    data.pop("agent", None)
    return data

def show(r):
    icon = {"BAD": "🚨", "GOOD": "✅", "NEUTRAL": "⚪"}.get(r.get("classification"), "❓")
    print(f"\n{icon}  {r.get('classification')}  [{r.get('risk_score','?')}/10]  —  {r.get('area_affected','')}")
    print(f"    Headline : {r.get('headline','')}")
    print(f"    Reason   : {r.get('reason','')}")
    print(f"    Action   : {r.get('action_needed','')}   |   Source: {r.get('source','')}")
    print(f"    {'─'*55}")


# ── 4. SAVE (handoff file for teammates) ──────
def save(r, seen_links=None):
    link = r.get("link", "")
    if seen_links is not None and link in seen_links:
        return False
    if seen_links is not None:
        seen_links.add(link)
    with open("scout_output.json", "a") as f:
        f.write(json.dumps(r) + "\n")
    return True


# ── 5. LOOP ───────────────────────────────────
def run(interval_minutes=1):
    """
    30 min interval keeps you well within NewsAPI's
    100 requests/day free limit (48 calls/day max)
    """
    print("🛰️  Scout Agent running — Gemini + NewsAPI\n")
    cycle = 0

    while True:
        cycle += 1
        print(f"\n{'━'*50}")
        print(f"  Cycle {cycle}  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'━'*50}")

        articles = fetch_news(max_articles=10)
        seen_links = set()

        bad_count = 0
        for item in articles:
            result = classify(item)
            show(result)
            saved = save(result, seen_links)
            if saved:
                print("  Saved new item")
            else:
                print("  Skipped duplicate item")
            if result.get("classification") == "BAD":
                bad_count += 1
            time.sleep(2)   # small pause — respect Gemini rate limit

        print(f"\n  Summary: {bad_count} bad signals / {len(articles)} articles this cycle")
        if bad_count >= 3:
            print("  ⚠️  HIGH ALERT — multiple bad signals detected")

        print(f"\n⏳ Next scan in {interval_minutes} min...")
        time.sleep(interval_minutes * 60)


if __name__ == "__main__":
    run()
