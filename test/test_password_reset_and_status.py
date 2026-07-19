import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.table_model import Base, User, PDFMaster
import services.auth_service as auth_service
import services.db_handler as db_handler


@pytest.fixture()
def test_session_factory():
    engine = create_engine("sqlite:///:memory:")
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    def _factory():
        return Session()

    return _factory


def test_password_reset_flow(test_session_factory, monkeypatch):
    monkeypatch.setattr(auth_service, "SessionLocal", test_session_factory)

    db = test_session_factory()
    user = User(full_name="Test User", email="test@example.com", password_hash="hashed")
    db.add(user)
    db.commit()
    db.close()

    result = auth_service.request_password_reset("test@example.com")
    assert result["success"] is True

    db = test_session_factory()
    saved_user = db.query(User).filter(User.email == "test@example.com").first()
    assert saved_user.otp_code is not None
    otp = saved_user.otp_code
    db.close()

    verify_result = auth_service.verify_password_reset_otp("test@example.com", otp)
    assert verify_result["success"] is True

    reset_result = auth_service.reset_password("test@example.com", otp, "NewPass123!")
    assert reset_result["success"] is True


def test_pdf_status_helpers(test_session_factory, monkeypatch):
    monkeypatch.setattr(db_handler, "SessionLocal", test_session_factory)

    db = test_session_factory()
    user = User(full_name="Owner", email="owner@example.com", password_hash="hashed")
    db.add(user)
    db.commit()
    db.close()

    pdf_id = db_handler.create_pdf_master("sample.pdf", 2, file_size=123, user_id=1)
    db_handler.update_pdf_status(pdf_id, "processing", progress=35)

    status = db_handler.get_pdf_status(pdf_id, user_id=1)
    assert status is not None
    assert status["status"] == "processing"
    assert status["progress"] == 35
