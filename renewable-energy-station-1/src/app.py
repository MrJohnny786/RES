from datetime import datetime
from flask import Flask, render_template
from flask_restful import Api
from src.models.photovoltaic import Photovoltaic
from src.models.wind_turbine import WindTurbine
from src.models.grid import Grid
from src.config.database import init_db, SessionLocal
from src.api import batteries, scenarios  # Import blueprints
from src.schemas import Base, Scenario, Location  # Import models


def create_app():
    app = Flask(__name__)
    api = Api(app)

    # Initialize database first
    init_db()

    # Register blueprints
    app.register_blueprint(batteries.bp)
    app.register_blueprint(scenarios.bp)

    # Initialize components
    app.solar_panel = Photovoltaic(capacity=500, efficiency=0.15)
    app.wind_turbine = WindTurbine(capacity=2000, location="Main Site")
    app.grid = Grid("MAIN-GRID-01", capacity=10000, current_load=0)

    @app.context_processor
    def utility_processor():
        return dict(current_year=datetime.utcnow().year)

    @app.route("/")
    def index():
        return render_template(
            "dashboard.html",
            battery_factory=batteries.battery_factory,
            batteries=batteries.battery_factory.get_available_batteries(),
            solar_status=str(app.solar_panel),
            wind_status=app.wind_turbine.get_status(),
            grid_status=app.grid.get_status(),
        )

    return app


app = create_app()
