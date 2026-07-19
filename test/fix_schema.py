# from sqlalchemy import inspect
# from database.connection import engine, Base
# from models.table_model import ExtractedData

# # Drop all tables
# Base.metadata.drop_all(bind=engine)
# print('Old tables dropped')

# # Recreate all tables
# Base.metadata.create_all(bind=engine)
# print('New tables created')

# # Verify the schema
# inspector = inspect(engine)
# columns = inspector.get_columns('extracted_data')
# print('\nColumns in extracted_data:')
# for col in columns:
#     print(f'  - {col["name"]}: {col["type"]}')
