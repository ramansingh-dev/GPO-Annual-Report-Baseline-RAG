import re


def clean_text(text: str) -> str:
    """Clean common PDF layout noise while preserving report content."""

    text = text.replace("\r", "\n")

    cleaned_lines = []

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        # Remove the report's repeated, spaced-out running header.
        normalized = re.sub(r"\s+", "", line).upper()

        if (
            "GOVERNMENTPUBLISHINGOFFICE" in normalized
            and "ANNUALREPORT" in normalized
        ):
            continue

        # Ignore lines containing only a printed page number.
        if re.fullmatch(r"\d{1,3}", line):
            continue

        cleaned_lines.append(line)

    # PDF extraction often adds a newline after every visual line.
    # Join those lines so sentences can be read continuously.
    text = " ".join(cleaned_lines)

    # Repair the specific drop-cap split found on page 7.
    text = re.sub(r"\bT\s+he\b", "The", text)

    # Normalize excessive spaces.
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def create_chunks(pages, target_size=1200):
    """Create chunks across pages and preserve source page ranges."""

    chunks = []
    current_text = ""
    current_page_start = None
    current_page_end = None

    def save_chunk():
        nonlocal current_text
        nonlocal current_page_start
        nonlocal current_page_end

        if not current_text.strip():
            return

        chunks.append({
            "text": current_text.strip(),
            "page_start": current_page_start,
            "page_end": current_page_end,
        })

        current_text = ""
        current_page_start = None
        current_page_end = None

    for page in pages:
        page_number = page["page_number"]
        text = clean_text(page["text"])

        if not text:
            continue

        # Split at sentence endings when possible.
        sentences = re.split(r"(?<=[.!?])\s+", text)

        for sentence in sentences:
            sentence = sentence.strip()

            if not sentence:
                continue

            # If adding this sentence would exceed our target,
            # save the current chunk first.
            if (
                current_text
                and len(current_text) + len(sentence) + 1 > target_size
            ):
                save_chunk()

            if current_page_start is None:
                current_page_start = page_number

            current_page_end = page_number

            if current_text:
                current_text += " "

            current_text += sentence

    save_chunk()

    return chunks