# export_jsonl.py
# Purpose: Export a ChromaDB collection to JSONL (id, source, title, page, chunk_index, text)

import json
from pathlib import Path

PERSIST_DIR = "/Users/pelicanzimu/books-assistant/.chroma"  # <- your Chroma directory
COLLECTION_NAME = "books_async"                              # <- your collection name
OUT_PATH = "export_books_async.jsonl"                        # <- output file name
BATCH_SIZE = 1000                                            # <- adjust if needed


def get_chroma_client(persist_dir: str):
    """
    Connect to Chroma persistent store, compatible with both newer and older versions.
    """
    import chromadb
    if hasattr(chromadb, "PersistentClient"):
        return chromadb.PersistentClient(path=persist_dir)
    # Fallback for older chromadb
    from chromadb.config import Settings
    return chromadb.Client(Settings(persist_directory=persist_dir))


def open_collection(client, name: str):
    """
    Open an existing collection by name. If not found, show available names.
    """
    try:
        return client.get_collection(name=name)
    except Exception as e:
        try:
            available = [c.name for c in client.list_collections()]
        except Exception:
            available = []
        raise RuntimeError(
            f"Collection '{name}' not found. Available: {available}"
        ) from e


def fetch_page(collection, offset: int, limit: int):
    """
    Fetch a page of items using offset/limit.
    """
    # include controls what comes back besides ids
    results = collection.get(
        include=["metadatas", "documents"],
        limit=limit,
        offset=offset,
    )
    # Ensure keys exist
    return {
        "ids": results.get("ids", []) or [],
        "documents": results.get("documents", []) or [],
        "metadatas": results.get("metadatas", []) or [],
    }


def export_to_jsonl(collection, out_path: str, batch_size: int = 1000):
    """
    Stream through the collection and write JSONL lines safely.
    """
    out_file = Path(out_path)
    exported = 0
    offset = 0

    with out_file.open("w", encoding="utf-8") as f:
        while True:
            page = fetch_page(collection, offset=offset, limit=batch_size)
            ids = page["ids"]
            if not ids:
                break

            docs = page["documents"]
            metas = page["metadatas"]

            # Write each record as one JSON line
            for i, _id in enumerate(ids):
                doc = docs[i] if i < len(docs) and docs[i] is not None else ""
                meta = metas[i] if i < len(metas) and metas[i] is not None else {}

                line = {
                    "id": _id,
                    "source": meta.get("source"),
                    "title": meta.get("title"),
                    "page": meta.get("page"),
                    "chunk_index": meta.get("chunk_index"),
                    "text": doc or "",
                }
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
                exported += 1

            # Advance by the actual number returned
            offset += len(ids)

    return exported


if __name__ == "__main__":
    print(f"Connecting to Chroma at: {PERSIST_DIR}")
    client = get_chroma_client(PERSIST_DIR)

    print(f"Opening collection: {COLLECTION_NAME}")
    collection = open_collection(client, COLLECTION_NAME)

    try:
        total = collection.count()
        print(f"Collection count reported by Chroma: {total}")
    except Exception:
        total = None

    print("Exporting…")
    n = export_to_jsonl(collection, OUT_PATH, BATCH_SIZE)
    print(f"Done. Wrote {n} lines to {OUT_PATH}.")
    if total is not None:
        if n == total:
            print("✅ Export count matches collection count.")
        else:
            print(f"ℹ️ Exported {n}, but collection reported {total}. This can be normal if filters/permissions apply.")

