import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import chromadb
import ollama

from app.pdf_parser import extract_pdf_pages
from app.chunker import create_chunks


PDF_PATH = PROJECT_ROOT / "data" / "GPO-Anual-report.pdf"
DB_PATH = PROJECT_ROOT / "chroma_db" / "gpo"
COLLECTION_NAME = "gpo_annual_report"


def main():
    print("Reading PDF...")
    pages = extract_pdf_pages(str(PDF_PATH))

    print("Creating chunks...")
    chunks = create_chunks(pages)

    print(f"Chunks created: {len(chunks)}")

    client = chromadb.PersistentClient(path=str(DB_PATH))

    # Rebuild this task's collection from scratch on each indexing run.
    # This prevents duplicate chunks after rerunning the script.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    batch_size = 16

    for start in range(0, len(chunks), batch_size):
        batch = chunks[start:start + batch_size]

        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for index, chunk in enumerate(batch, start=start):
            result = ollama.embed(
                model="qwen3-embedding:0.6b",
                input=chunk["text"],
            )

            ids.append(f"gpo_chunk_{index}")
            documents.append(chunk["text"])
            metadatas.append({
                "page_start": chunk["page_start"],
                "page_end": chunk["page_end"],
                "document": "GPO 2018 Annual Report",
            })
            embeddings.append(result["embeddings"][0])

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        print(f"Indexed {min(start + batch_size, len(chunks))}/{len(chunks)}")

    print(f"Index complete. Stored {collection.count()} chunks.")
    print(f"Database location: {DB_PATH}")


if __name__ == "__main__":
    main()