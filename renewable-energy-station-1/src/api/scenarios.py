from flask import Blueprint, render_template, redirect, url_for, request
from src.config.database import SessionLocal
from src.schemas import (
    Scenario,
    Location,
    ScenarioBattery,
    ScenarioPhotovoltaic,
    ScenarioWindTurbine,
    ScenarioGrid,
)
from src.models.battery import BatteryFactory
from src.models.photovoltaic_factory import PhotovoltaicFactory
from src.models.turbine_factory import TurbineFactory
from src.models.grid_factory import GridFactory
from pathlib import Path

bp = Blueprint("scenarios", __name__, url_prefix="/scenarios")

# Initialize factories
battery_factory = BatteryFactory("/app/config/battery_configs.json")
pv_factory = PhotovoltaicFactory("/app/config/pv.json")
turbine_factory = TurbineFactory("/app/config/turbines.json")
grid_factory = GridFactory("/app/config/grids.json")


@bp.route("/", methods=["GET"])
def list_scenarios():
    db = SessionLocal()
    scenarios = db.query(Scenario).all()
    return render_template(
        "scenarios.html",
        scenarios=scenarios,
        battery_factory=battery_factory,  # Make sure this is included
    )


@bp.route("/new", methods=["GET", "POST"])
def create_scenario():
    if request.method == "POST":
        db = SessionLocal()

        # Create location
        location = Location(
            name=request.form["location_name"],
            latitude=float(request.form["latitude"]),
            longitude=float(request.form["longitude"]),
            timezone=request.form.get("timezone", "UTC"),
            average_solar_hours=float(request.form["solar_hours"]),
            average_wind_speed=float(request.form["wind_speed"]),
        )
        db.add(location)

        # Create scenario
        scenario = Scenario(
            name=request.form["name"],
            description=request.form["description"],
            location=location,
        )
        db.add(scenario)

        # Add batteries
        battery_types = request.form.getlist("batteries")
        for battery_type in battery_types:
            quantity = int(request.form.get(f"battery_quantity_{battery_type}", 1))
            battery = ScenarioBattery(
                scenario=scenario, battery_type=battery_type, quantity=quantity
            )
            db.add(battery)

        # Add PV panels
        pv_types = request.form.getlist("pvs")
        for pv_type in pv_types:
            quantity = int(request.form.get(f"pv_quantity_{pv_type}", 1))
            pv_config = pv_factory.pv_configs[pv_type]
            pv = ScenarioPhotovoltaic(
                scenario=scenario,
                model_type=pv_type,
                capacity=pv_config["capacity_per_panel"],
                efficiency=pv_config["efficiency"],
                quantity=quantity,
                is_active=True,
            )
            db.add(pv)

        # Add wind turbines
        turbine_types = request.form.getlist("turbines")
        for turbine_type in turbine_types:
            quantity = int(request.form.get(f"turbine_quantity_{turbine_type}", 1))
            turbine_config = turbine_factory.turbine_configs[turbine_type]
            turbine = ScenarioWindTurbine(
                scenario=scenario,
                turbine_type=turbine_type,
                capacity=turbine_config["capacity_per_turbine"],
                cut_in_speed=turbine_config["cut_in_wind_speed"],
                cut_out_speed=turbine_config["cut_out_wind_speed"],
                rated_speed=turbine_config.get("rated_speed", 15.0),
                quantity=quantity,
            )
            db.add(turbine)

        # Add grid connection
        grid_type = request.form.get("grid_type")
        if grid_type:
            grid_config = grid_factory.grid_configs[grid_type]
            grid = ScenarioGrid(
                scenario=scenario,
                grid_id=grid_type,
                capacity=grid_config["capacity"],
                flexible_capacity=grid_config.get("flexible_capacity"),
                voltage_level=grid_config.get("voltage_level", 110.0),
            )
            db.add(grid)

        db.commit()
        return redirect(url_for("scenarios.list_scenarios"))

    return render_template(
        "scenario_form.html",
        scenario=None,
        edit_mode=False,
        battery_factory=battery_factory,
        pv_factory=pv_factory,
        turbine_factory=turbine_factory,
        grid_factory=grid_factory,
        available_batteries=battery_factory.get_available_batteries(),
        available_pvs=pv_factory.get_available_pvs(),
        available_turbines=turbine_factory.get_available_turbines(),
        available_grids=grid_factory.get_available_grids(),
    )


@bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_scenario(id):
    """Edit an existing scenario"""
    db = SessionLocal()
    scenario = db.query(Scenario).filter(Scenario.id == id).first()

    if request.method == "POST":
        # Update scenario details
        scenario.name = request.form["name"]
        scenario.description = request.form["description"]

        # Update location details
        scenario.location.name = request.form["location_name"]
        scenario.location.latitude = float(request.form["latitude"])
        scenario.location.longitude = float(request.form["longitude"])
        scenario.location.average_solar_hours = float(request.form["solar_hours"])
        scenario.location.average_wind_speed = float(request.form["wind_speed"])

        # Update components...
        db.commit()
        return redirect(url_for("scenarios.list_scenarios"))

    return render_template(
        "scenario_form.html",
        scenario=scenario,
        edit_mode=True,
        battery_factory=battery_factory,
        pv_factory=pv_factory,
        turbine_factory=turbine_factory,
        grid_factory=grid_factory,
        available_batteries=battery_factory.get_available_batteries(),
        available_pvs=pv_factory.get_available_pvs(),
        available_turbines=turbine_factory.get_available_turbines(),
        available_grids=grid_factory.get_available_grids(),
    )


@bp.route("/<int:id>/activate", methods=["POST"])
def activate_scenario(id):
    """Activate a scenario"""
    db = SessionLocal()
    scenario = db.query(Scenario).filter(Scenario.id == id).first()
    scenario.is_active = True
    db.commit()
    return {"status": "success"}


@bp.route("/<int:id>/deactivate", methods=["POST"])
def deactivate_scenario(id):
    """Deactivate a scenario"""
    db = SessionLocal()
    scenario = db.query(Scenario).filter(Scenario.id == id).first()
    scenario.is_active = False
    db.commit()
    return {"status": "success"}
