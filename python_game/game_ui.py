import pygame
from .units import Swordsman

class GameUI:
    def __init__(self, screen_width, screen_height, board_size, square_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.board_size = board_size
        self.square_size = square_size
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 18)
        
        # UI-Bereich unter dem Spielfeld
        self.ui_area_y = board_size * square_size
        self.ui_height = screen_height - self.ui_area_y
        
        # Buttons
        button_width = 120
        button_height = 40
        button_spacing = 10
        
        self.attack_button = pygame.Rect(
            screen_width - button_width - 20, 
            self.ui_area_y + 20, 
            button_width, 
            button_height
        )
        
        self.special_button = pygame.Rect(
            screen_width - button_width - 20, 
            self.ui_area_y + 20 + button_height + button_spacing, 
            button_width, 
            button_height
        )
        
        # Farben
        self.ui_bg_color = (50, 50, 50)
        self.text_color = (255, 255, 255)
        self.button_color = (100, 100, 100)
        self.button_hover_color = (150, 150, 150)
        self.special_button_color = (150, 100, 50)  # Orange für Spezialfähigkeiten
        self.special_button_hover_color = (200, 150, 100)
        self.damage_text_color = (255, 0, 0)
        self.tooltip_bg_color = (0, 0, 0, 200)
        
        # Spezialfähigkeiten-Tooltips
        self.special_tooltips = {
            "Swordsman": "Schild hoch: Halbiert erlittenen Schaden für 1 Runde",
            "Archer": "Pfeilregen: Trifft Ziel und alle angrenzenden Felder",
            "Rider": "Sturmangriff: Bewegt sich mehrere Felder und greift an"
        }
        
    def draw(self, screen, selected_unit, game):
        # UI-Hintergrund
        ui_rect = pygame.Rect(0, self.ui_area_y, self.screen_width, self.ui_height)
        pygame.draw.rect(screen, self.ui_bg_color, ui_rect)
        pygame.draw.line(screen, (255, 255, 255), (0, self.ui_area_y), (self.screen_width, self.ui_area_y), 2)
        
        if selected_unit:
            self._draw_unit_info(screen, selected_unit)
            self._draw_attack_button(screen)
            self._draw_special_button(screen, selected_unit)
            self._draw_tooltips(screen)
        else:
            # Keine Einheit ausgewählt
            text = self.font_medium.render("Wähle eine Einheit aus", True, self.text_color)
            text_rect = text.get_rect(center=(self.screen_width // 2, self.ui_area_y + self.ui_height // 2))
            screen.blit(text, text_rect)
            
    def _draw_unit_info(self, screen, unit):
        # Einheiten-Informationen
        info_x = 20
        info_y = self.ui_area_y + 20
        
        # Name und Typ
        unit_name = f"{unit.__class__.__name__} (Spieler {unit.player.id})"
        name_text = self.font_medium.render(unit_name, True, self.text_color)
        screen.blit(name_text, (info_x, info_y))
        
        # HP
        hp_text = self.font_small.render(f"HP: {unit.health}/{unit.max_health}", True, self.text_color)
        screen.blit(hp_text, (info_x, info_y + 35))
        
        # Bewegungsreichweite
        move_text = self.font_small.render(f"Bewegung: {unit.movement_speed} Felder", True, self.text_color)
        screen.blit(move_text, (info_x, info_y + 55))
        
        # Angriffskraft
        attack_text = self.font_small.render(f"Angriff: {unit.attack_power}", True, self.text_color)
        screen.blit(attack_text, (info_x, info_y + 75))
        
        # Spezialfähigkeit Status
        if hasattr(unit, 'special_ability_used') and unit.special_ability_used:
            if isinstance(unit, Swordsman) and hasattr(unit, 'shield_active'):
                if unit.shield_active:
                    special_status = self.font_small.render("Schild: Aktiv", True, (0, 255, 0))
                else:
                    special_status = self.font_small.render("Schild: Verbraucht", True, (255, 0, 0))
            else:
                special_status = self.font_small.render("Spezialfähigkeit: Verbraucht", True, (255, 0, 0))
        else:
            special_status = self.font_small.render("Spezialfähigkeit: Verfügbar", True, (0, 255, 0))
        screen.blit(special_status, (info_x, info_y + 95))
        
    def _draw_attack_button(self, screen):
        # Button-Hintergrund
        color = self.button_hover_color if self._is_mouse_over_button(self.attack_button) else self.button_color
        pygame.draw.rect(screen, color, self.attack_button)
        pygame.draw.rect(screen, (255, 255, 255), self.attack_button, 2)
        
        # Button-Text
        text = self.font_small.render("Angreifen", True, self.text_color)
        text_rect = text.get_rect(center=self.attack_button.center)
        screen.blit(text, text_rect)
        
    def _draw_special_button(self, screen, unit):
        # Button-Hintergrund
        color = self.special_button_hover_color if self._is_mouse_over_button(self.special_button) else self.special_button_color
        pygame.draw.rect(screen, color, self.special_button)
        pygame.draw.rect(screen, (255, 255, 255), self.special_button, 2)
        
        # Button-Text
        text = self.font_small.render("Spezial", True, self.text_color)
        text_rect = text.get_rect(center=self.special_button.center)
        screen.blit(text, text_rect)
        
    def _is_mouse_over_button(self, button):
        mouse_pos = pygame.mouse.get_pos()
        return button.collidepoint(mouse_pos)
        
    def handle_click(self, mouse_pos):
        if self.attack_button.collidepoint(mouse_pos):
            return "attack"
        elif self.special_button.collidepoint(mouse_pos):
            return "special"
        return None
        
    def _draw_tooltips(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        
        # Tooltip für Angreifen-Button
        if self.attack_button.collidepoint(mouse_pos):
            self._draw_tooltip(screen, "Normale Angriff", mouse_pos)
            
        # Tooltip für Spezial-Button
        elif self.special_button.collidepoint(mouse_pos):
            self._draw_tooltip(screen, "Spezialfähigkeit verwenden", mouse_pos)
            
    def _draw_tooltip(self, screen, text, pos):
        # Tooltip-Hintergrund
        text_surface = self.font_tiny.render(text, True, (255, 255, 255))
        bg_rect = text_surface.get_rect()
        bg_rect.x = pos[0] + 10
        bg_rect.y = pos[1] - 25
        bg_rect.inflate_ip(10, 5)
        
        # Semi-transparente Hintergrund
        overlay = pygame.Surface((bg_rect.width, bg_rect.height))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, bg_rect.topleft)
        
        # Tooltip-Text
        screen.blit(text_surface, (bg_rect.x + 5, bg_rect.y + 2))
        
    def draw_damage_prediction(self, screen, mouse_pos, selected_unit, game):
        """Zeichnet Schadensvorhersage beim Hovern über Gegner"""
        if not selected_unit:
            return
            
        # Konvertiere Mausposition zu Gitter-Koordinaten
        grid_x = mouse_pos[0] // self.square_size
        grid_y = mouse_pos[1] // self.square_size
        
        # Prüfe, ob Maus über dem Spielfeld ist
        if not (0 <= grid_x < self.board_size and 0 <= grid_y < self.board_size):
            return
            
        target_unit = game.board.get_unit_at(grid_x, grid_y)
        
        # Nur anzeigen, wenn über einem gegnerischen Einheit gehovert wird
        if target_unit and target_unit.player != selected_unit.player:
            # Berechne voraussichtlichen Schaden
            damage_modifier = selected_unit.get_damage_modifier(target_unit)
            predicted_damage = int(selected_unit.attack_power * damage_modifier)
            
            # Zeichne Schadensvorhersage über der Einheit
            damage_text = self.font_small.render(f"{predicted_damage} Schaden", True, self.damage_text_color)
            
            # Position über der Einheit
            text_x = grid_x * self.square_size + self.square_size // 2 - damage_text.get_width() // 2
            text_y = grid_y * self.square_size - 30
            
            # Hintergrund für bessere Lesbarkeit
            bg_rect = damage_text.get_rect()
            bg_rect.x = text_x
            bg_rect.y = text_y
            bg_rect.inflate_ip(10, 5)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            pygame.draw.rect(screen, self.damage_text_color, bg_rect, 2)
            
            screen.blit(damage_text, (text_x, text_y)) 