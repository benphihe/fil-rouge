import pygame
from constants import *

class Obstacle:
    def __init__(self, x, y, width, height, obstacle_type="WALL", rotation=0):
        if isinstance(x, float):
            x = int(x * WINDOW_WIDTH)
        if isinstance(y, float):
            y = int(y * WINDOW_HEIGHT)
        if isinstance(width, float):
            width = int(width * WINDOW_WIDTH)
        if isinstance(height, float):
            height = int(height * WINDOW_HEIGHT)
            
        self.original_rect = pygame.Rect(x, y, width, height)
        self.rect = self.original_rect.copy()
        self.type = obstacle_type
        self.rotation = rotation
        self.surface = None
        self.rotated_surface = None
        
        # Définition des propriétés selon le type
        if obstacle_type == "WALL":
            self.color = (128, 128, 128)  # Gris
            self.blocks_movement = True
            self.blocks_bullets = True
        elif obstacle_type == "SLOW":
            self.color = (0, 128, 128)  # Cyan foncé
            self.blocks_movement = False
            self.blocks_bullets = False
            self.slow_factor = 0.5
            
        # Création de la surface de l'obstacle
        self.update_surface()
            
    def update_surface(self):
        # Création d'une surface pour l'obstacle
        self.surface = pygame.Surface((self.original_rect.width, self.original_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(self.surface, self.color, self.surface.get_rect())
        
        if self.rotation != 0:
            # Rotation de la surface
            self.rotated_surface = pygame.transform.rotate(self.surface, self.rotation)
            # Mise à jour du rect pour la collision
            self.rect = self.rotated_surface.get_rect(center=self.original_rect.center)
        else:
            self.rotated_surface = self.surface
            self.rect = self.original_rect
            
    def draw(self, screen):
        screen.blit(self.rotated_surface, self.rect)
        
    def draw_preview(self, screen, preview_rect):
        # Calcul des facteurs d'échelle
        scale_x = preview_rect.width / WINDOW_WIDTH
        scale_y = preview_rect.height / WINDOW_HEIGHT
        
        # Création d'une version mise à l'échelle de l'obstacle
        preview_x = preview_rect.x + int(self.original_rect.x * scale_x)
        preview_y = preview_rect.y + int(self.original_rect.y * scale_y)
        preview_width = max(1, int(self.original_rect.width * scale_x))
        preview_height = max(1, int(self.original_rect.height * scale_y))
        
        if self.rotation != 0:
            # Création d'une surface mise à l'échelle
            preview_surface = pygame.Surface((preview_width, preview_height), pygame.SRCALPHA)
            pygame.draw.rect(preview_surface, self.color, preview_surface.get_rect())
            rotated_preview = pygame.transform.rotate(preview_surface, self.rotation)
            preview_rect = rotated_preview.get_rect(center=(preview_x + preview_width//2, preview_y + preview_height//2))
            screen.blit(rotated_preview, preview_rect)
        else:
            pygame.draw.rect(screen, self.color, (preview_x, preview_y, preview_width, preview_height))
        
    def affect_movement(self, dx, dy):
        if self.type == "SLOW":
            return dx * self.slow_factor, dy * self.slow_factor
        return dx, dy
        
class ObstacleManager:
    def __init__(self, map_type=None):
        self.obstacles = []
        if map_type:
            from maps import MapManager
            self.obstacles = MapManager.create_obstacles(map_type, WINDOW_WIDTH, WINDOW_HEIGHT)
        else:
            self.create_default_layout()
        
    def create_default_layout(self):
        # Murs centraux
        self.obstacles.extend([
            Obstacle(WINDOW_WIDTH//2 - 20, WINDOW_HEIGHT//4, 40, WINDOW_HEIGHT//4),
            Obstacle(WINDOW_WIDTH//2 - 20, WINDOW_HEIGHT*3//4 - WINDOW_HEIGHT//4, 40, WINDOW_HEIGHT//4)
        ])
        
        # Zones de ralentissement
        self.obstacles.extend([
            Obstacle(WINDOW_WIDTH//4, WINDOW_HEIGHT//4, 100, 100, "SLOW"),
            Obstacle(WINDOW_WIDTH*3//4 - 100, WINDOW_HEIGHT*3//4 - 100, 100, 100, "SLOW")
        ])
        
        # Murs latéraux
        wall_thickness = 20
        wall_length = 150
        self.obstacles.extend([
            # Côté gauche
            Obstacle(100, 100, wall_thickness, wall_length),
            Obstacle(100, WINDOW_HEIGHT - 100 - wall_length, wall_thickness, wall_length),
            # Côté droit
            Obstacle(WINDOW_WIDTH - 100 - wall_thickness, 100, wall_thickness, wall_length),
            Obstacle(WINDOW_WIDTH - 100 - wall_thickness, 
                    WINDOW_HEIGHT - 100 - wall_length, wall_thickness, wall_length)
        ])
        
    def check_collision(self, rect):
        for obstacle in self.obstacles:
            if obstacle.blocks_movement and rect.colliderect(obstacle.rect):
                return True
        return False
        
    def check_bullet_collision(self, bullet_rect):
        for obstacle in self.obstacles:
            if obstacle.blocks_bullets and bullet_rect.colliderect(obstacle.rect):
                return True
        return False
        
    def get_movement_modifier(self, rect):
        dx, dy = 1.0, 1.0
        for obstacle in self.obstacles:
            if rect.colliderect(obstacle.rect):
                dx, dy = obstacle.affect_movement(dx, dy)
        return dx, dy
        
    def draw(self, screen):
        for obstacle in self.obstacles:
            obstacle.draw(screen) 