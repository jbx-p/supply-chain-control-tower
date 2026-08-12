"""
briefing_prompt.py
Builds the system and user prompt for the executive briefing, given
the structured data from data_aggregator.py.
"""

import json


SYSTEM_PROMPT = """You are a supply chain analyst writing a concise weekly executive \
briefing for senior leadership at a mid-size company. Your audience is busy, \
non-technical, and cares about business impact, not methodology.

Rules:
- Ground every claim in the data provided. Never invent numbers not present in the input.
- Be direct and specific — name actual products, suppliers, and figures, not vague generalities.
- Keep it genuinely brief: leadership will skim this, not study it.
- Use plain business language, not data science jargon (say "demand is rising" not "positive trend coefficient").
- If a number reflects a tradeoff (e.g. higher cost for better resilience), say so honestly rather than only reporting the positive framing.
"""

BRIEFING_TEMPLATE = """Write this week's supply chain executive briefing using the data below.

Structure it with these sections:
1. **Headline** — one sentence, the single most important thing to know this week
2. **Demand Outlook** — 2-3 sentences on what's trending up/down and overall forecast confidence
3. **Supplier Risk Alerts** — the highest-risk suppliers right now and what that means practically
4. **Inventory & Cost** — the optimization recommendation and its cost tradeoff, explained plainly
5. **Resilience Check** — what the disruption simulation shows about how well current policy would hold up

Keep the whole briefing under 300 words. Use markdown formatting with the section headers above.

DATA:
{data_json}
"""


def build_briefing_prompt(briefing_data):
    data_json = json.dumps(briefing_data, indent=2, default=str)
    return BRIEFING_TEMPLATE.format(data_json=data_json)