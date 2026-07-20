"""
Dealmaker Agent — refactored to use LangChain ChatGroq with structured output.

Demonstrates the BEFORE vs AFTER difference:

  BEFORE (dealmaker.py):    raw groq SDK + manual JSON parsing + regex + validate_output()
  AFTER  (this file):      ChatGroq.with_structured_output() → typed Pydantic model, zero parsing

Everything else (news fetching, result saving, Navigator auto-launch) is identical.
"""

import argparse
import json
import os
import requests
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from config import settings

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


# ──────────────────────────────────────────────────────────────
#  LangChain Pydantic models — the structured output schema
# ──────────────────────────────────────────────────────────────

class DealOption(BaseModel):
    """A single alternative supplier option for India."""
    country: str = Field(description="Supplier country name")
    resource: str = Field(description="Resource being sourced (e.g. crude_oil, lpg)")
    price_per_unit_usd: float = Field(description="Price per unit in USD")
    unit: str = Field(description="Unit of measurement (e.g. barrel, metric ton, MMBtu)")
    available_capacity: str = Field(description="Rough available export capacity (e.g. '500,000 barrels/day')")
    reliability_score: int = Field(ge=1, le=10, description="1–10 based on political stability and India relations")
    existing_trade_relation: bool = Field(description="Whether India already buys from this country")
    notes: str = Field(description="Caveats: sanctions exposure, lead time, political tension, logistics")


class DealOutput(BaseModel):
    """Structured output from the Dealmaker agent."""
    resource: str = Field(description="Resource in shortage")
    shortage_amount: str = Field(description="Shortage amount India needs to replace")
    options: list[DealOption] = Field(min_length=3, max_length=6, description="Candidate supplier options (3–6 entries)")
    recommended_country: str = Field(description="Exactly one recommended country from the options list")
    recommendation_reason: str = Field(description="One to two sentence justification for the recommendation")
    error: bool = Field(default=False, description="Whether an error occurred")
    timestamp: str = Field(default="", description="ISO timestamp of when the analysis was run")


# ──────────────────────────────────────────────────────────────
#  Prompt template (no more JSON format scaffolding!)
# ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a senior global energy trade negotiator. You source alternative crude oil and LPG supply deals for India when an existing supply source becomes unreliable due to war, sanctions, or geopolitical disruption. You know real-world export capacities, typical commodity pricing, and which supplier relationships are politically and logistically dependable versus risky.

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
For each candidate determine price, unit, available capacity, reliability score (1–10), existing trade relation, and notes.

### Step 5 — Recommend
Select exactly ONE recommended country. Base the choice on the full picture — price, capacity, reliability, and speed of deal-closing — not price alone. Justify in one to two sentences.

