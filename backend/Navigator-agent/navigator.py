"""
Navigator Agent — refactored to use LangChain ChatGroq with structured output.

BEFORE: raw Groq SDK + manual JSON parsing + regex + validate_output()
AFTER:  ChatGroq.with_structured_output() -> typed Pydantic model, zero parsing

Everything else (news fetching, reference coordinates, checkpoint tracking, CLI) is identical.
"""

import argparse
import json
import os
import requests
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

class RouteWaypoint(BaseModel):
    """A single waypoint along a shipping route."""
    name: str = Field(description="Port, chokepoint, or pipeline node name")
    lat: float = Field(description="Latitude coordinate")
    lng: float = Field(description="Longitude coordinate")
    type: str = Field(description="Type: origin_port, chokepoint, pipeline_node, or destination_port")


class Route(BaseModel):
    """A complete shipping route from supplier country to an Indian port."""
    mode: str = Field(description="Transport mode: sea, pipeline, or sea+pipeline")
    origin_country: str = Field(description="Supplier country name")
    origin_port: str = Field(description="Export terminal name")
    destination_port: str = Field(description="Indian receiving port name")
    waypoints: list[RouteWaypoint] = Field(
        min_length=2,
        description="Ordered waypoints from origin to destination (includes origin_port, chokepoints, destination_port)"
    )
    distance_km: float = Field(description="Total distance in kilometers")
    estimated_transit_days: float = Field(description="Estimated transit time in days")
    chokepoints: list[str] = Field(description="Major chokepoints along this route")
    risk_notes: str = Field(description="Route risks: chokepoint congestion, piracy, geopolitical tension, weather")


class NavigatorOutput(BaseModel):
    """Structured output from the Navigator agent."""
    country: str = Field(description="Supplier country")
    resource: str = Field(description="Resource being transported (e.g. crude_oil, lpg)")
    routes: list[Route] = Field(min_length=1, max_length=3, description="Route options (1–3 entries)")
    recommended_route_index: int = Field(ge=0, le=2, description="Index of the recommended route (0-based)")
    recommendation_reason: str = Field(description="Fastest-vs-safest tradeoff justification")
    error: bool = Field(default=False, description="Whether an error occurred")
    timestamp: str = Field(default="", description="ISO timestamp of when the analysis was run")


# ── Shipping news keywords by resource ──────────────────────────────────────

SHIPPING_NEWS_KEYWORDS = {
    "crude_oil": "oil tanker shipping route Strait of Hormuz chokepoint India crude",
    "lpg": "LPG tanker shipping route Strait of Hormuz chokepoint India gas",
    "coal": "bulk carrier coal shipping route India chokepoint",
    "lng": "LNG tanker shipping route Strait of Hormuz chokepoint India gas",
}


def fetch_shipping_news(resource, max_articles=5):
    """Fetch recent news about shipping routes and chokepoints."""
    if not settings.news_api_key:
        return []

    q = SHIPPING_NEWS_KEYWORDS.get(resource, "shipping route India tanker chokepoint")

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": max_articles,
    }
    headers = {"X-Api-Key": settings.news_api_key}

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
                }
            )
        print(f"  Fetched {len(articles)} shipping news articles")
        return articles
    except Exception as e:
        print(f"  NewsAPI request error: {e}")
        return []


def build_shipping_news_context(articles):
    """Turn news articles into a short context block for the prompt."""
    if not articles:
        return ""
    lines = ["## Recent Shipping & Chokepoint News"]
    for a in articles[:5]:
        summary = a.get("summary", "").strip()
        if summary:
            lines.append(f"- {a['headline']}: {summary} ({a['source']})")
        else:
            lines.append(f"- {a['headline']} ({a['source']})")
    lines.append(
        "Use the news above for current chokepoint conditions, delays, or route risks."
    )
    lines.append("")
    return "\n".join(lines)


# ── Reference coordinates for major ports & chokepoints ─────────────────────
# Used by the LLM prompt to ground its waypoint generation in real geography.

