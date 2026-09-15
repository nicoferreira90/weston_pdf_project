"""Read text from well-formed PDFs without retaining the document."""

from io import BytesIO

from pypdf import PdfReader


class DocumentProcessingError(Exception):
    """The document cannot supply text for field extraction."""


def read_pdf_text(document: bytes) -> str:
    with BytesIO(document) as stream, PdfReader(stream) as reader:
        text = "\n".join(page.extract_text() or "" for page in reader.pages)

    if not text.strip():
        raise DocumentProcessingError("The PDF contains no extractable text.")
    return text
