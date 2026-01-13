"""Embeddings utilities."""

import openai
import numpy as np


class EmbeddingService:

    def embed(self, text):
        response = openai.Embedding.create(
            model="text-embedding-3-small",
            input=text
        )
        return np.array(response["data"][0]["embedding"])

    def cosine_similarity(self, a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
