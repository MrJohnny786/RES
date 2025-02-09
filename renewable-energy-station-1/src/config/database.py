import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from src.schemas import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@db:5432/renewable_energy"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Initialize the database"""
    # Import all models

    # Drop views and tables with cascade
    with engine.connect() as conn:
        # Drop materialized view if exists
        conn.execute(
            text("DROP MATERIALIZED VIEW IF EXISTS battery_metrics_daily CASCADE")
        )
        conn.commit()

    # Drop all tables
    Base.metadata.drop_all(bind=engine)

    # Create fresh tables
    Base.metadata.create_all(bind=engine)

    # Create TimescaleDB hypertable
    with engine.connect() as conn:
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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
