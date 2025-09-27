import argparse
import json
from pathlib import Path

# If you don't have pypdf yet: pip install pypdf
from pypdf import PdfReader

def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200):
    """Simple character-based chunker with overlap."""
    if not text:
        return
    start = 0
    n = len(text)
    while start < n:
        end = min(n, start + chunk_size)
        yield text[start:end]
        if end == n:
            break
        start = max(end - overlap, start + 1)

def extract_pdf_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    parts = []
    for page in reader.pages:
        t = page.extract_text() or ""
        parts.append(t)
    return "\n".join(parts).strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", required=True, help="Folder with input PDFs")
    parser.add_argument("--output-dir", required=True, help="Folder to write chunks.jsonl")
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "chunks.jsonl"

    pdf_files = sorted(in_dir.rglob("*.pdf"))

    records = []
    for pdf in pdf_files:
        text = extract_pdf_text(pdf)
        for i, chunk in enumerate(chunk_text(text)):
            records.append({
                "id": f"{pdf.stem}-{i}",
                "source": str(pdf),
                "chunk_index": i,
                "text": chunk,
            })

    with out_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {len(records)} chunks to {out_path}")

if __name__ == "__main__":
    main()
