
from app.llm.embeddings import EmbeddingService
import numpy as np

class Evaluator:
    def __init__(self):
        self.embedding_service = EmbeddingService()

    def score_factual(self, summary, location):
        # Simple heuristic: location name and resident names present
        score = 3
        if location["name"] in summary:
            score += 1
        if location.get("residents"):
            covered = sum(1 for r in location["residents"] if r in summary)
            if covered > 0:
                score += 1
        return min(score, 5)

    def score_creativity(self, summary):
        # Heuristic: variance in sentence length
        sentences = [s.strip() for s in summary.split('.') if s.strip()]
        if not sentences:
            return 3
        lengths = [len(s.split()) for s in sentences]
        variance = np.var(lengths)
        return min(5, max(3, int(3 + variance // 5)))

    def score_completeness(self, summary, location):
        # Heuristic: mentions of all key facts
        score = 3
        if location.get("type") and location["type"] in summary:
            score += 1
        if location.get("dimension") and location["dimension"] in summary:
            score += 1
        return min(score, 5)

    def semantic_similarity(self, summary, residents):
        # Embedding-based similarity between summary and all character details for the location (no notes)
        if not residents:
            return 0.0
        # Concatenate all character details (name, status, species, gender, origin, location, episodes)
        details = []
        for r in residents:
            c = r["character"]
            details.append(
                f"Name: {c.get('name', '-')}, Status: {c.get('status', '-')}, Species: {c.get('species', '-')}, "
                f"Gender: {c.get('gender', '-')}, Origin: {(c.get('origin') or {}).get('name', '-')}, "
                f"Current location: {(c.get('location') or {}).get('name', '-')}, Episodes: {len(c.get('episode') or [])}"
            )
        all_details = " ".join(details)
        emb1 = self.embedding_service.embed(summary)
        emb2 = self.embedding_service.embed(all_details)
        return float(self.embedding_service.cosine_similarity(emb1, emb2))

    def rubric_evaluation(self, summary, location):
        # Prompt-based rubric (simple heuristic)
        rubric = {
            "factual": self.score_factual(summary, location),
            "creativity": self.score_creativity(summary),
            "completeness": self.score_completeness(summary, location)
        }
        rubric["final_score"] = round(
            rubric["factual"] * 0.4 + rubric["creativity"] * 0.3 + rubric["completeness"] * 0.3, 2
        )
        return rubric

    def evaluate(self, summary, location, residents=None):
        # Modular evaluation: rubric + semantic similarity
        rubric = self.rubric_evaluation(summary, location)
        sim = self.semantic_similarity(summary, residents or [])
        rubric["semantic_similarity"] = round(sim, 3)
        return rubric
