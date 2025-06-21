import pygame
import math
import time

class Animation:
    def __init__(self, duration=0.5):
        self.start_time = time.time()
        self.duration = duration
        self.finished = False

    def update(self):
        current_time = time.time()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            self.finished = True
            return 1.0
        return elapsed / self.duration

class MeleeAttackAnimation(Animation):
    def __init__(self, start_pos, target_pos, color=(255, 255, 0)):
        super().__init__(duration=0.4)
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.color = color
        
        # Berechne Richtung und Winkel
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle = math.atan2(dy, dx)
        
    def draw(self, screen, square_size):
        if self.finished:
            return
            
        progress = self.update()
        
        # Startposition in Pixeln (Mittelpunkt der Figur)
        center_x = self.start_pos[0] * square_size + square_size // 2
        center_y = self.start_pos[1] * square_size + square_size // 2
        
        # Schwingende Animation (0 -> 180 Grad)
        swing_angle = progress * math.pi
        
        # Schwert außerhalb der Figur positionieren
        sword_distance = square_size * 0.6
        
        # Position des Schwertes berechnen (außerhalb der Figur in Richtung Ziel)
        sword_x = center_x + math.cos(self.angle) * sword_distance
        sword_y = center_y + math.sin(self.angle) * sword_distance
        
        # Längliches Rechteck für das Schwert
        sword_length = square_size * 0.8
        sword_width = square_size * 0.15
        
        # Schwert wie ein Pendel schwingen lassen
        # Das Schwert zeigt immer zur Figur hin
        pendulum_angle = self.angle + swing_angle
        
        # Start- und Endpunkt des Schwertes berechnen
        # Das Ende des Schwertes zeigt zur Figur
        sword_end_x = sword_x - math.cos(pendulum_angle) * sword_length
        sword_end_y = sword_y - math.sin(pendulum_angle) * sword_length
        
        # Zeichne das Schwert als Linie
        pygame.draw.line(screen, self.color, 
                        (sword_x, sword_y), 
                        (sword_end_x, sword_end_y), 
                        int(sword_width))

class ArrowAnimation(Animation):
    def __init__(self, start_pos, target_pos, color=(255, 255, 0)):
        super().__init__(duration=0.6)
        self.start_pos = start_pos
        self.target_pos = target_pos
        self.color = color
        
        # Berechne Richtung
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        self.angle = math.atan2(dy, dx)
        
    def draw(self, screen, square_size):
        if self.finished:
            return
            
        progress = self.update()
        
        # Startposition in Pixeln
        start_x = self.start_pos[0] * square_size + square_size // 2
        start_y = self.start_pos[1] * square_size + square_size // 2
        
        # Endposition in Pixeln
        end_x = self.target_pos[0] * square_size + square_size // 2
        end_y = self.target_pos[1] * square_size + square_size // 2
        
        # Aktuelle Position (linear interpolated)
        current_x = start_x + (end_x - start_x) * progress
        current_y = start_y + (end_y - start_y) * progress
        
        # Pfeil zeichnen (kleines Rechteck)
        arrow_length = square_size * 0.3
        arrow_width = square_size * 0.1
        
        # Rechteck um die aktuelle Position rotieren
        points = [
            (-arrow_length//2, -arrow_width//2),
            (arrow_length//2, -arrow_width//2),
            (arrow_length//2, arrow_width//2),
            (-arrow_length//2, arrow_width//2)
        ]
        
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        
        rotated_points = []
        for x, y in points:
            new_x = x * cos_a - y * sin_a + current_x
            new_y = x * sin_a + y * cos_a + current_y
            rotated_points.append((new_x, new_y))
        
        # Zeichne den Pfeil
        if len(rotated_points) >= 3:
            pygame.draw.polygon(screen, self.color, rotated_points)

class HitAnimation(Animation):
    def __init__(self, target_pos):
        super().__init__(duration=0.3)
        self.target_pos = target_pos
        
    def draw(self, screen, square_size):
        if self.finished:
            return
            
        progress = self.update()
        
        # Fade-out Effekt (1.0 -> 0.0)
        alpha = 1.0 - progress
        
        # Zielposition in Pixeln
        x = self.target_pos[0] * square_size
        y = self.target_pos[1] * square_size
        
        # Rotes Highlight mit abnehmender Intensität
        intensity = int(255 * alpha)
        color = (intensity, 0, 0)
        
        rect = pygame.Rect(x, y, square_size, square_size)
        pygame.draw.rect(screen, color, rect)

class ArrowStormAnimation(Animation):
    def __init__(self, target_pos, color=(255, 0, 0)):
        super().__init__(duration=float('inf'))  # Unendliche Dauer
        self.target_pos = target_pos
        self.color = color
        
    def draw(self, screen, square_size):
        if self.finished:
            return
            
        # 3x3 Bereich um das Ziel markieren (dauerhaft)
        target_x, target_y = self.target_pos
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x = target_x + dx
                y = target_y + dy
                
                # Prüfe Grenzen
                if 0 <= x < 9 and 0 <= y < 9:  # 9x9 Spielfeld
                    rect = pygame.Rect(x * square_size, y * square_size, square_size, square_size)
                    
                    # Semi-transparente rote Markierung
                    overlay = pygame.Surface((square_size, square_size))
                    overlay.set_alpha(128)
                    overlay.fill(self.color)
                    screen.blit(overlay, rect.topleft)
                    
                    # Rahmen
                    pygame.draw.rect(screen, self.color, rect, 2)
                    
    def finish(self):
        """Beendet die Animation manuell"""
        self.finished = True

class AnimationManager:
    def __init__(self):
        self.animations = []
        
    def add_animation(self, animation):
        self.animations.append(animation)
        
    def update_and_draw(self, screen, square_size):
        # Alle Animationen aktualisieren und zeichnen
        for animation in self.animations[:]:
            animation.draw(screen, square_size)
            if animation.finished:
                self.animations.remove(animation)
                
    def is_animating(self):
        return len(self.animations) > 0 