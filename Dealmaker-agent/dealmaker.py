import os, json, re, argparse, requests, sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from groq import Groq
from config import settings

client = Groq(api_key=settings.groq_api_key)

DEALMAKER_PROMPT = """\
You are a senior global energy trade negotiator. You source alternative crude oil and LPG supply deals for India when an existing supply source becomes unreliable due to war, sanctions, or geopolitical disruption. You know real-world export capacities, typical commodity pricing, and which supplier relationships are politically and logistically dependable versus risky.

## Context

Current date: {today}

{news_context}

## Input

- Resource in shortage: **{resource}**
- Shortage amount India needs to replace: **{shortage_amount}**

## Your Task

Follow these steps IN ORDER:

### Step 1 — Research
Search your knowledge for current global export prices and spare export capacity for {resource}. Consider all major exporting countries.

### Step 2 — Cross-check
If your knowledge of any candidate is thin, use your broader understanding of the region and historical trade flows — never leave a country's numbers blank.

### Step 3 — Shortlist
Select 3–6 candidate supplier countries that are realistically capable of covering the shortage.

### Step 4 — Evaluate each candidate
For each candidate determine:
- **price_per_unit_usd**: price per unit (with unit specified — barrel, metric ton, MMBtu)
- **unit**: the unit of measurement (e.g. "barrel", "metric ton", "MMBtu")
- **available_capacity**: rough available export capacity (e.g. "500,000 barrels/day")
- **reliability_score**: 1–10 based on political stability and current relations with India
- **existing_trade_relation**: whether India already buys from them
- **notes**: any caveats (sanctions exposure, contract lead time, political tension, logistical challenges)

### Step 5 — Recommend
Select exactly ONE recommended country. Base the choice on the full picture — price, capacity, reliability, and speed of deal-closing — not price alone. Justify in one to two sentences.

## Output Format

Reply ONLY with a valid JSON object. No preamble, no markdown fences, no commentary.

{{
  "resource": "{resource}",
  "shortage_amount": "{shortage_amount}",
  "options": [
    {{
      "country": "string",
      "resource": "{resource}",
      "price_per_unit_usd": number,
      "unit": "string",
      "available_capacity": "string",
      "reliability_score": integer,
      "existing_trade_relation": true or false,
      "notes": "string"
    }}
  ],
  "recommended_country": "string",
  "recommendation_reason": "string"
}}

## Constraints
- options must contain 3–6 entries.
- recommended_country must be one of the countries in options.
- Do not invent implausible prices — ground every figure in well-known market data or clearly label it as an estimate.
- Output ONLY the JSON object.
"""


RESOURCE_KEYWORDS = {
    "crude_oil": "crude oil export price supply India",
    "lpg": "LPG export price supply India",
}


def fetch_relevant_news(resource, max_articles=8):
    """Fetch recent news relevant to the resource shortage."""
    q = RESOURCE_KEYWORDS.get(resource, f"{resource} export supply India shortage")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_articles,
    }
    headers = {"X-Api-Key": settings.news_api_key}

    if not settings.news_api_key:
        return []

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "ok":
            print(f"  NewsAPI error: {data.get('message')}")
            return []
        articles = []
        for a in data.get("articles", []):
            articles.append(
                {
                    "headline": a.get("title", ""),
                    "summary": (a.get("description") or "")[:300],
                    "source": a.get("source", {}).get("name", "unknown"),
                    "link": a.get("url", ""),
                }
            )
        print(f"  Fetched {len(articles)} news articles about {resource}")
        return articles
    except requests.exceptions.RequestException as e:
        print(f"  NewsAPI request error: {e}")
        return []


def build_news_context(articles):
    """Turn news articles into a short context block for the prompt."""
    if not articles:
        return ""
    lines = ["## Recent News Context"]
    for a in articles[:5]:
        summary = a.get("summary", "").strip()
        if summary:
            lines.append(f"- {a['headline']}: {summary} ({a['source']})")
        else:
            lines.append(f"- {a['headline']} ({a['source']})")
    return "\n".join(lines)


