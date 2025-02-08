class Photovoltaic:
    def __init__(self, capacity: float, efficiency: float):
        self.capacity = capacity  # in kW
        self.efficiency = efficiency  # as a decimal (e.g., 0.15 for 15% efficiency)

    def calculate_energy_production(self, sunlight_hours: float) -> float:
        """Calculate the energy produced by the photovoltaic system."""
        return self.capacity * self.efficiency * sunlight_hours

    def __str__(self):
        return f"Photovoltaic System: {self.capacity} kW, {self.efficiency * 100}% efficiency"