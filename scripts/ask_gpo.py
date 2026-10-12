import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import chromadb
import ollama


DB_PATH = PROJECT_ROOT / "chroma_db" / "gpo"
COLLECTION_NAME = "gpo_annual_report"

EMBEDDING_MODEL = "qwen3-embedding:0.6b"
LLM_MODEL = "qwen2.5:1.5b"


def retrieve_chunks(question, collection):
    """
    Search ChromaDB for the five most relevant chunks.
    """

    result = ollama.embed(
        model=EMBEDDING_MODEL,
        input=question,
    )

    question_embedding = result["embeddings"][0]

    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5,
        include=["documents", "metadatas", "distances"],
    )

    retrieved_chunks = []

    for document, metadata in zip(
        results["documents"][0],
        results["metadatas"][0],
    ):
        retrieved_chunks.append({
            "text": document,
            "page_start": metadata["page_start"],
            "page_end": metadata["page_end"],
        })

    return retrieved_chunks


def build_context(chunks):
    """
    Combine retrieved chunks into one context string.
    """

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):

        page_start = chunk["page_start"]
        page_end = chunk["page_end"]

        page_label = (
            f"Page {page_start}"
            if page_start == page_end
            else f"Pages {page_start}-{page_end}"
        )

        context_parts.append(
            f"[Source {index} | {page_label}]\n"
            f"{chunk['text']}"
        )

    return "\n\n".join(context_parts)



def generate_answer(question, context):
    """Generate a concise answer from retrieved report evidence."""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You answer questions about the GPO 2018 Annual Report. "
                    "Use only the supplied report context. "
                    "Answer directly in one or two sentences. "
                    "Do not include reasoning or analysis. "
                    "If the answer is unavailable, say you could not find it. "
                    "Cite the source page."
                ),
            },
            {
                "role": "user",
                "content": (
                    "/no_think\n"
                    f"REPORT CONTEXT:\n{context}\n\n"
                    f"QUESTION:\n{question}"
                ),
            },
        ],
        think=False,
        options={
            "temperature": 0,
            "num_predict": 150,
        },
        keep_alive="10m",
    )

    message = response["message"]
    answer = (message.get("content") or "").strip()

    # Print diagnostic information only if the final answer is empty.
    if not answer:
        print("No final answer returned.")
        print("Thinking field:", message.get("thinking"))
        print("Finish reason:", getattr(response, "done_reason", None))
        return "I couldn't generate an answer. Please check the model response."

    return answer



def main():

    question = input("Ask a question about the GPO report: ").strip()

    if not question:
        print("Please enter a question.")
        return

    client = chromadb.PersistentClient(path=str(DB_PATH))

    collection = client.get_collection(
        name=COLLECTION_NAME
    )

    print("\nSearching the report...")

    chunks = retrieve_chunks(question, collection)

    context = build_context(chunks)

    print("Generating answer using Ollama...\n")

    answer = generate_answer(question, context)

    print("=" * 80)
    print("ANSWER")
    print("=" * 80)

    print(answer)


if __name__ == "__main__":
    main()