def run_deal(resource, shortage_amount):
    """Run the dealmaker analysis once."""
    print(f"\n{'='*60}")
    print(f"  DEALMAKER AGENT")
    print(f"  Resource: {resource}")
    print(f"  Shortage: {shortage_amount}")
    print(f"{'='*60}\n")

    # 1. Fetch news context
    articles = fetch_relevant_news(resource)
    news_context = build_news_context(articles)

    today = datetime.now().strftime("%B %d, %Y")

    # 2. Build the prompt
    prompt = DEALMAKER_PROMPT.format(
        today=today,
        news_context=news_context,
        resource=resource,
        shortage_amount=shortage_amount,
    )

    # 3. Call Groq
    print("  Calling Groq (llama-3.1-8b-instant)...")
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
        )
        raw = completion.choices[0].message.content.strip()
    except Exception as e:
        error_text = str(e)
        print(f"  Groq error: {error_text[:200]}")
        fallback = {
            "resource": resource,
            "shortage_amount": shortage_amount,
            "options": [],
            "recommended_country": "",
            "recommendation_reason": f"Groq API error: {error_text[:120]}",
            "error": True,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        save_result(fallback)
        return fallback

    # 4. Strip markdown fences if present
    raw = re.sub(r"```json|```", "", raw).strip()

    # 5. Parse JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
            except json.JSONDecodeError:
                data = {
                    "resource": resource,
                    "shortage_amount": shortage_amount,
                    "options": [],
                    "recommended_country": "",
                    "recommendation_reason": "Could not parse Groq response as JSON",
                    "error": True,
                }
        else:
            data = {
                "resource": resource,
                "shortage_amount": shortage_amount,
                "options": [],
                "recommended_country": "",
                "recommendation_reason": "Could not parse Groq response as JSON",
                "error": True,
            }

    # 6. Validate and repair structure
    errors = validate_output(data, resource, shortage_amount)
    if errors:
        print(f"  Validation issues: {'; '.join(errors)}")
        data["_validation_warnings"] = errors

    if not isinstance(data.get("options"), list):
        data["options"] = []
        data["_error"] = True
    if "recommended_country" not in data:
        data["recommended_country"] = ""
        data["_error"] = True

    data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 7. Print summary
    print(f"\n  Recommendation: {data.get('recommended_country', 'N/A')}")
    print(f"  Options considered: {len(data.get('options', []))}")
    for opt in data.get("options", []):
        print(
            f"    - {opt.get('country')}: ${opt.get('price_per_unit_usd')}/{opt.get('unit')}, "
            f"reliability {opt.get('reliability_score')}/10, "
            f"capacity {opt.get('available_capacity')}"
        )
    print(f"  Reason: {data.get('recommendation_reason', 'N/A')}")

    # 8. Save
    save_result(data)
    return data


def validate_output(data, resource, shortage_amount):
    """Validate parsed output against the spec and return a list of warnings."""
    warnings = []

    options = data.get("options", [])
    if not isinstance(options, list):
        warnings.append("options is not a list")
        return warnings

    # Must be 3–6 entries
    if len(options) < 3:
        warnings.append(f"options has {len(options)} entries, spec requires 3-6")
    elif len(options) > 6:
        warnings.append(f"options has {len(options)} entries, spec requires 3-6")

    # recommended_country must be in options
    recommended = data.get("recommended_country", "")
    countries_in_options = [o.get("country") for o in options if isinstance(o, dict)]
    if recommended and recommended not in countries_in_options:
        warnings.append(f"recommended_country '{recommended}' not found in options")

    # Validate each option's fields
    for i, opt in enumerate(options):
        if not isinstance(opt, dict):
            warnings.append(f"options[{i}] is not an object")
            continue

        country = opt.get("country", "?")

        # price_per_unit_usd must be a number
        price = opt.get("price_per_unit_usd")
        if not isinstance(price, (int, float)):
            warnings.append(f"{country}: price_per_unit_usd is not a number")

        # reliability_score must be int 1–10
        score = opt.get("reliability_score")
        if not isinstance(score, int) or score < 1 or score > 10:
            warnings.append(f"{country}: reliability_score must be int 1-10")

        # existing_trade_relation must be boolean
        trade = opt.get("existing_trade_relation")
        if not isinstance(trade, bool):
            warnings.append(f"{country}: existing_trade_relation must be boolean")

    return warnings


_seen_result_ids = set()


def save_result(data):
    """Append result to dealmaker_output.json (skip duplicates)."""
    output_path = BASE_DIR / "dealmaker_output.json"

    # Generate a stable dedup key based on resource + shortage + recommended country
    dedup_key = (
        data.get("resource", ""),
        data.get("shortage_amount", ""),
        data.get("recommended_country", ""),
    )
    if dedup_key in _seen_result_ids:
        print(
            f"  Skipping duplicate result ({dedup_key[0]} / {dedup_key[1]} -> {dedup_key[2]})"
        )
        return
    _seen_result_ids.add(dedup_key)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([data], f, indent=4)
        f.write("\n")
    print(f"\n  Result saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Dealmaker Agent — source alternative crude oil / LPG supply for India"
    )
    parser.add_argument(
        "--resource",
        "-r",
        default=os.getenv("DEALMAKER_RESOURCE", "crude_oil"),
        choices=["crude_oil", "lpg"],
        help="Resource in shortage (crude_oil or lpg)",
    )
    parser.add_argument(
        "--shortage",
        "-s",
        default=os.getenv("DEALMAKER_SHORTAGE", "45,000 barrels/day"),
        help="Shortage amount India needs to replace (e.g. '45,000 barrels/day')",
    )
    args = parser.parse_args()

    run_deal(args.resource, args.shortage)


if __name__ == "__main__":
    main()
