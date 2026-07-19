"""
==========================================================
PDF HANDLER
----------------------------------------------------------
Is file ka kaam sirf PDF ko handle karna hai.

Functions:
1. PDF ko Image me convert karna
2. Total pages count karna
3. Blank PDF detect karna
4. Corrupted PDF detect karna
5. Password protected PDF detect karna
6. File size validate karna
7. Final validation result return karna
==========================================================
"""

import fitz  # PyMuPDF
from pdf2image import convert_from_path
import os


# ==========================================================
# PDF -> Images
# ==========================================================

def get_all_pages_as_images(pdf_path: str) -> list:
    """
    PDF ke har page ko image me convert karo.
    Ye images Gemini ko bheji jayengi.
    """
    return convert_from_path(pdf_path, dpi=200)


# ==========================================================
# Total Pages
# ==========================================================

def get_page_count(pdf_path: str) -> int:
    """
    PDF me total kitne pages hain.
    """
    doc = fitz.open(pdf_path)
    pages = len(doc)
    doc.close()
    return pages


# ==========================================================
# Blank PDF Check
# ==========================================================

def is_blank_pdf(pdf_path: str) -> bool:
    """
    Agar kisi bhi page me text, image, vector drawing (lines/shapes/diagrams),
    ya annotation hai to PDF blank nahi hai.

    Pehle sirf text + raster images check hote the — isse PDFs jinme sirf
    vector graphics ya diagrams the (koi text/raster image nahi), galat se
    "blank" flag ho jaate the. Ab drawings aur annotations bhi check hote hain.
    """

    try:
        doc = fitz.open(pdf_path)

        for page in doc:

            text = page.get_text().strip()

            images = page.get_images(full=True)

            drawings = page.get_drawings()

            annotations = list(page.annots()) if page.annots() else []

            if text or images or drawings or annotations:
                doc.close()
                return False

        doc.close()
        return True

    except Exception:
        return False


# ==========================================================
# Corrupted PDF Check
# ==========================================================

def is_corrupted_pdf(pdf_path: str) -> bool:
    """
    Agar PDF open hi nahi ho rahi
    to corrupted hai.
    """

    try:
        doc = fitz.open(pdf_path)
        doc.close()
        return False

    except Exception:
        return True


# ==========================================================
# Password Protected PDF
# ==========================================================

def is_password_protected(pdf_path: str) -> bool:
    """
    Password protected PDF detect karo.
    """

    try:

        doc = fitz.open(pdf_path)

        if doc.needs_pass:
            doc.close()
            return True

        doc.close()
        return False

    except Exception:
        return False


# ==========================================================
# File Size Validation
# ==========================================================

def is_file_size_valid(pdf_path: str, max_size_mb: int = 20) -> bool:
    """
    Maximum file size check.
    Default = 20 MB
    """

    size_mb = os.path.getsize(pdf_path) / (1024 * 1024)

    return size_mb <= max_size_mb


# ==========================================================
# MASTER VALIDATION
# ==========================================================

def validate_pdf(pdf_path: str):
    """
    Is function ko upload.py call karega.

    Ye decide karega PDF accept hogi ya reject.
    """

    # Corrupted PDF
    if is_corrupted_pdf(pdf_path):
        return {
            "valid": False,
            "reason": "corrupted",
            "folder": "corrupted",
            "message": "Corrupted PDF detected."
        }

    # Password Protected
    if is_password_protected(pdf_path):
        return {
            "valid": False,
            "reason": "protected",
            "folder": "protected",
            "message": "Password protected PDF."
        }

    # Blank PDF
    if is_blank_pdf(pdf_path):
        return {
            "valid": False,
            "reason": "blank",
            "folder": "blank",
            "message": "Blank PDF detected."
        }

    # File Size
    if not is_file_size_valid(pdf_path):
        return {
            "valid": False,
            "reason": "large_file",
            "folder": "large_file",
            "message": "PDF size exceeds allowed limit."
        }

    # Accepted
    return {
        "valid": True,
        "reason": None,
        "folder": "accepted",
        "message": "PDF validation successful."
    }