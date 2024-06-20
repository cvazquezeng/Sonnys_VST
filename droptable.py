from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.schema import DropTable, CreateTable

# Database connection string
DATABASE_URI = 'mysql+pymysql://cvazquez:Sonnys2024@192.168.1.222/andon'
engine = create_engine(DATABASE_URI)
metadata = MetaData()


# Reflect the database schema to list tables
metadata.reflect(bind=engine)

# Print all available tables
print("Available tables in the database:")
for table_name in metadata.tables.keys():
    print(table_name)

# Check if the target table exists
table_name = 'closed_ticket'
if table_name in metadata.tables:
    table = metadata.tables[table_name]

    # Generate the schema
    table_schema = CreateTable(table)

    # Drop and recreate the table using a connection
    with engine.connect() as connection:
        connection.execute(DropTable(table))
        connection.execute(table_schema)

    print(f"Table {table_name} dropped and recreated successfully.")
else:
    print(f"Table {table_name} not found in the database.")