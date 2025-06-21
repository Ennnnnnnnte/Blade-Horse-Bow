from .board import Board
from .player import Player
from .units import Swordsman, Archer, Rider
from .animations import AnimationManager, MeleeAttackAnimation, ArrowAnimation, HitAnimation, ArrowStormAnimation

class Game:
    def __init__(self):
        self.board = Board()
        self.players = [Player(1, "Player 1"), Player(2, "Player 2")]
        self.current_turn = 0
        self.animation_manager = AnimationManager()
        self.pending_special_effects = []  # Spezialfähigkeiten, die in der nächsten Runde ausgeführt werden
        self.arrow_storm_effects = []  # Pfeilregen-Effekte, die nach dem Gegnerzug ausgeführt werden
        self.arrow_storm_animation = None  # Referenz auf die Pfeilregen-Animation
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
            self._handle_special(unit)
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

    def _handle_special(self, unit):
        print("Enter target coordinates (x,y):")
        try:
            x_str, y_str = self._get_player_input("Coordinates: ").split(',')
            target_x, target_y = int(x_str), int(y_str)
            result, message = self.attempt_special_ability(unit, target_x, target_y)
            if not result:
                print(message)
        except (ValueError, IndexError):
            print("Invalid input for coordinates.")

    def attempt_special_ability(self, unit, target_x, target_y):
        """
        Versucht eine Spezialfähigkeit zu verwenden.
        Gibt (True, Nachricht) bei Erfolg und (False, Nachricht) bei Misserfolg zurück.
        """
        if unit.special_ability_used:
            return False, "Spezialfähigkeit bereits verbraucht."
            
        if isinstance(unit, Swordsman):
            # Schild hoch - sofort aktiv
            success = unit.use_special_ability()
            if success:
                return True, "Schild hoch aktiviert! Schaden wird für den nächsten Angriff halbiert."
            return False, "Spezialfähigkeit fehlgeschlagen."
            
        elif isinstance(unit, Archer):
            # Pfeilregen - wird nach dem Gegnerzug ausgeführt
            success = unit.use_special_ability(target_x, target_y, self.board)
            if success:
                # Animation für Pfeilregen-Bereich
                self.arrow_storm_animation = ArrowStormAnimation((target_x, target_y))
                self.animation_manager.add_animation(self.arrow_storm_animation)
                self.arrow_storm_effects.append(('arrow_storm', unit))
                return True, f"Pfeilregen vorbereitet auf ({target_x}, {target_y})!"
            return False, "Pfeilregen fehlgeschlagen."
            
        elif isinstance(unit, Rider):
            # Sturmangriff - wird sofort ausgeführt
            success = unit.use_special_ability(target_x, target_y, self.board)
            if success:
                # Führe Sturmangriff aus (ohne Angriffs-Animation)
                charge_success = unit.execute_charge(self.board)
                if charge_success:
                    return True, "Sturmangriff erfolgreich ausgeführt!"
                else:
                    return False, "Sturmangriff fehlgeschlagen."
            return False, "Sturmangriff fehlgeschlagen."
            
        return False, "Unbekannte Spezialfähigkeit."

    def execute_pending_special_effects(self):
        """Führt alle ausstehenden Spezialfähigkeiten aus"""
        effects_to_execute = self.pending_special_effects.copy()
        self.pending_special_effects.clear()
        
        for effect_type, unit in effects_to_execute:
            if effect_type == 'arrow_storm':
                # Beende die Pfeilregen-Animation
                if self.arrow_storm_animation:
                    self.arrow_storm_animation.finish()
                    self.arrow_storm_animation = None
                
                targets_hit = unit.execute_arrow_storm(self.board)
                
                # Animationen für getroffene Ziele
                for x, y, target_unit, damage in targets_hit:
                    self.animation_manager.add_animation(
                        HitAnimation((x, y))
                    )
                    
                    # Entferne besiegte Einheiten
                    if target_unit.health == 0:
                        target_unit.player.remove_unit(target_unit)
                        self.board.grid[y][x] = None

    def execute_arrow_storm_effects(self):
        """Führt alle Pfeilregen-Effekte aus (nach dem Gegnerzug)"""
        effects_to_execute = self.arrow_storm_effects.copy()
        self.arrow_storm_effects.clear()
        
        for effect_type, unit in effects_to_execute:
            if effect_type == 'arrow_storm':
                targets_hit = unit.execute_arrow_storm(self.board)
                
                # Animationen für getroffene Ziele
                for x, y, target_unit, damage in targets_hit:
                    self.animation_manager.add_animation(
                        HitAnimation((x, y))
                    )
                    
                    # Entferne besiegte Einheiten
                    if target_unit.health == 0:
                        target_unit.player.remove_unit(target_unit)
                        self.board.grid[y][x] = None
        
        # Beende die Pfeilregen-Animation nach der Ausführung aller Effekte
        if self.arrow_storm_animation:
            self.arrow_storm_animation.finish()
            self.arrow_storm_animation = None

    def end_turn(self):
        """Beendet den aktuellen Zug und führt Rundenende-Effekte aus"""
        # Beende Effekte für alle Einheiten des aktuellen Spielers
        current_player = self.players[self.current_turn]
        for unit in current_player.units:
            if hasattr(unit, 'end_turn'):
                unit.end_turn()
        
        # Wechsle zum nächsten Spieler
        self.switch_turn()
        
        # Führe ausstehende Spezialfähigkeiten aus (nach dem Zugwechsel)
        self.execute_pending_special_effects()
        
        # Führe Pfeilregen-Effekte aus (nach dem Gegnerzug)
        self.execute_arrow_storm_effects()

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
