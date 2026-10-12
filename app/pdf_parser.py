import pymupdf

def extract_pdf_pages(pdf_path):
    document = pymupdf.open(pdf_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text("text").strip()

        pages.append({
            "page_number": page_number,
            "text": text,
        })

    document.close()

    return pages