import pygame

class GameUI:
    def __init__(self, screen_width, screen_height, board_size, square_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.board_size = board_size
        self.square_size = square_size
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # UI-Bereich unter dem Spielfeld
        self.ui_area_y = board_size * square_size
        self.ui_height = screen_height - self.ui_area_y
        
        # Angriffs-Button
        button_width = 120
        button_height = 40
        self.attack_button = pygame.Rect(
            screen_width - button_width - 20, 
            self.ui_area_y + 20, 
            button_width, 
            button_height
        )
        
        # Farben
        self.ui_bg_color = (50, 50, 50)
        self.text_color = (255, 255, 255)
        self.button_color = (100, 100, 100)
        self.button_hover_color = (150, 150, 150)
        self.damage_text_color = (255, 0, 0)
        
    def draw(self, screen, selected_unit, game):
        # UI-Hintergrund
        ui_rect = pygame.Rect(0, self.ui_area_y, self.screen_width, self.ui_height)
        pygame.draw.rect(screen, self.ui_bg_color, ui_rect)
        pygame.draw.line(screen, (255, 255, 255), (0, self.ui_area_y), (self.screen_width, self.ui_area_y), 2)
        
        if selected_unit:
            self._draw_unit_info(screen, selected_unit)
            self._draw_attack_button(screen)
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
        
    def _draw_attack_button(self, screen):
        # Button-Hintergrund
        color = self.button_hover_color if self._is_mouse_over_button() else self.button_color
        pygame.draw.rect(screen, color, self.attack_button)
        pygame.draw.rect(screen, (255, 255, 255), self.attack_button, 2)
        
        # Button-Text
        text = self.font_small.render("Angreifen", True, self.text_color)
        text_rect = text.get_rect(center=self.attack_button.center)
        screen.blit(text, text_rect)
        
    def _is_mouse_over_button(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.attack_button.collidepoint(mouse_pos)
        
    def handle_click(self, mouse_pos):
        if self.attack_button.collidepoint(mouse_pos):
            return "attack"
        return None
        
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