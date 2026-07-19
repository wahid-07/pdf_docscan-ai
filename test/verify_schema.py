# from sqlalchemy import inspect
# from database.connection import engine

# inspector = inspect(engine)
# tables = inspector.get_table_names()
# print('Tables created:', tables)
# print()

# for table_name in tables:
#     cols = inspector.get_columns(table_name)
#     print(f'{table_name}:')
#     for col in cols:
#         print(f'  - {col["name"]}: {col["type"]}')
#     print()
