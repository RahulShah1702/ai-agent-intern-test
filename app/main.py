import uuid
import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from .agent import Agent
from .kb import load_documents
from .llm import GeminiLLM
from .orders import OrderService
from .retriever import Retriever
from .logging_config import configure_logging
from .session import SessionManager


load_dotenv()
configure_logging()

logger = logging.getLogger("aster-agent")

ROOT = Path(__file__).resolve().parents[1]

KB_DIR = ROOT / "knowledge-base"
ORDERS_FILE = ROOT / "data" / "orders.json"


documents = load_documents(KB_DIR)
retriever = Retriever(documents)
order_service = OrderService(ORDERS_FILE)

# Live application uses Gemini.
llm = GeminiLLM()

agent = Agent(
    retriever,
    order_service,
    llm,
)

sessions = SessionManager()

app = FastAPI(
    title="Aster & Row Support Agent"
)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


@app.get("/health")
def health():
    return {
        "status": "ok",
        "documents": len(documents),
    }


@app.post("/chat")
def chat(request: ChatRequest):
    session_id = (
        request.session_id
        or str(uuid.uuid4())
    )

    session = sessions.get_or_create(
        session_id
    )

    logger.info(
        "user_message session=%s message=%s",
        session_id,
        request.message,
    )

    history = session.recent_history()

    response = agent.answer(
        request.message,
        history,
    )

    session.add_user_message(
        request.message
    )

    session.add_assistant_message(
        response.answer
    )

    logger.info(
        "agent_response session=%s intent=%s "
        "tool_called=%s handoff=%s",
        session_id,
        response.intent,
        response.tool_called,
        response.handoff,
    )

    return {
        "session_id": session_id,
        "answer": response.answer,
        "sources": response.sources,
        "handoff": response.handoff,
        "intent": response.intent,
        "tool_called": response.tool_called,
    }