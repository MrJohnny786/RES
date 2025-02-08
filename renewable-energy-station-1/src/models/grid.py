class Grid:
    def __init__(self, grid_id, capacity, current_load):
        self.grid_id = grid_id
        self.capacity = capacity
        self.current_load = current_load

    def is_overloaded(self):
        return self.current_load > self.capacity

    def add_load(self, load):
        self.current_load += load

    def remove_load(self, load):
        self.current_load -= load

    def get_status(self):
        return {
            "grid_id": self.grid_id,
            "capacity": self.capacity,
            "current_load": self.current_load,
            "overloaded": self.is_overloaded()
        }