import pygame
import sys
from game import Game
from input_handler import InputHandler
from constants import *

def main():
    # Initialisation de Pygame
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()
    
    # Création des objets principaux
    input_handler = InputHandler()
    game = Game()
    
    try:
        # Boucle principale
        while True:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    # Redémarrage du jeu avec R
                    elif event.key == pygame.K_r and game.game_over:
                        game = Game()
            
            # Mise à jour du jeu
            game.update(input_handler)
            
            # Rendu
            game.draw(screen)
            pygame.display.flip()
            
            # Limitation du framerate
            clock.tick(FPS)
            
    finally:
        # Nettoyage
        input_handler.cleanup()
        pygame.quit()
        
if __name__ == "__main__":
    main() 