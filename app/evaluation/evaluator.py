"""Evaluation helpers."""



class Evaluator:
    def rule_based_evaluate(self, summary, location):
        """Rule-based evaluation (original logic)."""
        factual = 5 if location["name"] in summary else 3
        creativity = min(5, max(3, len(summary) // 200))
        completeness = 5 if str(len(location["residents"])) in summary else 3
        final_score = (
            factual * 0.4 +
            creativity * 0.3 +
            completeness * 0.3
        )
        return {
            "factual": factual,
            "creativity": creativity,
            "completeness": completeness,
            "final_score": round(final_score, 2)
        }

    def semantic_similarity_evaluate(self, summary, source_text):
        """Semantic similarity between summary and source text using embeddings."""
        from app.llm.embeddings import EmbeddingService
        embedding_service = EmbeddingService()
        summary_emb = embedding_service.embed(summary)
        source_emb = embedding_service.embed(source_text)
        similarity = embedding_service.cosine_similarity(summary_emb, source_emb)
        # Map similarity to a 1-5 scale for each metric (simple mapping)
        score = int(1 + 4 * similarity)
        return {
            "factual": score,
            "creativity": score,
            "completeness": score,
            "similarity": similarity,
            "final_score": round(score, 2)
        }

    def llm_judge_evaluate(self, summary, location):
        """Use LLM as a judge to score factual, creativity, completeness."""
        from app.llm.llm_service import LLMService
        llm = LLMService()
        prompt = f"""
You are an expert evaluator. Given the following location data and a summary, rate the summary on a scale of 1-5 for factual accuracy, creativity, and completeness. Return a JSON object with keys: factual, creativity, completeness.

Location: {location}
Summary: {summary}
"""
        import openai
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        import json
        try:
            scores = json.loads(response.choices[0].message.content)
        except Exception:
            # fallback if LLM output is not valid JSON
            scores = {"factual": 3, "creativity": 3, "completeness": 3}
        final_score = (
            scores.get("factual", 3) * 0.4 +
            scores.get("creativity", 3) * 0.3 +
            scores.get("completeness", 3) * 0.3
        )
        scores["final_score"] = round(final_score, 2)
        return scores

    def compare_evaluations(self, summary, location, source_text):
        """Run all three evaluation techniques and compare results."""
        rule = self.rule_based_evaluate(summary, location)
        semantic = self.semantic_similarity_evaluate(summary, source_text)
        llm = self.llm_judge_evaluate(summary, location)
        return {
            "rule_based": rule,
            "semantic_similarity": semantic,
            "llm_judge": llm
        }
