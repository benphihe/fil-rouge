import pygame
try:
    import RPi.GPIO as GPIO
    RPI_AVAILABLE = True
except ImportError:
    RPI_AVAILABLE = False
    print("GPIO non disponible - Mode de développement actif")

from constants import *

class InputHandler:
    def __init__(self):
        # Initialisation des joysticks
        pygame.joystick.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)
            
        # Initialisation GPIO si disponible
        if RPI_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            for pin in GPIO_BUTTONS.values():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                
    def get_player_input(self, player_id):
        if player_id >= len(self.joysticks):
            return {
                'dx': 0,
                'dy': 0,
                'fire': False,
                'shield': False
            }
            
        joystick = self.joysticks[player_id]
        
        # Lecture des axes du joystick
        dx = joystick.get_axis(0)
        dy = joystick.get_axis(1)
        
        # Application de la zone morte
        if abs(dx) < JOYSTICK_DEADZONE:
            dx = 0
        if abs(dy) < JOYSTICK_DEADZONE:
            dy = 0
            
        # Lecture des boutons
        if RPI_AVAILABLE:
            fire = not GPIO.input(GPIO_BUTTONS[f'PLAYER{player_id+1}_FIRE'])
            shield = not GPIO.input(GPIO_BUTTONS[f'PLAYER{player_id+1}_SHIELD'])
        else:
            # En mode développement, utiliser les boutons du joystick
            fire = joystick.get_button(BUTTON_FIRE)
            shield = joystick.get_button(BUTTON_SHIELD)
            
        return {
            'dx': dx,
            'dy': dy,
            'fire': fire,
            'shield': shield
        }
        
    def cleanup(self):
        pygame.joystick.quit()
        if RPI_AVAILABLE:
            GPIO.cleanup() 