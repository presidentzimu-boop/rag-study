# audit_rag.py
import sys, os, glob, json, importlib.util
from pathlib import Path

def print_h(title):
    print("\n" + "="*len(title))
    print(title)
    print("="*len(title))

def import_version(modname):
    try:
        mod = __import__(modname)
    except Exception as e:
        return None, str(e)
    ver = getattr(mod, "__version__", None)
    return ver or "unknown", None

def try_import(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False

def check_python_env():
    print_h("Environment")
    import platform
    print(f"Python: {platform.python_version()} ({platform.python_implementation()})")
    print(f"Platform: {platform.platform()}")

    pkgs = ["numpy", "torch", "sentence_transformers", "faiss", "faiss_cpu", "faiss_gpu", "fitz"]
    # fitz is PyMuPDF
    for p in pkgs:
        ver, err = import_version(p)
        if ver:
            print(f"{p}: {ver}")
        else:
            print(f"{p}: not installed ({err})")

def check_pdf_dir(pdf_dir: Path, sample_n: int = 5):
    print_h("PDFs")
    print(f"PDF directory: {pdf_dir}")
    if not pdf_dir.exists():
        print("Status: MISSING directory")
        return

    pdfs = sorted([p for p in pdf_dir.glob("**/*.pdf") if p.is_file()])
    print(f"Total PDFs found: {len(pdfs)}")

    if len(pdfs) == 0:
        return

    # Sample a few files and check for extractable text on the first page
    try:
        import fitz  # PyMuPDF
        sample = pdfs[:sample_n]
        has_text = 0
        for p in sample:
            try:
                doc = fitz.open(p)
                text = ""
                if len(doc) > 0:
                    text = doc[0].get_text("text") or ""
                doc.close()
                if text.strip():
                    has_text += 1
            except Exception as e:
                print(f"- Error reading {p.name}: {e}")

        print(f"OCR check (first page text present): {has_text}/{len(sample)}")
        if has_text == 0:
            print("Hint: These may be image-only PDFs or extraction failed. Re-check OCR or try another extractor.")
    except Exception as e:
        print(f"PyMuPDF not available or failed: {e}")
        print("Hint: install PyMuPDF with: pip install pymupdf")

def look_for_index_files(root: Path):
    print_h("RAG Artifacts")
    candidates = []
    patterns = [
        "*.faiss", "*.index", "index.faiss", "rag_index.faiss",
        "*.jsonl", "chunks.jsonl", "metadata.jsonl",
        "*.parquet", "chunks.parquet"
    ]
    for pat in patterns:
        candidates.extend(root.glob(pat))
        candidates.extend((root / "index").glob(pat))
        candidates.extend((root / "data").glob(pat))
    seen = sorted(set([p for p in candidates if p.exists()]))

    if not seen:
        print("No index/metadata files detected in current folder, ./index, or ./data.")
    else:
        print("Detected artifacts:")
        for p in seen:
            print(f"- {p}")

def quick_embed_smoke_test():
    print_h("Embedding smoke test")
    try:
        from sentence_transformers import SentenceTransformer
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        model = SentenceTransformer(model_name)
        vec = model.encode(["hello world"], convert_to_numpy=True)
        shape = getattr(vec, "shape", None)
        print(f"Model loaded: {model_name}")
        print(f"Vector shape: {shape}")
        print("Status: OK")
    except Exception as e:
        print(f"Skipped/failed: {e}")
        print("Hint: pip install sentence-transformers; ensure network access to download the model.")

def main():
    pdf_dir = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path("~/ocr").expanduser()
    check_python_env()
    check_pdf_dir(pdf_dir)
    look_for_index_files(Path(".").resolve())

    # Light test; comment out if you want to skip model download
    quick_embed_smoke_test()

    print_h("Next actions guidance")
    print("- If PDFs show text: you can proceed to chunk + embed.")
    print("- If PyMuPDF missing: pip install pymupdf.")
    print("- If no index detected: build one (chunk, embed, and save FAISS + JSONL metadata).")
    print("- If embedding test failed: install sentence-transformers (and ensure network).")

if __name__ == "__main__":
    main()
