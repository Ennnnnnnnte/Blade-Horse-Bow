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
    
    def take_damage(self, damage):
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
        super().__init__(player, health=100, attack_power=30, movement_speed=1)
        self.shield_active = False
        self.shield_used = False

    def attack(self, target_unit, board):
        if self.position is None or target_unit.position is None:
            return False
        # Attack range is 1
        dist_x = abs(self.position[0] - target_unit.position[0])
        dist_y = abs(self.position[1] - target_unit.position[1])
        if (dist_x + dist_y) == 1:
            damage_modifier = self.get_damage_modifier(target_unit)
            damage = self.attack_power * damage_modifier
            target_unit.take_damage(damage)
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
        
    def take_damage(self, damage):
        if self.shield_active and not self.shield_used:
            original_damage = damage
            damage = damage // 2  # Halbiere den Schaden
            self.shield_used = True
            self.shield_active = False  # Schild ist nach einem Angriff verbraucht
            print(f"Shield absorbed damage! Reduced from {original_damage} to {damage}")
        super().take_damage(damage)
        
    def end_turn(self):
        """Wird am Ende des Spielerzugs aufgerufen"""
        # Schild bleibt aktiv bis zum ersten Angriff
        pass

class Archer(Unit):
    @property
    def unit_type(self):
        return UnitType.ARCHER

    def __init__(self, player):
        super().__init__(player, health=80, attack_power=25, movement_speed=1)
        self.arrow_storm_target = None
        self.arrow_storm_damage = 20  # Reduzierter Schaden für AOE

    def attack(self, target_unit, board):
        if self.position is None or target_unit.position is None:
            return False
        # Attack range 2-3
        dist_x = abs(self.position[0] - target_unit.position[0])
        dist_y = abs(self.position[1] - target_unit.position[1])
        distance = dist_x + dist_y
        if 2 <= distance <= 3:
            damage_modifier = self.get_damage_modifier(target_unit)
            damage = self.attack_power * damage_modifier
            target_unit.take_damage(damage)
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
                        target_unit.take_damage(damage)
                        targets_hit.append((check_x, check_y, target_unit, damage))
                        print(f"Arrow Storm hit {target_unit.__class__.__name__} at ({check_x}, {check_y}) for {damage} damage!")
        
        self.arrow_storm_target = None
        return targets_hit

class Rider(Unit):
    @property
    def unit_type(self):
        return UnitType.RIDER

    def __init__(self, player):
        super().__init__(player, health=120, attack_power=35, movement_speed=2)
        self.charge_target = None
        self.charge_path = []
        self.charge_damage = 50  # Erhöhter Schaden für Sturmangriff

    def attack(self, target_unit, board):
        if self.position is None or target_unit.position is None:
            return False
        # Melee attack
        dist_x = abs(self.position[0] - target_unit.position[0])
        dist_y = abs(self.position[1] - target_unit.position[1])
        if (dist_x + dist_y) == 1:
            damage_modifier = self.get_damage_modifier(target_unit)
            damage = self.attack_power * damage_modifier
            target_unit.take_damage(damage)
            print(f"Rider attacked {target_unit.__class__.__name__} for {damage} damage.")
            return True
        print("Target is not in range.")
        return False

    def use_special_ability(self, target_x, target_y, board):
        # Charge: move multiple fields and attack
        if not self.special_ability_used:
            if self.position is None:
                return False
                
            # Berechne Pfad zum Ziel
            path = self._calculate_charge_path(target_x, target_y, board)
            if path:
                self.charge_target = (target_x, target_y)
                self.charge_path = path
                self.special_ability_used = True
                print(f"Rider used Charge towards ({target_x}, {target_y})!")
                return True
            else:
                print("Charge target is not reachable!")
                return False
        return False
        
    def _calculate_charge_path(self, target_x, target_y, board):
        """Berechnet den Pfad für den Sturmangriff"""
        if self.position is None:
            return []
            
        start_x, start_y = self.position
        dx = target_x - start_x
        dy = target_y - start_y
        
        # Nur orthogonale Bewegung
        if dx != 0 and dy != 0:
            return []  # Keine diagonalen Sturmangriffe
            
        # Maximale Reichweite für Sturmangriff
        max_charge_distance = 4
        
        if abs(dx) > max_charge_distance or abs(dy) > max_charge_distance:
            return []  # Zu weit
            
        path = []
        current_x, current_y = start_x, start_y
        
        # Bewege sich Schritt für Schritt zum Ziel
        while current_x != target_x or current_y != target_y:
            if current_x < target_x:
                current_x += 1
            elif current_x > target_x:
                current_x -= 1
            elif current_y < target_y:
                current_y += 1
            elif current_y > target_y:
                current_y -= 1
                
            # Prüfe, ob das Feld frei ist
            if board.get_unit_at(current_x, current_y) is not None:
                return []  # Pfad blockiert
                
            path.append((current_x, current_y))
            
        return path
        
    def execute_charge(self, board):
        """Führt den Sturmangriff aus"""
        if not self.charge_path or not self.charge_target:
            return False
            
        # Bewege zur letzten Position im Pfad
        final_x, final_y = self.charge_path[-1]
        if board.move_unit(self, final_x, final_y):
            print(f"Rider charged to ({final_x}, {final_y})!")
            
            # Angriff am Ziel
            target_x, target_y = self.charge_target
            target_unit = board.get_unit_at(target_x, target_y)
            
            if target_unit and target_unit.player != self.player:
                # Erhöhter Schaden für Sturmangriff
                damage_modifier = self.get_damage_modifier(target_unit)
                damage = int(self.charge_damage * damage_modifier)
                target_unit.take_damage(damage)
                print(f"Charge attack hit {target_unit.__class__.__name__} for {damage} damage!")
                
                # Entferne besiegte Einheit
                if target_unit.health == 0:
                    target_unit.player.remove_unit(target_unit)
                    board.grid[target_y][target_x] = None
                    
        self.charge_target = None
        self.charge_path = []
        return True
