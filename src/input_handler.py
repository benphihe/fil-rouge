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
        self.input_mode = 'ARCADE'
        
        pygame.joystick.init()
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)
            
        if RPI_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            for pin in GPIO_BUTTONS.values():
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
                
        self.keyboard_controls = {
            0: {
                'UP': pygame.K_w,
                'DOWN': pygame.K_s,
                'LEFT': pygame.K_a,
                'RIGHT': pygame.K_d,
                'FIRE': pygame.K_SPACE,
                'SHIELD': pygame.K_LSHIFT
            },
            1: {
                'UP': pygame.K_UP,
                'DOWN': pygame.K_DOWN,
                'LEFT': pygame.K_LEFT,
                'RIGHT': pygame.K_RIGHT,
                'FIRE': pygame.K_RETURN,
                'SHIELD': pygame.K_RCTRL
            }
        }
                
    def get_player_input(self, player_id):
        if self.input_mode == 'ARCADE':
            return self._get_arcade_input(player_id)
        else:
            return self._get_keyboard_input(player_id)
            
    def _get_arcade_input(self, player_id):
        if player_id >= len(self.joysticks):
            return {
                'dx': 0,
                'dy': 0,
                'fire': False,
                'shield': False
            }
            
        joystick = self.joysticks[player_id]
        
        dx = joystick.get_axis(0)
        dy = joystick.get_axis(1)
        
        if abs(dx) < JOYSTICK_DEADZONE:
            dx = 0
        if abs(dy) < JOYSTICK_DEADZONE:
            dy = 0
            
        if RPI_AVAILABLE:
            fire = not GPIO.input(GPIO_BUTTONS[f'PLAYER{player_id+1}_FIRE'])
            shield = not GPIO.input(GPIO_BUTTONS[f'PLAYER{player_id+1}_SHIELD'])
        else:
            fire = joystick.get_button(BUTTON_FIRE)
            shield = joystick.get_button(BUTTON_SHIELD)
            
        return {
            'dx': dx,
            'dy': dy,
            'fire': fire,
            'shield': shield
        }
        
    def _get_keyboard_input(self, player_id):
        keys = pygame.key.get_pressed()
        controls = self.keyboard_controls[player_id]
        
        dx = 0
        dy = 0
        
        if keys[controls['LEFT']]:
            dx = -1
        if keys[controls['RIGHT']]:
            dx = 1
        if keys[controls['UP']]:
            dy = -1
        if keys[controls['DOWN']]:
            dy = 1
            
        if dx != 0 and dy != 0:
            dx *= 0.707
            dy *= 0.707
            
        return {
            'dx': dx,
            'dy': dy,
            'fire': keys[controls['FIRE']],
            'shield': keys[controls['SHIELD']]
        }
        
    def cleanup(self):
        pygame.joystick.quit()
        if RPI_AVAILABLE:
            GPIO.cleanup() 