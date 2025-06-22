from enum import Enum

class TerrainType(Enum):
    GRASS = "grass"      # Normales Gras
    MOUNTAIN = "mountain"  # Berg
    WATER = "water"      # Sumpf/Gewässer
    FOREST = "forest"    # Wald
    HEALING = "healing"  # Heilquelle

class Terrain:
    def __init__(self, terrain_type):
        self.terrain_type = terrain_type
        self.color = self._get_color()
        self.symbol = self._get_symbol()
        
    def _get_color(self):
        """Gibt die Farbe für das Terrain zurück."""
        colors = {
            TerrainType.GRASS: (34, 139, 34),      # Dunkelgrün
            TerrainType.MOUNTAIN: (128, 128, 128),  # Grau
            TerrainType.WATER: (0, 0, 255),        # Blau
            TerrainType.FOREST: (0, 100, 0),       # Dunkelgrün
            TerrainType.HEALING: (135, 206, 235)   # Hellblau
        }
        return colors.get(self.terrain_type, (34, 139, 34))
        
    def _get_symbol(self):
        """Gibt das Symbol für das Terrain zurück."""
        symbols = {
            TerrainType.GRASS: "",
            TerrainType.MOUNTAIN: "X",
            TerrainType.WATER: "",
            TerrainType.FOREST: "",
            TerrainType.HEALING: "+"
        }
        return symbols.get(self.terrain_type, "")
        
    def is_passable(self, unit):
        """Prüft, ob eine Einheit das Terrain betreten kann."""
        if self.terrain_type == TerrainType.MOUNTAIN:
            return False  # Berge sind unpassierbar
        elif self.terrain_type == TerrainType.WATER:
            # Bogenschützen können Gewässer nicht betreten
            from .units import Archer
            if isinstance(unit, Archer):
                return False
        return True
        
    def get_movement_penalty(self, unit):
        """Gibt die Bewegungsstrafe für eine Einheit zurück."""
        if self.terrain_type == TerrainType.WATER:
            from .units import Rider
            if isinstance(unit, Rider):
                return 2  # Pferde werden um 2 Felder eingeschränkt
            else:
                return 1  # Andere Einheiten um 1 Feld
        return 0
        
    def get_defense_bonus(self):
        """Gibt den Verteidigungsbonus zurück."""
        if self.terrain_type == TerrainType.FOREST:
            return 0.75  # 3/4 des Schadens (25% weniger Schaden)
        return 1.0
        
    def get_healing_amount(self, unit):
        """Gibt die Heilungsmenge zurück."""
        if self.terrain_type == TerrainType.HEALING:
            return int(unit.max_health * 0.15)  # 15% der max HP
        return 0
        
    def blocks_line_of_sight(self):
        """Prüft, ob das Terrain die Sichtlinie blockiert."""
        return self.terrain_type == TerrainType.MOUNTAIN 