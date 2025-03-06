import pygame

# Configuration de la fenêtre
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
GAME_TITLE = "Space Duel"

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Configuration des joueurs
PLAYER_SIZE = 32
PLAYER_SPEED = 5
PLAYER_MAX_HEALTH = 100
PLAYER_COLORS = [BLUE, RED]
PLAYER_START_POSITIONS = [
    (WINDOW_WIDTH * 0.2, WINDOW_HEIGHT * 0.5),  # Joueur 1
    (WINDOW_WIDTH * 0.8, WINDOW_HEIGHT * 0.5)   # Joueur 2
]

# Configuration des projectiles
BULLET_SIZE = 8
BULLET_SPEED = 7
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