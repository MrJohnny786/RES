import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse, parse_qs
from src.schemas import Base  # Import Base from schemas instead of creating new one

# Get database URL from environment
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/renewable_energy"
)

# Parse the URL to extract parameters
parsed_url = urlparse(DATABASE_URL)
connect_args = {}

# Determine if we're running in development or production
is_development = os.getenv("FLASK_ENV", "development") == "development"

# If there are query parameters, extract them
if parsed_url.query:
    query_params = parse_qs(parsed_url.query)

    # Handle SSL requirement - only if not in development
    if (
        "ssl" in query_params
        and query_params["ssl"][0] == "require"
        and not is_development
    ):
        connect_args["sslmode"] = "require"

# Remove ssl=require from the URL if we're in development
if is_development:
    # Strip the ssl parameter from the URL if present
    db_parts = DATABASE_URL.split("?")
    if len(db_parts) > 1:
        params = db_parts[1].split("&")
        filtered_params = [p for p in params if not p.startswith("ssl=")]
        DATABASE_URL = db_parts[0]
        if filtered_params:
            DATABASE_URL += "?" + "&".join(filtered_params)

# Create the engine with proper settings
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database"""
    try:
        print("Starting database initialization...")

        # Drop materialized view if it exists
        with engine.connect() as conn:
            conn.execute(
                text("DROP MATERIALIZED VIEW IF EXISTS battery_metrics_daily CASCADE")
            )
            conn.commit()
            print("Dropped existing materialized views")

        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("Dropped all existing tables")

        # Create all tables defined in schemas
        Base.metadata.create_all(bind=engine)
        print("Created all tables from schemas")

        # Create TimescaleDB hypertable
        with engine.connect() as conn:
            try:
                conn.execute(
                    text(
                        """
                        SELECT create_hypertable('battery_metrics', 'time', 
                            if_not_exists => TRUE,
                            chunk_time_interval => INTERVAL '1 day'
                        )
                    """
                    )
                )
                conn.commit()
                print("Created TimescaleDB hypertable")
            except Exception as e:
                print(f"Warning: Could not create hypertable: {e}")
                # Continue even if hypertable creation fails

        print("Database initialization completed successfully")

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
