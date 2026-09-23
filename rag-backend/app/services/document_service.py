import io
from fastapi import UploadFile
from pypdf import PdfReader


def extract_text(file: UploadFile) -> tuple[str, str]:
    filename = file.filename or ""
    content = file.file.read()

    if filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        text = "\n".join([page.extract_text() or "" for page in reader.pages])
        return text, "pdf"

    if filename.lower().endswith(".txt"):
        return content.decode("utf-8"), "txt"

    raise ValueError("Unsupported file format")

