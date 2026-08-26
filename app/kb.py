from dataclasses import dataclass
from pathlib import Path
import re

import yaml


@dataclass
class DocumentChunk:
    filename: str
    title: str
    status: str
    effective_date: str
    audience: str
    policy_authority: str
    supersedes: str | None
    heading: str
    text: str


def parse_front_matter(content: str) -> tuple[dict, str]:
    """
    Separate YAML front matter from the Markdown body.

    Expected format:

    ---
    status: active
    ...
    ---

    # Heading

    Content...
    """

    if not content.startswith("---"):
        return {}, content.strip()

    parts = content.split("---", 2)

    if len(parts) != 3:
        return {}, content.strip()

    front_matter = parts[1]
    body = parts[2].strip()

    metadata = yaml.safe_load(front_matter) or {}

    if not isinstance(metadata, dict):
        metadata = {}

    return metadata, body


def split_into_sections(body: str) -> list[tuple[str, str]]:
    """
    Split a Markdown document into heading + text sections.

    Example:

    # Return Window
    30 days...

    # Refunds
    Refunds are...

    becomes:

    [
        ("Return Window", "30 days..."),
        ("Refunds", "Refunds are...")
    ]
    """

    sections = []

    current_heading = "Document"
    current_lines = []

    for line in body.splitlines():
        heading_match = re.match(r"^#{1,3}\s+(.+)$", line)

        if heading_match:
            if current_lines:
                text = "\n".join(current_lines).strip()

                if text:
                    sections.append(
                        (current_heading, text)
                    )

            current_heading = heading_match.group(1).strip()
            current_lines = []

        else:
            current_lines.append(line)

    if current_lines:
        text = "\n".join(current_lines).strip()

        if text:
            sections.append(
                (current_heading, text)
            )

    return sections


def load_documents(kb_dir: Path) -> list[DocumentChunk]:
    """
    Read all Markdown files in the knowledge base
    and convert them into searchable document chunks.
    """

    documents = []

    for file_path in sorted(kb_dir.glob("*.md")):
        content = file_path.read_text(
            encoding="utf-8"
        )

        metadata, body = parse_front_matter(content)

        title = metadata.get(
            "title",
            file_path.stem
        )

        status = str(
            metadata.get("status", "unknown")
        )

        effective_date = str(
            metadata.get("effective_date", "")
        )

        audience = str(
            metadata.get("audience", "unknown")
        )

        policy_authority = str(
            metadata.get(
                "policy_authority",
                "unknown"
            )
        )

        supersedes = metadata.get("supersedes")

        sections = split_into_sections(body)

        for heading, text in sections:
            documents.append(
                DocumentChunk(
                    filename=file_path.name,
                    title=title,
                    status=status,
                    effective_date=effective_date,
                    audience=audience,
                    policy_authority=policy_authority,
                    supersedes=supersedes,
                    heading=heading,
                    text=text,
                )
            )

    return documents