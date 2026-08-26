import json
import re
from pathlib import Path


ORDER_ID_PATTERN = re.compile(
    r"\bORD-\d{4}\b",
    re.IGNORECASE,
)


class OrderService:
    def __init__(self, orders_file: Path):
        self.orders = self._load_orders(orders_file)

    def _load_orders(self, orders_file: Path) -> dict:
        with orders_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return {
            order["order_id"].upper(): order
            for order in data["orders"]
        }

    def lookup(self, order_id: str) -> dict:
        """
        Look up one order and return only customer-safe information.
        """

        normalized_id = order_id.strip().upper()

        # Validate the expected order-ID format first.
        if not ORDER_ID_PATTERN.fullmatch(normalized_id):
            return {
                "found": False,
                "reason": "malformed_order_id",
            }

        order = self.orders.get(normalized_id)

        if order is None:
            return {
                "found": False,
                "reason": "not_found",
                "order_id": normalized_id,
            }

        status = order["status"]

        result = {
            "found": True,
            "order_id": normalized_id,
            "status": status,
            "customer_safe_message": order.get(
                "customer_safe_message"
            ),
        }

        # Cancelled and returned orders can contain old delivery
        # fields. Do not expose those stale fields.
        if status in {"cancelled", "returned"}:
            return result

        # Only include fields that actually exist.
        # We never invent an ETA or tracking information.
        if order.get("carrier"):
            result["carrier"] = order["carrier"]

        if order.get("tracking_number"):
            result["tracking_number"] = order[
                "tracking_number"
            ]

        if order.get("estimated_delivery"):
            result["estimated_delivery"] = order[
                "estimated_delivery"
            ]

        return result


def extract_order_id(text: str) -> str | None:
    """
    Find an order ID inside a customer's message.

    Examples:
        "Where is ORD-1007?" -> "ORD-1007"
        "check ord-1007 please" -> "ORD-1007"
    """

    match = ORDER_ID_PATTERN.search(text)

    if match is None:
        return None

    return match.group(0).upper()

def extract_latest_order_id_from_history(
    history: list[dict],
) -> str | None:

    for message in reversed(history):
        content = message.get(
            "content",
            "",
        )

        order_id = extract_order_id(content)

        if order_id:
            return order_id

    return None