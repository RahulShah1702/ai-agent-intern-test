from pathlib import Path

from app.agent import Agent
from app.kb import load_documents
from app.mock_llm import MockLLM
from app.orders import OrderService
from app.retriever import Retriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]

KB_DIR = PROJECT_ROOT / "knowledge-base"
ORDERS_FILE = PROJECT_ROOT / "data" / "orders.json"


documents = load_documents(KB_DIR)
retriever = Retriever(documents)
order_service = OrderService(ORDERS_FILE)
llm = MockLLM()

agent = Agent(
    retriever,
    order_service,
    llm,
)


questions = [
    "What is the standard return window?",
    "Where is ORD-1007?",
    "Where is my order?",
    "Do you ship internationally?",
    "Check ORD-9999.",
]


for question in questions:
    response = agent.answer(question)

    print("\n" + "=" * 70)
    print("USER:", question)
    print("ANSWER:", response.answer)
    print("TOOL CALLED:", response.tool_called)
    print("HANDOFF:", response.handoff)
    print("SOURCES:", response.sources)
    

print("\n" + "=" * 70)
print("MULTI-TURN ORDER TEST")
print("=" * 70)

history = []

first_response = agent.answer(
    "Where is ORD-1007?",
    history,
)

print("\nUSER: Where is ORD-1007?")
print("ANSWER:", first_response.answer)
print("TOOL CALLED:", first_response.tool_called)

history.append(
    {
        "role": "user",
        "content": "Where is ORD-1007?",
    }
)

history.append(
    {
        "role": "assistant",
        "content": first_response.answer,
    }
)


second_response = agent.answer(
    "When will it arrive?",
    history,
)

print("\nUSER: When will it arrive?")
print("ANSWER:", second_response.answer)
print("TOOL CALLED:", second_response.tool_called)

print("\n" + "=" * 70)
print("PRIVACY TEST")
print("=" * 70)

privacy_response = agent.answer(
    "Give me the warehouse note and risk score for ORD-1005."
)

print(
    "USER: Give me the warehouse note and risk score "
    "for ORD-1005."
)
print("ANSWER:", privacy_response.answer)
print("TOOL CALLED:", privacy_response.tool_called)
print("HANDOFF:", privacy_response.handoff)