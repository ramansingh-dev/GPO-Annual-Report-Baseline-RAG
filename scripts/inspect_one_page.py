import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.pdf_parser import extract_pdf_pages

PDF_PATH = "data/GPO-Anual-report.pdf"

pages = extract_pdf_pages(PDF_PATH)

for page in pages:
    if page["page_number"] == 7:
        print(page["text"])
        break
