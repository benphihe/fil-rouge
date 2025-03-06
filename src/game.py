import pygame
from player import Player
from constants import *

class Game:
    def __init__(self):
        self.players = [Player(0), Player(1)]
        self.game_over = False
        self.winner = None
        self.start_time = pygame.time.get_ticks()
        self.time_remaining = GAME_DURATION
        
    def update(self, input_handler):
        if self.game_over:
            return
            
        current_time = pygame.time.get_ticks()
        self.time_remaining = max(0, GAME_DURATION - (current_time - self.start_time))
        
        # Mise à jour des joueurs
        for i, player in enumerate(self.players):
            # Lecture des entrées
            inputs = input_handler.get_player_input(i)
            
            # Application des mouvements
            player.move(inputs['dx'], inputs['dy'])
            
            # Gestion des actions
            if inputs['fire']:
                player.shoot()
            if inputs['shield']:
                player.activate_shield()
                
            player.update()
            
        # Vérification des collisions
        self.check_collisions()
        
        # Vérification des conditions de fin de partie
        self.check_game_over()
        
    def check_collisions(self):
        # Vérification des collisions entre les projectiles et les joueurs
        for i, player in enumerate(self.players):
            other_player = self.players[1 - i]  # L'autre joueur
            
            for bullet in player.bullets[:]:
                if bullet['rect'].colliderect(other_player.rect):
                    other_player.take_damage(BULLET_DAMAGE)
                    player.bullets.remove(bullet)
                    
    def check_game_over(self):
        # Vérification du temps écoulé
        if self.time_remaining <= 0:
            self.game_over = True
            # Le joueur avec le plus de vie gagne
            if self.players[0].health > self.players[1].health:
                self.winner = 0
            elif self.players[1].health > self.players[0].health:
                self.winner = 1
            else:
                self.winner = -1  # Match nul
            return
            
        # Vérification de la santé des joueurs
        for i, player in enumerate(self.players):
            if player.health <= 0:
                self.game_over = True
                self.winner = 1 - i  # L'autre joueur gagne
                return
                
    def draw(self, screen):
        # Fond noir
        screen.fill(BLACK)
        
        # Dessin des joueurs
        for player in self.players:
            player.draw(screen)
            
        # Affichage du temps restant
        minutes = int(self.time_remaining / 60000)
        seconds = int((self.time_remaining % 60000) / 1000)
        time_text = f"{minutes:02d}:{seconds:02d}"
        font = pygame.font.Font(None, 36)
        time_surface = font.render(time_text, True, WHITE)
        screen.blit(time_surface, (WINDOW_WIDTH/2 - 40, 10))
        
        # Affichage du game over
        if self.game_over:
            font = pygame.font.Font(None, 74)
            if self.winner >= 0:
                text = f"JOUEUR {self.winner + 1} GAGNE!"
            else:
                text = "MATCH NUL!"
            game_over_surface = font.render(text, True, WHITE)
            screen.blit(game_over_surface,
                       (WINDOW_WIDTH/2 - game_over_surface.get_width()/2,
                        WINDOW_HEIGHT/2 - game_over_surface.get_height()/2)) 