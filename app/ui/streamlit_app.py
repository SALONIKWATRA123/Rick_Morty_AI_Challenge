"""Streamlit UI entrypoint for Rick & Morty AI Explorer."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is on sys.path so `import app...` works when executed by Streamlit.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import streamlit as st

from app.api.rick_morty_client import RickMortyClient
from app.llm.llm_service import LLMService
from app.evaluation.evaluator import Evaluator
from app.persistence.notes_repository import NotesRepository
from app.llm.embeddings import EmbeddingService


def main() -> None:

    client = RickMortyClient()
    notes_repo = NotesRepository()
    llm = LLMService()
    evaluator = Evaluator()
    embedding_service = EmbeddingService()

    try:
        locations = client.get_all_locations()
    except Exception as e:
        st.error(
            "Failed to load locations from https://rickandmortyapi.com (connection reset). "
            "Please check your internet/VPN/proxy and try again.\n\n"
            f"Details: {type(e).__name__}: {e}"
        )
        st.stop()

    # --- Simple selectbox-based location selection ---
    location_names = [loc["name"] for loc in locations]
    selected_name = st.selectbox("Select Location", location_names)
    location = next((l for l in locations if l["name"] == selected_name), None)
    if location is None:
        st.warning("No location selected. Please select a location above.")
        st.stop()

    # All code using 'location' must come after this check
    st.caption(f"Type: {location.get('type', '—')} | Dimension: {location.get('dimension', '—')}")

    # --- Collect all character details and all notes per character ---
    residents = []
    all_notes = []
    for resident_url in location["residents"]:
        character = client.get_character_by_url(resident_url)
        # Get ALL notes for this character (not just 3)
        notes = notes_repo.get_notes(character["id"])
        note_texts = [n for n, _ in notes]
        all_notes.extend(note_texts)
        residents.append({
            "character": character,
            "notes": note_texts
        })


    if st.button("Generate AI Summary"):
        summary = llm.generate_location_summary(location, residents)
        scores = evaluator.evaluate(summary, location, residents=residents)
        st.subheader("AI Summary")
        st.write(summary)

        # --- Enhanced Evaluation UI ---
        st.markdown("### Evaluation Results by scoring function 🏆")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Factual**")
            st.write(render_stars(scores.get("factual", 0)))
        with col2:
            st.markdown("**Creativity**")
            st.write(render_stars(scores.get("creativity", 0)))
        with col3:
            st.markdown("**Completeness**")
            st.write(render_stars(scores.get("completeness", 0)))

        st.markdown("**Semantic Similarity** (Embedding-based metric)")
        sim = float(scores.get("semantic_similarity", 0))
        st.progress(sim)
        st.write(f"{int(sim * 100)}% similar")

        # LLM as a judge (independent, not using our scores)
        # Prepare a source context for the LLM: location, residents, and notes
        source_context = f"Location: {location['name']}\nType: {location.get('type', '-')}, Dimension: {location.get('dimension', '-')}\n"
        for r in residents:
            c = r["character"]
            notes = r["notes"]
            source_context += f"\nResident: {c.get('name', '-')}, Status: {c.get('status', '-')}, Species: {c.get('species', '-')}, Gender: {c.get('gender', '-')}, Origin: {(c.get('origin') or {}).get('name', '-')}, Current location: {(c.get('location') or {}).get('name', '-')}, Episodes: {len(c.get('episode') or [])}"
            if notes:
                source_context += f"\n  Notes: {'; '.join(notes)}"

        judge_prompt = f"""