REFERENCE_PORTS = {
    # Middle East export terminals
    "Ras Tanura": {"lat": 26.642, "lng": 50.160, "country": "Saudi Arabia"},
    "Juaymah": {"lat": 26.783, "lng": 50.133, "country": "Saudi Arabia"},
    "Ras Al Khafji": {"lat": 28.433, "lng": 48.500, "country": "Saudi Arabia"},
    "Yanbu": {"lat": 24.083, "lng": 38.067, "country": "Saudi Arabia"},
    "Basra": {"lat": 30.517, "lng": 47.850, "country": "Iraq"},
    "Khor Al Amaya": {"lat": 29.767, "lng": 50.250, "country": "Iraq"},
    "Kuwait": {"lat": 29.350, "lng": 48.083, "country": "Kuwait"},
    "Bandar Abbas": {"lat": 27.183, "lng": 56.267, "country": "Iran"},
    "Kharg Island": {"lat": 29.233, "lng": 50.317, "country": "Iran"},
    "Das Island": {"lat": 25.150, "lng": 52.867, "country": "UAE"},
    "Fujairah": {"lat": 25.133, "lng": 56.350, "country": "UAE"},
    "Mina Al Ahmadi": {"lat": 29.067, "lng": 48.150, "country": "Kuwait"},
    "Lagos": {"lat": 6.433, "lng": 3.400, "country": "Nigeria"},
    "Bonny": {"lat": 4.433, "lng": 7.167, "country": "Nigeria"},
    "Luanda": {"lat": -8.800, "lng": 13.233, "country": "Angola"},
    "Soyo": {"lat": -6.133, "lng": 12.350, "country": "Angola"},
    "Port Harcourt": {"lat": 4.750, "lng": 7.017, "country": "Nigeria"},
    # USA
    "Houston": {"lat": 29.750, "lng": -95.267, "country": "United States"},
    "Corpus Christi": {"lat": 27.800, "lng": -97.400, "country": "United States"},
    "Beaumont": {"lat": 30.083, "lng": -94.100, "country": "United States"},
    "Lake Charles": {"lat": 30.217, "lng": -93.217, "country": "United States"},
    # Russia
    "Novorossiysk": {"lat": 44.717, "lng": 37.783, "country": "Russia"},
    "Primorsk": {"lat": 60.350, "lng": 28.617, "country": "Russia"},
    "Ust-Luga": {"lat": 59.667, "lng": 28.317, "country": "Russia"},
    # India receiving ports
    "Jawaharlal Nehru Port (JNPT)": {"lat": 18.950, "lng": 72.950, "country": "India"},
    "Mumbai": {"lat": 18.933, "lng": 72.833, "country": "India"},
    "Kandla": {"lat": 23.033, "lng": 70.217, "country": "India"},
    "Chennai": {"lat": 13.083, "lng": 80.283, "country": "India"},
    "Visakhapatnam": {"lat": 17.683, "lng": 83.300, "country": "India"},
    "Paradip": {"lat": 20.267, "lng": 86.683, "country": "India"},
    "Mundra": {"lat": 22.750, "lng": 69.717, "country": "India"},
    "Cochin": {"lat": 9.967, "lng": 76.267, "country": "India"},
    # Southeast Asia
    "Singapore": {"lat": 1.267, "lng": 103.833, "country": "Singapore"},
    "Port Klang": {"lat": 3.000, "lng": 101.400, "country": "Malaysia"},
    # Australia
    "Port Hedland": {"lat": -20.317, "lng": 118.567, "country": "Australia"},
    "Gladstone": {"lat": -23.833, "lng": 151.250, "country": "Australia"},
    # Africa
    "Richards Bay": {"lat": -28.800, "lng": 32.050, "country": "South Africa"},
    "Dar es Salaam": {"lat": -6.817, "lng": 39.283, "country": "Tanzania"},
}

