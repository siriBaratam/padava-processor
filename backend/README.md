# 🛰️ Scout Agent

## Overview
The Scout Agent is the first intelligence layer of the AI-Driven Energy Supply Chain Resilience System.
Its responsibility is to continuously monitor global energy-related news, identify potential disruption events, and convert unstructured news into structured intelligence for downstream agents.
The Scout Agent uses a Large Language Model (Llama 3.3 70B via Groq) to analyze multiple news articles simultaneously, merge duplicate reports referring to the same real-world event, and generate standardized event summaries.
---

## Responsibilities
- Fetch global energy news using NewsAPI
- Remove duplicate articles
- Merge multiple reports describing the same event
- Identify:
  - Event Type
  - Country
  - Commodity
  - Severity
  - Risk Score
  - Corridor at Risk
- Generate structured JSON
- Pass disruption events to the Accountant Agent
---

## Workflow
NewsAPI
    │
    ▼
Fetch Articles
    │
    ▼
Remove Duplicates
    │
    ▼
LLM Analysis
    │
    ▼
Merge Similar Events
    │
    ▼
Structured JSON
    │
    ▼
Accountant Agent
---

## Input
News articles from NewsAPI.

Example:

```json
{
  "title": "Missile attack disrupts shipping in the Strait of Hormuz",
  "description": "...",
  "source": "Reuters"
}
```
---

## Output
```json
[
  {
    "Headline": "Missile attack disrupts shipping in the Strait of Hormuz",
    "Event Type": "Geopolitical Conflict",
    "Classification": "BAD",
    "Severity": "CRITICAL",
    "Risk Score": 10,
    "Country": "Iran",
    "Commodity": "Crude Oil",
    "Corridor at Risk": "Strait of Hormuz",
    "Summary": "Military escalation threatens global crude oil shipments."
  }
]
```
---

## Project Structure
```
Scout-Agent/
│
├── scout.py
```
---

## Technologies Used
- Python
- NewsAPI
- Agno
- Groq API
- Llama 3.3 70B
---

## Future Improvements
- Multi-language news analysis
- Real-time streaming
- Social media monitoring
- Confidence estimation

# 📊 Accountant Agent

## Overview
The Accountant Agent evaluates the operational impact of disruption events identified by the Scout Agent.
It estimates the effect on supply chains by analyzing shipping routes, suppliers, refineries, tanker availability, and potential supply losses.
The output is a concise business impact assessment used by the Strategist Agent.
---

## Responsibilities
- Receive disruption events from Scout Agent
- Analyze affected shipping corridors
- Identify impacted suppliers
- Estimate supply loss
- Evaluate refinery impact
- Determine tanker availability
- Calculate operational risk
- Generate business impact summary
---

## Workflow
Scout Output
      │
      ▼
Shipment Analysis
      │
      ▼
Corridor Analysis
      │
      ▼
Supplier Analysis
      │
      ▼
Business Impact Assessment
      │
      ▼
Strategist Agent
---

## Input
Structured disruption events.
Example:
```json
[
  {
    "Headline": "Missile attack disrupts shipping",
    "Country": "Iran",
    "Risk Score": 10,
    "Corridor at Risk": "Strait of Hormuz"
  }
]
```
---

## Output
```json
{
  "Headline": "Missile attack disrupts shipping",
  "Overall Risk": "CRITICAL",
  "Estimated Supply Loss (bpd)": 1200000,
  "Affected Suppliers": 4,
  "Affected Tankers": 18,
  "Affected Refineries": 6,
  "Business Impact": "Severe disruption expected across crude oil imports."
}
```
---

## Project Structure
```
Accountant/
│
├── analyzers/
├── report/
├── accountant.py
```
## Technologies Used

- Python
- Pandas
- NumPy
- JSON
- Modular Rule-Based Analytics
---

## Features
- Shipment impact estimation
- Supplier analysis
- Corridor risk assessment
- Refinery impact analysis
- Tanker analysis
- Business impact reporting
---

## Future Improvements
- Real-time AIS vessel tracking
- Dynamic refinery database
- Live supplier contracts
- Cost estimation
- Demand forecasting integration
---

## Installation 

```bash
pip install -r requirements.txt
```

Create a `.env` file:
```
NEWS_API_KEY=your_news_api_key
GROQ_API_KEY=your_groq_api_key
```
---

## Usage

```bash
python main.py
```
---