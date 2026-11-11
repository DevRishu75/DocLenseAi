from sqlalchemy import text
from app.database import engine

print("Database URL:", engine.url.render_as_string(hide_password=True))

with engine.connect() as connection:
    migration_table = connection.execute(
        text("SELECT to_regclass('public.alembic_version')")
    ).scalar()

    print("Migration table:", migration_table)

    if migration_table:
        revisions = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).fetchall()

        print("Recorded migration revisions:", revisions)
    else:
        print("The alembic_version table does not exist.")