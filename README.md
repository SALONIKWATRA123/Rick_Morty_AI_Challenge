# Rick & Morty AI Challenge

A lightweight, AI-powered application built on the Rick & Morty API. It retrieves structured data about locations and characters, generates creative summaries using an LLM, and evaluates those summaries using multiple complementary techniques.

## Features

- Fetches locations and residents from the Rick & Morty API
- Generates AI-powered summaries of locations
- Evaluates summaries using:
	- Rule-based heuristics
	- Embedding-based semantic similarity
	- LLM-as-a-judge scoring
- Transparent evaluation output (no hidden aggregation)

## Tech Stack

- Python
- Rick & Morty REST API
- OpenAI GPT-4o-mini (generation + evaluation)
- Embeddings for semantic comparison

## How It Works

1. Data is fetched from the Rick & Morty API
2. Locations and residents are structured into clean objects
3. An LLM generates a creative summary
4. The summary is evaluated using three independent methods
5. Results are returned for inspection and comparison

## Design Rationale

The project focuses on both generation and evaluation. By combining deterministic rules, semantic embeddings, and LLM judgment, the system provides a more honest and interpretable view of AI quality.

## Running the Project

1. Install dependencies
2. Set your OpenAI API key
3. Run the main script to fetch data, generate summaries, and view evaluations

## Notes

This project is intentionally simple in scope but deliberate in design. It showcases responsible AI development—grounded in data, evaluated thoughtfully, and explained clearly.

---

Thank you for reviewing this submission!
# rick_morty_ai

Project scaffold.

## Structure
- `app/` application code
- `db/` local SQLite database

## Run (example)
- `streamlit run app/ui/streamlit_app.py`
