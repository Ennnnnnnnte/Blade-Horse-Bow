from abc import ABC, abstractmethod
from enum import Enum

class UnitType(Enum):
    SWORDSMAN = "Swordsman"
    ARCHER = "Archer"
    RIDER = "Rider"

class Unit(ABC):
    def __init__(self, player, health, attack_power, movement_speed):
        self.player = player
        self.health = health
        self.max_health = health
        self.attack_power = attack_power
        self.movement_speed = movement_speed
        self.position = None
        self.special_ability_used = False

    @property
    @abstractmethod
    def unit_type(self):
        pass

    @abstractmethod
    def attack(self, target_unit, board):
        pass

    @abstractmethod
    def use_special_ability(self, **kwargs):
        pass
    
    def take_damage(self, damage, board=None):
        # Berücksichtige Terrain-Verteidigungsbonus
        if self.position is not None and board is not None:
            terrain = board.get_terrain_at(self.position[0], self.position[1])
            terrain_defense = terrain.get_defense_bonus()
            damage = int(damage * terrain_defense)
            
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            # Let the game handle removal of the unit
            print(f"{self.__class__.__name__} from Player {self.player.id} has been defeated.")

    def get_damage_modifier(self, target_unit):
        if self.unit_type == UnitType.SWORDSMAN and target_unit.unit_type == UnitType.RIDER:
            return 1.5 # Strong against Rider
        if self.unit_type == UnitType.SWORDSMAN and target_unit.unit_type == UnitType.ARCHER:
            return 0.75 # Weak against Archer
            
        if self.unit_type == UnitType.ARCHER and target_unit.unit_type == UnitType.SWORDSMAN:
            return 1.5 # Strong against Swordsman
        if self.unit_type == UnitType.ARCHER and target_unit.unit_type == UnitType.RIDER:
            return 0.75 # Weak against Rider

        if self.unit_type == UnitType.RIDER and target_unit.unit_type == UnitType.ARCHER:
            return 1.5 # Strong against Archer
        if self.unit_type == UnitType.RIDER and target_unit.unit_type == UnitType.SWORDSMAN:
            return 0.75 # Weak against Swordsman
            
        return 1.0

class Swordsman(Unit):
    @property
    def unit_type(self):
        return UnitType.SWORDSMAN

    def __init__(self, player):
        super().__init__(player, health=100, attack_power=30, movement_speed=2)  # 2 Felder Bewegung
        self.shield_active = False
        self.shield_used = False

    def attack(self, target_unit, board):
        if self.position is None or target_unit.position is None:
            return False
        # Attack range is 2 (Lanze)
        dist_x = abs(self.position[0] - target_unit.position[0])
        dist_y = abs(self.position[1] - target_unit.position[1])
        distance = max(dist_x, dist_y)  # Diagonale Distanz
        if distance <= 2:
            damage_modifier = self.get_damage_modifier(target_unit)
            damage = self.attack_power * damage_modifier
            target_unit.take_damage(damage, board)
            print(f"Swordsman attacked {target_unit.__class__.__name__} for {damage} damage.")
            return True
        print("Target is not in range.")
        return False

    def use_special_ability(self, **kwargs):
        # Shield Wall: Halve incoming damage for 1 attack
        if not self.special_ability_used:
            self.shield_active = True
            self.shield_used = False
            self.special_ability_used = True
            print("Swordsman used Shield Wall!")
            return True
        return False
        
    def take_damage(self, damage, board=None):
        if self.shield_active and not self.shield_used:
            original_damage = damage
            damage = damage // 2  # Halbiere den Schaden
            self.shield_used = True
            self.shield_active = False  # Schild ist nach einem Angriff verbraucht
            print(f"Shield absorbed damage! Reduced from {original_damage} to {damage}")
        super().take_damage(damage, board)
        
    def end_turn(self):
        """Wird am Ende des Spielerzugs aufgerufen"""
        # Schild bleibt aktiv bis zum ersten Angriff
        pass

