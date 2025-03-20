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
                'speed': 5,  # Alias pour la compatibilité
                'color': (255, 255, 255),  # Blanc
                'description': 'Stats équilibrées',
                'size': 32
            },
            'TANK': {
                'name': 'Tank',
                'health': 150,
                'damage': 8,
                'bullet_speed': 5,
                'move_speed': 4,
                'speed': 4,  # Alias pour la compatibilité
                'color': (100, 100, 255),  # Bleu clair
                'description': 'Plus de vie, moins de dégâts',
                'size': 40
            },
            'SCOUT': {
                'name': 'Scout',
                'health': 70,
                'damage': 7,
                'bullet_speed': 9,
                'move_speed': 7,
                'speed': 7,  # Alias pour la compatibilité
                'color': (50, 255, 50),  # Vert
                'description': 'Rapide mais fragile',
                'size': 25
            },
            'SNIPER': {
                'name': 'Sniper',
                'health': 80,
                'damage': 15,
                'bullet_speed': 12,
                'move_speed': 4,
                'speed': 4,  # Alias pour la compatibilité
                'color': (255, 50, 50),  # Rouge
                'description': 'Dégâts élevés, lent',
                'size': 30
            },
            'BALANCED': {
                'name': 'Équilibré',
                'health': 100,
                'damage': 10,
                'bullet_speed': 7,
                'move_speed': 5,
                'speed': 5,  # Alias pour la compatibilité
                'color': (255, 255, 50),  # Jaune
                'description': 'Stats équilibrées',
                'size': 32
            }
        }

    def __init__(self, class_type):
        self.class_type = class_type
        self.stats = self.get_classes()[class_type]

    def draw_preview(self, screen, x, y):
        """Dessine une prévisualisation de la classe."""
        # Fond du cadre de prévisualisation
        preview_size = 100
        preview_rect = pygame.Rect(x - preview_size/2, y - preview_size/2,
                                 preview_size, preview_size)
        
        # Dessin des statistiques sous forme de barres
        stats_to_show = [
            ('VIE', self.stats['health'] / 150),  # Normalisé par rapport au max (TANK)
            ('VITESSE', self.stats['speed'] / 7),  # Normalisé par rapport au max (SCOUT)
            ('DEGATS', self.stats['damage'] / 15)  # Normalisé par rapport au max (TANK)
        ]
        
        # Ajustement des dimensions des barres
        bar_width = 70  # Réduit pour rentrer dans la case
        bar_height = 8  # Réduit pour un meilleur espacement
        y_offset = -40  # Déplacé plus haut pour plus d'espace
        spacing = 35  # Augmenté pour plus d'espace entre les groupes
        text_bar_spacing = 18  # Augmenté l'espacement entre le texte et la barre
        
        # Affichage du nom de la classe au-dessus des statistiques
        font = pygame.font.Font(None, 32)
        name_text = font.render(self.stats['name'], True, self.stats['color'])
        name_rect = name_text.get_rect(centerx=x, bottom=y + y_offset - 15)  # Augmenté l'espace sous le nom
        screen.blit(name_text, name_rect)
        
        # Affichage des statistiques
        stat_font = pygame.font.Font(None, 20)  # Police légèrement réduite
        for stat_name, stat_value in stats_to_show:
            # Position de la barre - centrée dans la case
            bar_x = x - bar_width/2  # Centré horizontalement
            bar_y = y + y_offset + text_bar_spacing  # Augmenté l'espacement entre texte et barre
            
            # Texte de la statistique - aligné à gauche
            text = stat_font.render(stat_name, True, WHITE)
            text_rect = text.get_rect(left=bar_x, top=bar_y - text_bar_spacing)  # Utilise le même espacement
            screen.blit(text, text_rect)
            
            # Fond de la barre avec coins arrondis
            pygame.draw.rect(screen, (50, 50, 50),
                           (bar_x, bar_y, bar_width, bar_height), border_radius=2)
            
            # Barre de valeur avec coins arrondis
            pygame.draw.rect(screen, GOLD,
                           (bar_x, bar_y, bar_width * stat_value, bar_height), border_radius=2)
            
            y_offset += spacing  # Utilise l'espacement défini 