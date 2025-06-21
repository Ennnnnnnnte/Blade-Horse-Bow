import pygame
import sys
import os
from python_game.game import Game
from python_game.menu import Menu, GameState
from python_game.game_ui import GameUI
from python_game.units import Swordsman

# --- Konstanten ---
BOARD_SIZE = 9
SQUARE_SIZE = 60
BOARD_WIDTH = BOARD_SIZE * SQUARE_SIZE
BOARD_HEIGHT = BOARD_SIZE * SQUARE_SIZE
UI_HEIGHT = 150
WINDOW_WIDTH = BOARD_WIDTH
WINDOW_HEIGHT = BOARD_HEIGHT + UI_HEIGHT
GRID_COLOR = (80, 80, 80)  # Dunkleres Grau
PLAYER1_COLOR = (0, 150, 255)  # Blau
PLAYER2_COLOR = (255, 50, 50)   # Rot
HIGHLIGHT_COLOR = (255, 255, 0) # Gelb
REACHABLE_COLOR = (255, 255, 255)  # Weiß für erreichbare Felder
ATTACKABLE_COLOR = (255, 0, 0)  # Rot für angreifbare Felder

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

def draw_highlights(screen, game, selected_pos, attack_mode):
    """Zeichnet Highlights für erreichbare und angreifbare Felder."""
    if not selected_pos:
        return
        
    selected_unit = game.board.get_unit_at(selected_pos[0], selected_pos[1])
    if not selected_unit:
        return
        
    if attack_mode:
        # Zeige angreifbare Felder in Rot
        attackable_positions = game.board.get_attackable_positions(selected_unit)
        for x, y in attackable_positions:
            rect = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            overlay.set_alpha(80)  # Niedrigere Alpha für bessere Sichtbarkeit
            overlay.fill(ATTACKABLE_COLOR)
            screen.blit(overlay, rect.topleft)
            pygame.draw.rect(screen, ATTACKABLE_COLOR, rect, 3)  # Dickerer Rahmen
    else:
        # Zeige erreichbare Felder in Weiß (Rautenform)
        reachable_positions = game.board.get_reachable_positions_rhombus(selected_unit, selected_unit.movement_speed)
        for x, y in reachable_positions:
            rect = pygame.Rect(x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            overlay = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            overlay.set_alpha(60)  # Niedrigere Alpha für bessere Sichtbarkeit
            overlay.fill(REACHABLE_COLOR)
            screen.blit(overlay, rect.topleft)
            pygame.draw.rect(screen, REACHABLE_COLOR, rect, 3)  # Dickerer Rahmen

def draw_units(screen, board, unit_images, game):
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
                
                # Zeichne Schild-Animation für Lanzenträger
                if isinstance(unit, Swordsman) and unit.shield_active and not unit.shield_used:
                    from python_game.animations import ShieldAnimation
                    shield_anim = ShieldAnimation((x, y))
                    shield_anim.draw(screen, SQUARE_SIZE)

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
    special_mode = False  # Spezialfähigkeiten-Modus
    attack_mode = False  # Angriffsmodus

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
                special_mode = False
                attack_mode = False
            elif action == 'multiplayer':
                game = Game()
                unit_images = load_unit_images()
                game_state = GameState.PLAYING
                selected_pos = None
                game_over = False
                special_mode = False
                attack_mode = False
            elif action == 'quit':
                running = False
                
        elif game_state == GameState.PLAYING:
            # Spiellogik
            # Erlaube Mausklicks auch während der Pfeilregen-Animation
            allow_clicks = (game and not game_over and 
                          (not game.animation_manager.is_animating() or 
                           len(game.arrow_storm_animations) > 0))
            
            if allow_clicks:
                for event in events:
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        
                        # Prüfe UI-Clicks
                        ui_action = game_ui.handle_click(mouse_pos)
                        if ui_action == "attack" and selected_pos and not special_mode:
                            attack_mode = True  # Angriffsmodus
                            special_mode = False
                        elif ui_action == "special" and selected_pos and not attack_mode:
                            special_mode = True  # Spezialfähigkeiten-Modus
                            attack_mode = False
                        
                        # Prüfe Spielfeld-Clicks (nur wenn Maus über dem Brett ist)
                        if mouse_pos[1] < BOARD_HEIGHT:
                            clicked_x, clicked_y = mouse_pos[0] // SQUARE_SIZE, mouse_pos[1] // SQUARE_SIZE
                            current_player = game.players[game.current_turn]

                            if selected_pos:
                                selected_unit = game.board.get_unit_at(selected_pos[0], selected_pos[1])
                                
                                if not selected_unit:
                                    selected_pos = None
                                    special_mode = False
                                    attack_mode = False
                                    continue

                                target_unit = game.board.get_unit_at(clicked_x, clicked_y)
                                
                                if special_mode:
                                    # Spezialfähigkeiten-Modus
                                    success, message = game.attempt_special_ability(selected_unit, clicked_x, clicked_y)
                                    print(message)
                                    if success:
                                        game.end_turn()  # Beende Zug nach Spezialfähigkeit
                                    selected_pos = None
                                    special_mode = False
                                    attack_mode = False
                                elif attack_mode:
                                    # Angriffsmodus
                                    if target_unit and target_unit.player != current_player:
                                        success, message = game.attempt_attack(selected_unit, clicked_x, clicked_y)
                                        print(message)
                                        if success:
                                            game.end_turn()
                                        selected_pos = None
                                        attack_mode = False
                                    else:
                                        # Klick auf leeres Feld oder eigene Einheit - wechsle zu Bewegung
                                        attack_mode = False
                                else:
                                    # Normaler Modus (Bewegung)
                                    if target_unit and target_unit.player != current_player: # Angriff
                                        success, message = game.attempt_attack(selected_unit, clicked_x, clicked_y)
                                        print(message)
                                        if success:
                                            game.end_turn()
                                        selected_pos = None
                                    elif not target_unit: # Bewegung
                                        success, message = game.attempt_move(selected_unit, clicked_x, clicked_y)
                                        print(message)
                                        if success:
                                            game.end_turn()
                                        selected_pos = None
                                    elif target_unit and target_unit.player == current_player: # Andere eigene Einheit ausgewählt
                                        selected_pos = (clicked_x, clicked_y)
                                        special_mode = False
                                        attack_mode = False
                                    else: # Klick auf dieselbe Einheit
                                        selected_pos = None
                                        special_mode = False
                                        attack_mode = False
                            else:
                                # Einheit auswählen
                                unit_to_select = game.board.get_unit_at(clicked_x, clicked_y)
                                if unit_to_select and unit_to_select.player == current_player:
                                    selected_pos = (clicked_x, clicked_y)
                                    special_mode = False
                                    attack_mode = False

            # Rendering
            if game:
                screen.fill((0, 0, 0))
                draw_grid(screen)
                draw_units(screen, game.board, unit_images, game)
                draw_selection(screen, selected_pos)
                
                # Animationen zeichnen
                game.animation_manager.update_and_draw(screen, SQUARE_SIZE)
                
                # Highlights über den Einheiten zeichnen (aber mit niedrigerer Alpha für bessere Sichtbarkeit)
                draw_highlights(screen, game, selected_pos, attack_mode)
                
                # UI zeichnen
                selected_unit = None
                if selected_pos:
                    selected_unit = game.board.get_unit_at(selected_pos[0], selected_pos[1])
                game_ui.draw(screen, selected_unit, game)
                
                # Schadensvorhersage (nur im normalen Modus)
                if not special_mode and not attack_mode:
                    mouse_pos = pygame.mouse.get_pos()
                    game_ui.draw_damage_prediction(screen, mouse_pos, selected_unit, game)
                
                # Spezialfähigkeiten-Modus Anzeige
                if special_mode and selected_unit:
                    font = pygame.font.Font(None, 24)
                    special_text = f"Spezialfähigkeit: {selected_unit.__class__.__name__}"
                    text_surface = font.render(special_text, True, (255, 255, 0))
                    screen.blit(text_surface, (20, WINDOW_HEIGHT - 30))
                
                # Angriffsmodus Anzeige
                if attack_mode and selected_unit:
                    font = pygame.font.Font(None, 24)
                    attack_text = f"Angriff: {selected_unit.__class__.__name__}"
                    text_surface = font.render(attack_text, True, (255, 0, 0))
                    screen.blit(text_surface, (20, WINDOW_HEIGHT - 30))

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
                special_mode = False
                attack_mode = False
                game_state = GameState.PLAYING
            elif action == 'main_menu':
                game_state = GameState.MAIN_MENU

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
