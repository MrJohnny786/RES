from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TIMESTAMP

# Use PostgreSQL/TimescaleDB specific metadata
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class BatteryInstance(Base):
    __tablename__ = "battery_instances"

    # Regular columns
    id = Column(Integer, primary_key=True)
    battery_type = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    capacity = Column(Float, nullable=False)
    max_charge_rate = Column(Float)
    max_discharge_rate = Column(Float)
    manufactured_date = Column(String)
    installation_date = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class BatteryMetrics(Base):
    __tablename__ = "battery_metrics"

    # Time-series specific columns
    time = Column(TIMESTAMP, primary_key=True)
    battery_id = Column(Integer, nullable=False)
    current_charge = Column(Float, default=0.0)
    voltage = Column(Float)
    temperature = Column(Float)
    cycle_count = Column(Integer)
    health = Column(Float)
    status = Column(String)
    last_eoc = Column(TIMESTAMP)
    next_eoc = Column(TIMESTAMP)

    # TimescaleDB hypertable configuration
    __table_args__ = {
        "postgresql_extension": "timescaledb",
        "timescaledb_hypertable": {
            "time_column_name": "time",
            "chunk_time_interval": "1 day",
        },
    }
