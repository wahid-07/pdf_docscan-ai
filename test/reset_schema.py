# from sqlalchemy import create_engine, inspect
# from database.connection import engine, Base
# from models.table_model import PDFMaster, PDFTemp, ExtractedData

# print("Dropping all existing tables...")
# Base.metadata.drop_all(bind=engine)
# print("✓ All tables dropped")

# print("\nCreating new tables...")
# Base.metadata.create_all(bind=engine)
# print("✓ All tables created")

# print("\nVerifying schema...")
# inspector = inspect(engine)
# tables = inspector.get_table_names()
# print(f"Tables present: {tables}")

# for table_name in tables:
#     cols = inspector.get_columns(table_name)
#     if table_name in ['pdf_master', 'pdf_temp', 'extracted_data']:
#         print(f"\n{table_name}:")
#         for col in cols:
#             print(f"  - {col['name']}: {col['type']}")
