from obstacle import Obstacle
from constants import *

class Map:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.obstacles = []
        
    def draw_preview(self, screen, preview_rect):
        # Fond noir
        pygame.draw.rect(screen, BLACK, preview_rect)
        # Bordure blanche
        pygame.draw.rect(screen, WHITE, preview_rect, 2)
        
        # Dessin des obstacles en miniature
        for obstacle in self.obstacles:
            obstacle.draw_preview(screen, preview_rect)

class MapManager:
    @staticmethod
    def get_maps():
        maps = {
            'CLASSIC': Map('Classique', ''),
            'ARENA': Map('Arène', ''),
            'MAZE': Map('Tactique', '')
        }

        # Map Classique - Symétrique avec des obstacles centraux
        maps['CLASSIC'].obstacles = [
            # Mur central
            Obstacle(0.48, 0.2, 0.04, 0.6, "WALL"),
            # Zones de ralentissement symétriques
            Obstacle(0.2, 0.2, 0.15, 0.15, "SLOW"),
            Obstacle(0.65, 0.65, 0.15, 0.15, "SLOW"),
            # Petits murs de protection
            Obstacle(0.15, 0.4, 0.1, 0.05, "WALL"),
            Obstacle(0.75, 0.55, 0.1, 0.05, "WALL")
        ]

        # Map Arène - Configuration simple avec zones stratégiques
        maps['ARENA'].obstacles = [
            # Murs en L inversés de chaque côté
            Obstacle(0.2, 0.2, 0.2, 0.05, "WALL"),  # Haut gauche horizontal
            Obstacle(0.2, 0.2, 0.05, 0.2, "WALL"),  # Haut gauche vertical
            Obstacle(0.6, 0.75, 0.2, 0.05, "WALL"),  # Bas droite horizontal
            Obstacle(0.75, 0.6, 0.05, 0.2, "WALL"),  # Bas droite vertical
            # Zones de ralentissement aux points stratégiques
            Obstacle(0.45, 0.45, 0.1, 0.1, "SLOW"),  # Centre
            Obstacle(0.15, 0.75, 0.1, 0.1, "SLOW"),  # Bas gauche
            Obstacle(0.75, 0.15, 0.1, 0.1, "SLOW")   # Haut droite
        ]

        # Map Tactique - Configuration avec obstacles en diagonale
        maps['MAZE'].obstacles = [
            # Obstacles diagonaux
            Obstacle(0.3, 0.3, 0.05, 0.2, "WALL", 45),    # Haut gauche
            Obstacle(0.65, 0.3, 0.05, 0.2, "WALL", -45),  # Haut droite
            Obstacle(0.3, 0.7, 0.05, 0.2, "WALL", -45),   # Bas gauche
            Obstacle(0.65, 0.7, 0.05, 0.2, "WALL", 45),   # Bas droite
            # Zones de ralentissement
            Obstacle(0.45, 0.2, 0.1, 0.1, "SLOW"),    # Haut
            Obstacle(0.45, 0.7, 0.1, 0.1, "SLOW"),    # Bas
            Obstacle(0.2, 0.45, 0.1, 0.1, "SLOW"),    # Gauche
            Obstacle(0.7, 0.45, 0.1, 0.1, "SLOW")     # Droite
        ]

        return maps

    @staticmethod
    def create_obstacles(map_name, screen_width, screen_height):
        maps = MapManager.get_maps()
        if map_name not in maps:
            return []
            
        # Création d'une nouvelle liste d'obstacles avec les dimensions en pixels
        obstacles = []
        for obs in maps[map_name].obstacles:
            # Conversion des pourcentages en pixels
            x = obs.original_rect.x
            y = obs.original_rect.y
            width = obs.original_rect.width
            height = obs.original_rect.height
            
            new_obstacle = Obstacle(x, y, width, height, obs.type, obs.rotation)
            obstacles.append(new_obstacle)
            
        return obstacles 