## Constraints
- Provide exactly 3–6 options.
- recommended_country must be one of the countries in options.
- Do not invent implausible prices — ground every figure in well-known market data or clearly label it as an estimate.
"""

RESOURCE_KEYWORDS = {
    "crude_oil": "crude oil export price supply India",
    "lpg": "LPG export price supply India",
}


# ──────────────────────────────────────────────────────────────
#  News fetching (unchanged from original)
# ──────────────────────────────────────────────────────────────

def fetch_relevant_news(resource: str, max_articles: int = 8) -> list[dict]:
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
            articles.append({
                "headline": a.get("title", ""),
                "summary": (a.get("description") or "")[:300],
                "source": a.get("source", {}).get("name", "unknown"),
                "link": a.get("url", ""),
            })
        print(f"  Fetched {len(articles)} news articles about {resource}")
        return articles
    except Exception as e:
        print(f"  NewsAPI request error: {e}")
        return []


def build_news_context(articles: list[dict]) -> str:
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


# ──────────────────────────────────────────────────────────────
#  Result saving (unchanged from original)
# ──────────────────────────────────────────────────────────────

_seen_result_ids: set[tuple[str, str, str]] = set()


def save_result(data: dict) -> None:
    """Append result to dealmaker_output.json (skip duplicates)."""
    output_path = BASE_DIR / "dealmaker_output.json"

    dedup_key = (
        data.get("resource", ""),
        data.get("shortage_amount", ""),
        data.get("recommended_country", ""),
    )
    if dedup_key in _seen_result_ids:
        print(f"  Skipping duplicate result ({dedup_key[0]} / {dedup_key[1]} -> {dedup_key[2]})")
        return
    _seen_result_ids.add(dedup_key)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([data], f, indent=4)
        f.write("\n")
    print(f"\n  Result saved to {output_path}")


# ──────────────────────────────────────────────────────────────
#  Navigator launcher (unchanged from original)
# ──────────────────────────────────────────────────────────────

def run_navigator(country: str, resource: str) -> None:
    """Run the Navigator agent as a subprocess with Dealmaker's recommendation."""
    navigator_script = BASE_DIR.parent / "Navigator-agent" / "navigator.py"
    if not navigator_script.exists():
        print(f"\n  ⚠️  Navigator agent not found at {navigator_script}")
        print("  Skipping route planning.")
        return

    dealmaker_output = BASE_DIR / "dealmaker_output.json"

    print(f"\n{'─'*60}")
    print(f"  Launching Navigator Agent for route planning...")
    print(f"  Country : {country}")
    print(f"  Resource: {resource}")
    print(f"{'─'*60}\n")

    try:
        result = subprocess.run(
            [
                sys.executable, str(navigator_script),
                "--country-from", str(dealmaker_output),
                "--resource", resource,
            ],
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        if result.returncode != 0:
            print(f"\n  Navigator agent exited with code {result.returncode}")
            if result.stderr:
                print(f"  stderr: {result.stderr.strip()[:500]}")
        if result.stdout:
            print(result.stdout.strip())
    except FileNotFoundError:
        print("  Could not find Python executable to run Navigator agent")
    except Exception as e:
        print(f"  Error launching Navigator agent: {e}")


# ──────────────────────────────────────────────────────────────
#  Core logic — LangChain edition
# ──────────────────────────────────────────────────────────────

def run_deal(resource: str, shortage_amount: str) -> DealOutput:
    """Run the dealmaker analysis using LangChain ChatGroq with structured output.

    This replaces ~60 lines of manual JSON parsing, regex, and validation
    with a single ``with_structured_output()`` call.
    """
    print(f"\n{'='*60}")
    print(f"  DEALMAKER AGENT  (LangChain edition)")
    print(f"  Resource: {resource}")
    print(f"  Shortage: {shortage_amount}")
    print(f"{'='*60}\n")

    # 1. Fetch news context
    articles = fetch_relevant_news(resource)
    news_context = build_news_context(articles)
    today = datetime.now().strftime("%B %d, %Y")

    # 2. Build the LangChain prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("human", SYSTEM_PROMPT),
    ])
    formatted_prompt = prompt.format_messages(
        today=today,
        news_context=news_context,
        resource=resource,
        shortage_amount=shortage_amount,
    )

    # 3. Create the LLM with structured output
    #    LangChain converts DealOutput → JSON schema → tool call binding.
    #    The LLM returns JSON matching DealOutput; LangChain parses & validates it.
    print("  Calling Groq via LangChain (llama-3.1-8b-instant, structured output)...")
    try:
        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=settings.groq_api_key,
            temperature=0.4,
        )
        structured_llm = llm.with_structured_output(DealOutput)
        result: DealOutput = structured_llm.invoke(formatted_prompt)
    except Exception as e:
        error_text = str(e)
        print(f"  LangChain/Groq error: {error_text[:200]}")
        result = DealOutput(
            resource=resource,
            shortage_amount=shortage_amount,
            options=[],
            recommended_country="",
            recommendation_reason=f"Groq API error: {error_text[:120]}",
            error=True,
        )

    result.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. Print summary
    print(f"\n  Recommendation: {result.recommended_country or 'N/A'}")
    print(f"  Options considered: {len(result.options)}")
    for opt in result.options:
        print(
            f"    - {opt.country}: ${opt.price_per_unit_usd}/{opt.unit}, "
            f"reliability {opt.reliability_score}/10, "
            f"capacity {opt.available_capacity}"
        )
    print(f"  Reason: {result.recommendation_reason or 'N/A'}")

    # 5. Save (convert to dict for JSON serialisation)
    result_dict = result.model_dump(mode="json")
    save_result(result_dict)

    return result


# ──────────────────────────────────────────────────────────────
#  CLI (unchanged interface)
# ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Dealmaker Agent (LangChain edition) — source alternative crude oil / LPG supply for India"
    )
    parser.add_argument(
        "--resource", "-r",
        default=os.getenv("DEALMAKER_RESOURCE", "crude_oil"),
        choices=["crude_oil", "lpg"],
        help="Resource in shortage (crude_oil or lpg)",
    )
    parser.add_argument(
        "--shortage", "-s",
        default=os.getenv("DEALMAKER_SHORTAGE", "45,000 barrels/day"),
        help="Shortage amount India needs to replace (e.g. '45,000 barrels/day')",
    )
    parser.add_argument(
        "--run-navigator", "-n",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Automatically run Navigator agent for route planning after a successful deal (default: True)",
    )
    args = parser.parse_args()

    data = run_deal(args.resource, args.shortage)

    # Auto-launch Navigator if we got a valid recommendation
    if args.run_navigator and data and not data.error:
        if data.recommended_country:
            run_navigator(data.recommended_country, args.resource)


if __name__ == "__main__":
    main()
