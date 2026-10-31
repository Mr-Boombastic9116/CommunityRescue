import sys
from sqlalchemy import create_engine, text
from app.core.config import settings
from app.database.session import Base, engine
import app.models  # Import all models so metadata is populated

def init_database() -> bool:
    """
    Checks MySQL connection, creates database if it does not exist,
    and creates all tables according to SQLAlchemy models.
    """
    try:
        # Step 1: Connect to server without database to ensure database exists
        server_engine = create_engine(settings.server_database_url, isolation_level="AUTOCOMMIT")
        with server_engine.connect() as conn:
            conn.execute(
                text(f"CREATE DATABASE IF NOT EXISTS `{settings.DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
            )
        server_engine.dispose()
        print(f"[OK] Database '{settings.DB_NAME}' ensured.")

        # Step 2: Create all tables on the actual database engine
        Base.metadata.create_all(bind=engine)
        print("[OK] All database tables and indexes verified successfully.")

        # Step 3: Seed Food Safety Rules
        from app.database.seed_safety_rules import seed_safety_rules
        seed_safety_rules()
        print("[OK] Curated FSSAI Food Safety Rules verified.")
        return True
    except Exception as e:
        print(f"[ERROR] Database initialization failed: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

