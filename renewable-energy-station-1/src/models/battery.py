import json
from pathlib import Path


class Battery:
    def __init__(
        self,
        model_name: str,
        capacity: float,
        max_charge_rate: float,
        max_discharge_rate: float,
        manufactured_date: str,
        eoc_voltage: float = 4.2,
        charge_level: float = 0.0,
    ):

        self.model_name = model_name
        self.capacity = capacity  # GWh
        self.max_charge_rate = max_charge_rate  # GW
        self.max_discharge_rate = max_discharge_rate  # GW
        self.manufactured_date = manufactured_date
        self.eoc_voltage = eoc_voltage  # V
        self.charge_level = charge_level
        self.cycle_count = 0
        self.status = "Ready"

    def charge(self, amount: float) -> None:
        """Charge the battery with rate limiting"""
        if amount < 0:
            raise ValueError("Charge amount must be positive")
        if amount > self.max_charge_rate:
            raise ValueError(f"Charge rate cannot exceed {self.max_charge_rate} GW")

        prev_level = self.charge_level
        self.charge_level = min(self.capacity, self.charge_level + amount)

        if self.is_full():
            self.end_of_charge()

        if prev_level < self.capacity and self.charge_level >= self.capacity:
            self.cycle_count += 1

    def discharge(self, amount: float) -> None:
        """Discharge the battery with rate limiting"""
        if amount < 0:
            raise ValueError("Discharge amount must be positive")
        if amount > self.max_discharge_rate:
            raise ValueError(
                f"Discharge rate cannot exceed {self.max_discharge_rate} GW"
            )
        if amount > self.charge_level:
            raise ValueError("Not enough charge")

        self.charge_level -= amount

    def get_charge_level(self) -> float:
        return self.charge_level

    def get_status(self) -> dict:
        return {
            "model": self.model_name,
            "capacity": self.capacity,
            "charge_level": self.charge_level,
            "charge_percentage": (self.charge_level / self.capacity) * 100,
            "cycles": self.cycle_count,
            "status": self.status,
        }

    def is_full(self) -> bool:
        return self.charge_level >= self.capacity

    def is_empty(self) -> bool:
        return self.charge_level <= 0.0

    def end_of_charge(self) -> None:
        """End of Charge management"""
        if self.is_full():
            self.status = "Fully Charged - EOC Active"
            # Additional EOC logic like voltage monitoring
            if self.get_voltage() >= self.eoc_voltage:
                self.status = "EOC Complete"

    def get_voltage(self) -> float:
        """Simulate voltage reading"""
        # Simple voltage simulation based on charge level
        min_voltage = 3.2
        voltage_range = self.eoc_voltage - min_voltage
        return min_voltage + (voltage_range * (self.charge_level / self.capacity))


class BatteryFactory:
    def __init__(self, config_path: str = "config/battery_configs.json"):
        self.config_path = Path(config_path)
        self.battery_configs = self._load_configs()

    def _load_configs(self) -> dict:
        """Load battery configurations from JSON file"""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {}

    def get_available_batteries(self) -> list:
        """Return list of available battery configurations"""
        return list(self.battery_configs.keys())

    def create_battery(self, battery_type: str) -> "Battery":
        """Create a battery instance from configuration"""
        if battery_type not in self.battery_configs:
            raise ValueError(f"Unknown battery type: {battery_type}")

        config = self.battery_configs[battery_type]
        return Battery(**config)

    def add_battery_config(self, name: str, config: dict) -> None:
        """Add a new battery configuration"""
        self.battery_configs[name] = config
        # Save to file
        with open(self.config_path, "w") as f:
            json.dump(self.battery_configs, f, indent=4)


# Example batteries:

# 1. Moss Landing Energy Storage (California)
moss_landing = Battery(
    model_name="Vistra Moss Landing",
    capacity=1.6,  # 1.6 GWh
    max_charge_rate=0.4,  # 400 MW
    max_discharge_rate=0.4,
    manufactured_date="2021-08",
    eoc_voltage=4.2,
)

# 2. Hornsdale Power Reserve (Australia)
hornsdale = Battery(
    model_name="Tesla Hornsdale",
    capacity=0.194,  # 194 MWh
    max_charge_rate=0.150,  # 150 MW
    max_discharge_rate=0.193,
    manufactured_date="2017-12",
    eoc_voltage=4.2,
)

# # Create battery factory
# factory = BatteryFactory()

# # List available batteries
# print(factory.get_available_batteries())  # ['moss_landing', 'hornsdale']

# # Create a specific battery
# moss_landing = factory.create_battery("moss_landing")

# # Add a new battery configuration
# new_battery_config = {
#     "model_name": "New Battery Model",
#     "capacity": 2.0,
#     "max_charge_rate": 0.5,
#     "max_discharge_rate": 0.5,
#     "manufactured_date": "2024-01",
#     "eoc_voltage": 4.2,
# }
# factory.add_battery_config("new_battery", new_battery_config)
