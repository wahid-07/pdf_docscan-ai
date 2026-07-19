from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Boolean, ForeignKey, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database.connection import Base


class PDFMaster(Base):
    __tablename__ = "pdf_master"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_data = Column(LargeBinary, nullable=True)
    file_hash = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    total_pages = Column(Integer, default=0)
    status = Column(String, default="processing")
    progress = Column(Integer, default=0)
    processing_message = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=func.now())

    # RBAC: Kon sa user ne upload kiya
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    temp_records = relationship("PDFTemp", back_populates="pdf")
    final_records = relationship("ExtractedData", back_populates="pdf")
    owner = relationship("User", back_populates="pdfs")


class PDFTemp(Base):
    __tablename__ = "pdf_temp"

    id = Column(Integer, primary_key=True, index=True)
    pdf_id = Column(Integer, ForeignKey("pdf_master.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    content_type = Column(String, nullable=True)
    raw_data = Column(JSON, nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    pdf = relationship("PDFMaster", back_populates="temp_records")


class ExtractedData(Base):
    __tablename__ = "extracted_data"

    id = Column(Integer, primary_key=True, index=True)
    pdf_id = Column(Integer, ForeignKey("pdf_master.id"), nullable=False)
    file_name = Column(String, nullable=False)
    page_number = Column(Integer, nullable=True)
    content_type = Column(String, nullable=True)
    data = Column(JSON, nullable=True)
    raw_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=func.now())

    # RBAC: Owner track karne ke liye
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    pdf = relationship("PDFMaster", back_populates="final_records")


class RejectedUpload(Base):
    __tablename__ = "rejected_uploads"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, server_default=func.now())

    # RBAC: Kisne upload kiya
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)
    failed_attempts = Column(Integer, default=0)
    account_locked = Column(Boolean, default=False)
    lock_until = Column(DateTime, nullable=True)
    email_verified = Column(Boolean, default=False)
    profile_image = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    refresh_token_expires_at = Column(DateTime, nullable=True)
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    token_version = Column(Integer, default=0)

    # Relationship — User ke saare PDFs
    pdfs = relationship("PDFMaster", back_populates="owner")