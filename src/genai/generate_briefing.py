"""
generate_briefing.py
Calls Claude via OpenRouter (OpenAI-compatible API) to generate the
executive briefing from aggregated data, and saves the result.

Note: originally designed for the Anthropic API directly; switched to
OpenRouter due to an Anthropic billing/card issue during development.
See docs/genai_briefing_approach.md for details.

Run:
    python src/genai/generate_briefing.py
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

sys.path.append(os.path.dirname(__file__))
from data_aggregator import build_full_briefing_data
from briefing_prompt import SYSTEM_PROMPT, build_briefing_prompt


# OpenRouter model naming convention: "provider/model-name"
MODEL_NAME = "anthropic/claude-sonnet-4.5"


def load_api_key():
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise ValueError("OPENROUTER_API_KEY not found — check your .env file")
    return key


def generate_briefing():
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=load_api_key(),
    )

    print("Aggregating data from all phases...")
    try:
        briefing_data = build_full_briefing_data()
    except Exception as e:
        print(f"❌ Failed to aggregate data: {e}")
        print("   Check that Phases 3-6 have all been run and their tables exist.")
        raise

    print("Building prompt...")
    user_prompt = build_briefing_prompt(briefing_data)

    print(f"Calling {MODEL_NAME} via OpenRouter...")
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=1000,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as e:
        print(f"❌ OpenRouter API error: {e}")
        raise

    briefing_text = response.choices[0].message.content
    return briefing_text, briefing_data


def save_briefing(briefing_text):
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "reports")
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, f"executive_briefing_{timestamp}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Executive Briefing — {timestamp}\n\n")
        f.write(briefing_text)

    print(f"\n✅ Briefing saved to {filepath}")
    return filepath


if __name__ == "__main__":
    briefing_text, briefing_data = generate_briefing()

    print("\n" + "=" * 60)
    print("GENERATED BRIEFING")
    print("=" * 60)
    print(briefing_text)

    save_briefing(briefing_text)