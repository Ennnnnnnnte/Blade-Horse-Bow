import pygame
import sys
import os
from python_game.game import Game
from python_game.menu import Menu, GameState
from python_game.game_ui import GameUI

# --- Konstanten ---
BOARD_SIZE = 9
SQUARE_SIZE = 60
BOARD_WIDTH = BOARD_SIZE * SQUARE_SIZE
BOARD_HEIGHT = BOARD_SIZE * SQUARE_SIZE
UI_HEIGHT = 150
WINDOW_WIDTH = BOARD_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT + UI_HEIGHT
GRID_COLOR = (50, 50, 50)
PLAYER1_COLOR = (0, 150, 255)  # Blau
PLAYER2_COLOR = (255, 50, 50)   # Rot
HIGHLIGHT_COLOR = (255, 255, 0) # Gelb

# Farben für Einheitentypen als Fallback
UNIT_COLORS = {
    "Swordsman": (200, 200, 200), # Grau
    "Archer": (0, 255, 0),       # Grün
    "Rider": (255, 165, 0)      # Orange
}

def load_unit_images():
    """Lädt die Bilder für die Einheiten und skaliert sie."""
    images = {}
    image_names = {
        "Swordsman": "swordsman.png",
        "Archer": "archer.png",
        "Rider": "rider.png"
    }
    for unit_name, file_name in image_names.items():
        path = os.path.join("assets", "images", file_name)
        try:
            image = pygame.image.load(path).convert_alpha()
            images[unit_name] = pygame.transform.scale(image, (SQUARE_SIZE, SQUARE_SIZE))
        except pygame.error:
            print(f"Warnung: Bild für '{unit_name}' nicht gefunden unter '{path}'.")
            images[unit_name] = None
    return images

def draw_grid(screen):
    """Zeichnet das Gitter."""
    for x in range(0, BOARD_WIDTH, SQUARE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, BOARD_HEIGHT))
    for y in range(0, BOARD_HEIGHT, SQUARE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (BOARD_WIDTH, y))

def draw_units(screen, board, unit_images):
    """Zeichnet die Einheiten auf dem Brett."""
    for y in range(board.size):
        for x in range(board.size):
            unit = board.get_unit_at(x, y)
            if unit:
                rect = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                unit_name = unit.__class__.__name__
                image = unit_images.get(unit_name)

                if image:
                    # Bild zeichnen
                    screen.blit(image, rect.topleft)
                else:
                    # Fallback: Farbiges Rechteck zeichnen
                    base_color = UNIT_COLORS.get(unit_name, (255, 255, 255))
                    pygame.draw.rect(screen, base_color, rect.inflate(-8, -8))
                
                player_color = PLAYER1_COLOR if unit.player.id == 1 else PLAYER2_COLOR
                pygame.draw.rect(screen, player_color, rect, 4)

def draw_selection(screen, selected_pos):
    """Hebt das ausgewählte Feld hervor."""
    if selected_pos:
        x, y = selected_pos
        rect = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect, 4)

