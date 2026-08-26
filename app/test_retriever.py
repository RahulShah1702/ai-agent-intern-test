from pathlib import Path

from app.kb import load_documents
from app.retriever import Retriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_DIR = PROJECT_ROOT / "knowledge-base"


documents = load_documents(KB_DIR)

retriever = Retriever(documents)


queries = [
    "What is the standard return window?",
    "Do you ship internationally?",
    "What is the warranty period?",
    "What does the migration note say about the return policy?",
    "Is the Breeze Tumbler dishwasher safe?",
]


for query in queries:
    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = retriever.search(
        query,
        top_k=3,
    )

    for rank, result in enumerate(
        results,
        start=1,
    ):
        document = result.document

        print(f"\n#{rank}")
        print("Filename:", document.filename)
        print("Heading:", document.heading)
        print("Status:", document.status)
        print(
            "Authority:",
            document.policy_authority,
        )
        print(
            "Text score:",
            round(result.text_score, 4),
        )
        print(
            "Final score:",
            round(result.final_score, 4),
        )
        print(
            "Text:",
            document.text[:250],
        )