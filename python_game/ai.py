import random
from .units import Swordsman, Archer, Rider

class AI:
    def __init__(self, player, difficulty="medium"):
        self.player = player
        self.difficulty = difficulty
        self.game = None
        self.debug = True  # Debug-Modus aktivieren
        
    def set_game(self, game):
        """Setzt das Spiel-Objekt für die KI."""
        self.game = game
        
    def make_turn(self):
        """Führt einen kompletten KI-Zug aus."""
        if not self.game:
            self._debug_print("FEHLER: Kein Spiel-Objekt gesetzt!")
            return False
            
        # Sammle alle verfügbaren Einheiten
        available_units = [unit for unit in self.player.units if unit.position is not None]
        self._debug_print(f"Verfügbare Einheiten: {len(available_units)}")
        
        if not available_units:
            self._debug_print("FEHLER: Keine verfügbaren Einheiten!")
            return False
            
        # Wähle eine Einheit basierend auf der Schwierigkeit
        selected_unit = self._select_unit(available_units)
        if not selected_unit:
            self._debug_print("FEHLER: Keine Einheit ausgewählt!")
            return False
            
        self._debug_print(f"Gewählte Einheit: {selected_unit.__class__.__name__} an Position {selected_unit.position}")
        
        # Führe Aktionen für die ausgewählte Einheit aus
        self._execute_unit_turn(selected_unit)
        
        return True
        
    def _debug_print(self, message):
        """Gibt Debug-Nachrichten aus."""
        if self.debug:
            print(f"KI-DEBUG: {message}")
        
    def _select_unit(self, units):
        """Wählt eine Einheit basierend auf der Schwierigkeit aus."""
        self._debug_print(f"Wähle Einheit aus {len(units)} verfügbaren Einheiten")
        
        if self.difficulty == "easy":
            # Zufällige Auswahl
            selected = random.choice(units)
            self._debug_print(f"Leicht: Zufällig gewählt: {selected.__class__.__name__}")
            return selected
        elif self.difficulty == "medium":
            # Priorisiere Einheiten mit hoher HP und verfügbaren Spezialfähigkeiten
            selected = self._select_best_unit_medium(units)
            self._debug_print(f"Mittel: Gewählt: {selected.__class__.__name__} (HP: {selected.health}/{selected.max_health})")
            return selected
        else:  # hard
            # Komplexe Strategie mit Bewertung aller Faktoren
            selected = self._select_best_unit_hard(units)
            self._debug_print(f"Schwer: Gewählt: {selected.__class__.__name__}")
            return selected
            
    def _select_best_unit_medium(self, units):
        """Wählt die beste Einheit für mittlere Schwierigkeit."""
        best_unit = None
        best_score = -1
        
        for unit in units:
            score = 0
            
            # HP-Bonus
            score += unit.health / unit.max_health * 10
            
            # Spezialfähigkeit verfügbar
            if not unit.special_ability_used:
                score += 5
                
            # Einheitentyp-Bonus
            if isinstance(unit, Archer):
                score += 3  # Bogenschützen sind wertvoll
            elif isinstance(unit, Rider):
                score += 2  # Reiter sind schnell
                
            if score > best_score:
                best_score = score
                best_unit = unit
                
        return best_unit
        
    def _select_best_unit_hard(self, units):
        """Wählt die beste Einheit für hohe Schwierigkeit."""
        best_unit = None
        best_score = -1
        
        for unit in units:
            score = self._evaluate_unit_position(unit)
            
            if score > best_score:
                best_score = score
                best_unit = unit
                
        return best_unit
        
    def _evaluate_unit_position(self, unit):
        """Bewertet die Position und den Zustand einer Einheit."""
        if not unit.position:
            return -1000
            
        score = 0
        
        # Basis-Score basierend auf HP
        score += unit.health / unit.max_health * 15
        
        # Spezialfähigkeit verfügbar
        if not unit.special_ability_used:
            score += 8
            
        # Position bewerten
        x, y = unit.position
        score += self._evaluate_position(x, y, unit)
        
        # Bedrohung durch Gegner bewerten
        score += self._evaluate_threats(unit)
        
        # Chancen für Angriffe bewerten
        score += self._evaluate_attack_opportunities(unit)
        
        return score
        
    def _evaluate_position(self, x, y, unit):
        """Bewertet die Position einer Einheit."""
        score = 0
        
        # Terrain-Bonus
        terrain = self.game.board.get_terrain_at(x, y)
        if terrain.terrain_type.value == "forest":
            score += 3  # Wald gibt Verteidigungsbonus
        elif terrain.terrain_type.value == "healing":
            score += 2  # Heilquelle ist gut
            
        # Zentrale Position (für Kontrolle)
        center_distance = abs(x - 4) + abs(y - 4)
        score += (8 - center_distance) * 0.5
        
        return score
        
    def _evaluate_threats(self, unit):
        """Bewertet Bedrohungen für die Einheit."""
        score = 0
        x, y = unit.position
        
        # Prüfe alle gegnerischen Einheiten
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                # Berechne Distanz
                dist_x = abs(x - enemy_unit.position[0])
                dist_y = abs(y - enemy_unit.position[1])
                distance = max(dist_x, dist_y)
                
                # Bedrohung basierend auf Distanz und Einheitentyp
                if isinstance(enemy_unit, Archer) and distance <= 6:
                    score -= 10  # Bogenschütze in Reichweite
                elif isinstance(enemy_unit, Rider) and distance <= 4:
                    score -= 8   # Reiter in Reichweite
                elif isinstance(enemy_unit, Swordsman) and distance <= 2:
                    score -= 6   # Lanzenträger in Reichweite
                    
        return score
        
    def _evaluate_attack_opportunities(self, unit):
        """Bewertet Angriffsmöglichkeiten der Einheit."""
        score = 0
        
        # Prüfe alle gegnerischen Einheiten
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                # Berechne Distanz
                dist_x = abs(unit.position[0] - enemy_unit.position[0])
                dist_y = abs(unit.position[1] - enemy_unit.position[1])
                distance = max(dist_x, dist_y)
                
                # Angriffsmöglichkeit basierend auf Reichweite
                attack_range = self._get_attack_range(unit)
                if distance <= attack_range:
                    score += 5
                    
                    # Bonus für verwundbare Gegner
                    if enemy_unit.health < enemy_unit.max_health * 0.5:
                        score += 3
                        
                    # Bonus für effektive Einheitenpaarungen
                    score += self._get_type_advantage_bonus(unit, enemy_unit)
                    
        return score
        
    def _get_attack_range(self, unit):
        """Gibt die Angriffsreichweite einer Einheit zurück."""
        if isinstance(unit, Swordsman):
            return 2
        elif isinstance(unit, Archer):
            return 6
        elif isinstance(unit, Rider):
            return 1
        return 1
        
    def _get_type_advantage_bonus(self, unit, enemy_unit):
        """Gibt Bonus für effektive Einheitenpaarungen."""
        if isinstance(unit, Swordsman) and isinstance(enemy_unit, Rider):
            return 3  # Lanzenträger ist stark gegen Reiter
        elif isinstance(unit, Archer) and isinstance(enemy_unit, Swordsman):
            return 3  # Bogenschütze ist stark gegen Lanzenträger
        elif isinstance(unit, Rider) and isinstance(enemy_unit, Archer):
            return 3  # Reiter ist stark gegen Bogenschütze
        return 0
        
    def _execute_unit_turn(self, unit):
        """Führt einen Zug für eine Einheit aus."""
        self._debug_print(f"Führe Zug für {unit.__class__.__name__} aus")
        
        # Priorität 1: Spezialfähigkeit verwenden, wenn sinnvoll
        if not unit.special_ability_used:
            self._debug_print("Prüfe Spezialfähigkeit...")
            if self._should_use_special_ability(unit):
                self._debug_print("Verwende Spezialfähigkeit")
                self._use_special_ability(unit)
                return
            else:
                self._debug_print("Spezialfähigkeit nicht sinnvoll")
                
        # Priorität 2: Angreifen, wenn möglich
        self._debug_print("Prüfe Angriffsmöglichkeiten...")
        if self._should_attack(unit):
            self._debug_print("Führe Angriff aus")
            self._execute_attack(unit)
            return
        else:
            self._debug_print("Keine Angriffsmöglichkeiten")
            
        # Priorität 3: Bewegen
        self._debug_print("Prüfe Bewegungsmöglichkeiten...")
        if self._should_move(unit):
            self._debug_print("Führe Bewegung aus")
            self._execute_movement(unit)
        else:
            self._debug_print("Keine Bewegungsmöglichkeiten - Zug beendet")
            
    def _should_use_special_ability(self, unit):
        """Entscheidet, ob eine Spezialfähigkeit verwendet werden soll."""
        self._debug_print(f"Prüfe Spezialfähigkeit für {unit.__class__.__name__}")
        
        if isinstance(unit, Swordsman):
            # Schild verwenden, wenn in Gefahr
            threatened = self._is_unit_threatened(unit)
            self._debug_print(f"Swordsman bedroht: {threatened}")
            return threatened
        elif isinstance(unit, Archer):
            # Pfeilregen verwenden, wenn mehrere Gegner in Reichweite
            enemies_in_range = self._count_enemies_in_range(unit, 2)
            self._debug_print(f"Archer - Gegner in Reichweite: {enemies_in_range}")
            return enemies_in_range >= 2
        elif isinstance(unit, Rider):
            # Sturmangriff verwenden, wenn ein verwundbarer Gegner erreichbar ist
            has_vulnerable_target = self._has_vulnerable_target_in_range(unit)
            self._debug_print(f"Rider - Verwundbare Ziele: {has_vulnerable_target}")
            return has_vulnerable_target
        return False
        
    def _should_attack(self, unit):
        """Entscheidet, ob angegriffen werden soll."""
        self._debug_print(f"Prüfe Angriffsmöglichkeiten für {unit.__class__.__name__}")
        
        # Prüfe, ob Gegner in Reichweite sind
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                dist_x = abs(unit.position[0] - enemy_unit.position[0])
                dist_y = abs(unit.position[1] - enemy_unit.position[1])
                distance = max(dist_x, dist_y)
                
                attack_range = self._get_attack_range(unit)
                if distance <= attack_range:
                    self._debug_print(f"Gegner {enemy_unit.__class__.__name__} in Reichweite {distance}/{attack_range}")
                    return True
                    
        self._debug_print("Keine Gegner in Reichweite")
        return False
        
    def _should_move(self, unit):
        """Entscheidet, ob sich bewegt werden soll."""
        self._debug_print(f"Prüfe Bewegungsmöglichkeiten für {unit.__class__.__name__}")
        
        # Bewege dich, wenn du bedroht bist oder bessere Position erreichen kannst
        if self._is_unit_threatened(unit):
            self._debug_print("Einheit ist bedroht - Bewegung empfohlen")
            return True
            
        # Prüfe, ob Gegner in Reichweite sind
        has_enemies_in_range = self._has_enemies_in_attack_range(unit)
        if not has_enemies_in_range:
            self._debug_print("Keine Gegner in Reichweite - bewege dich zu Gegnern")
            return True
            
        # Bewege dich zu besseren Positionen
        has_better_position = self._has_better_position_available(unit)
        self._debug_print(f"Bessere Position verfügbar: {has_better_position}")
        return has_better_position
        
    def _is_unit_threatened(self, unit):
        """Prüft, ob eine Einheit bedroht ist."""
        x, y = unit.position
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                dist_x = abs(x - enemy_unit.position[0])
                dist_y = abs(y - enemy_unit.position[1])
                distance = max(dist_x, dist_y)
                
                # Bedrohung basierend auf Einheitentyp und Reichweite
                if isinstance(enemy_unit, Archer) and distance <= 6:
                    return True
                elif isinstance(enemy_unit, Rider) and distance <= 4:
                    return True
                elif isinstance(enemy_unit, Swordsman) and distance <= 2:
                    return True
        return False
        
    def _count_enemies_in_range(self, unit, range_distance):
        """Zählt Gegner in einem bestimmten Bereich."""
        count = 0
        x, y = unit.position
        
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                dist_x = abs(x - enemy_unit.position[0])
                dist_y = abs(y - enemy_unit.position[1])
                distance = max(dist_x, dist_y)
                
                if distance <= range_distance:
                    count += 1
        return count
        
    def _has_vulnerable_target_in_range(self, unit):
        """Prüft, ob verwundbare Ziele in Reichweite sind."""
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                # Prüfe, ob Ziel verwundbar ist (weniger als 50% HP)
                if enemy_unit.health < enemy_unit.max_health * 0.5:
                    return True
        return False
        
    def _has_better_position_available(self, unit):
        """Prüft, ob bessere Positionen verfügbar sind."""
        self._debug_print(f"Prüfe bessere Positionen für {unit.__class__.__name__}")
        
        # Einfache Implementierung: Bewege dich zu Heilquellen oder Wäldern
        reachable = self.game.board.get_reachable_positions_rhombus(unit, unit.movement_speed)
        self._debug_print(f"Erreichbare Positionen: {len(reachable)}")
        
        for x, y in reachable:
            terrain = self.game.board.get_terrain_at(x, y)
            if terrain.terrain_type.value in ["healing", "forest"]:
                self._debug_print(f"Bessere Position gefunden: {terrain.terrain_type.value} bei ({x}, {y})")
                return True
                
        # Wenn keine speziellen Terrain verfügbar sind, bewege dich zum Zentrum
        center_x, center_y = 4, 4
        if (center_x, center_y) in reachable:
            self._debug_print(f"Zentrum erreichbar: ({center_x}, {center_y})")
            return True
            
        # Oder bewege dich zu einer beliebigen erreichbaren Position
        if reachable:
            self._debug_print(f"Beliebige erreichbare Position verfügbar")
            return True
            
        self._debug_print("Keine besseren Positionen verfügbar")
        return False
        
    def _use_special_ability(self, unit):
        """Verwendet eine Spezialfähigkeit."""
        self._debug_print(f"Verwende Spezialfähigkeit für {unit.__class__.__name__}")
        
        if isinstance(unit, Swordsman):
            # Schild aktivieren
            self._debug_print("Aktiviere Schild für Swordsman")
            success, message = self.game.attempt_special_ability(unit, 0, 0)
            self._debug_print(f"Schild-Aktivierung: {success} - {message}")
            
        elif isinstance(unit, Archer):
            # Pfeilregen auf beste Position
            self._debug_print("Suche Ziel für Pfeilregen")
            target = self._find_best_arrow_storm_target(unit)
            if target:
                self._debug_print(f"Pfeilregen auf Position {target}")
                success, message = self.game.attempt_special_ability(unit, target[0], target[1])
                self._debug_print(f"Pfeilregen: {success} - {message}")
            else:
                self._debug_print("Kein gutes Ziel für Pfeilregen gefunden")
                
        elif isinstance(unit, Rider):
            # Sturmangriff auf beste Position
            self._debug_print("Suche Ziel für Sturmangriff")
            target = self._find_best_charge_target(unit)
            if target:
                self._debug_print(f"Sturmangriff auf Position {target}")
                success, message = self.game.attempt_special_ability(unit, target[0], target[1])
                self._debug_print(f"Sturmangriff: {success} - {message}")
            else:
                self._debug_print("Kein gutes Ziel für Sturmangriff gefunden")
                
    def _execute_attack(self, unit):
        """Führt einen Angriff aus."""
        self._debug_print(f"Führe Angriff mit {unit.__class__.__name__} aus")
        best_target = self._find_best_attack_target(unit)
        if best_target:
            self._debug_print(f"Angriff auf Position {best_target}")
            success, message = self.game.attempt_attack(unit, best_target[0], best_target[1])
            self._debug_print(f"Angriff: {success} - {message}")
        else:
            self._debug_print("Kein Angriffsziel gefunden")
            
    def _execute_movement(self, unit):
        """Führt eine Bewegung aus."""
        self._debug_print(f"Führe Bewegung mit {unit.__class__.__name__} aus")
        best_position = self._find_best_movement_target(unit)
        if best_position:
            self._debug_print(f"Bewegung zu Position {best_position}")
            success, message = self.game.attempt_move(unit, best_position[0], best_position[1])
            self._debug_print(f"Bewegung: {success} - {message}")
        else:
            self._debug_print("Keine Bewegungszielposition gefunden")
            
    def _find_best_arrow_storm_target(self, unit):
        """Findet das beste Ziel für Pfeilregen."""
        best_target = None
        best_score = -1
        
        for x in range(self.game.board.size):
            for y in range(self.game.board.size):
                score = 0
                
                # Zähle Gegner im 3x3 Bereich
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        check_x, check_y = x + dx, y + dy
                        if 0 <= check_x < self.game.board.size and 0 <= check_y < self.game.board.size:
                            target_unit = self.game.board.get_unit_at(check_x, check_y)
                            if target_unit and target_unit.player != self.player:
                                score += 1
                                
                if score > best_score:
                    best_score = score
                    best_target = (x, y)
                    
        return best_target if best_score > 0 else None
        
    def _find_best_charge_target(self, unit):
        """Findet das beste Ziel für Sturmangriff."""
        best_target = None
        best_score = -1
        
        for x in range(self.game.board.size):
            for y in range(self.game.board.size):
                score = 0
                
                # Bonus für Positionen mit Gegnern
                target_unit = self.game.board.get_unit_at(x, y)
                if target_unit and target_unit.player != self.player:
                    score += 5
                    
                    # Bonus für verwundbare Gegner
                    if target_unit.health < target_unit.max_health * 0.5:
                        score += 3
                        
                # Bonus für gute Positionen
                terrain = self.game.board.get_terrain_at(x, y)
                if terrain.terrain_type.value == "forest":
                    score += 2
                    
                if score > best_score:
                    best_score = score
                    best_target = (x, y)
                    
        return best_target
        
    def _find_best_attack_target(self, unit):
        """Findet das beste Angriffsziel."""
        best_target = None
        best_score = -1
        
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                # Prüfe Reichweite
                dist_x = abs(unit.position[0] - enemy_unit.position[0])
                dist_y = abs(unit.position[1] - enemy_unit.position[1])
                distance = max(dist_x, dist_y)
                
                if distance <= self._get_attack_range(unit):
                    score = 0
                    
                    # Basis-Score für Angriff
                    score += 5
                    
                    # Bonus für verwundbare Gegner
                    if enemy_unit.health < enemy_unit.max_health * 0.5:
                        score += 3
                        
                    # Bonus für effektive Einheitenpaarungen
                    score += self._get_type_advantage_bonus(unit, enemy_unit)
                    
                    if score > best_score:
                        best_score = score
                        best_target = enemy_unit.position
                        
        return best_target
        
    def _find_best_movement_target(self, unit):
        """Findet die beste Bewegungszielposition."""
        reachable = self.game.board.get_reachable_positions_rhombus(unit, unit.movement_speed)
        best_position = None
        best_score = -1
        
        # Prüfe, ob Gegner in Reichweite sind
        has_enemies_in_range = self._has_enemies_in_attack_range(unit)
        
        for x, y in reachable:
            score = 0
            
            # Priorität 1: Wenn keine Gegner in Reichweite sind, ziehe zu den nächsten Gegnern
            if not has_enemies_in_range:
                closest_enemy_distance = self._get_closest_enemy_distance(x, y)
                # Je näher an Gegnern, desto besser
                score += (10 - closest_enemy_distance) * 2
                self._debug_print(f"Position ({x}, {y}): {score} Punkte (Nähe zu Gegnern)")
            
            # Priorität 2: Terrain-Bonus
            terrain = self.game.board.get_terrain_at(x, y)
            if terrain.terrain_type.value == "forest":
                score += 3  # Verteidigungsbonus
            elif terrain.terrain_type.value == "healing":
                score += 2  # Heilung
                
            # Priorität 3: Position-Bonus (näher zum Zentrum)
            center_distance = abs(x - 4) + abs(y - 4)
            score += (8 - center_distance) * 0.5
            
            # Priorität 4: Sicherheitsbonus (weg von Gegnern, wenn bereits in Reichweite)
            if has_enemies_in_range and not self._is_position_threatened(x, y):
                score += 2
                
            if score > best_score:
                best_score = score
                best_position = (x, y)
                
        self._debug_print(f"Beste Bewegungszielposition: {best_position} mit {best_score} Punkten")
        return best_position
        
    def _get_closest_enemy_distance(self, x, y):
        """Berechnet die Distanz zum nächsten Gegner."""
        closest_distance = 1000
        
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                dist_x = abs(x - enemy_unit.position[0])
                dist_y = abs(y - enemy_unit.position[1])
                distance = max(dist_x, dist_y)
                
                if distance < closest_distance:
                    closest_distance = distance
                    
        return closest_distance
        
    def _is_position_threatened(self, x, y):
        """Prüft, ob eine Position bedroht ist."""
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                dist_x = abs(x - enemy_unit.position[0])
                dist_y = abs(y - enemy_unit.position[1])
                distance = max(dist_x, dist_y)
                
                # Bedrohung basierend auf Einheitentyp und Reichweite
                if isinstance(enemy_unit, Archer) and distance <= 6:
                    return True
                elif isinstance(enemy_unit, Rider) and distance <= 4:
                    return True
                elif isinstance(enemy_unit, Swordsman) and distance <= 2:
                    return True
        return False
        
    def _has_enemies_in_attack_range(self, unit):
        """Prüft, ob Gegner in Angriffsreichweite sind."""
        attack_range = self._get_attack_range(unit)
        
        for enemy_player in self.game.players:
            if enemy_player == self.player:
                continue
                
            for enemy_unit in enemy_player.units:
                if not enemy_unit.position:
                    continue
                    
                dist_x = abs(unit.position[0] - enemy_unit.position[0])
                dist_y = abs(unit.position[1] - enemy_unit.position[1])
                distance = max(dist_x, dist_y)
                
                if distance <= attack_range:
                    return True
        return False 