You are an expert judge for Rick & Morty summaries. Here is the source information about a location and its residents, and an AI-generated summary.\n\nSOURCE:\n{source_context}\n\nAI SUMMARY:\n{summary}\n\nYour task:\n- Give a Factual score (1-5) for how factually accurate the summary is compared to the source.\n- Give a Creativity score (1-5) for how creative or entertaining the summary is.\n- Give a Completeness score (1-5) for how well the summary covers the important details from the source.\n- Then, provide a 1-2 sentence verdict on the summary's overall quality.\n\nRespond in this JSON format:\n{{\n  \"factual\": <int>,\n  \"creativity\": <int>,\n  \"completeness\": <int>,\n  \"verdict\": <string>\n}}"""
        judge_response = llm.generate_judge_verdict(judge_prompt)
        import json
        try:
            judge_json = json.loads(judge_response)
        except Exception:
            judge_json = {"factual": "-", "creativity": "-", "completeness": "-", "verdict": judge_response}
        st.subheader("LLM Judge (Independent)")
        colj1, colj2, colj3 = st.columns(3)
        with colj1:
            st.markdown("**Factual**")
            st.write(render_stars(judge_json.get("factual", 0)))
        with colj2:
            st.markdown("**Creativity**")
            st.write(render_stars(judge_json.get("creativity", 0)))
        with colj3:
            st.markdown("**Completeness**")
            st.write(render_stars(judge_json.get("completeness", 0)))
        st.markdown(f"**Verdict:** {judge_json.get('verdict', judge_response)}")

    # --- Unified Semantic Search for Characters (Details + Notes) in Selected Location ---
    st.subheader("🔍 AI Semantic Search: Characters (Details + Notes)")
    # Use session state to manage search text and trigger
    if 'last_location' not in st.session_state:
        st.session_state['last_location'] = selected_name
    if 'char_search_text' not in st.session_state:
        st.session_state['char_search_text'] = ''
    if 'char_search_triggered' not in st.session_state:
        st.session_state['char_search_triggered'] = False
    # If location changed, clear search (and force rerender)
    if st.session_state['last_location'] != selected_name:
        st.session_state['char_search_text'] = ''
        st.session_state['char_search_triggered'] = False
        st.session_state['last_location'] = selected_name
        st.rerun()
    def update_char_search_text():
        st.session_state['char_search_text'] = st.session_state['char_note_search']
        st.session_state['char_search_triggered'] = False
    char_query = st.text_input(
        "Search characters in this location (details & notes included)",
        value=st.session_state['char_search_text'],
        key="char_note_search",
        on_change=update_char_search_text
    )
    search_button = st.button("Search Characters", key="search_char_btn")
    # Only search if triggered by button or Enter
    if search_button or (char_query != '' and char_query == st.session_state['char_search_text'] and not st.session_state['char_search_triggered']):
        st.session_state['char_search_text'] = char_query
        st.session_state['char_search_triggered'] = True
    # Only search if triggered and text is not empty
    if st.session_state['char_search_triggered'] and st.session_state['char_search_text']:
        char_query_emb = embedding_service.embed(st.session_state['char_search_text'])
        # Prepare a single corpus per character: all details + all notes
        char_items = []  # (character, full_text)
        for resident_url in location["residents"]:
            character = client.get_character_by_url(resident_url)
            notes = notes_repo.get_notes(character["id"])
            notes_text = "; ".join([n for n, _ in notes])
            char_details = f"Name: {character.get('name', '-')}; Status: {character.get('status', '-')}; Species: {character.get('species', '-')}; Gender: {character.get('gender', '-')}; Origin: {(character.get('origin') or {}).get('name', '-')}; Current location: {(character.get('location') or {}).get('name', '-')}; Episodes: {len(character.get('episode') or [])}; Notes: {notes_text}"
            char_items.append((character, char_details))
        # Embeddings for characters (details + notes)
        char_corpus = [full_text for _, full_text in char_items]
        char_embs = [embedding_service.embed(text) for text in char_corpus]
        import numpy as np
        char_sims = [embedding_service.cosine_similarity(char_query_emb, emb) for emb in char_embs]
        # Top results
        top_char_idx = np.argsort(char_sims)[::-1][:5]
        st.markdown("#### Top Matching Characters (Details + Notes):")
        for idx in top_char_idx:
            character, full_text = char_items[idx]
            st.write(f"**{character.get('name', '-')}** — {full_text}")

    # Always show Residents section for the selected location
    st.subheader("Residents")
    for resident_url in location["residents"]:
        character = client.get_character_by_url(resident_url)
        with st.expander(character["name"]):
            st.image(character["image"], width=150)
            st.write(f"Status: {character['status']}")
            st.write(f"Species: {character['species']}")

            details_key = f"char_details_{character['id']}"
            if st.button("Load more details", key=f"details_{character['id']}"):
                st.session_state[details_key] = character

            if details_key in st.session_state:
                c = st.session_state[details_key]
                st.subheader("Character details")
                st.write(f"Gender: {c.get('gender', '—')}")
                st.write(f"Origin: {(c.get('origin') or {}).get('name', '—')}")
                st.write(f"Current location: {(c.get('location') or {}).get('name', '—')}")
                st.write(f"Episode count: {len(c.get('episode') or [])}")

            note = st.text_area("Add Note (max 100 chars)", key=character["id"], max_chars=100)
            if st.button("Save Note", key=f"save_{character['id']}"):
                notes_repo.add_note(character["id"], note)

            st.caption("All notes for this character")
            notes = notes_repo.get_notes(character["id"])
            for n, ts in notes:
                st.write(f"📝 {n} ({ts})")

def render_stars(score, max_stars=5):
    """Render a star rating as emoji."""
    try:
        score = int(round(float(score)))
    except Exception:
        score = 0
    stars = "⭐" * score + "☆" * (max_stars - score)
    return f"{stars} ({score}/{max_stars})"


if __name__ == "__main__":
    main()
