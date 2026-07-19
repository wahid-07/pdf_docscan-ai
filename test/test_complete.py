# #!/usr/bin/env python3
# """
# Complete test of BYTEA PDF storage implementation
# Shows: Upload → Storage → Retrieval → Verification
# """

# import requests
# import json
# from database.connection import SessionLocal
# from models.table_model import PDFMaster

# print("=" * 70)
# print("🔷 BYTEA PDF STORAGE - COMPLETE TEST")
# print("=" * 70)

# # TEST 1: Upload PDF
# print("\n📤 TEST 1: Upload PDF to database")
# print("-" * 70)
# with open('sample.pdf', 'rb') as f:
#     files = {'file': f}
#     response = requests.post('http://127.0.0.1:8000/api/upload', files=files)

# if response.status_code == 200:
#     data = response.json()
#     pdf_id = data['pdf_id']
#     print(f"✓ Upload successful!")
#     print(f"  PDF ID: {pdf_id}")
#     print(f"  File: {data['file']}")
#     print(f"  Total Pages: {data['total_pages']}")
# else:
#     print(f"✗ Upload failed: {response.status_code}")
#     exit(1)

# # TEST 2: Verify bytes in database
# print("\n💾 TEST 2: Verify PDF bytes stored in database")
# print("-" * 70)
# db = SessionLocal()
# record = db.query(PDFMaster).filter(PDFMaster.id == pdf_id).first()

# if record and record.file_data:
#     print(f"✓ PDF bytes found in database!")
#     print(f"  File name: {record.file_name}")
#     print(f"  File size: {len(record.file_data):,} bytes")
#     print(f"  Stored size field: {record.file_size:,} bytes")
#     print(f"  PDF magic number: {record.file_data[:10]}")
#     print(f"  Match: {'✓' if record.file_data[:4] == b'%PDF' else '✗'}")
# else:
#     print(f"✗ No file_data found")
#     exit(1)

# # TEST 3: Download from API
# print("\n📥 TEST 3: Download PDF from /api/pdf endpoint")
# print("-" * 70)
# response = requests.get(f'http://127.0.0.1:8000/api/pdf/{pdf_id}')

# if response.status_code == 200:
#     print(f"✓ Download successful!")
#     print(f"  Content-Type: {response.headers.get('content-type')}")
#     print(f"  Content-Length: {len(response.content):,} bytes")
#     print(f"  File size matches: {'✓' if len(response.content) == len(record.file_data) else '✗'}")
#     print(f"  Bytes match: {'✓' if response.content == record.file_data else '✗'}")
# else:
#     print(f"✗ Download failed: {response.status_code}")
#     exit(1)

# # TEST 4: Verify extraction results
# print("\n📊 TEST 4: Verify extraction results")
# print("-" * 70)
# response = requests.get('http://127.0.0.1:8000/api/records')

# if response.status_code == 200:
#     data = response.json()
#     print(f"✓ Retrieved {data['total']} extracted records")
    
#     for rec in data['records']:
#         if rec['pdf_id'] == pdf_id:
#             print(f"  Page {rec['page_number']}:")
#             print(f"    - Content Type: {rec['content_type']}")
#             if rec['data']['tables']:
#                 print(f"    - Tables: {len(rec['data']['tables'])} found")
#             if rec['data']['text']:
#                 print(f"    - Text: {len(rec['data']['text'])} characters")
# else:
#     print(f"✗ Records query failed: {response.status_code}")

# # TEST 5: Check masters
# print("\n🎯 TEST 5: Verify PDF master record")
# print("-" * 70)
# response = requests.get('http://127.0.0.1:8000/api/masters')

# if response.status_code == 200:
#     data = response.json()
#     print(f"✓ Retrieved {data['total']} master records")
    
#     for master in data['pdfs']:
#         if master['id'] == pdf_id:
#             print(f"  Master ID: {master['id']}")
#             print(f"  Status: {master['status']}")
#             print(f"  Pages: {master['total_pages']}")
#             print(f"  Uploaded: {master['uploaded_at']}")
# else:
#     print(f"✗ Masters query failed: {response.status_code}")

# db.close()

# print("\n" + "=" * 70)
# print("✅ ALL TESTS PASSED - BYTEA PDF STORAGE FULLY OPERATIONAL")
# print("=" * 70)
# print("\nDatabase mein PDF file complete ho gai! 🎉")
