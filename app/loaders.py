from pathlib import Path

from pypdf import PdfReader


def load_document(path: str | Path) -> str:
    path = Path(path)

    if path.suffix == ".txt":
        return path.read_text(encoding="utf-8")

    if path.suffix == ".pdf":
        reader = PdfReader(path)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    raise ValueError(f"Unsupported file type: {path.suffix}")
