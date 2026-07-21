import os
import json
import requests

from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.groq import Groq

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def fetch_news():

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": '''
        ("crude oil" OR "oil tanker" OR LNG OR OPEC
        OR "Strait of Hormuz"
        OR "Red Sea"
        OR "Suez Canal"
        OR refinery
        OR pipeline
        OR sanctions
        OR "oil supply")
        ''',

        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 50,
        "apiKey": NEWS_API_KEY
    }

    response = requests.get(url, params=params)

    response.raise_for_status()

    return response.json()["articles"]
def prepare_articles(articles):

    cleaned = []

    for article in articles:

        cleaned.append({

            "title": article.get("title"),

            "description": article.get("description"),

            "source": article["source"]["name"],

            "publishedAt": article.get("publishedAt"),

            "url": article.get("url")

        })

    return cleaned

def remove_duplicates(articles):

    seen = set()

    unique = []

    for article in articles:

        title = article["title"]

        if title not in seen:

            unique.append(article)

            seen.add(title)

    return unique

def build_prompt(news):

    return f"""For every unique event return ONLY:

- Headline
- Event Type
- Classification
- Severity
- Risk Score
- Country
- Commodity
- Corridor at Risk
- Summary

Rules:

Classification MUST be ONLY one of:
GOOD
BAD
NEUTRAL

Severity MUST be ONLY one of:
LOW
MEDIUM
HIGH
CRITICAL

Risk Score MUST be an INTEGER from 1 to 10.

Commodity MUST be one of:
Crude Oil
Petroleum
LNG
Natural Gas
Diesel

Corridor at Risk should be the affected maritime corridor or pipeline.
If unknown return "Unknown".

Event Type MUST be one of:
Geopolitical Conflict
Sanctions
Production Cut
OPEC Announcement
Pipeline Failure
Port Closure
Shipping Delay
Tanker Attack
Refinery Shutdown
Natural Disaster
Market Disruption
Never classify a refinery fire as Tanker Attack.

Never use corridor names as Event Type.

IMPORTANT RULES:

1. Many articles may describe the same real-world event.

2. If multiple articles refer to the same incident
(e.g., Iran attacks, US retaliation, Hormuz tension),
merge them into ONE event.

3. Keep the most informative headline.

4. Never return duplicate events.

Return only unique real-world disruption events.
Return ONLY valid JSON.

{json.dumps(news, indent=2)}
"""
scout = Agent(
    model=Groq(
        id="llama-3.3-70b-versatile",
        api_key=GROQ_API_KEY
    ),
    markdown=False,
)
def run_scout():

    articles = fetch_news()

    articles = prepare_articles(articles)

    articles = remove_duplicates(articles)

    prompt = build_prompt(articles)

    response = scout.run(prompt)

    return response.content


if __name__ == "__main__":
    print(run_scout())