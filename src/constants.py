import pygame

# Initialisation de pygame
pygame.init()

# Obtention de la résolution de l'écran
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h

# Configuration de la fenêtre
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
GAME_TITLE = "SPACE DUEL"

# Couleurs
BLACK = (0, 0, 0)  # Fond spatial
WHITE = (255, 255, 255)
YELLOW = (255, 229, 127)  # Jaune Star Wars
RED = (255, 59, 48)  # Rouge impérial
BLUE = (10, 132, 255)  # Bleu Rebelle
LIGHT_BLUE = (88, 197, 255)  # Bleu sabre laser
IMPERIAL_RED = (236, 0, 0)  # Rouge vif impérial
REBEL_BLUE = (30, 144, 255)  # Bleu Alliance Rebelle
JEDI_GREEN = (57, 255, 20)  # Vert sabre laser
SITH_RED = (255, 0, 0)  # Rouge sabre laser
GOLD = (255, 215, 0)  # Or pour les textes importants
SHIELD_BLUE = (0, 191, 255)  # Bleu bouclier
GREEN = (0, 255, 0)  # Vert pour le bouclier
SLOW_ZONE = (128, 0, 128, 128)  # Violet transparent pour les zones de ralentissement

# Configuration des joueurs
PLAYER_SIZE = int(min(WINDOW_WIDTH, WINDOW_HEIGHT) * 0.05)  # 5% de la plus petite dimension
PLAYER_SPEED = WINDOW_WIDTH * 0.005  # 0.5% de la largeur de l'écran
PLAYER_MAX_HEALTH = 100
PLAYER_COLORS = [BLUE, RED]
PLAYER_START_POSITIONS = [
    (WINDOW_WIDTH * 0.2, WINDOW_HEIGHT * 0.5),  # Joueur 1
    (WINDOW_WIDTH * 0.8, WINDOW_HEIGHT * 0.5)   # Joueur 2
]

# Configuration des projectiles
BULLET_SIZE = int(PLAYER_SIZE * 0.25)  # 25% de la taille du joueur
BULLET_SPEED = WINDOW_WIDTH * 0.007  # 0.7% de la largeur de l'écran
BULLET_DAMAGE = 10
BULLET_COOLDOWN = 250  # Millisecondes entre chaque tir

# Configuration du bouclier
SHIELD_DURATION = 2000  # Millisecondes
SHIELD_COOLDOWN = 5000  # Millisecondes

# Configuration des contrôles
JOYSTICK_DEADZONE = 0.2
BUTTON_FIRE = 0
BUTTON_SHIELD = 1

# GPIO Pins (pour Raspberry Pi)
GPIO_BUTTONS = {
    'PLAYER1_FIRE': 17,
    'PLAYER1_SHIELD': 18,
    'PLAYER2_FIRE': 22,
    'PLAYER2_SHIELD': 23
}

# Configuration du jeu
GAME_DURATION = 180000  # 3 minutes en millisecondes
VICTORY_SCORE = 3

# Configuration de l'interface
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
FONT_SIZE_LARGE = 72
FONT_SIZE_MEDIUM = 36
FONT_SIZE_SMALL = 24

# Dimensions de la fenêtre
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720 