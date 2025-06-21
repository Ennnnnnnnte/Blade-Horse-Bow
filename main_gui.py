import pygame
import sys
import os
from python_game.game import Game

# --- Konstanten ---
BOARD_SIZE = 9
SQUARE_SIZE = 60
WINDOW_WIDTH = BOARD_SIZE * SQUARE_SIZE
WINDOW_HEIGHT = BOARD_SIZE * SQUARE_SIZE
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
    for x in range(0, WINDOW_WIDTH, SQUARE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, WINDOW_HEIGHT))
    for y in range(0, WINDOW_HEIGHT, SQUARE_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WINDOW_WIDTH, y))

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
    font = pygame.font.Font(None, 36)
    
    unit_images = load_unit_images()
    game = Game()
    selected_pos = None  # (x, y) der ausgewählten Einheit
    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Nur Eingaben verarbeiten, wenn keine Animation läuft
            if not game_over and not game.animation_manager.is_animating() and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clicked_x, clicked_y = mouse_pos[0] // SQUARE_SIZE, mouse_pos[1] // SQUARE_SIZE
                current_player = game.players[game.current_turn]

                if selected_pos:
                    selected_unit = game.board.get_unit_at(selected_pos[0], selected_pos[1])
                    
                    # Wenn kein Zug mehr möglich ist
                    if not selected_unit:
                        selected_pos = None
                        continue

                    # Zielfeld angeklickt
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

        screen.fill((0, 0, 0))
        draw_grid(screen)
        draw_units(screen, game.board, unit_images)
        draw_selection(screen, selected_pos)
        
        # Animationen zeichnen (über den Einheiten)
        game.animation_manager.update_and_draw(screen, SQUARE_SIZE)

        if not game_over and game._check_game_over():
            game_over = True
            winner = game.players[0] if not game.players[1].units else game.players[1]
            print(f"Game Over! {winner.name} wins!")

        if game_over:
            winner = game.players[0] if not game.players[1].units else game.players[1]
            text = font.render(f"{winner.name} hat gewonnen!", True, (255, 255, 255))
            text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
