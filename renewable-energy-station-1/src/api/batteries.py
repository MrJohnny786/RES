from flask import Blueprint, render_template, redirect, url_for, request
from src.models.battery import BatteryFactory

bp = Blueprint("batteries", __name__, url_prefix="/batteries")
battery_factory = BatteryFactory("config/battery_configs.json")


@bp.route("/")
def list_batteries():
    return render_template(
        "batteries.html",
        batteries=battery_factory.get_available_batteries(),
        battery_factory=battery_factory,
    )


@bp.route("/<battery_type>")
def battery_detail(battery_type):
    battery = battery_factory.create_battery(battery_type)
    return render_template(
        "battery_detail.html", battery=battery, battery_type=battery_type
    )


@bp.route("/update/<battery_type>", methods=["POST"])
def update_battery(battery_type):
    quantity = request.form.get("quantity", type=int)
    status = request.form.get("status")
    # Update database
    return redirect(url_for("batteries.battery_detail", battery_type=battery_type))
