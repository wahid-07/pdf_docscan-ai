import hashlib
import os

from database.connection import SessionLocal
from models.table_model import (
    PDFMaster,
    PDFTemp,
    ExtractedData,
    RejectedUpload
)


def calculate_file_sha256(file_path: str) -> str:
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def find_duplicate_pdf(file_hash: str, user_id: int = None):
    db = SessionLocal()
    try:
        query = db.query(PDFMaster).filter(PDFMaster.file_hash == file_hash)
        if user_id is not None:
            query = query.filter(PDFMaster.user_id == user_id)
        return query.first()
    except Exception:
        return None
    finally:
        db.close()


# ── MASTER TABLE ──

def create_pdf_master(
    file_name: str,
    total_pages: int,
    file_data: bytes = None,
    file_size: int = 0,
    user_id: int = None,
    file_hash: str = None
) -> int:
    db = SessionLocal()
    try:
        record = PDFMaster(
            file_name=file_name,
            total_pages=total_pages,
            file_data=file_data,
            file_size=file_size,
            status="processing",
            user_id=user_id,
            file_hash=file_hash,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def update_pdf_status(pdf_id: int, status: str, progress: int | None = None, message: str | None = None):
    db = SessionLocal()
    try:
        record = db.query(PDFMaster).filter(PDFMaster.id == pdf_id).first()
        if record:
            record.status = status
            if progress is not None:
                record.progress = max(0, min(100, progress))
            if message is not None:
                record.processing_message = message
            db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_pdf_status(pdf_id: int, user_id: int = None, role: str = "user"):
    db = SessionLocal()
    try:
        record = db.query(PDFMaster).filter(PDFMaster.id == pdf_id).first()
        if not record:
            return None
        if role != "admin" and record.user_id != user_id:
            return None
        return {
            "id": record.id,
            "file_name": record.file_name,
            "status": record.status,
            "progress": record.progress,
            "processing_message": record.processing_message,
            "total_pages": record.total_pages,
            "uploaded_at": str(record.uploaded_at),
        }
    finally:
        db.close()


# ── TEMPORARY TABLE ──

def insert_temp(pdf_id: int, page_data: dict):
    db = SessionLocal()
    try:
        record = PDFTemp(
            pdf_id=pdf_id,
            page_number=page_data.get("page_number", 0),
            content_type=page_data.get("content_type", "unknown"),
            raw_data={
                "tables": page_data.get("tables", []),
                "text":   page_data.get("text", ""),
                "images": page_data.get("images", [])
            },
            is_verified=False
        )
        db.add(record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def move_temp_to_final(pdf_id: int, file_name: str, user_id: int = None):
    db = SessionLocal()
    try:
        temp_records = db.query(PDFTemp).filter(PDFTemp.pdf_id == pdf_id).all()

        for temp in temp_records:
            final = ExtractedData(
                pdf_id=pdf_id,
                file_name=file_name,
                page_number=temp.page_number,
                content_type=temp.content_type,
                data=temp.raw_data,
                raw_text=temp.raw_data.get("text", "") if temp.raw_data else "",
                user_id=user_id
            )
            db.add(final)
            temp.is_verified = True

        db.commit()

        db.query(PDFTemp).filter(PDFTemp.pdf_id == pdf_id).delete()
        db.commit()

        print(f"{len(temp_records)} records temp se final mein move ho gaye!")

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


# ── FETCH ──

def get_all_records(user_id: int = None, role: str = "user"):
    """
    Admin: sab records
    User: sirf apne records
    """
    db = SessionLocal()
    try:
        query = db.query(ExtractedData)
        if role != "admin":
            query = query.filter(ExtractedData.user_id == user_id)
        return query.order_by(ExtractedData.id).all()
    finally:
        db.close()


def get_all_masters(user_id: int = None, role: str = "user"):
    """
    Admin: sab PDFs
    User: sirf apne PDFs
    """
    db = SessionLocal()
    try:
        query = db.query(PDFMaster)
        if role != "admin":
            query = query.filter(PDFMaster.user_id == user_id)
        return query.order_by(PDFMaster.id.desc()).all()
    finally:
        db.close()


def delete_pdf_by_id(pdf_id: int, user_id: int = None, role: str = "user") -> bool:
    """
    Admin: koi bhi PDF delete kar sakta hai
    User: sirf apni PDF delete kar sakta hai
    Returns False agar PDF nahi mili ya permission nahi hai
    """
    db = SessionLocal()
    try:
        master = db.query(PDFMaster).filter(PDFMaster.id == pdf_id).first()

        if not master:
            return False

        # Ownership check
        if role != "admin" and master.user_id != user_id:
            return None  # None = 403, False = 404

        db.query(ExtractedData).filter(ExtractedData.pdf_id == pdf_id).delete()
        db.query(PDFTemp).filter(PDFTemp.pdf_id == pdf_id).delete()
        db.delete(master)
        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def search_records(query: str, user_id: int = None, role: str = "user") -> list:
    """
    Admin: poori database mein search
    User: sirf apne records mein search
    """
    db = SessionLocal()
    try:
        q = db.query(ExtractedData).filter(
            ExtractedData.raw_text.ilike(f"%{query}%")
        )
        if role != "admin":
            q = q.filter(ExtractedData.user_id == user_id)
        return q.all()
    finally:
        db.close()


# ── REJECTED PDF ──

def create_rejected_upload(
    file_name: str,
    file_path: str,
    reason: str,
    file_size: int,
    user_id: int = None
) -> int:
    db = SessionLocal()
    try:
        record = RejectedUpload(
            file_name=file_name,
            file_path=file_path,
            reason=reason,
            file_size=file_size,
            user_id=user_id
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_rejected_uploads(user_id: int = None, role: str = "user"):
    db = SessionLocal()
    try:
        query = db.query(RejectedUpload)
        if role != "admin":
            query = query.filter(RejectedUpload.user_id == user_id)
        return query.order_by(RejectedUpload.id.desc()).all()
    finally:
        db.close()