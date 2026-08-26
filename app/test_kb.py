from pathlib import Path

from app.kb import load_documents


PROJECT_ROOT = Path(__file__).resolve().parents[1]
KB_DIR = PROJECT_ROOT / "knowledge-base"


documents = load_documents(KB_DIR)

print(f"Loaded chunks: {len(documents)}")

for document in documents[:5]:
    print("\n---")
    print("Filename:", document.filename)
    print("Title:", document.title)
    print("Status:", document.status)
    print("Authority:", document.policy_authority)
    print("Heading:", document.heading)
    print("Text:", document.text[:200])