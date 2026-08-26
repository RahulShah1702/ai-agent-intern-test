from app.session import SessionManager


manager = SessionManager()


session = manager.get_or_create(
    "customer-1"
)

session.add_user_message(
    "Where is ORD-1007?"
)

session.add_assistant_message(
    "Your order has shipped via UPS."
)

session.add_user_message(
    "When will it arrive?"
)


print("SESSION 1")
print(session.recent_history())


session_2 = manager.get_or_create(
    "customer-2"
)

session_2.add_user_message(
    "Do you ship internationally?"
)


print("\nSESSION 2")
print(session_2.recent_history())


print("\nSESSION 1 AGAIN")
print(session.recent_history())