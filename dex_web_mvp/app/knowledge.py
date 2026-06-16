from pathlib import Path

KB_DIR = Path("app/knowledge_base")
KB_DIR.mkdir(parents=True, exist_ok=True)


def load_knowledge() -> str:
    parts = []
    for path in sorted(KB_DIR.glob("*.md")):
        parts.append(f"\n# SOURCE: {path.name}\n")
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def save_knowledge_file(filename: str, content: str):
    safe = filename.strip().replace("/", "_").replace("\\", "_")
    if not safe.endswith(".md"):
        safe += ".md"
    path = KB_DIR / safe
    path.write_text(content, encoding="utf-8")
    return path


def list_knowledge_files():
    return [p.name for p in sorted(KB_DIR.glob("*.md"))]


def read_knowledge_file(filename: str):
    path = KB_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""
