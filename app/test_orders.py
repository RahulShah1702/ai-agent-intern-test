from pathlib import Path

from app.orders import (
    OrderService,
    extract_order_id,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ORDERS_FILE = PROJECT_ROOT / "data" / "orders.json"


order_service = OrderService(ORDERS_FILE)


def show_result(label: str, result: dict):
    print("\n" + "=" * 70)
    print(label)
    print("=" * 70)

    for key, value in result.items():
        print(f"{key}: {value}")


# Test 1: normal lookup
result = order_service.lookup("ORD-1001")
show_result("ORD-1001", result)


# Test 2: harmless lowercase input
result = order_service.lookup(" ord-1001 ")
show_result("lowercase + whitespace", result)


# Test 3: unknown order
result = order_service.lookup("ORD-9999")
show_result("unknown order", result)


# Test 4: malformed order ID
result = order_service.lookup("ABC123")
show_result("malformed order", result)


# Test 5: order ID extraction
messages = [
    "Where is ORD-1007?",
    "check ord-1007 please",
    "Can you track ORD-9999?",
    "I need help with my order",
]

print("\n" + "=" * 70)
print("ORDER ID EXTRACTION")
print("=" * 70)

for message in messages:
    print(
        f"{message!r} -> "
        f"{extract_order_id(message)}"
    )
    
# Test 6: cancelled order must not expose stale delivery fields
result = order_service.lookup("ORD-1004")
show_result("cancelled order", result)

assert result["found"] is True
assert result["status"] == "cancelled"
assert "carrier" not in result
assert "tracking_number" not in result
assert "estimated_delivery" not in result


# Test 7: returned order must not expose stale delivery fields
result = order_service.lookup("ORD-1008")
show_result("returned order", result)

assert result["found"] is True
assert result["status"] == "returned"
assert "carrier" not in result
assert "tracking_number" not in result
assert "estimated_delivery" not in result

# Test 8: shipped order with no ETA
result = order_service.lookup("ORD-1011")
show_result("shipped without ETA", result)

assert result["found"] is True
assert result["status"] == "shipped"
assert result["carrier"] == "Canada Post"
assert "estimated_delivery" not in result