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
        # Shield Wall: Halve incoming damage for 1 round.
        if not self.special_ability_used:
            print("Swordsman used Shield Wall!")
            # This needs to be handled in the game logic, perhaps with a status effect on the unit
            self.special_ability_used = True
            return True
        return False

class Archer(Unit):
    @property
    def unit_type(self):
        return UnitType.ARCHER

    def __init__(self, player):
        super().__init__(player, health=80, attack_power=25, movement_speed=1)

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

    def use_special_ability(self, **kwargs):
        # Piercing Shot: Hit two enemies in a line.
        if not self.special_ability_used:
             print("Archer used Piercing Shot!")
             # Needs implementation in game logic
             self.special_ability_used = True
             return True
        return False

class Rider(Unit):
    @property
    def unit_type(self):
        return UnitType.RIDER

    def __init__(self, player):
        super().__init__(player, health=120, attack_power=35, movement_speed=2)

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

    def use_special_ability(self, **kwargs):
        # Charge: move multiple fields and attack
        if not self.special_ability_used:
            print("Rider used Charge!")
            # Needs implementation in game logic
            self.special_ability_used = True
            return True
        return False
