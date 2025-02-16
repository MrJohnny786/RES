import json
from pathlib import Path

class WindTurbine:
    def __init__(self, model_name: str, capacity: float, rotor_diameter: float, manufactured_date: str):
        self.model_name = model_name
        self.capacity = capacity  # Maximum power output in kW
        self.rotor_diameter = rotor_diameter  # Rotor diameter in meters
        self.manufactured_date = manufactured_date
        self.current_output = 0.0  # Current power output in kW

    def generate_power(self, wind_speed: float) -> float:
        """Calculate power generated based on wind speed."""
        if wind_speed < 3:  # Cut-in speed
            self.current_output = 0.0
        elif 3 <= wind_speed <= 15:  # Rated speed
            self.current_output = self.capacity * (wind_speed / 15) ** 3
        else:  # Cut-out speed
            self.current_output = self.capacity

        return self.current_output

    def get_status(self) -> str:
        """Return the status of the wind turbine."""
        return f"Wind Turbine {self.model_name} - Current Output: {self.current_output} kW"


class WindTurbineFactory:
    def __init__(self, config_path: str = "config/turbines.json"):
        self.config_path = Path(config_path)
        self.turbine_configs = self._load_configs()

    def _load_configs(self) -> dict:
        """Load wind turbine configurations from JSON file"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}

    def get_available_turbines(self) -> list:
        """Return list of available wind turbine configurations"""
        return list(self.turbine_configs.keys())

    def create_turbine(self, turbine_type: str) -> "WindTurbine":
        """Create a wind turbine instance from configuration"""
        if turbine_type not in self.turbine_configs:
            raise ValueError(f"Unknown turbine type: {turbine_type}")

        config = self.turbine_configs[turbine_type]
        return WindTurbine(**config)