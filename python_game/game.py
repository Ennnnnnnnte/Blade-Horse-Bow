from .board import Board
from .player import Player
from .units import Swordsman, Archer, Rider
from .animations import AnimationManager, MeleeAttackAnimation, ArrowAnimation, HitAnimation, ArrowStormAnimation, MovementAnimation
from .ai import AI

class Game:
    def __init__(self, game_mode="multiplayer", ai_difficulty="medium"):
        self.board = Board()
        self.players = [Player(1, "Player 1"), Player(2, "Player 2")]
        self.current_turn = 0
        self.animation_manager = AnimationManager()
        self.pending_special_effects = []  # Spezialfähigkeiten, die in der nächsten Runde ausgeführt werden
        self.arrow_storm_effects = []  # Pfeilregen-Effekte, die nach dem Gegnerzug ausgeführt werden
        self.delayed_arrow_storm_effects = []  # Pfeilregen-Effekte, die erst nach dem kompletten Gegnerzug ausgeführt werden
        self.arrow_storm_animations = []  # Liste aller aktiven Pfeilregen-Animationen
        self.turn_switch_count = 0  # Zähler für Zugwechsel
        self.last_arrow_storm_player = None  # Spieler, der den Pfeilregen vorbereitet hat
        
        # KI-Einstellungen
        self.game_mode = game_mode
        self.ai_difficulty = ai_difficulty
        self.ai = None
        
        if game_mode == "singleplayer":
            # KI für Spieler 2 (Computer)
            self.ai = AI(self.players[1], ai_difficulty)
            self.ai.set_game(self)
            
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
            # Pfeilregen - wird nach dem kompletten Gegnerzug ausgeführt
            success = unit.use_special_ability(target_x, target_y, self.board)
            if success:
                print(f"DEBUG: Pfeilregen vorbereitet auf ({target_x}, {target_y}) von Spieler {unit.player.id}")
                # Animation für Pfeilregen-Bereich
                arrow_storm_anim = ArrowStormAnimation((target_x, target_y))
                self.animation_manager.add_animation(arrow_storm_anim)
                self.arrow_storm_animations.append(arrow_storm_anim)
                self.delayed_arrow_storm_effects.append(('arrow_storm', unit, arrow_storm_anim))
                self.last_arrow_storm_player = unit.player.id
                print(f"DEBUG: Verzögerte Pfeilregen-Effekte in Queue: {len(self.delayed_arrow_storm_effects)}")
                return True, f"Pfeilregen vorbereitet auf ({target_x}, {target_y})!"
            return False, "Pfeilregen fehlgeschlagen."
            
        elif isinstance(unit, Rider):
            # Sturmangriff - wird sofort ausgeführt
            success = unit.use_special_ability(target_x, target_y, self.board)
            if success:
                # Führe Sturmangriff aus
                charge_success = unit.execute_charge(self.board)
                if charge_success:
                    return True, "Sturmangriff erfolgreich ausgeführt!"
                else:
                    # Wenn der Sturmangriff fehlschlägt, setze die Fähigkeit zurück
                    unit.special_ability_used = False
                    unit.charge_target = None
                    unit.charge_path = []
                    return False, "Sturmangriff fehlgeschlagen - Unerwarteter Fehler."
            return False, "Sturmangriff fehlgeschlagen - Ungültiges Ziel."
            
        return False, "Unbekannte Spezialfähigkeit."

    def execute_delayed_arrow_storm_effects(self):
        """Führt alle verzögerten Pfeilregen-Effekte aus (nach dem kompletten Gegnerzug)"""
        if not self.delayed_arrow_storm_effects:
            return
            
        # Führe nur die Effekte aus, die dem aktuellen Spieler gehören
        current_player_id = self.current_turn + 1
        effects_to_execute = []
        remaining_effects = []
        
        for effect in self.delayed_arrow_storm_effects:
            effect_type, unit, animation = effect
            if effect_type == 'arrow_storm' and unit.player.id == current_player_id:
                effects_to_execute.append(effect)
            else:
                remaining_effects.append(effect)
        
        self.delayed_arrow_storm_effects = remaining_effects
        
        if effects_to_execute:
            print(f"DEBUG: Führe {len(effects_to_execute)} verzögerte Pfeilregen-Effekte für Spieler {current_player_id} aus")
            
            for effect_type, unit, animation in effects_to_execute:
                if effect_type == 'arrow_storm':
                    print(f"DEBUG: Führe verzögerten Pfeilregen für {unit.__class__.__name__} aus")
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
            
            # Beende die entsprechenden Pfeilregen-Animationen
            animations_to_finish = [effect[2] for effect in effects_to_execute]
            print(f"DEBUG: Beende {len(animations_to_finish)} Pfeilregen-Animationen")
            for anim in animations_to_finish:
                if anim in self.arrow_storm_animations:
                    anim.finish()
                    self.arrow_storm_animations.remove(anim)
            
            # Wenn keine Pfeilregen-Animationen mehr übrig sind, setze last_arrow_storm_player zurück
            if not self.arrow_storm_animations:
                self.last_arrow_storm_player = None

    def end_turn(self):
        """Beendet den aktuellen Zug und führt Rundenende-Effekte aus"""
        print(f"DEBUG: Ende Zug für Spieler {self.current_turn + 1}")
        # Beende Effekte für alle Einheiten des aktuellen Spielers
        current_player = self.players[self.current_turn]
        for unit in current_player.units:
            if hasattr(unit, 'end_turn'):
                unit.end_turn()
        
        # Wechsle zum nächsten Spieler
        self.switch_turn()
        print(f"DEBUG: Wechsle zu Spieler {self.current_turn + 1}")

    def _check_game_over(self):
        return not self.players[0].units or not self.players[1].units

    def _get_player_input(self, prompt):
        return input(prompt).lower().strip()

    def switch_turn(self):
        """Switches the turn to the next player."""
        old_turn = self.current_turn
        self.current_turn = (self.current_turn + 1) % 2
        self.turn_switch_count += 1
        
        print(f"DEBUG: Zugwechsel von Spieler {old_turn + 1} zu Spieler {self.current_turn + 1}")
        print(f"DEBUG: Turn switch count: {self.turn_switch_count}")
        print(f"DEBUG: Last arrow storm player: {self.last_arrow_storm_player}")
        
        # Führe verzögerte Pfeilregen-Effekte aus, wenn der Spieler wechselt
        # Jeder Pfeilregen wird ausgeführt, wenn der entsprechende Spieler wieder an der Reihe ist
        self.execute_delayed_arrow_storm_effects()

    def attempt_move(self, unit, new_x, new_y):
        """
        Versucht, eine Einheit zu bewegen.
        Gibt (True, Nachricht) bei Erfolg und (False, Nachricht) bei Misserfolg zurück.
        """
        if unit.position is None:
            return False, "Einheit hat keine Position."

        # Prüfe, ob das Ziel erreichbar ist (Rautenform)
        reachable_positions = self.board.get_reachable_positions_rhombus(unit, unit.movement_speed)
        if (new_x, new_y) not in reachable_positions:
            return False, "Ziel ist nicht erreichbar."

        old_pos = unit.position
        if self.board.move_unit(unit, new_x, new_y):
            # Füge Bewegungsanimation hinzu
            self.animation_manager.add_animation(
                MovementAnimation(old_pos, (new_x, new_y), unit)
            )
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
        
        # Prüfe Sichtlinie für Bogenschützen
        if isinstance(attacker, Archer) and attacker.position is not None:
            if not self.board._has_line_of_sight(attacker.position[0], attacker.position[1], target_x, target_y):
                return False, "Sichtlinie blockiert (Berg im Weg)."
        
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

    def attack_unit(self, attacking_unit, target_unit):
        """Führt einen Angriff zwischen zwei Einheiten aus."""
        current_player = self.players[self.current_turn]
        if attacking_unit.player != current_player:
            print("It's not your turn!")
            return False
            
        if attacking_unit.special_ability_used:
            print("Unit has already used its special ability this turn!")
            return False
            
        # Führe den Angriff aus
        success = attacking_unit.attack(target_unit, self.board)
        
        if success:
            # Prüfe, ob die Ziel-Einheit besiegt wurde
            if target_unit.health <= 0:
                # Entferne die Einheit vom Brett
                if target_unit.position:
                    self.board.grid[target_unit.position[1]][target_unit.position[0]] = None
                    target_unit.position = None
                    
                # Entferne die Einheit aus der Spieler-Liste
                if target_unit in target_unit.player.units:
                    target_unit.player.units.remove(target_unit)
                    
                print(f"{target_unit.__class__.__name__} from Player {target_unit.player.id} has been defeated!")
                
                # Prüfe, ob das Spiel vorbei ist
                if len(target_unit.player.units) == 0:
                    self.game_over = True
                    self.winner = current_player
                    print(f"Player {self.winner.id} wins!")
        
        return success
