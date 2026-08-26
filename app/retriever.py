from dataclasses import dataclass
import re

from sklearn.feature_extraction.text import TfidfVectorizer

from .kb import DocumentChunk



@dataclass
class RetrievalResult:
    document: DocumentChunk
    text_score: float
    final_score: float


class Retriever:
    def __init__(self, documents: list[DocumentChunk]):
        self.documents = documents

        # We create one searchable text string for each chunk.
        self.corpus = [
            f"{document.title}\n"
            f"{document.heading}\n"
            f"{document.heading}\n"
            f"{document.text}"
            for document in documents
        ]

        # TF-IDF converts text into numerical vectors.
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )

        self.matrix = self.vectorizer.fit_transform(
            self.corpus
        )

    def _tokenize(self, text: str) -> set[str]:
        return set(
            re.findall(
                r"\b[a-z0-9]+\b",
                text.lower(),
            )
        )
        
    def _metadata_bonus(self, document: DocumentChunk) -> float:
        """
        Adjust the text similarity score using document metadata.

        Higher score = more trustworthy for customer answers.
        """

        bonus = 0.0

        # Current documents should be preferred.
        if document.status == "active":
            bonus += 0.25

        # Official policies should be preferred.
        if document.policy_authority == "official":
            bonus += 0.30

        # Customer-facing information is more relevant to a
        # customer-support question than internal material.
        if document.audience == "customer":
            bonus += 0.10

        # Superseded/legacy content should be penalized.
        if document.status in {"superseded", "legacy"}:
            bonus -= 0.50

        # Internal documents should be strongly penalized.
        if document.audience == "internal":
            bonus -= 0.80

        return bonus

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[RetrievalResult]:

        # Convert the user's question into the same numerical
        # representation used for our document chunks.
        query_vector = self.vectorizer.transform([query])

        # Compare the query against every document chunk.
        similarities = (
            self.matrix @ query_vector.T
        ).toarray().ravel()

        results = []

        for index, text_score in enumerate(similarities):
            document = self.documents[index]

            text_score = float(text_score)

            if text_score <= 0:
                final_score = 0.0
            else:
                metadata_bonus = self._metadata_bonus(document)

                query_words = self._tokenize(query)
                heading_words = self._tokenize(
                    document.heading
                )

                heading_overlap = (
                    len(query_words & heading_words)
                    / max(len(query_words), 1)
                )

                heading_bonus = 0.20 * heading_overlap

                final_score = (
                    text_score
                    + metadata_bonus
                    + heading_bonus
                )

            results.append(
                RetrievalResult(
                    document=document,
                    text_score=text_score,
                    final_score=final_score,
                )
            )

        # Highest final score first.
        results.sort(
            key=lambda result: result.final_score,
            reverse=True,
        )

        relevant_results = [
            result
            for result in results
            if result.text_score > 0
        ]

        return relevant_results[:top_k]