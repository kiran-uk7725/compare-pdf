from _hashlib import HASH
import os
import hashlib
from pypdf import PdfReader

def get_binary_hash(filepath: str) -> str:
    """Computes the SHA-256 hash of the file's raw bytes

    Args:
        filepath: file location in string formate

    Returns:
        str: The SHA-256 hexadecimal digest of the file's raw bytes.
    """
    with open(file=filepath, mode="rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def get_text_hash(filepath: str) -> str:
    """Compute a SHA-256 hash of normalized text extracted from a PDF.

    Text is extracted from each page in order, with runs of whitespace
    collapsed to a single space, then encoded as UTF-8 before hashing.

    Args:
        filepath: Path to the PDF file.

    Returns:
        The SHA-256 digest as a hexadecimal string.
    """
    reader: PdfReader = PdfReader(stream=filepath)
    sha256: HASH = hashlib.sha256()

    for page in reader.pages:
        text: str = page.extract_text() or ""
        normalized_text: str =  ' '.join(text.split())
        sha256.update(normalized_text.encode(encoding="utf-8"))

    return sha256.hexdigest()

def compare_pdf(pdf1: str, pdf2: str, check_text_fallback: bool = False)  -> dict[str, bool | str]:
    """Compare two PDF files for binary or normalized-text equality.

    Args:
        pdf1: Path to the first PDF file.
        pdf2: Path to the second PDF file.
        check_text_fallback: Whether to compare normalized extracted text when
            the PDFs do not have an exact binary match.

    Returns:
        A dictionary with two keys:
            - ``match``: Whether the PDFs are considered to match.
            - ``type``: The type of match or the reason for no match.

    Raises:
        FileNotFoundError: If either PDF path does not exist.
    """
    if not (os.path.exists(path=pdf1) and os.path.exists(path=pdf2)):
        raise FileNotFoundError("One or both PDF file path do not exist")

    # Checking binary match if file sizes are same
    if os.path.getsize(filename=pdf1) == os.path.getsize(filename=pdf2):
        if get_binary_hash(filepath=pdf1) == get_binary_hash(filepath=pdf2):
            return {"match": True, "type": "Exact binary match"}

    # Text fallback (Pdf's with identical text, different metadata)
    if check_text_fallback:
        if get_text_hash(filepath=pdf1) == get_text_hash(filepath=pdf2):
            return {"match": True, "type": "Text content match(Different metadata/encoding)"}

    return {"match": False, "type": "Different files"}



