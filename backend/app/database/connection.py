from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.database.models.base import Base


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

MIGRATION_COLUMNS = {
    "training_sessions": [
        ("user_id", "INTEGER"),
        ("tenant_id", "INTEGER"),
        ("scenario_json", "TEXT"),
        ("response_json", "TEXT"),
        ("evaluation_json", "TEXT"),
        ("score", "REAL"),
        ("attack_mode", "VARCHAR"),
        ("docker_lab_key", "VARCHAR"),
        ("completed_at", "DATETIME"),
        ("behavior_json", "TEXT"),
        ("difficulty_adaptation_json", "TEXT"),
    ],
}


def _apply_sqlite_migrations():
    inspector = inspect(engine)

    with engine.begin() as connection:
        for table_name, columns in MIGRATION_COLUMNS.items():
            if table_name not in inspector.get_table_names():
                continue

            existing = {
                column["name"]
                for column in inspector.get_columns(table_name)
            }

            for column_name, column_type in columns:
                if column_name not in existing:
                    connection.execute(
                        text(
                            f"ALTER TABLE {table_name} "
                            f"ADD COLUMN {column_name} {column_type}"
                        )
                    )


def create_tables():
    import app.database.models.tenant  # noqa: F401
    import app.database.models.user  # noqa: F401
    import app.database.models.training_session  # noqa: F401
    import app.database.models.research  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _apply_sqlite_migrations()


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
