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

    def get_top_relevant_notes(self, character_id, source, threshold=0.75, top_k=3):
        """
        Retrieve the top-k most semantically relevant notes for a character, given a source string.
        Only notes with similarity above the threshold are returned.
        """
        from app.persistence.notes_repository import NotesRepository
        from app.llm.embeddings import EmbeddingService

        notes_repo = NotesRepository()
        embedding_service = EmbeddingService()

        # Get all notes for the character (not just the latest 3)
        import sqlite3
        DB_PATH = "db/notes.db"
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute(
                "SELECT note FROM character_notes WHERE character_id = ?",
                (character_id,)
            )
            notes = [row[0] for row in cursor.fetchall()]

        if not notes:
            return []

        source_emb = embedding_service.embed(source)
        note_sims = []
        for note in notes:
            note_emb = embedding_service.embed(note)
            sim = embedding_service.cosine_similarity(source_emb, note_emb)
            note_sims.append((note, sim))

        # Filter by threshold and sort by similarity
        filtered = [n for n in note_sims if n[1] >= threshold]
        filtered.sort(key=lambda x: x[1], reverse=True)
        return [n[0] for n in filtered[:top_k]]

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
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message.content.strip()