REFERENCE_CHOKEPOINTS = {
    "Strait of Hormuz": {"lat": 26.567, "lng": 56.250},
    "Bab-el-Mandeb": {"lat": 12.583, "lng": 43.500},
    "Suez Canal": {"lat": 30.500, "lng": 32.550},
    "Strait of Malacca": {"lat": 2.000, "lng": 102.000},
    "Cape of Good Hope": {"lat": -34.500, "lng": 18.500},
    "Strait of Gibraltar": {"lat": 35.967, "lng": -5.483},
    "Lombok Strait": {"lat": -8.500, "lng": 115.833},
    "Sunda Strait": {"lat": -6.000, "lng": 105.500},
    "Panama Canal": {"lat": 9.083, "lng": -79.683},
    "Palk Strait": {"lat": 10.000, "lng": 79.833},
    "Sixth Degree Channel": {"lat": 1.500, "lng": 73.000},
    "Eight Degree Channel": {"lat": 8.000, "lng": 73.500},
    "Ten Degree Channel": {"lat": 10.000, "lng": 73.000},
}

INDIAN_RECEIVING_PORTS_BY_RESOURCE = {
    "crude_oil": "Jawaharlal Nehru Port (JNPT), Mundra, Kandla, Visakhapatnam, Chennai, Paradip, Cochin",
    "lpg": "Mundra, Kandla, Visakhapatnam, Jawaharlal Nehru Port (JNPT), Chennai",
    "coal": "Paradip, Visakhapatnam, Kandla, Chennai, Mormugao",
    "lng": "Mundra, Hazira, Dahej, Kochi, Jawaharlal Nehru Port (JNPT) — (LNG terminals)",
}


def build_coordinates_reference():
    """Build a reference text block for the prompt with known coordinates."""
    lines = []
    lines.append("## Reference Port Coordinates (use these exact values when applicable)")
    for name, info in sorted(REFERENCE_PORTS.items()):
        lines.append(f"  {name} ({info['country']}): lat={info['lat']}, lng={info['lng']}")
    lines.append("")
    lines.append("## Reference Chokepoint Coordinates (use these exact values when applicable)")
    for name, info in sorted(REFERENCE_CHOKEPOINTS.items()):
        lines.append(f"  {name}: lat={info['lat']}, lng={info['lng']}")
    lines.append("")
    lines.append("## Indian Receiving Ports by Resource")
    for resource, ports in INDIAN_RECEIVING_PORTS_BY_RESOURCE.items():
        lines.append(f"  {resource}: {ports}")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
#  Prompt template (no more JSON format scaffolding!)
# ──────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are a maritime and pipeline logistics planner. You have years of experience routing oil tankers, LPG carriers, and pipeline shipments from global supplier countries to Indian ports. You know the major shipping chokepoints (Strait of Hormuz, Suez Canal, Bab-el-Mandeb, Strait of Malacca, Cape of Good Hope) and which Indian ports typically handle which cargo. You always flag route-specific risks such as chokepoint congestion, piracy, or geopolitical tension.

Current date: {today}

## Input

- Supplier country: **{country}**
- Resource: **{resource}**

{shipping_news_context}
## Your Task

Follow these steps IN ORDER:

### Step 1 — Identify Export Port
Identify the most likely export port in {country} for {resource}. Use your knowledge of real export terminals. If multiple ports exist, choose the most prominent one for the given resource.

### Step 2 — Identify Indian Receiving Port
Identify the most suitable receiving port in India for {resource}.

### Step 3 — Research Shipping Route
Consider the standard tanker route between the identified ports. Account for known shipping distances, transit times, and seasonal factors.

### Step 4 — Identify Chokepoints
Identify every major chokepoint the route passes through.

### Step 5 — Produce Route Options
Produce 1–3 realistic route options:
- Route A (shortest / fastest): the most direct path.
- Route B (alternative): e.g. avoiding a high-risk chokepoint, or a different export/receiving port combination.
- Route C (safe but longer): e.g. going around the Cape of Good Hope to avoid the Red Sea, if relevant.

