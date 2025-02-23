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
        try:
            # Create new scenario
            scenario = Scenario(
                name=request.form["name"], description=request.form["description"]
            )

            # Create and link location
            location = Location(
                name=request.form["location_name"],
                latitude=float(request.form["latitude"]),
                longitude=float(request.form["longitude"]),
                average_solar_hours=float(request.form["solar_hours"]),
                average_wind_speed=float(request.form["wind_speed"]),
            )
            scenario.location = location

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
                pv = ScenarioPhotovoltaic(
                    scenario=scenario, model_type=pv_type, quantity=quantity
                )
                db.add(pv)

            # Add wind turbines
            turbine_types = request.form.getlist("turbines")
            for turbine_type in turbine_types:
                quantity = int(request.form.get(f"turbine_quantity_{turbine_type}", 1))
                turbine = ScenarioWindTurbine(
                    scenario=scenario, turbine_type=turbine_type, quantity=quantity
                )
                db.add(turbine)

            # Add grid connection
            grid_type = request.form.get("grid_type")
            if grid_type:
                grid = ScenarioGrid(scenario=scenario, grid_id=grid_type)
                db.add(grid)

            db.add(scenario)
            db.commit()
            return redirect(url_for("scenarios.list_scenarios"))

        except Exception as e:
            db.rollback()
            print(f"Error creating scenario: {e}")
            return render_template(
                "error.html", error="Failed to create scenario. Please try again."
            )

    # GET request - show form
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
