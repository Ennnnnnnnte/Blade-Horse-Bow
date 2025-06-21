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

class Menu:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Hauptmenü Buttons
        button_width = 200
        button_height = 50
        center_x = screen_width // 2 - button_width // 2
        
        self.main_menu_buttons = {
            'singleplayer': Button(center_x, 200, button_width, button_height, "Singleplayer"),
            'multiplayer': Button(center_x, 270, button_width, button_height, "Multiplayer"),
            'quit': Button(20, screen_height - 70, 120, 40, "Spiel beenden")
        }
        
        # Pause-Menü Buttons (kleiner, zentriert)
        pause_button_width = 150
        pause_button_height = 40
        pause_center_x = screen_width // 2 - pause_button_width // 2
        
        self.pause_menu_buttons = {
            'continue': Button(pause_center_x, 200, pause_button_width, pause_button_height, "Weiter"),
            'restart': Button(pause_center_x, 260, pause_button_width, pause_button_height, "Neustart"),
            'main_menu': Button(pause_center_x, 320, pause_button_width, pause_button_height, "Hauptmenü")
        }
        
    def draw_main_menu(self, screen):
        screen.fill((0, 0, 0))
        
        # Titel
        title = self.font_large.render("Blade Horse Bow", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title, title_rect)
        
        # Buttons zeichnen
        for button in self.main_menu_buttons.values():
            button.draw(screen, self.font_medium)
            
    def draw_pause_menu(self, screen):
        # Semi-transparente Overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Pause-Titel
        title = self.font_medium.render("Spiel pausiert", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title, title_rect)
        
        # Buttons zeichnen
        for button in self.pause_menu_buttons.values():
            button.draw(screen, self.font_small)
            
    def handle_main_menu_events(self, events):
        for event in events:
            for button_name, button in self.main_menu_buttons.items():
                if button.handle_event(event):
                    return button_name
        return None
        
    def handle_pause_menu_events(self, events):
        for event in events:
            for button_name, button in self.pause_menu_buttons.items():
                if button.handle_event(event):
                    return button_name
        return None

class GameState:
    MAIN_MENU = "main_menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over" 