from datetime import datetime
from flask import Flask, render_template
from flask_restful import Api
from src.models.photovoltaic_factory import PhotovoltaicFactory
from src.models.wind_turbine import WindTurbine
from src.models.grid import Grid
from src.config.database import init_db, SessionLocal
from src.api import batteries, scenarios, photovoltaics  # Import blueprints
from src.schemas import Base, Scenario, Location  # Import models


def create_app():
    app = Flask(__name__)
    api = Api(app)

    # Initialize database first
    init_db()

    # Register blueprints
    app.register_blueprint(batteries.bp)
    app.register_blueprint(scenarios.bp)
    app.register_blueprint(photovoltaics.bp)

    # Initialize components
    pv_factory = PhotovoltaicFactory("/app/config/pv.json")
    # Use first available PV model as default
    app.solar_panel = pv_factory.create_pv(pv_factory.get_available_pvs()[0])
    app.wind_turbine = WindTurbine(capacity=2000, location="Main Site")
    app.grid = Grid("MAIN-GRID-01", capacity=10000, current_load=0)

    @app.context_processor
    def utility_processor():
        return dict(current_year=datetime.utcnow().year)

    @app.route("/")
    def index():
        try:
            available_batteries = batteries.battery_factory.get_available_batteries()
        except Exception as e:
            print(f"Error loading batteries: {e}")
            available_batteries = []

        return render_template(
            "dashboard.html",
            battery_factory=batteries.battery_factory,
            batteries=available_batteries,
            solar_status=str(app.solar_panel),
            wind_status=app.wind_turbine.get_status(),
            grid_status=app.grid.get_status(),
        )

    return app


app = create_app()