def main():
    """Haupt-Funktion für das Spiel mit GUI."""
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Blade Horse Bow")
    clock = pygame.time.Clock()
    
    # Initialisiere Menü und UI
    menu = Menu(WINDOW_WIDTH, WINDOW_HEIGHT)
    game_ui = GameUI(WINDOW_WIDTH, WINDOW_HEIGHT, BOARD_SIZE, SQUARE_SIZE)
    
    # Spielzustand
    game_state = GameState.MAIN_MENU
    game = None
    unit_images = None
    selected_pos = None
    game_over = False

    running = True
    while running:
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                
            # ESC-Taste für Pause-Menü
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if game_state == GameState.PLAYING:
                    game_state = GameState.PAUSED
                elif game_state == GameState.PAUSED:
                    game_state = GameState.PLAYING

        # Zustandsbehandlung
        if game_state == GameState.MAIN_MENU:
            menu.draw_main_menu(screen)
            action = menu.handle_main_menu_events(events)
            
            if action == 'singleplayer':
                game = Game()
                unit_images = load_unit_images()
                game_state = GameState.PLAYING
                selected_pos = None
                game_over = False
            elif action == 'multiplayer':
                game = Game()
                unit_images = load_unit_images()
                game_state = GameState.PLAYING
                selected_pos = None
                game_over = False
            elif action == 'quit':
                running = False
                
        elif game_state == GameState.PLAYING:
            # Spiellogik
            if game and not game_over and not game.animation_manager.is_animating():
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Prüfe UI-Clicks
                        ui_action = game_ui.handle_click(mouse_pos)
                        if ui_action == "attack" and selected_pos:
                            # Angriffsmodus aktivieren
                            pass  # TODO: Implementiere Angriffsmodus
                        
                        # Prüfe Spielfeld-Clicks (nur wenn Maus über dem Brett ist)
                        if mouse_pos[1] < BOARD_HEIGHT:
                            clicked_x, clicked_y = mouse_pos[0] // SQUARE_SIZE, mouse_pos[1] // SQUARE_SIZE
                            current_player = game.players[game.current_turn]

                            if selected_pos:
                                selected_unit = game.board.get_unit_at(selected_pos[0], selected_pos[1])
                                
                                if not selected_unit:
                                    selected_pos = None
                                    continue

                                target_unit = game.board.get_unit_at(clicked_x, clicked_y)
                                
                                if target_unit and target_unit.player != current_player: # Angriff
                                    success, message = game.attempt_attack(selected_unit, clicked_x, clicked_y)
                                    print(message)
                                    if success:
                                        game.switch_turn()
                                    selected_pos = None
                                elif not target_unit: # Bewegung
                                    success, message = game.attempt_move(selected_unit, clicked_x, clicked_y)
                                    print(message)
                                    if success:
                                        game.switch_turn()
                                    selected_pos = None
                                elif target_unit and target_unit.player == current_player: # Andere eigene Einheit ausgewählt
                                    selected_pos = (clicked_x, clicked_y)
                                else: # Klick auf dieselbe Einheit
                                    selected_pos = None
                            else:
                                # Einheit auswählen
                                unit_to_select = game.board.get_unit_at(clicked_x, clicked_y)
                                if unit_to_select and unit_to_select.player == current_player:
                                    selected_pos = (clicked_x, clicked_y)

            # Rendering
            if game:
                screen.fill((0, 0, 0))
                draw_grid(screen)
                draw_units(screen, game.board, unit_images)
                draw_selection(screen, selected_pos)
                
                # Animationen zeichnen
                game.animation_manager.update_and_draw(screen, SQUARE_SIZE)
                
                # UI zeichnen
                selected_unit = None
                if selected_pos:
                    selected_unit = game.board.get_unit_at(selected_pos[0], selected_pos[1])
                game_ui.draw(screen, selected_unit, game)
                
                # Schadensvorhersage
                mouse_pos = pygame.mouse.get_pos()
                game_ui.draw_damage_prediction(screen, mouse_pos, selected_unit, game)

                # Spielende prüfen
                if not game_over and game._check_game_over():
                    game_over = True
                    winner = game.players[0] if not game.players[1].units else game.players[1]
                    print(f"Game Over! {winner.name} wins!")

                if game_over:
                    font = pygame.font.Font(None, 36)
                    winner = game.players[0] if not game.players[1].units else game.players[1]
                    text = font.render(f"{winner.name} hat gewonnen!", True, (255, 255, 255))
                    text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                    screen.blit(text, text_rect)
                
        elif game_state == GameState.PAUSED:
            # Pause-Menü zeichnen (über dem Spiel)
            menu.draw_pause_menu(screen)
            action = menu.handle_pause_menu_events(events)
            
            if action == 'continue':
                game_state = GameState.PLAYING
            elif action == 'restart':
                game = Game()
                unit_images = load_unit_images()
                selected_pos = None
                game_over = False
                game_state = GameState.PLAYING
            elif action == 'main_menu':
                game_state = GameState.MAIN_MENU

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
