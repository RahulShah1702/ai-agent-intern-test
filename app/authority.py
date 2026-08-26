def authority_score(document) -> float:
    score = 0.0

    if document.status == "active":
        score += 1.0

    if document.policy_authority == "official":
        score += 1.0

    if document.audience == "customer":
        score += 0.5

    if document.status in {"superseded", "legacy"}:
        score -= 2.0

    if document.audience == "internal":
        score -= 3.0

    return score

def select_authoritative_results(results, limit=5):
    ranked = sorted(
        results,
        key=lambda result: (
            authority_score(result.document),
            result.final_score,
        ),
        reverse=True,
    )

    return ranked[:limit]