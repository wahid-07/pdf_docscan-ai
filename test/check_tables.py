# from database.connection import SessionLocal
# from models.table_model import PDFMaster, PDFTemp, ExtractedData

# db = SessionLocal()

# print("=== PDF MASTER ===")
# masters = db.query(PDFMaster).all()
# for m in masters:
#     print(f"ID: {m.id}, File: {m.file_name}, Pages: {m.total_pages}, Status: {m.status}")

# print("\n=== PDF TEMP ===")
# temps = db.query(PDFTemp).all()
# print(f"Total temp records: {len(temps)}")
# for t in temps:
#     print(f"PDF ID: {t.pdf_id}, Page: {t.page_number}, Type: {t.content_type}, Verified: {t.is_verified}")

# print("\n=== EXTRACTED DATA (FINAL) ===")
# finals = db.query(ExtractedData).all()
# print(f"Total final records: {len(finals)}")
# for f in finals:
#     print(f"ID: {f.id}, PDF ID: {f.pdf_id}, File: {f.file_name}, Page: {f.page_number}, Type: {f.content_type}")

# db.close()
