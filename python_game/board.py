from .units import Swordsman, Archer, Rider
from .terrain import Terrain, TerrainType

class Board:
    def __init__(self, size=9):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.terrain = [[Terrain(TerrainType.GRASS) for _ in range(size)] for _ in range(size)]
        self._setup_default_terrain()

    def _setup_default_terrain(self):
        """Setzt Standard-Terrain auf dem Spielfeld."""
        # Beispiel-Terrain (kann später angepasst werden)
        # Berge in der Mitte
        self.terrain[4][4] = Terrain(TerrainType.MOUNTAIN)
        self.terrain[3][3] = Terrain(TerrainType.MOUNTAIN)
        self.terrain[5][5] = Terrain(TerrainType.MOUNTAIN)
        
        # Gewässer
        self.terrain[2][2] = Terrain(TerrainType.WATER)
        self.terrain[6][6] = Terrain(TerrainType.WATER)
        self.terrain[2][6] = Terrain(TerrainType.WATER)
        self.terrain[6][2] = Terrain(TerrainType.WATER)
        
        # Wälder
        self.terrain[1][4] = Terrain(TerrainType.FOREST)
        self.terrain[7][4] = Terrain(TerrainType.FOREST)
        self.terrain[4][1] = Terrain(TerrainType.FOREST)
        self.terrain[4][7] = Terrain(TerrainType.FOREST)
        
        # Heilquellen
        self.terrain[0][4] = Terrain(TerrainType.HEALING)
        self.terrain[8][4] = Terrain(TerrainType.HEALING)

    def place_unit(self, unit, x, y):
        """Platziert eine Einheit auf dem Brett."""
        if 0 <= x < self.size and 0 <= y < self.size and self.grid[y][x] is None:
            # Prüfe, ob das Terrain passierbar ist
            if not self.terrain[y][x].is_passable(unit):
                return False
                
            self.grid[y][x] = unit
            unit.position = (x, y)
            
            # Heilung beim Betreten einer Heilquelle
            healing = self.terrain[y][x].get_healing_amount(unit)
            if healing > 0:
                unit.health = min(unit.max_health, unit.health + healing)
                print(f"{unit.__class__.__name__} wurde um {healing} HP geheilt!")
                
            return True
        return False

    def move_unit(self, unit, new_x, new_y):
        """Bewegt eine Einheit zu einer neuen Position."""
        if unit.position is None:
            return False
            
        old_x, old_y = unit.position
        
        # Prüfe, ob das neue Feld frei ist
        if not (0 <= new_x < self.size and 0 <= new_y < self.size):
            return False
            
        if self.grid[new_y][new_x] is not None:
            return False
            
        # Prüfe, ob das Terrain passierbar ist
        if not self.terrain[new_y][new_x].is_passable(unit):
            return False
            
        # Entferne Einheit von alter Position
        self.grid[old_y][old_x] = None
        
        # Platziere Einheit auf neuer Position
        self.grid[new_y][new_x] = unit
        unit.position = (new_x, new_y)
        
        # Heilung beim Betreten einer Heilquelle
        healing = self.terrain[new_y][new_x].get_healing_amount(unit)
        if healing > 0:
            unit.health = min(unit.max_health, unit.health + healing)
            print(f"{unit.__class__.__name__} wurde um {healing} HP geheilt!")
        
        return True

    def get_unit_at(self, x, y):
        """Gibt die Einheit an der Position (x, y) zurück."""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[y][x]
        return None

    def get_terrain_at(self, x, y):
        """Gibt das Terrain an der Position (x, y) zurück."""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.terrain[y][x]
        return Terrain(TerrainType.GRASS)

    def get_reachable_positions(self, unit, max_distance):
        """Berechnet alle erreichbaren Positionen für eine Einheit mit Pfadfindung."""
        if unit.position is None:
            return []
            
        start_x, start_y = unit.position
        reachable = set()
        visited = set()
        
        # BFS (Breadth-First Search) für Pfadfindung
        queue = [(start_x, start_y, 0)]  # (x, y, distance)
        
        while queue:
            x, y, distance = queue.pop(0)
            
            if (x, y) in visited:
                continue
                
            visited.add((x, y))
            
            # Wenn wir die maximale Distanz erreicht haben, stoppe
            if distance >= max_distance:
                continue
                
            # Füge Position zu erreichbaren hinzu (außer Startposition)
            if distance > 0:
                reachable.add((x, y))
            
            # Prüfe alle 8 Richtungen (orthogonal und diagonal)
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                        
                    new_x, new_y = x + dx, y + dy
                    
                    # Prüfe Grenzen
                    if not (0 <= new_x < self.size and 0 <= new_y < self.size):
                        continue
                        
                    # Prüfe, ob Feld blockiert ist
                    if self.grid[new_y][new_x] is not None:
                        continue
                        
                    # Füge zur Queue hinzu
                    if (new_x, new_y) not in visited:
                        queue.append((new_x, new_y, distance + 1))
        
        return list(reachable)

    def get_reachable_positions_rhombus(self, unit, max_distance):
        """Berechnet erreichbare Positionen mit korrekter Bewegungslogik und Terrain."""
        if unit.position is None:
            return []
            
        start_x, start_y = unit.position
        reachable = set()
        
        # Bestimme Bewegungsreichweiten basierend auf Einheitentyp
        if isinstance(unit, Swordsman):
            orthogonal_range = 2  # 2 Felder in alle 4 Hauptrichtungen
            diagonal_range = 1    # 1 Feld diagonal
        elif isinstance(unit, Archer):
            orthogonal_range = 1  # 1 Feld in alle Richtungen
            diagonal_range = 1
        elif isinstance(unit, Rider):
            orthogonal_range = 4  # 4 Felder in alle 4 Hauptrichtungen
            diagonal_range = 2    # 2 Felder diagonal
        else:
            orthogonal_range = max_distance
            diagonal_range = max_distance
        
        # Reduziere Reichweite basierend auf aktuellem Terrain
        current_terrain = self.terrain[start_y][start_x]
        movement_penalty = current_terrain.get_movement_penalty(unit)
        orthogonal_range = max(0, orthogonal_range - movement_penalty)
        diagonal_range = max(0, diagonal_range - movement_penalty)
        
        # Prüfe alle Positionen im Bewegungsradius
        for x in range(self.size):
            for y in range(self.size):
                if (x, y) == (start_x, start_y):
                    continue  # Startposition überspringen
                    
                # Berechne Distanz
                dist_x = abs(start_x - x)
                dist_y = abs(start_y - y)
                
                # Bestimme, ob Position erreichbar ist
                is_reachable = False
                
                if dist_x == 0 and dist_y == 0:
                    continue  # Startposition
                elif dist_x == 0:  # Vertikale Bewegung
                    is_reachable = dist_y <= orthogonal_range
                elif dist_y == 0:  # Horizontale Bewegung
                    is_reachable = dist_x <= orthogonal_range
                elif dist_x == dist_y:  # Diagonale Bewegung
                    is_reachable = dist_x <= diagonal_range
                else:
                    # Kombinierte Bewegung
                    total_steps = dist_x + dist_y
                    is_reachable = total_steps <= orthogonal_range and max(dist_x, dist_y) <= diagonal_range
                
                if is_reachable:
                    # Prüfe, ob der Weg frei ist und das Ziel passierbar ist
                    if self._is_path_clear(start_x, start_y, x, y) and self.terrain[y][x].is_passable(unit):
                        reachable.add((x, y))
        
        return list(reachable)
    
    def _is_path_clear(self, start_x, start_y, end_x, end_y):
        """Prüft, ob der Weg zwischen zwei Punkten frei ist (inklusive Terrain)."""
        # Einfache Linien-Pfadfindung
        dx = end_x - start_x
        dy = end_y - start_y
        
        # Normalisiere die Richtung
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
            
        current_x, current_y = start_x, start_y
        
        # Prüfe jeden Schritt auf dem Weg
        while current_x != end_x or current_y != end_y:
            if current_x != end_x:
                current_x += dx
            if current_y != end_y:
                current_y += dy
                
            # Prüfe, ob das Feld blockiert ist (außer Start- und Endposition)
            if (current_x, current_y) != (start_x, start_y) and (current_x, current_y) != (end_x, end_y):
                # Prüfe Einheiten und unpassierbare Terrain
                if self.grid[current_y][current_x] is not None:
                    return False
                if self.terrain[current_y][current_x].terrain_type == TerrainType.MOUNTAIN:
                    return False
        
        return True

    def get_attackable_positions(self, unit):
        """Berechnet alle angreifbaren Positionen für eine Einheit (mit Sichtlinie)."""
        if unit.position is None:
            return []
            
        start_x, start_y = unit.position
        attackable = []
        
        # Bestimme Angriffsreichweite basierend auf Einheitentyp
        if isinstance(unit, Swordsman):
            range_distance = 2  # Lanze
        elif isinstance(unit, Archer):
            range_distance = 6  # Bogen
        elif isinstance(unit, Rider):
            range_distance = 1  # Nahkampf
        else:
            range_distance = 1
        
        # Prüfe alle Positionen in Reichweite
        for x in range(self.size):
            for y in range(self.size):
                # Berechne Distanz (diagonal)
                dist_x = abs(start_x - x)
                dist_y = abs(start_y - y)
                distance = max(dist_x, dist_y)
                
                if distance <= range_distance:
                    target_unit = self.get_unit_at(x, y)
                    if target_unit and target_unit.player != unit.player:
                        # Prüfe Sichtlinie für Bogenschützen
                        if isinstance(unit, Archer):
                            if not self._has_line_of_sight(start_x, start_y, x, y):
                                continue
                        attackable.append((x, y))
        
        return attackable
    
    def _has_line_of_sight(self, start_x, start_y, end_x, end_y):
        """Prüft, ob eine Sichtlinie zwischen zwei Punkten besteht."""
        # Prüfe Start- und Endposition auf Berge
        if self.terrain[start_y][start_x].blocks_line_of_sight():
            return False
        if self.terrain[end_y][end_x].blocks_line_of_sight():
            return False
            
        # Einfache Linien-Pfadfindung
        dx = end_x - start_x
        dy = end_y - start_y
        
        # Normalisiere die Richtung
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
            
        current_x, current_y = start_x, start_y
        
        # Prüfe jeden Schritt auf dem Weg
        while current_x != end_x or current_y != end_y:
            if current_x != end_x:
                current_x += dx
            if current_y != end_y:
                current_y += dy
                
            # Prüfe, ob das Terrain die Sichtlinie blockiert
            if self.terrain[current_y][current_x].blocks_line_of_sight():
                return False
        
        return True

    def display(self):
        """Zeigt das Brett in der Konsole an."""
        print("   " + " ".join([f" {i} " for i in range(self.size)]))
        print("  " + "-" * (self.size * 4 + 1))
        
        for y in range(self.size):
            row = f"{y} |"
            for x in range(self.size):
                unit = self.grid[y][x]
                terrain = self.terrain[y][x]
                
                if unit is None:
                    # Zeige Terrain
                    symbol = terrain.symbol if terrain.symbol else " "
                    row += f" {symbol} |"
                else:
                    unit_type = unit.__class__.__name__[0]
                    player_id = unit.player.id
                    row += f" {unit_type}{player_id} |"
            print(row)
            print("  " + "-" * (self.size * 4 + 1))

