from pathlib import Path

from app.evidence import assess_evidence
from app.kb import load_documents
from app.retriever import Retriever


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_DIR = PROJECT_ROOT / "knowledge-base"


documents = load_documents(KB_DIR)
retriever = Retriever(documents)


queries = [
    "What is the standard return window?",
    "Is the Breeze Tumbler dishwasher safe?",
    "Are all bags and adhesives vegan?",
]


for query in queries:
    results = retriever.search(
        query,
        top_k=5,
    )

    assessment = assess_evidence(
        query,
        results,
    )

    print("\n" + "=" * 70)
    print("QUERY:", query)
    print("SUFFICIENT:", assessment.sufficient)
    print("CONFLICT:", assessment.has_conflict)
    print("REASON:", assessment.reason)

    print("\nRETRIEVED SOURCES:")

    for result in results:
        print(
            f"- {result.document.filename} "
            f"| {result.document.heading} "
            f"| {result.final_score:.3f}"
        )