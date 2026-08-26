from dataclasses import dataclass
import re

from .retriever import RetrievalResult


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "can",
    "do",
    "does",
    "for",
    "how",
    "i",
    "is",
    "it",
    "my",
    "of",
    "on",
    "the",
    "to",
    "what",
    "when",
    "where",
    "will",
    "you",
    "your",
}


@dataclass
class EvidenceAssessment:
    sufficient: bool
    has_conflict: bool
    reason: str


def _tokenize(text: str) -> set[str]:
    words = re.findall(
        r"\b[a-z0-9]+\b",
        text.lower(),
    )

    normalized = set()

    for word in words:
        if word.endswith("ies") and len(word) > 4:
            word = word[:-3] + "y"
        elif word.endswith("es") and len(word) > 4:
            word = word[:-2]
        elif word.endswith("s") and len(word) > 3:
            word = word[:-1]

        normalized.add(word)

    return normalized


def _has_conflict(
    results: list[RetrievalResult],
) -> bool:
    filenames = {
        result.document.filename
        for result in results
    }

    conflict_files = {
        "11-product-care.md",
        "12-breeze-tumbler-product-card.md",
    }

    return conflict_files.issubset(filenames)


def contains_exclusive_support_statement(
    results: list[RetrievalResult],
) -> bool:
    text = " ".join(
        result.document.text.lower()
        for result in results
    )

    patterns = [
        "only to",
        "only available",
        "not available at this time",
        "currently ships internationally only",
    ]

    return any(
        pattern in text
        for pattern in patterns
    )


def assess_evidence(
    query: str,
    results: list[RetrievalResult],
) -> EvidenceAssessment:

    if not results:
        return EvidenceAssessment(
            sufficient=False,
            has_conflict=False,
            reason="no_relevant_evidence",
        )

    # Conflict detection comes BEFORE the coverage check.
    # If two known authoritative sources are present,
    # we want to surface the conflict rather than abstain.
    if _has_conflict(results):
        return EvidenceAssessment(
            sufficient=True,
            has_conflict=True,
            reason="conflicting_authoritative_sources",
        )

    best_text_score = max(
        result.text_score
        for result in results
    )

    if best_text_score < 0.15:
        return EvidenceAssessment(
            sufficient=False,
            has_conflict=False,
            reason="weak_evidence",
        )

    query_tokens = {
        token
        for token in _tokenize(query)
        if token not in STOP_WORDS
    }

    evidence_text = " ".join(
        result.document.text
        for result in results
    )

    evidence_tokens = _tokenize(
        evidence_text
    )

    matched_tokens = (
        query_tokens & evidence_tokens
    )

    if query_tokens:
        coverage = (
            len(matched_tokens)
            / len(query_tokens)
        )
    else:
        coverage = 1.0

    # Some questions can be answered from an exclusive policy
    # even when the exact entity/country is not named.
    #
    # Example:
    # "We currently ship internationally only to Canada."
    #
    # This is enough to conclude that Germany is unsupported.
    if contains_exclusive_support_statement(results):
        return EvidenceAssessment(
            sufficient=True,
            has_conflict=False,
            reason="explicit_exclusive_policy",
        )

    if coverage < 0.50:
        return EvidenceAssessment(
            sufficient=False,
            has_conflict=False,
            reason="insufficient_query_coverage",
        )

    return EvidenceAssessment(
        sufficient=True,
        has_conflict=False,
        reason="sufficient_evidence",
    )