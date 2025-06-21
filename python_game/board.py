class Board:
    def __init__(self, size=9):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]

    def place_unit(self, unit, x, y):
        if self.is_valid_position(x, y) and self.grid[y][x] is None:
            self.grid[y][x] = unit
            unit.position = (x, y)
            return True
        return False

    def is_valid_position(self, x, y):
        return 0 <= x < self.size and 0 <= y < self.size

    def get_unit_at(self, x, y):
        if self.is_valid_position(x, y):
            return self.grid[y][x]
        return None

    def move_unit(self, unit, new_x, new_y):
        if not self.is_valid_position(new_x, new_y) or self.grid[new_y][new_x] is not None:
            return False
        
        old_x, old_y = unit.position
        self.grid[old_y][old_x] = None
        self.grid[new_y][new_x] = unit
        unit.position = (new_x, new_y)
        return True

    def display(self):
        for y in range(self.size):
            row_str = "|"
            for x in range(self.size):
                unit = self.grid[y][x]
                if unit:
                    # Show the first letter of the unit type and the player number (1 or 2)
                    player_id = "1" if unit.player.id == 1 else "2"
                    row_str += f" {unit.__class__.__name__[0]}{player_id} |"
                else:
                    row_str += "    |"
            print(row_str)
            print("-" * (self.size * 5 + 1))

