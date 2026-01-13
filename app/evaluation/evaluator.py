"""Evaluation helpers."""


class Evaluator:

    def evaluate(self, summary, location):
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
