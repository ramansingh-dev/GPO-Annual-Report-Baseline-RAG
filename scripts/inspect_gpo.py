import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.pdf_parser import extract_pdf_pages


PDF_PATH = PROJECT_ROOT / "data" / "GPO-Anual-report.pdf"


pages = extract_pdf_pages(PDF_PATH)

print(f"Total pages: {len(pages)}")

for page in pages[:5]:
    print("=" * 80)
    print(f"PAGE {page['page_number']}")
    print("=" * 80)
    print(page["text"][:2000])
    print()