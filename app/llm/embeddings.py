"""Embeddings utilities."""

import openai
import numpy as np


class EmbeddingService:

    def embed(self, text):
        # openai>=1.0.0 embedding API
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=[text]
        )
        return np.array(response.data[0].embedding)

    def cosine_similarity(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