If fewer than 3 meaningful routes exist, produce only what is realistic.

### Step 6 — Determine Waypoints
For each route, determine an ordered list of waypoints from origin port to destination port. Every waypoint MUST use real, genuine latitude/longitude from the reference tables below. If a port or chokepoint is not in the reference tables, use its well-known geographic coordinate. Never invent or approximate coordinates.

### Step 7 — Estimate Distance & Time
Estimate total distance (km) and transit time (days) for each route. Base this on standard tanker speeds (~13-15 knots) and known shipping distances.

### Step 8 — Identify Risks
Note risk factors per route: chokepoint congestion, piracy, geopolitical tension, seasonal weather (e.g. monsoon in Indian Ocean, typhoons in South China Sea).

### Step 9 — Recommend
Select exactly ONE recommended route. Choose based on a fastest-vs-safest tradeoff appropriate for the resource and current geopolitical context.

## Constraints
- Provide exactly 1–3 route options.
- recommended_route_index must be a valid 0-based index into the routes list.
- All lat/lng values must be genuine geographic coordinates — use the reference tables provided below. Never invent or approximate coordinates.

{coordinates_reference}
"""


# ──────────────────────────────────────────────────────────────
#  Checkpoint & result saving (unchanged from original)
# ──────────────────────────────────────────────────────────────


def append_checkpoint(result, name, status, details=None):
    """Append a checkpoint entry to the navigator result payload."""
    checkpoint = {"name": name, "status": status}
    if details is not None:
        checkpoint["details"] = details
    result.setdefault("checkpoints", []).append(checkpoint)
    return checkpoint


def save_result(data):
    """Persist the navigator result to navigator_output.json."""
    output_path = BASE_DIR / "navigator_output.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        f.write("\n")
    print(f"\n  Result saved to {output_path}")


# ──────────────────────────────────────────────────────────────
#  Core logic — LangChain edition
# ──────────────────────────────────────────────────────────────


def run_navigation(country, resource):
    """Run the navigator agent using LangChain ChatGroq with structured output.

    This replaces ~65 lines of manual JSON parsing, regex, and validation
    with a single ``with_structured_output()`` call.
    """
    print(f"\n{'='*60}")
    print(f"  NAVIGATOR AGENT  (LangChain edition)")
    print(f"  Country : {country}")
    print(f"  Resource: {resource}")
    print(f"{'='*60}\n")

    started_at = datetime.now()
    result = {
        "country": country,
        "resource": resource,
        "status": "running",
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": None,
        "routes": [],
        "recommended_route_index": -1,
        "recommendation_reason": "",
        "checkpoints": [],
        "validation_warnings": [],
        "error": False,
        "raw_response": "",
    }
    append_checkpoint(
        result, "initialized", "in_progress", {"country": country, "resource": resource}
    )
    save_result(result)

    today = datetime.now().strftime("%B %d, %Y")
    coordinates_ref = build_coordinates_reference()

    # Fetch shipping news for current context
    articles = fetch_shipping_news(resource)
    append_checkpoint(
        result,
        "news_fetch",
        "completed" if articles else "skipped",
        {"article_count": len(articles)},
    )
    save_result(result)

    shipping_news_context = build_shipping_news_context(articles)

    # Build the LangChain prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("human", SYSTEM_PROMPT),
    ])
    formatted_prompt = prompt.format_messages(
        today=today,
        country=country,
        resource=resource,
        shipping_news_context=shipping_news_context,
        coordinates_reference=coordinates_ref,
    )

    append_checkpoint(
        result, "prompt_ready", "completed", {"prompt_length": len(str(formatted_prompt))}
    )
    save_result(result)

    # Create the LLM with structured output
    print("  Calling Groq via LangChain (llama-3.3-70b-versatile, structured output)...")
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=settings.groq_api_key,
            temperature=0.4,
        )
        structured_llm = llm.with_structured_output(NavigatorOutput)
        nav_result: NavigatorOutput = structured_llm.invoke(formatted_prompt)
        result["raw_response"] = nav_result.model_dump_json(indent=2)
        append_checkpoint(
            result, "llm_response", "completed", {"response_length": len(result["raw_response"])}
        )
        save_result(result)
    except Exception as e:
        error_text = str(e)
        print(f"  LangChain/Groq error: {error_text[:200]}")
        result.update({
            "status": "failed",
            "error": True,
            "recommendation_reason": f"Groq API error: {error_text[:120]}",
            "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })
        append_checkpoint(result, "llm_response", "failed", {"error": error_text[:200]})
        save_result(result)
        return result

    nav_result.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Merge structured output into result dict
    nav_dict = nav_result.model_dump(mode="json")
    result.update(nav_dict)
    result["status"] = "completed"
    result["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result["validation_warnings"] = []

    append_checkpoint(
        result, "validation", "completed", {"warnings": []}
    )
    save_result(result)

    # Print summary
    routes = result.get("routes", [])
    rec_idx = result.get("recommended_route_index", -1)
    print(f"\n  Routes planned: {len(routes)}")
    for i, route in enumerate(routes):
        marker = " * RECOMMENDED" if i == rec_idx else ""
        print(
            f"    Route {i}: {route.get('origin_port', '?')} -> {route.get('destination_port', '?')}"
            f"  [{route.get('distance_km', '?')} km, {route.get('estimated_transit_days', '?')} days]{marker}"
        )
        for wp in route.get("waypoints", []):
            print(f"      -> {wp.get('name')} ({wp.get('type')}) [{wp.get('lat')}, {wp.get('lng')}]")
        if route.get("chokepoints"):
            print(f"      Chokepoints: {', '.join(route['chokepoints'])}")
        if route.get("risk_notes"):
            print(f"      Risks: {route['risk_notes']}")
    print(f"  Reason: {result.get('recommendation_reason', 'N/A')}")

    return result


# ──────────────────────────────────────────────────────────────
#  CLI (unchanged interface)
# ──────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Navigator Agent (LangChain edition) — plan shipping routes from supplier countries to India"
    )
    parser.add_argument(
        "--country", "-c",
        default=os.getenv("NAVIGATOR_COUNTRY", ""),
        help="Supplier country recommended by Dealmaker (e.g. 'Saudi Arabia')",
        required=False,
    )
    parser.add_argument(
        "--resource", "-r",
        default=os.getenv("NAVIGATOR_RESOURCE", "crude_oil"),
        help="Resource being transported (e.g. crude_oil, lpg)",
    )
    parser.add_argument(
        "--country-from",
        help="Read country from this file (Dealmaker output JSON), overrides --country",
    )
    args = parser.parse_args()

    # If --country-from is provided, read country from that file
    country = args.country
    if args.country_from:
        try:
            with open(args.country_from, "r") as f:
                dealmaker_data = json.load(f)
            if isinstance(dealmaker_data, list) and len(dealmaker_data) > 0:
                country = dealmaker_data[0].get("recommended_country", "")
            elif isinstance(dealmaker_data, dict):
                country = dealmaker_data.get("recommended_country", "")
            if country:
                print(f"  Read country from {args.country_from}: {country}")
        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            print(f"  Warning: could not read country from {args.country_from}: {e}")

    if not country:
        failed_result = {
            "country": country,
            "resource": args.resource,
            "status": "failed",
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "routes": [],
            "recommended_route_index": -1,
            "recommendation_reason": "No country provided. Use --country or --country-from.",
            "checkpoints": [
                {
                    "name": "input_validation",
                    "status": "failed",
                    "details": {"reason": "missing country"},
                }
            ],
            "validation_warnings": [],
            "error": True,
        }
        save_result(failed_result)
        print("  Error: no country provided. Use --country or --country-from.")
        sys.exit(1)

    run_navigation(country, args.resource)


if __name__ == "__main__":
    main()
