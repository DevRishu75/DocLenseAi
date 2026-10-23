
from sqlalchemy import inspect
from app.database import engine

inspector = inspect(engine)

for table in ["users", "documents", "refresh_tokens"]:
    print(f"\n--- TABLE: {table} ---")

    print("\nColumns:")
    for column in inspector.get_columns(table):
        print(
            column["name"],
            "| type:", column["type"],
            "| nullable:", column["nullable"]
        )

    print("\nPrimary key:")
    print(inspector.get_pk_constraint(table))

    print("\nForeign keys:")
    print(inspector.get_foreign_keys(table))

    print("\nUnique constraints:")
    print(inspector.get_unique_constraints(table))
