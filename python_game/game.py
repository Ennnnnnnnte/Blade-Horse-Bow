from .board import Board
from .player import Player
from .units import Swordsman, Archer, Rider
from .animations import AnimationManager, MeleeAttackAnimation, ArrowAnimation, HitAnimation

class Game:
    def __init__(self):
        self.board = Board()
        self.players = [Player(1, "Player 1"), Player(2, "Player 2")]
        self.current_turn = 0
        self.animation_manager = AnimationManager()
        self._setup_units()

    def _setup_units(self):
        # Player 1 units
        p1 = self.players[0]
        units_p1 = [Swordsman(p1), Archer(p1), Rider(p1)]
        for i, unit in enumerate(units_p1):
            p1.add_unit(unit)
            self.board.place_unit(unit, i * 2 + 1, 0)
        
        # Player 2 units
        p2 = self.players[1]
        units_p2 = [Swordsman(p2), Archer(p2), Rider(p2)]
        for i, unit in enumerate(units_p2):
            p2.add_unit(unit)
            self.board.place_unit(unit, i * 2 + 1, 8)

    def start_game(self):
        while not self._check_game_over():
            self.board.display()
            current_player = self.players[self.current_turn]
            print(f"It's {current_player.name}'s turn.")
            
            self._handle_turn(current_player)

            self.current_turn = (self.current_turn + 1) % 2
        
        winner = self.players[0] if self.players[1].units else self.players[1]
        print(f"Game Over! {winner.name} wins!")

    def _handle_turn(self, player):
        # Rudimentary turn logic
        print("Choose an action: (move, attack, special, pass)")
        action = self._get_player_input("Action: ")

        if action == "pass":
            return

        print("Select a unit (x,y):")
        try:
            x_str, y_str = self._get_player_input("Coordinates: ").split(',')
            x, y = int(x_str), int(y_str)
            unit = self.board.get_unit_at(x,y)
            if not unit or unit.player != player:
                print("Invalid unit selected.")
                self._handle_turn(player) # simple retry
                return
        except (ValueError, IndexError):
            print("Invalid input for coordinates.")
            self._handle_turn(player) # simple retry
            return

        if action == "move":
            self._handle_move(unit)
        elif action == "attack":
            self._handle_attack(unit)
        elif action == "special":
            unit.use_special_ability() # Placeholder
        else:
            print("Invalid action.")
            self._handle_turn(player) # simple retry

    def _handle_move(self, unit):
        print("Enter new coordinates (x,y):")
        try:
            x_str, y_str = self._get_player_input("Coordinates: ").split(',')
            new_x, new_y = int(x_str), int(y_str)

            if unit.position is None:
                print("Unit has no position.") # Should not happen if logic is correct
                return

            # Basic validation for distance
            dist_x = abs(unit.position[0] - new_x)
            dist_y = abs(unit.position[1] - new_y)
            if (dist_x + dist_y) > unit.movement_speed:
                print("Cannot move that far.")
                return

            if self.board.move_unit(unit, new_x, new_y):
                print(f"Moved unit to ({new_x},{new_y})")
            else:
                print("Invalid move.")
        except (ValueError, IndexError):
            print("Invalid input for coordinates.")

    def _handle_attack(self, unit):
        print("Enter target coordinates (x,y):")
        try:
            x_str, y_str = self._get_player_input("Coordinates: ").split(',')
            target_x, target_y = int(x_str), int(y_str)
            target_unit = self.board.get_unit_at(target_x, target_y)

            if not target_unit:
                print("No unit at target position.")
                return

            if target_unit.player == unit.player:
                print("Cannot attack your own unit.")
                return
            
            if unit.attack(target_unit, self.board):
                if target_unit.health == 0:
                    target_unit.player.remove_unit(target_unit)
                    self.board.grid[target_y][target_x] = None
            else:
                 print("Attack failed.")

        except (ValueError, IndexError):
            print("Invalid input for coordinates.")


    def _check_game_over(self):
        return not self.players[0].units or not self.players[1].units

    def _get_player_input(self, prompt):
        return input(prompt).lower().strip()

    def switch_turn(self):
        """Switches the turn to the next player."""
        self.current_turn = (self.current_turn + 1) % 2

    def attempt_move(self, unit, new_x, new_y):
        """
        Versucht, eine Einheit zu bewegen.
        Gibt (True, Nachricht) bei Erfolg und (False, Nachricht) bei Misserfolg zurück.
        """
        if unit.position is None:
            return False, "Einheit hat keine Position."

        dist_x = abs(unit.position[0] - new_x)
        dist_y = abs(unit.position[1] - new_y)
        if (dist_x + dist_y) == 0:
            return False, "Muss zu einem anderen Feld ziehen."
        if (dist_x + dist_y) > unit.movement_speed:
            return False, "Kann sich nicht so weit bewegen."

        if self.board.move_unit(unit, new_x, new_y):
            return True, f"Einheit nach ({new_x},{new_y}) bewegt."
        else:
            return False, "Ungültiger Zug. Position ist möglicherweise besetzt."

    def attempt_attack(self, attacker, target_x, target_y):
        """
        Versucht einen Angriff.
        Gibt (True, Nachricht) bei Erfolg und (False, Nachricht) bei Misserfolg zurück.
        """
        target_unit = self.board.get_unit_at(target_x, target_y)

        if not target_unit:
            return False, "Keine Einheit am Zielort."

        if target_unit.player == attacker.player:
            return False, "Kann eigene Einheit nicht angreifen."
        
        if attacker.attack(target_unit, self.board):
            # Animation basierend auf Einheitentyp hinzufügen
            attacker_pos = attacker.position
            target_pos = (target_x, target_y)
            
            if isinstance(attacker, (Swordsman, Rider)):
                # Melee-Angriff Animation
                self.animation_manager.add_animation(
                    MeleeAttackAnimation(attacker_pos, target_pos)
                )
            elif isinstance(attacker, Archer):
                # Pfeil-Animation
                self.animation_manager.add_animation(
                    ArrowAnimation(attacker_pos, target_pos)
                )
            
            # Hit-Animation für das Ziel
            self.animation_manager.add_animation(
                HitAnimation(target_pos)
            )
            
            message = f"Angriff erfolgreich. {target_unit.__class__.__name__} hat {target_unit.health} HP übrig."
            if target_unit.health == 0:
                target_unit.player.remove_unit(target_unit)
                self.board.grid[target_y][target_x] = None
                message += f" {target_unit.__class__.__name__} wurde besiegt."
            return True, message
        else:
             return False, "Angriff fehlgeschlagen. Ziel möglicherweise außer Reichweite."
