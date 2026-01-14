# Rick & Morty AI Explorer

An interactive AI-powered explorer for the Rick & Morty universe. Select locations, view and annotate character details, generate and evaluate AI summaries, and perform advanced semantic search—all through a user-friendly Streamlit interface.

---

## Features
- **Location Explorer:** Browse all locations from the Rick & Morty API.
- **Character Details:** View, add, and persist notes for each character.
- **AI Summaries:** Generate and evaluate summaries for locations and residents using OpenAI GPT-3.5-turbo.
- **LLM Judge:** Get independent LLM-based verdicts and scores for summaries.
- **Semantic Search:** Find characters using natural language, powered by OpenAI embeddings.
- **Robust UI:** Responsive, intuitive, and error-tolerant Streamlit interface.

---

## Installation & Setup

### 1. Clone the Repository
```
git clone https://github.com/SALONIKWATRA123/Rick_Morty_AI_Challenge.git
cd Rick_Morty_AI_Challenge
```

### 2. Create and Activate a Virtual Environment (Recommended)
```
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Set Up OpenAI API Key
- Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Initialize the Notes Database
- The app will auto-create the SQLite database (`db/notes.db`) on first run.

---

## Running the App

```
streamlit run app/ui/streamlit_app.py
```
- The app will open in your browser at [http://localhost:8501](http://localhost:8501)

---

## Project Structure

```
Rick_Morty_AI_Challenge/
├── app/
│   ├── api/                # Rick & Morty API client
│   ├── evaluation/         # Summary evaluation logic
│   ├── llm/                # LLM and embeddings services
│   ├── persistence/        # Notes repository (SQLite)
│   └── ui/                 # Streamlit UI
├── db/                     # SQLite database for notes
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
└── ...
```

---

## Usage Tips
- **Location Selection:** Use the dropdown to pick a location.
- **Add Notes:** Expand a character, write a note, and click "Save Note".
- **AI Summary:** Click "Generate AI Summary" for an LLM-generated summary and evaluation.
- **Semantic Search:** Enter a query in the search bar to find relevant characters (details + notes). Only relevant results are shown.
- **LLM Judge:** See independent LLM-based scores and verdicts for summaries.

---

## Troubleshooting
- If you see connection errors, check your internet and VPN/proxy settings.
- Make sure your OpenAI API key is valid and has quota.
- If you change the code, restart the Streamlit app to see updates.

---

## License
MIT License. See LICENSE file for details.

---

## Credits
- [Rick and Morty API](https://rickandmortyapi.com/)
- [OpenAI](https://openai.com/)
- Built with Python, Streamlit, and SQLite.

