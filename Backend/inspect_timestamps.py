
from sqlalchemy import text
from app.database import engine

query = text("""
    SELECT
        table_name,
        column_name,
        data_type,
        is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'public'
      AND table_name IN ('users', 'documents', 'refresh_tokens')
      AND data_type LIKE 'timestamp%'
    ORDER BY table_name, ordinal_position
""")

with engine.connect() as connection:
    rows = connection.execute(query).fetchall()

    for row in rows:
        print(
            f"Table: {row.table_name} | "
            f"Column: {row.column_name} | "
            f"Type: {row.data_type} | "
            f"Nullable: {row.is_nullable}"
        )
