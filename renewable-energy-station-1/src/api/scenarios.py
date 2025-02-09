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

bp = Blueprint("scenarios", __name__, url_prefix="/scenarios")
battery_factory = BatteryFactory("config/battery_configs.json")


@bp.route("/")
def list_scenarios():
    db = SessionLocal()
    scenarios = db.query(Scenario).all()
    return render_template("scenarios.html", scenarios=scenarios)


@bp.route("/new", methods=["GET", "POST"])
def create_scenario():
    if request.method == "POST":
        db = SessionLocal()
        # ... existing scenario creation logic ...
        db.commit()
        db.close()
        return redirect(url_for("scenarios.list_scenarios"))

    return render_template(
        "scenario_form.html",
        available_batteries=battery_factory.get_available_batteries(),
    )


@bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_scenario(id):
    db = SessionLocal()
    scenario = db.query(Scenario).get(id)

    if request.method == "POST":
        # Update location
        scenario.location.name = request.form["location_name"]
        scenario.location.latitude = float(request.form["latitude"])
        scenario.location.longitude = float(request.form["longitude"])
        scenario.location.timezone = request.form["timezone"]
        scenario.location.average_solar_hours = float(request.form["solar_hours"])
        scenario.location.average_wind_speed = float(request.form["wind_speed"])

        # Update scenario details
        scenario.name = request.form["name"]
        scenario.description = request.form["description"]

        # Update batteries
        for battery in scenario.batteries:
            db.delete(battery)

        battery_types = request.form.getlist("batteries")
        battery_quantities = request.form.getlist("battery_quantities")
        for battery_type, quantity in zip(battery_types, battery_quantities):
            battery = ScenarioBattery(
                scenario=scenario, battery_type=battery_type, quantity=int(quantity)
            )
            db.add(battery)

        # Update solar panels
        for panel in scenario.solar_panels:
            db.delete(panel)

        solar = ScenarioPhotovoltaic(
            scenario=scenario,
            capacity=float(request.form["solar_capacity"]),
            efficiency=float(request.form["solar_efficiency"])
            / 100,  # Convert from percentage
            quantity=int(request.form["solar_quantity"]),
        )
        db.add(solar)

        # Update wind turbines
        for turbine in scenario.wind_turbines:
            db.delete(turbine)

        wind = ScenarioWindTurbine(
            scenario=scenario,
            capacity=float(request.form["wind_capacity"]),
            cut_in_speed=float(request.form.get("wind_cut_in", 3.0)),
            rated_speed=float(request.form.get("wind_rated", 15.0)),
            quantity=int(request.form["wind_quantity"]),
        )
        db.add(wind)

        # Update grid connection
        for grid in scenario.grid_connections:
            db.delete(grid)

        grid = ScenarioGrid(
            scenario=scenario,
            grid_id=request.form["grid_id"],
            capacity=float(request.form["grid_capacity"]),
        )
        db.add(grid)

        db.commit()
        return redirect(url_for("scenarios.list_scenarios"))

    return render_template(
        "scenario_form.html",
        scenario=scenario,
        available_batteries=battery_factory.get_available_batteries(),
        edit_mode=True,
    )


@bp.route("/<int:id>/activate", methods=["POST"])
def activate_scenario(id):
    db = SessionLocal()
    scenario = db.query(Scenario).get(id)
    scenario.is_active = True
    db.commit()
    return redirect(url_for("scenarios.list_scenarios"))


@bp.route("/<int:id>/deactivate", methods=["POST"])
def deactivate_scenario(id):
    db = SessionLocal()
    scenario = db.query(Scenario).get(id)
    scenario.is_active = False
    db.commit()
    return redirect(url_for("scenarios.list_scenarios"))
