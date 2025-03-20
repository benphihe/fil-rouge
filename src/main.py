import pygame
import sys
from game import Game
from input_handler import InputHandler
from menu import Menu
from database import Database
from constants import *

def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()
    
    fullscreen = False
    
    MENU = "MENU"
    PLAYING = "PLAYING"
    current_state = MENU
    
    db = Database()
    menu = Menu(db)
    input_handler = None
    game = None
    
    pygame.init()
    pygame.joystick.init()

    joystick_count = pygame.joystick.get_count()
    joysticks = []
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        joysticks.append(joystick)

    print(f"Nombre de joysticks connectés : {joystick_count}")

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    db.close()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if current_state == PLAYING:
                            current_state = MENU
                        else:
                            db.close()
                            return
                    elif event.key == pygame.K_F11:
                        fullscreen = not fullscreen
                        if fullscreen:
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.joy == 0 and event.button == 1:
                        fullscreen = not fullscreen
                        if fullscreen:
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                        else:
                            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
                    print(f"Button {event.button} pressed on joystick {event.joy}")
                elif event.type == pygame.JOYAXISMOTION:
                    print(f"Joystick {event.joy} axis {event.axis} moved to {event.value}")
                
                if current_state == MENU:
                    if event.type == pygame.JOYAXISMOTION and event.joy == 0:
                        if event.axis == 1:
                            if event.value > 0.5:
                                menu.handle_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_DOWN}))
                            elif event.value < -0.5:
                                menu.handle_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_UP}))
                        elif event.axis == 0:
                            if event.value > 0.5:
                                menu.handle_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RIGHT}))
                            elif event.value < -0.5:
                                menu.handle_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_LEFT}))
                    
                    elif event.type == pygame.JOYBUTTONDOWN and event.joy == 0 and event.button == 0:
                        menu.handle_event(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_RETURN}))
                    
                    result = menu.handle_event(event)
                    if result == "START_GAME":
                        current_state = PLAYING
                        input_handler = InputHandler()
                        input_handler.input_mode = menu.settings['input_mode']
                        game = Game(menu.get_game_settings())
            
            if current_state == MENU:
                menu.draw(screen)
            elif current_state == PLAYING:
                game.update(input_handler)
                game.draw(screen)
                
                if game.return_to_menu:
                    db.save_match(game.get_match_data())
                    current_state = MENU
                    menu.set_state("MAIN")
                    game = None
            
            pygame.display.flip()
            clock.tick(FPS)
            
    finally:
        if input_handler:
            input_handler.cleanup()
        db.close()
        pygame.quit()
        
if __name__ == "__main__":
    main() 