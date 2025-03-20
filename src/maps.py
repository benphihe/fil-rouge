from obstacle import Obstacle
from constants import *

class Map:
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.obstacles = []
        
    def draw_preview(self, screen, preview_rect):
        pygame.draw.rect(screen, BLACK, preview_rect)
        pygame.draw.rect(screen, WHITE, preview_rect, 2)
        
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

        maps['CLASSIC'].obstacles = [
            Obstacle(0.48, 0.2, 0.04, 0.6, "WALL"),
            Obstacle(0.2, 0.2, 0.15, 0.15, "SLOW"),
            Obstacle(0.65, 0.65, 0.15, 0.15, "SLOW"),
            Obstacle(0.15, 0.4, 0.1, 0.05, "WALL"),
            Obstacle(0.75, 0.55, 0.1, 0.05, "WALL")
        ]

        maps['ARENA'].obstacles = [
            Obstacle(0.2, 0.2, 0.2, 0.05, "WALL"),
            Obstacle(0.2, 0.2, 0.05, 0.2, "WALL"),
            Obstacle(0.6, 0.75, 0.2, 0.05, "WALL"),
            Obstacle(0.75, 0.6, 0.05, 0.2, "WALL"),
            Obstacle(0.45, 0.45, 0.1, 0.1, "SLOW"),
            Obstacle(0.15, 0.75, 0.1, 0.1, "SLOW"),
            Obstacle(0.75, 0.15, 0.1, 0.1, "SLOW")
        ]

        maps['MAZE'].obstacles = [
            Obstacle(0.3, 0.3, 0.05, 0.2, "WALL", 45),
            Obstacle(0.65, 0.3, 0.05, 0.2, "WALL", -45),
            Obstacle(0.3, 0.7, 0.05, 0.2, "WALL", -45),
            Obstacle(0.65, 0.7, 0.05, 0.2, "WALL", 45),
            Obstacle(0.45, 0.2, 0.1, 0.1, "SLOW"),
            Obstacle(0.45, 0.7, 0.1, 0.1, "SLOW"),
            Obstacle(0.2, 0.45, 0.1, 0.1, "SLOW"),
            Obstacle(0.7, 0.45, 0.1, 0.1, "SLOW")
        ]

        return maps

    @staticmethod
    def create_obstacles(map_name, screen_width, screen_height):
        maps = MapManager.get_maps()
        if map_name not in maps:
            return []
            
        obstacles = []
        for obs in maps[map_name].obstacles:
            x = obs.original_rect.x
            y = obs.original_rect.y
            width = obs.original_rect.width
            height = obs.original_rect.height
            
            new_obstacle = Obstacle(x, y, width, height, obs.type, obs.rotation)
            obstacles.append(new_obstacle)
            
        return obstacles 