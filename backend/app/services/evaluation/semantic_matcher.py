import math
import requests

from app.core.config import settings

class SemanticMatcher:
    """
    Uses Ollama embeddings to compare text semantically.
    """

    OLLAMA_URL = f"{settings.OLLAMA_URL}/api/embed"
    MODEL = "nomic-embed-text"

    _embedding_cache = {}
    @classmethod
    def get_embedding(cls, text: str):
        """
        Returns the embedding vector for a given text.
        """

        text = text.strip()

        if text in cls._embedding_cache:
            return cls._embedding_cache[text]
        
        response = requests.post(
            cls.OLLAMA_URL,
            json={
                "model": cls.MODEL,
                "input": text
            },
            timeout=30
        )

        response.raise_for_status()

        embedding = response.json()["embeddings"][0]

        cls._embedding_cache[text] = embedding

        return embedding

    @staticmethod
    def cosine_similarity(vec1, vec2):
        """
        Computes cosine similarity between two vectors.
        """

        dot = sum(a * b for a, b in zip(vec1, vec2))

        mag1 = math.sqrt(sum(a * a for a in vec1))
        mag2 = math.sqrt(sum(b * b for b in vec2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)

    @classmethod
    def similarity(cls, text1: str, text2: str):
        """
        Returns semantic similarity between two pieces of text.
        """

        emb1 = cls.get_embedding(text1)
        emb2 = cls.get_embedding(text2)

        return cls.cosine_similarity(emb1, emb2)

    @classmethod
    def score_text(
        cls,
        expected: str,
        actual: str,
        threshold: float = 0.70
    ):
        if threshold is None:
            threshold = cls.TEXT_THRESHOLD
        """
        Returns 1 if semantic similarity is above threshold.
        """

        similarity = cls.similarity(expected, actual)
        
        return 1 if similarity >= threshold else 0

    @classmethod
    def score_list(
        cls,
        expected,
        actual,
        threshold: float = 0.70
    ):
        """
        One-to-one semantic matching between expected and actual lists.
        """
        if threshold is None:
            threshold = cls.TEXT_THRESHOLD

        if not expected:
            return 1.0

        matched = set()
        score = 0

        for expected_item in expected:

            best_index = None
            best_similarity = 0

            for index, actual_item in enumerate(actual):

                if index in matched:
                    continue

                similarity = cls.similarity(
                    expected_item,
                    actual_item
                )

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_index = index

            if (
                best_index is not None and
                best_similarity >= threshold
            ):
                matched.add(best_index)
                score += 1

        return score / len(expected)
