from flask import Blueprint, render_template, redirect, url_for, request
from src.models.wind_turbine import WindTurbineFactory

bp = Blueprint("air_turbines", __name__, url_prefix="/air_turbines")
turbine_factory = WindTurbineFactory("config/turbines.json")


@bp.route("/")
def list_air_turbines():
    return render_template(
        "air_turbines.html",
        air_turbines=turbine_factory.get_available_turbines(),
        turbine_factory=turbine_factory,
    )


@bp.route("/<turbine_type>")
def turbine_detail(turbine_type):
    turbine = turbine_factory.create_turbine(turbine_type)
    return render_template(
        "turbine_detail.html", turbine=turbine, turbine_type=turbine_type
    )


@bp.route("/update/<turbine_type>", methods=["POST"])
def update_turbine(turbine_type):
    capacity = request.form.get("capacity", type=float)
    rotor_diameter = request.form.get("rotor_diameter", type=float)
    # Update database
    return redirect(url_for("air_turbines.turbine_detail", turbine_type=turbine_type))