class Archer(Unit):
    @property
    def unit_type(self):
        return UnitType.ARCHER

    def __init__(self, player):
        super().__init__(player, health=80, attack_power=25, movement_speed=1)  # 1 Feld Bewegung
        self.arrow_storm_target = None
        self.arrow_storm_damage = 20  # Reduzierter Schaden für AOE

    def attack(self, target_unit, board):
        if self.position is None or target_unit.position is None:
            return False
        # Attack range 6 (Bogen)
        dist_x = abs(self.position[0] - target_unit.position[0])
        dist_y = abs(self.position[1] - target_unit.position[1])
        distance = max(dist_x, dist_y)  # Diagonale Distanz
        if distance <= 6:
            damage_modifier = self.get_damage_modifier(target_unit)
            damage = self.attack_power * damage_modifier
            target_unit.take_damage(damage, board)
            print(f"Archer attacked {target_unit.__class__.__name__} for {damage} damage.")
            return True
        print("Target is not in range.")
        return False

    def use_special_ability(self, target_x, target_y, board):
        # Arrow Storm: Hit target and adjacent fields
        if not self.special_ability_used:
            # Prüfe, ob das Ziel im Spielfeld ist
            if 0 <= target_x < board.size and 0 <= target_y < board.size:
                self.arrow_storm_target = (target_x, target_y)
                self.special_ability_used = True
                print(f"Archer used Arrow Storm on ({target_x}, {target_y})!")
                return True
            else:
                print("Arrow Storm target is outside the board!")
                return False
        return False
        
    def execute_arrow_storm(self, board):
        """Führt den Pfeilregen aus (wird nach dem Gegnerzug aufgerufen)"""
        if not self.arrow_storm_target:
            return []
            
        target_x, target_y = self.arrow_storm_target
        targets_hit = []
        
        # Ziel und alle angrenzenden Felder (3x3 Bereich)
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_x, check_y = target_x + dx, target_y + dy
                
                # Prüfe Grenzen
                if 0 <= check_x < board.size and 0 <= check_y < board.size:
                    target_unit = board.get_unit_at(check_x, check_y)
                    if target_unit and target_unit.player != self.player:
                        # Reduzierter Schaden für AOE
                        damage_modifier = self.get_damage_modifier(target_unit)
                        damage = int(self.arrow_storm_damage * damage_modifier)
                        target_unit.take_damage(damage, board)
                        targets_hit.append((check_x, check_y, target_unit, damage))
                        print(f"Arrow Storm hit {target_unit.__class__.__name__} at ({check_x}, {check_y}) for {damage} damage!")
        
        self.arrow_storm_target = None
        return targets_hit

class Rider(Unit):
    @property
    def unit_type(self):
        return UnitType.RIDER

    def __init__(self, player):
        super().__init__(player, health=120, attack_power=35, movement_speed=4)  # 4 Felder Bewegung
        self.charge_target = None
        self.charge_path = []
        self.charge_damage = 50  # Erhöhter Schaden für Sturmangriff

    def attack(self, target_unit, board):
        if self.position is None or target_unit.position is None:
            return False
        # Attack range 1 (Radius)
        dist_x = abs(self.position[0] - target_unit.position[0])
        dist_y = abs(self.position[1] - target_unit.position[1])
        distance = max(dist_x, dist_y)  # Diagonale Distanz
        if distance <= 1:
            damage_modifier = self.get_damage_modifier(target_unit)
            damage = self.attack_power * damage_modifier
            target_unit.take_damage(damage, board)
            print(f"Rider attacked {target_unit.__class__.__name__} for {damage} damage.")
            return True
        print("Target is not in range.")
        return False

    def use_special_ability(self, target_x, target_y, board):
        # Charge: move unlimited distance and attack
        if not self.special_ability_used:
            if 0 <= target_x < board.size and 0 <= target_y < board.size:
                self.charge_target = (target_x, target_y)
                self.charge_path = self._calculate_charge_path(target_x, target_y, board)
                self.special_ability_used = True
                print(f"Rider used Charge on ({target_x}, {target_y})!")
                return True
            else:
                print("Charge target is outside the board!")
                return False
        return False
        
    def _calculate_charge_path(self, target_x, target_y, board):
        """Berechnet den Weg für den Sturmangriff (unbegrenzte Distanz)"""
        if self.position is None:
            return []
            
        start_x, start_y = self.position
        path = []
        
        # Einfache Linie zum Ziel (kann durch Einheiten gehen)
        dx = target_x - start_x
        dy = target_y - start_y
        
        # Normalisiere die Richtung
        if dx != 0:
            dx = dx // abs(dx)
        if dy != 0:
            dy = dy // abs(dy)
            
        current_x, current_y = start_x, start_y
        
        while current_x != target_x or current_y != target_y:
            if current_x != target_x:
                current_x += dx
            if current_y != target_y:
                current_y += dy
            path.append((current_x, current_y))
            
        return path
        
    def execute_charge(self, board):
        """Führt den Sturmangriff aus"""
        if not self.charge_target or not self.charge_path:
            return False
            
        target_x, target_y = self.charge_target
        target_unit = board.get_unit_at(target_x, target_y)
        
        # Bewege zur Zielposition (immer möglich bei Sturmangriff)
        if self.charge_path:
            final_x, final_y = self.charge_path[-1]
            board.move_unit(self, final_x, final_y)
            print(f"Rider charged to ({final_x}, {final_y})!")
        
        # Führe Angriff aus, falls eine gegnerische Einheit am Ziel ist
        if target_unit and target_unit.player != self.player:
            damage_modifier = self.get_damage_modifier(target_unit)
            damage = int(self.charge_damage * damage_modifier)
            target_unit.take_damage(damage, board)
            print(f"Charge hit {target_unit.__class__.__name__} for {damage} damage!")
        else:
            print("Charge completed - no enemy at target position.")
        
        self.charge_target = None
        self.charge_path = []
        return True
