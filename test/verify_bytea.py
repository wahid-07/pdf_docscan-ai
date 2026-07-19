# from database.connection import SessionLocal
# from models.table_model import PDFMaster

# db = SessionLocal()

# masters = db.query(PDFMaster).all()

# for m in masters:
#     print(f"ID: {m.id}")
#     print(f"  File Name: {m.file_name}")
#     print(f"  File Size: {m.file_size} bytes")
#     print(f"  Total Pages: {m.total_pages}")
#     print(f"  Status: {m.status}")
#     print(f"  file_data stored: {'YES ✓' if m.file_data else 'NO ✗'}")
    
#     if m.file_data:
#         print(f"  file_data length: {len(m.file_data)} bytes")
#         print(f"  First 10 bytes: {m.file_data[:10]}")
#     print()

# db.close()
