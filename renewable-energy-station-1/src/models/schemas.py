from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    Boolean,
    MetaData,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship, declarative_base

metadata = MetaData()
Base = declarative_base(metadata=metadata)


class BatteryStatus(Base):
    __tablename__ = "battery_status"

    id = Column(Integer, primary_key=True)
    battery_id = Column(Integer, ForeignKey("scenario_batteries.id"))
    last_eoc = Column(TIMESTAMP)
    next_eoc = Column(TIMESTAMP)
    status = Column(String)  # Ready/Charging/Discharging/EOC/Error
    is_online = Column(Boolean, default=True)
    last_updated = Column(TIMESTAMP, default=datetime.utcnow)

    battery = relationship("ScenarioBattery", back_populates="battery_status")


class BatteryMetrics(Base):
    __tablename__ = "battery_metrics"

    # Primary key columns
    time = Column(TIMESTAMP, primary_key=True)
    battery_id = Column(Integer, ForeignKey("scenario_batteries.id"), primary_key=True)

    # Metrics
    charge_level = Column(Float, nullable=False)
    charge_rate = Column(Float)
    discharge_rate = Column(Float)
    temperature = Column(Float)
    voltage = Column(Float)
    state_of_charge = Column(Float)  # Percentage
    health = Column(Float)
    cycle_count = Column(Integer)
    energy_in = Column(Float)  # Energy charged in this hour
    energy_out = Column(Float)  # Energy discharged in this hour
    efficiency = Column(Float)  # Charging/discharging efficiency

    # Remove the TimescaleDB specific config from here
    # It will be handled in the init.sql file instead


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timezone = Column(String, nullable=False)
    average_solar_hours = Column(Float)
    average_wind_speed = Column(Float)


class Scenario(Base):
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

    # Relationships
    location = relationship("Location", backref="scenario")
    batteries = relationship("ScenarioBattery", back_populates="scenario")
    solar_panels = relationship("ScenarioPhotovoltaic", back_populates="scenario")
    wind_turbines = relationship("ScenarioWindTurbine", back_populates="scenario")
    grid_connections = relationship("ScenarioGrid", back_populates="scenario")


class ScenarioBattery(Base):
    __tablename__ = "scenario_batteries"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    battery_type = Column(String, nullable=False)  # References battery_configs.json
    quantity = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    scenario = relationship("Scenario", back_populates="batteries")
    battery_status = relationship(
        "BatteryStatus", back_populates="battery", uselist=False
    )


class ScenarioPhotovoltaic(Base):
    __tablename__ = "scenario_photovoltaics"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    capacity = Column(Float, nullable=False)  # kW
    efficiency = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    scenario = relationship("Scenario", back_populates="solar_panels")


class ScenarioWindTurbine(Base):
    __tablename__ = "scenario_wind_turbines"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    capacity = Column(Float, nullable=False)  # kW
    cut_in_speed = Column(Float, default=3.0)  # m/s
    rated_speed = Column(Float, default=15.0)  # m/s
    quantity = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)

    scenario = relationship("Scenario", back_populates="wind_turbines")


class ScenarioGrid(Base):
    __tablename__ = "scenario_grids"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    grid_id = Column(String, nullable=False)
    capacity = Column(Float, nullable=False)  # MW
    is_active = Column(Boolean, default=True)

    scenario = relationship("Scenario", back_populates="grid_connections")
