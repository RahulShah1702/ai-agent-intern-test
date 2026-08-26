from dataclasses import dataclass, field


@dataclass
class Session:
    session_id: str
    history: list[dict] = field(default_factory=list)

    def add_user_message(self, message: str):
        self.history.append(
            {
                "role": "user",
                "content": message,
            }
        )

    def add_assistant_message(self, message: str):
        self.history.append(
            {
                "role": "assistant",
                "content": message,
            }
        )

    def recent_history(
        self,
        limit: int = 6,
    ) -> list[dict]:
        return self.history[-limit:]


class SessionManager:
    def __init__(self):
        self.sessions: dict[str, Session] = {}

    def get_or_create(
        self,
        session_id: str,
    ) -> Session:

        if session_id not in self.sessions:
            self.sessions[session_id] = Session(
                session_id=session_id
            )

        return self.sessions[session_id]