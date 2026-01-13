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


def main() -> None:
    client = RickMortyClient()
    llm = LLMService()
    evaluator = Evaluator()
    notes_repo = NotesRepository()

    st.set_page_config(page_title="Rick & Morty AI", layout="wide")

    st.title("🧪 Rick & Morty AI Explorer")

    try:
        locations = client.get_all_locations()
    except Exception as e:
        st.error(
            "Failed to load locations from https://rickandmortyapi.com (connection reset). "
            "Please check your internet/VPN/proxy and try again.\n\n"
            f"Details: {type(e).__name__}: {e}"
        )
        st.stop()

    location_names = [loc["name"] for loc in locations]

    selected_name = st.selectbox("Select Location", location_names)
    location = next(l for l in locations if l["name"] == selected_name)

    st.caption(f"Type: {location.get('type', '—')} | Dimension: {location.get('dimension', '—')}")

    if st.button("Generate AI Summary"):
        # Gather all character details and their top 3 notes
        residents = []
        for resident_url in location["residents"]:
            character = client.get_character_by_url(resident_url)
            notes = notes_repo.get_notes(character["id"], limit=3)
            residents.append({
                "character": character,
                "notes": [n for n, _ in notes]
            })
        summary = llm.generate_location_summary(location, residents)
        scores = evaluator.evaluate(summary, location)

        st.subheader("AI Summary")
        st.write(summary)

        st.subheader("Evaluation")
        st.json(scores)

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

            st.caption("Showing only the latest 3 notes")
            notes = notes_repo.get_notes(character["id"], limit=3)
            for n, ts in notes:
                st.write(f"📝 {n} ({ts})")


if __name__ == "__main__":
    main()
