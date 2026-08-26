import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]

# Make the project root importable when this file is
# executed as a module.
sys.path.insert(0, str(ROOT))

from app.agent import Agent
from app.kb import load_documents
from app.mock_llm import MockLLM
from app.orders import OrderService
from app.retriever import Retriever


KB_DIR = ROOT / "knowledge-base"
ORDERS_FILE = ROOT / "data" / "orders.json"
VISIBLE_CASES = ROOT / "evaluation" / "visible-cases.json"
CUSTOM_CASES = ROOT / "evaluation" / "custom-cases.json"


def build_agent():
    documents = load_documents(KB_DIR)

    retriever = Retriever(documents)

    order_service = OrderService(
        ORDERS_FILE
    )

    llm = MockLLM()

    return Agent(
        retriever,
        order_service,
        llm,
    )


def load_cases(path):
    data = json.loads(
        path.read_text(encoding="utf-8")
    )

    # The supplied visible file contains the cases
    # under a "cases" key.
    if isinstance(data, dict):
        return data.get("cases", [])

    return data


def run_case(agent, case):
    history = []
    responses = []

    for message in case["messages"]:
        response = agent.answer(
            message["content"],
            history,
        )

        responses.append(response)

        history.append(
            {
                "role": "user",
                "content": message["content"],
            }
        )

        history.append(
            {
                "role": "assistant",
                "content": response.answer,
            }
        )

    final = responses[-1]
    expected = case.get("expect", {})

    failures = []

    # ---------------------------------------------------------
    # Basic answer assertions
    # ---------------------------------------------------------

    answer = final.answer.lower()

    for phrase in expected.get(
        "must_include",
        [],
    ):
        if phrase.lower() not in answer:
            failures.append(
                f"Missing text: {phrase}"
            )

    for phrase in expected.get(
        "must_not_include",
        [],
    ):
        if phrase.lower() in answer:
            failures.append(
                f"Forbidden text: {phrase}"
            )

    # ---------------------------------------------------------
    # Tool assertions
    # ---------------------------------------------------------

    if "tool_called" in expected:
        if (
            final.tool_called
            != expected["tool_called"]
        ):
            failures.append(
                "Unexpected tool_called value: "
                f"{final.tool_called}"
            )

    # ---------------------------------------------------------
    # Handoff assertions
    # ---------------------------------------------------------

    if "handoff" in expected:
        if (
            final.handoff
            != expected["handoff"]
        ):
            failures.append(
                "Unexpected handoff value: "
                f"{final.handoff}"
            )

    # ---------------------------------------------------------
    # Source assertions
    # ---------------------------------------------------------

    source_names = {
        source["filename"]
        for source in final.sources
    }

    for required_source in expected.get(
        "required_sources",
        [],
    ):
        if required_source not in source_names:
            failures.append(
                f"Missing source: {required_source}"
            )

    # ---------------------------------------------------------
    # Multi-turn tool assertion
    # ---------------------------------------------------------

    if expected.get(
        "second_turn_tool_called"
    ):
        if len(responses) < 2:
            failures.append(
                "Expected at least two turns."
            )
        elif not responses[1].tool_called:
            failures.append(
                "Second turn did not call the order tool."
            )

    return {
        "id": case["id"],
        "category": case.get(
            "category",
            "uncategorized",
        ),
        "passed": not failures,
        "failures": failures,
    }


def print_results(results):
    print("\n" + "=" * 75)
    print("ASTER & ROW AGENT EVALUATION")
    print("=" * 75)

    for result in results:
        status = (
            "PASS"
            if result["passed"]
            else "FAIL"
        )

        print(
            f"[{status}] "
            f"{result['id']} "
            f"({result['category']})"
        )

        for failure in result["failures"]:
            print(
                f"       - {failure}"
            )

    print("\n" + "-" * 75)

    passed = sum(
        result["passed"]
        for result in results
    )

    total = len(results)

    print(
        f"Overall: {passed}/{total} cases passed"
    )

    print("\nCategory results:")

    categories = {}

    for result in results:
        category = result["category"]

        categories.setdefault(
            category,
            {
                "passed": 0,
                "total": 0,
            },
        )

        categories[category]["total"] += 1

        if result["passed"]:
            categories[category]["passed"] += 1

    for category, stats in sorted(
        categories.items()
    ):
        print(
            f"  {category}: "
            f"{stats['passed']}/"
            f"{stats['total']}"
        )


def main():
    agent = build_agent()

    visible_cases = load_cases(
        VISIBLE_CASES
    )

    custom_cases = load_cases(
        CUSTOM_CASES
    )

    all_cases = (
        visible_cases
        + custom_cases
    )

    results = []

    for case in all_cases:
        results.append(
            run_case(agent, case)
        )

    print_results(results)


if __name__ == "__main__":
    main()