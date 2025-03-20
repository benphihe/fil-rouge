import pygame
import sys
from game import Game
from input_handler import InputHandler
from menu import Menu
from database import Database
from constants import *

def main():
    # Configuration de la fenêtre
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)
    clock = pygame.time.Clock()
    
    # États du jeu
    MENU = "MENU"
    PLAYING = "PLAYING"
    current_state = MENU
    
    # Création des objets principaux
    db = Database()
    menu = Menu(db)
    input_handler = None
    game = None
    
    try:
        # Boucle principale
        while True:
            # Gestion des événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    db.close()
                    return
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if current_state == PLAYING:
                        current_state = MENU
                    else:
                        db.close()
                        return
                
                if current_state == MENU:
                    result = menu.handle_event(event)
                    if result == "START_GAME":
                        current_state = PLAYING
                        # Initialisation du jeu avec les paramètres du menu
                        input_handler = InputHandler()
                        input_handler.input_mode = menu.settings['input_mode']
                        game = Game(menu.get_game_settings())
            
            # Mise à jour et rendu
            if current_state == MENU:
                menu.draw(screen)
            elif current_state == PLAYING:
                game.update(input_handler)
                game.draw(screen)
                
                # Vérification du retour au menu
                if game.return_to_menu:
                    # Sauvegarde des données de la partie
                    db.save_match(game.get_match_data())
                    current_state = MENU
                    menu.set_state("MAIN")  # Réinitialisation explicite de l'état du menu
                    game = None
            
            pygame.display.flip()
            clock.tick(FPS)
            
    finally:
        # Nettoyage
        if input_handler:
            input_handler.cleanup()
        db.close()
        pygame.quit()
        
if __name__ == "__main__":
    main() 