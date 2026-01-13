"""LLM service abstraction.

This is a placeholder interface layer so you can swap providers (OpenAI, Azure OpenAI,
local models, etc.) without touching UI/business logic.
"""

from __future__ import annotations

from dataclasses import dataclass
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class LLMService:

    def generate_location_summary(self, location, residents):
        prompt = f"""
You are a Rick & Morty narrator.

Location Name: {location['name']}
Type: {location['type']}
Dimension: {location['dimension']}
Number of residents: {len(residents)}

Residents:
"""
        for r in residents:
            c = r["character"]
            notes = r["notes"]
            prompt += (
                f"\n- Name: {c.get('name', '—')}, Status: {c.get('status', '—')}, Species: {c.get('species', '—')}, "
                f"Gender: {c.get('gender', '—')}, Origin: {(c.get('origin') or {}).get('name', '—')}, "
                f"Current location: {(c.get('location') or {}).get('name', '—')}, Episodes: {len(c.get('episode') or [])}"
            )
            if notes:
                prompt += f"\n  Top notes: " + "; ".join(notes)
        prompt += "\n\nGenerate a humorous but informative summary."

        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
