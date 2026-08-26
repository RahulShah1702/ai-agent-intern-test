from pathlib import Path

from dotenv import load_dotenv

from .agent import Agent
from .kb import load_documents
from .llm import GeminiLLM
from .orders import OrderService
from .retriever import Retriever
from .session import SessionManager


load_dotenv()

ROOT = Path(__file__).resolve().parents[1]

KB_DIR = ROOT / "knowledge-base"
ORDERS_FILE = ROOT / "data" / "orders.json"


documents = load_documents(KB_DIR)
retriever = Retriever(documents)
order_service = OrderService(ORDERS_FILE)
llm = GeminiLLM()

agent = Agent(
    retriever,
    order_service,
    llm,
)

sessions = SessionManager()
session = sessions.get_or_create("demo-session")


print("=" * 70)
print("ASTER & ROW CUSTOMER SUPPORT AGENT")
print("=" * 70)
print("Type 'exit' to quit.\n")


while True:
    message = input("You: ").strip()

    if not message:
        continue

    if message.lower() in {"exit", "quit"}:
        print("\nGoodbye!")
        break

    response = agent.answer(
        message,
        session.recent_history(),
    )

    session.add_user_message(message)
    session.add_assistant_message(response.answer)

    print(f"\nAgent: {response.answer}")

    if response.sources:
        print("\nSources:")
        for source in response.sources:
            print(
                f"- {source['filename']} — "
                f"{source['heading']}"
            )

    if response.handoff:
        print("\n⚠ Human handoff recommended.")

    print(
        f"\nIntent: {response.intent}"
        f" | Tool called: {response.tool_called}"
    )

    print("-" * 70)