class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.units = []

    def add_unit(self, unit):
        self.units.append(unit)

    def remove_unit(self, unit):
        if unit in self.units:
            self.units.remove(unit)
