import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.pdf_parser import extract_pdf_pages
from app.chunker import create_chunks

PDF_PATH = "data/GPO-Anual-report.pdf"

pages = extract_pdf_pages(PDF_PATH)
chunks = create_chunks(pages, target_size=1200)

print(f"Pages read: {len(pages)}")
print(f"Chunks created: {len(chunks)}")

for index, chunk in enumerate(chunks[:10], start=1):
    print("\n" + "=" * 80)
    print(f"CHUNK {index}")
    print(
        f"Pages: {chunk['page_start']}-{chunk['page_end']} | "
        f"Characters: {len(chunk['text'])}"
    )
    print("=" * 80)
    print(chunk["text"][:1000])
