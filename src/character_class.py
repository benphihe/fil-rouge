import pygame
import math
from constants import *

class CharacterClass:
    @staticmethod
    def get_classes():
        return {
            'ASSAULT': {
                'name': 'Assault',
                'health': 100,
                'damage': 10,
                'bullet_speed': 7,
                'move_speed': 5,
                'speed': 5,
                'color': (255, 255, 255),
                'description': 'Stats équilibrées',
                'size': 32
            },
            'TANK': {
                'name': 'Tank',
                'health': 150,
                'damage': 8,
                'bullet_speed': 5,
                'move_speed': 4,
                'speed': 4,
                'color': (100, 100, 255),
                'description': 'Plus de vie, moins de dégâts',
                'size': 40
            },
            'SCOUT': {
                'name': 'Scout',
                'health': 70,
                'damage': 7,
                'bullet_speed': 9,
                'move_speed': 7,
                'speed': 7,
                'color': (50, 255, 50),
                'description': 'Rapide mais fragile',
                'size': 25
            },
            'SNIPER': {
                'name': 'Sniper',
                'health': 80,
                'damage': 15,
                'bullet_speed': 12,
                'move_speed': 4,
                'speed': 4,
                'color': (255, 50, 50),
                'description': 'Dégâts élevés, lent',
                'size': 30
            },
            'BALANCED': {
                'name': 'Équilibré',
                'health': 100,
                'damage': 10,
                'bullet_speed': 7,
                'move_speed': 5,
                'speed': 5,
                'color': (255, 255, 50),
                'description': 'Stats équilibrées',
                'size': 32
            }
        }

    def __init__(self, class_type):
        self.class_type = class_type
        self.stats = self.get_classes()[class_type]

    def draw_preview(self, screen, x, y):
        preview_size = 100
        preview_rect = pygame.Rect(x - preview_size/2, y - preview_size/2,
                                 preview_size, preview_size)
        
        stats_to_show = [
            ('VIE', self.stats['health'] / 150),
            ('VITESSE', self.stats['speed'] / 7),
            ('DEGATS', self.stats['damage'] / 15)
        ]
        
        bar_width = 70
        bar_height = 8
        y_offset = -40
        spacing = 35
        text_bar_spacing = 18
        
        font = pygame.font.Font(None, 32)
        name_text = font.render(self.stats['name'], True, self.stats['color'])
        name_rect = name_text.get_rect(centerx=x, bottom=y + y_offset - 15)
        screen.blit(name_text, name_rect)
        
        stat_font = pygame.font.Font(None, 20)
        for stat_name, stat_value in stats_to_show:
            bar_x = x - bar_width/2
            bar_y = y + y_offset + text_bar_spacing
            
            text = stat_font.render(stat_name, True, WHITE)
            text_rect = text.get_rect(left=bar_x, top=bar_y - text_bar_spacing)
            screen.blit(text, text_rect)
            
            pygame.draw.rect(screen, (50, 50, 50),
                           (bar_x, bar_y, bar_width, bar_height), border_radius=2)
            
            pygame.draw.rect(screen, GOLD,
                           (bar_x, bar_y, bar_width * stat_value, bar_height), border_radius=2)
            
            y_offset += spacing 