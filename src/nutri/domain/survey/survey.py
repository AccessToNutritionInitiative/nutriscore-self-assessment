from dataclasses import dataclass
from pathlib import Path

RECOMMANDATIONS_DIR = Path(__file__).parent / "recommandations"


@dataclass
class Recommandation:
    question: str
    question_text: str
    score: str
    content: str


def get_recommandation(question: str, score: float) -> Recommandation | None:
    """Return the recommendation for a given question and score."""
    score_part = str(int(score)) if score == int(score) else str(score).replace(".", "_")
    filepath = RECOMMANDATIONS_DIR / f"q{question}_score_{score_part}.md"

    if not filepath.exists():
        return None

    text = filepath.read_text()
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None

    frontmatter = {}
    for line in parts[1].strip().splitlines():
        key, _, value = line.partition(":")
        frontmatter[key.strip()] = value.strip().strip('"')

    return Recommandation(
        question=frontmatter.get("question", question),
        question_text=frontmatter.get("question_text", ""),
        score=frontmatter.get("score", str(score)),
        content=parts[2].strip(),
    )
