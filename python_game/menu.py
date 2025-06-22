import pygame

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=(150, 150, 150)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                return True
        return False

class GameState:
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    SINGLEPLAYER_MENU = "singleplayer_menu"

class Menu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        
        # Farben
        self.title_color = (255, 255, 255)
        self.button_color = (100, 100, 100)
        self.button_hover_color = (150, 150, 150)
        self.text_color = (255, 255, 255)
        
        # Button-Dimensionen
        self.button_width = 200
        self.button_height = 50
        self.button_spacing = 20
        
        # Schwierigkeitsauswahl
        self.difficulty_buttons = {
            "easy": pygame.Rect(width//2 - self.button_width//2, height//2 - 50, self.button_width, self.button_height),
            "medium": pygame.Rect(width//2 - self.button_width//2, height//2, self.button_width, self.button_height),
            "hard": pygame.Rect(width//2 - self.button_width//2, height//2 + 50, self.button_width, self.button_height),
            "back": pygame.Rect(width//2 - self.button_width//2, height//2 + 100, self.button_width, self.button_height)
        }
        
    def draw_main_menu(self, screen):
        """Zeichnet das Hauptmenü."""
        # Hintergrund
        screen.fill((0, 0, 0))
        
        # Titel
        title = self.font_large.render("Blade Horse Bow", True, self.title_color)
        title_rect = title.get_rect(center=(self.width//2, self.height//3))
        screen.blit(title, title_rect)
        
        # Untertitel
        subtitle = self.font_medium.render("Medieval Turn-Based Strategy", True, self.text_color)
        subtitle_rect = subtitle.get_rect(center=(self.width//2, self.height//3 + 50))
        screen.blit(subtitle, subtitle_rect)
        
        # Buttons
        button_y_start = self.height//2 + 50
        
        # Singleplayer Button
        singleplayer_rect = pygame.Rect(self.width//2 - self.button_width//2, button_y_start, self.button_width, self.button_height)
        color = self.button_hover_color if self._is_mouse_over_button(singleplayer_rect) else self.button_color
        pygame.draw.rect(screen, color, singleplayer_rect)
        pygame.draw.rect(screen, (255, 255, 255), singleplayer_rect, 2)
        
        singleplayer_text = self.font_medium.render("Singleplayer", True, self.text_color)
        singleplayer_text_rect = singleplayer_text.get_rect(center=singleplayer_rect.center)
        screen.blit(singleplayer_text, singleplayer_text_rect)
        
        # Multiplayer Button
        multiplayer_rect = pygame.Rect(self.width//2 - self.button_width//2, button_y_start + self.button_height + self.button_spacing, self.button_width, self.button_height)
        color = self.button_hover_color if self._is_mouse_over_button(multiplayer_rect) else self.button_color
        pygame.draw.rect(screen, color, multiplayer_rect)
        pygame.draw.rect(screen, (255, 255, 255), multiplayer_rect, 2)
        
        multiplayer_text = self.font_medium.render("Multiplayer", True, self.text_color)
        multiplayer_text_rect = multiplayer_text.get_rect(center=multiplayer_rect.center)
        screen.blit(multiplayer_text, multiplayer_text_rect)
        
        # Quit Button
        quit_rect = pygame.Rect(self.width//2 - self.button_width//2, button_y_start + 2 * (self.button_height + self.button_spacing), self.button_width, self.button_height)
        color = self.button_hover_color if self._is_mouse_over_button(quit_rect) else self.button_color
        pygame.draw.rect(screen, color, quit_rect)
        pygame.draw.rect(screen, (255, 255, 255), quit_rect, 2)
        
        quit_text = self.font_medium.render("Quit", True, self.text_color)
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        screen.blit(quit_text, quit_text_rect)
        
    def draw_singleplayer_menu(self, screen):
        """Zeichnet das Singleplayer-Menü mit Schwierigkeitsauswahl."""
        # Hintergrund
        screen.fill((0, 0, 0))
        
        # Titel
        title = self.font_large.render("Singleplayer", True, self.title_color)
        title_rect = title.get_rect(center=(self.width//2, self.height//3))
        screen.blit(title, title_rect)
        
        # Untertitel
        subtitle = self.font_medium.render("Wähle die Schwierigkeit", True, self.text_color)
        subtitle_rect = subtitle.get_rect(center=(self.width//2, self.height//3 + 50))
        screen.blit(subtitle, subtitle_rect)
        
        # Schwierigkeitsbuttons
        for difficulty, rect in self.difficulty_buttons.items():
            color = self.button_hover_color if self._is_mouse_over_button(rect) else self.button_color
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            
            # Button-Text
            if difficulty == "easy":
                text = "Leicht"
                description = "KI macht zufällige Züge"
            elif difficulty == "medium":
                text = "Mittel"
                description = "KI verwendet grundlegende Strategien"
            elif difficulty == "hard":
                text = "Schwer"
                description = "KI verwendet komplexe Strategien"
            else:
                text = "Zurück"
                description = ""
                
            text_surface = self.font_medium.render(text, True, self.text_color)
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
            
            # Beschreibung für Schwierigkeiten
            if description:
                desc_surface = self.font_small.render(description, True, self.text_color)
                desc_rect = desc_surface.get_rect(center=(rect.centerx, rect.bottom + 15))
                screen.blit(desc_surface, desc_rect)
        
    def draw_pause_menu(self, screen):
        """Zeichnet das Pause-Menü."""
        # Semi-transparenter Hintergrund
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Menü-Box
        menu_width = 300
        menu_height = 200
        menu_x = self.width//2 - menu_width//2
        menu_y = self.height//2 - menu_height//2
        
        menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(screen, (50, 50, 50), menu_rect)
        pygame.draw.rect(screen, (255, 255, 255), menu_rect, 2)
        
        # Titel
        title = self.font_medium.render("Pause", True, self.title_color)
        title_rect = title.get_rect(center=(self.width//2, menu_y + 30))
        screen.blit(title, title_rect)
        
        # Buttons
        button_y = menu_y + 80
        
        # Continue Button
        continue_rect = pygame.Rect(menu_x + 50, button_y, 200, 30)
        color = self.button_hover_color if self._is_mouse_over_button(continue_rect) else self.button_color
        pygame.draw.rect(screen, color, continue_rect)
        pygame.draw.rect(screen, (255, 255, 255), continue_rect, 1)
        
        continue_text = self.font_small.render("Weiterspielen", True, self.text_color)
        continue_text_rect = continue_text.get_rect(center=continue_rect.center)
        screen.blit(continue_text, continue_text_rect)
        
        # Restart Button
        restart_rect = pygame.Rect(menu_x + 50, button_y + 40, 200, 30)
        color = self.button_hover_color if self._is_mouse_over_button(restart_rect) else self.button_color
        pygame.draw.rect(screen, color, restart_rect)
        pygame.draw.rect(screen, (255, 255, 255), restart_rect, 1)
        
        restart_text = self.font_small.render("Neustart", True, self.text_color)
        restart_text_rect = restart_text.get_rect(center=restart_rect.center)
        screen.blit(restart_text, restart_text_rect)
        
        # Main Menu Button
        main_menu_rect = pygame.Rect(menu_x + 50, button_y + 80, 200, 30)
        color = self.button_hover_color if self._is_mouse_over_button(main_menu_rect) else self.button_color
        pygame.draw.rect(screen, color, main_menu_rect)
        pygame.draw.rect(screen, (255, 255, 255), main_menu_rect, 1)
        
        main_menu_text = self.font_small.render("Hauptmenü", True, self.text_color)
        main_menu_text_rect = main_menu_text.get_rect(center=main_menu_rect.center)
        screen.blit(main_menu_text, main_menu_text_rect)
        
    def handle_main_menu_events(self, events):
        """Behandelt Events im Hauptmenü."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Button-Positionen
                button_y_start = self.height//2 + 50
                
                # Singleplayer Button
                singleplayer_rect = pygame.Rect(self.width//2 - self.button_width//2, button_y_start, self.button_width, self.button_height)
                if singleplayer_rect.collidepoint(mouse_pos):
                    return "singleplayer_menu"
                
                # Multiplayer Button
                multiplayer_rect = pygame.Rect(self.width//2 - self.button_width//2, button_y_start + self.button_height + self.button_spacing, self.button_width, self.button_height)
                if multiplayer_rect.collidepoint(mouse_pos):
                    return "multiplayer"
                
                # Quit Button
                quit_rect = pygame.Rect(self.width//2 - self.button_width//2, button_y_start + 2 * (self.button_height + self.button_spacing), self.button_width, self.button_height)
                if quit_rect.collidepoint(mouse_pos):
                    return "quit"
        return None
        
    def handle_singleplayer_menu_events(self, events):
        """Behandelt Events im Singleplayer-Menü."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                for difficulty, rect in self.difficulty_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        if difficulty == "back":
                            return "main_menu"
                        else:
                            return f"singleplayer_{difficulty}"
        return None
        
    def handle_pause_menu_events(self, events):
        """Behandelt Events im Pause-Menü."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Button-Positionen
                menu_width = 300
                menu_height = 200
                menu_x = self.width//2 - menu_width//2
                menu_y = self.height//2 - menu_height//2
                button_y = menu_y + 80
                
                # Continue Button
                continue_rect = pygame.Rect(menu_x + 50, button_y, 200, 30)
                if continue_rect.collidepoint(mouse_pos):
                    return "continue"
                
                # Restart Button
                restart_rect = pygame.Rect(menu_x + 50, button_y + 40, 200, 30)
                if restart_rect.collidepoint(mouse_pos):
                    return "restart"
                
                # Main Menu Button
                main_menu_rect = pygame.Rect(menu_x + 50, button_y + 80, 200, 30)
                if main_menu_rect.collidepoint(mouse_pos):
                    return "main_menu"
        return None
        
    def _is_mouse_over_button(self, button_rect):
        """Prüft, ob die Maus über einem Button ist."""
        mouse_pos = pygame.mouse.get_pos()
        return button_rect.collidepoint(mouse_pos) 