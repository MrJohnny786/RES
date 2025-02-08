from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request
from flask_restful import Api
from pathlib import Path
from src.models.battery import BatteryFactory
from src.models.photovoltaic import Photovoltaic
from src.models.wind_turbine import WindTurbine
from src.models.grid import Grid

app = Flask(__name__)
api = Api(app)

# Initialize components
battery_factory = BatteryFactory("config/battery_configs.json")
solar_panel = Photovoltaic(capacity=500, efficiency=0.15)  # 500kW solar system
wind_turbine = WindTurbine(capacity=2000, location="Main Site")  # 2MW turbine
grid = Grid("MAIN-GRID-01", capacity=10000, current_load=0)  # 10MW grid capacity


@app.context_processor
def utility_processor():
    return dict(current_year=datetime.utcnow().year)


@app.route("/")
def index():
    return render_template(
        "dashboard.html",
        battery_factory=battery_factory,
        batteries=battery_factory.get_available_batteries(),
        solar_status=str(solar_panel),
        wind_status=wind_turbine.get_status(),
        grid_status=grid.get_status(),
    )


@app.route("/batteries")
def batteries():
    return render_template(
        "batteries.html",
        batteries=battery_factory.get_available_batteries(),
        battery_factory=battery_factory,
    )


@app.route("/battery/<battery_type>")
def battery_detail(battery_type):
    battery = battery_factory.create_battery(battery_type)
    return render_template(
        "battery_detail.html", battery=battery, battery_type=battery_type
    )


@app.route("/battery/update/<battery_type>", methods=["POST"])
def update_battery(battery_type):
    quantity = request.form.get("quantity", type=int)
    status = request.form.get("status")
    # Update database
    return redirect(url_for("battery_detail", battery_type=battery_type))


@app.route("/status")
def status():
    """API Status endpoint"""
    return render_template(
        "status.html",
        components={
            "batteries": battery_factory.get_available_batteries(),
            "solar": str(solar_panel),
            "wind": wind_turbine.get_status(),
            "grid": grid.get_status(),
        },
    )


def create_app():
    # Create necessary directories
    Path("config").mkdir(exist_ok=True)

    # Create default battery configs if they don't exist
    config_path = Path("config/battery_configs.json")
    if not config_path.exists():
        default_configs = {
            "moss_landing": {
                "model_name": "Vistra Moss Landing",
                "capacity": 1.6,
                "max_charge_rate": 0.4,
                "max_discharge_rate": 0.4,
                "manufactured_date": "2021-08",
                "eoc_voltage": 4.2,
            },
            "hornsdale": {
                "model_name": "Tesla Hornsdale",
                "capacity": 0.194,
                "max_charge_rate": 0.150,
                "max_discharge_rate": 0.193,
                "manufactured_date": "2017-12",
                "eoc_voltage": 4.2,
            },
        }
        with open(config_path, "w") as f:
            json.dump(default_configs, f, indent=4)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
