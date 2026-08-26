PRIVATE_ORDER_TERMS = {
    "email",
    "email address",
    "shipping address",
    "home address",
    "risk score",
    "warehouse note",
    "warehouse instruction",
    "internal note",
    "internal notes",
    "support tags",
    "fraud score",
}


SECURITY_REQUEST_TERMS = {
    "system prompt",
    "hidden instructions",
    "hidden prompt",
    "secret",
    "api key",
    "api keys",
    "credentials",
    "developer instructions",
    "developer message",
    "system instructions",
}


def requests_private_order_data(
    message: str,
) -> bool:

    lower = message.lower()

    return any(
        term in lower
        for term in PRIVATE_ORDER_TERMS
    )


def requests_protected_information(
    message: str,
) -> bool:

    lower = message.lower()

    return any(
        term in lower
        for term in SECURITY_REQUEST_TERMS
    )


def contains_migration_policy_request(
    message: str,
) -> bool:

    lower = message.lower()

    migration_terms = [
        "migration note",
        "migration",
        "ignore the current return policy",
        "ignore the real policy",
        "give everyone 60 days",
        "give everyone 60 days",
        "60-day policy",
        "60 days",
    ]

    return any(
        term in lower
        for term in migration_terms
    )