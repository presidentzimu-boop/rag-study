#!/usr/bin/env python3
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent
    docs = root / "data" / "docs"

    print(f"Project root: {root}")
    print(f"Docs dir: {docs} (exists={docs.exists()})")

    # Look for common doc types
    patterns = ["**/*.pdf", "**/*.md", "**/*.txt"]
    files = []
    for pat in patterns:
        files.extend(docs.glob(pat))

    print(f"Found {len(files)} document(s).")
    for p in files[:10]:
        try:
            print(f" - {p.relative_to(root)}")
        except Exception:
            print(f" - {p}")

    if not files:
        print("No docs found yet — add files under data/docs/")

    print("build_index.py dry run OK ✅")

if __name__ == "__main__":
    main()
