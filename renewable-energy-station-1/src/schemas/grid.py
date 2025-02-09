from sqlalchemy import Column, Integer, Float, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class ScenarioGrid(Base):
    __tablename__ = "scenario_grids"

    id = Column(Integer, primary_key=True)
    scenario_id = Column(Integer, ForeignKey("scenarios.id"), nullable=False)
    grid_id = Column(String, nullable=False)
    capacity = Column(Float, nullable=False)  # MW
    is_active = Column(Boolean, default=True)

    scenario = relationship("Scenario", back_populates="grid_connections")
