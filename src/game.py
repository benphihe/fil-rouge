import pygame
from player import Player
from obstacle import ObstacleManager
from constants import *
from character_class import CharacterClass

class Game:
    def __init__(self, game_settings):
        self.obstacle_manager = ObstacleManager(game_settings['map_type'])
        self.players = [
            Player(0, CharacterClass(game_settings['player_classes'][0]), self.obstacle_manager),
            Player(1, CharacterClass(game_settings['player_classes'][1]), self.obstacle_manager)
        ]
        
        # Ajout de la référence au jeu pour chaque joueur
        for player in self.players:
            player.game = self
            
        self.player_data = game_settings['player_data']  # [{'id': id, 'name': name}, {...}]
        self.scores = [0, 0]  # Scores des joueurs
        self.game_over = False
        self.winner = None
        self.start_time = pygame.time.get_ticks()
        self.time_remaining = GAME_DURATION
        self.return_to_menu = False
        self.end_time = None
        
        # Compteurs pour le système de score
        self.last_damage_time = [0, 0]  # Dernier moment où des dégâts ont été infligés
        self.combo_multiplier = [1.0, 1.0]  # Multiplicateur de combo pour les dégâts rapides
        self.damage_dealt = [{}, {}]  # Stockage des dégâts par type de classe
        
    def calculate_score(self, player_index):
        player = self.players[player_index]
        other_player = self.players[1 - player_index]
        
        # Calcul des dégâts totaux infligés
        total_damage_dealt = sum(self.damage_dealt[player_index].values())
        
        # Calcul des dégâts reçus (dégâts infligés par l'autre joueur)
        total_damage_received = sum(self.damage_dealt[1 - player_index].values())
        
        # Score de base sur 10000 points
        # La formule prend en compte :
        # - Les dégâts infligés (5000 points max)
        # - Les dégâts évités (5000 points max)
        damage_score = 5000 * (total_damage_dealt / other_player.character_class.stats['health'])
        survival_score = 5000 * (1 - (total_damage_received / player.character_class.stats['health']))
        
        # Le score total est la somme des deux composantes, plafonné à 10000
        base_score = min(10000, damage_score + survival_score)
        
        # Bonus de victoire (+20% plafonné à 10000)
        victory_multiplier = 1.2 if self.winner == player_index else 1.0
        
        # Score final
        final_score = int(min(10000, base_score * victory_multiplier))
        
        return final_score
        
    def update(self, input_handler):
        if self.game_over:
            current_time = pygame.time.get_ticks()
            # Retour automatique au menu après 3 secondes
            if current_time - self.end_time > 3000:
                # Calcul des scores finaux
                self.scores = [self.calculate_score(0), self.calculate_score(1)]
                self.return_to_menu = True
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
                    damage = bullet['damage']
                    other_player.take_damage(damage)
                    
                    # Stockage des dégâts par type de classe
                    if other_player.character_class not in self.damage_dealt[i]:
                        self.damage_dealt[i][other_player.character_class] = 0
                    self.damage_dealt[i][other_player.character_class] += damage
                    
                    # Gestion du système de combo
                    current_time = pygame.time.get_ticks()
                    time_since_last_hit = current_time - self.last_damage_time[i]
                    
                    # Si les dégâts sont infligés dans un délai de 2 secondes
                    if time_since_last_hit < 2000:
                        # Augmente le multiplicateur de combo (plafonné à 2.0)
                        self.combo_multiplier[i] = min(2.0, self.combo_multiplier[i] + 0.1)
                    else:
                        # Réinitialise le multiplicateur si trop de temps s'est écoulé
                        self.combo_multiplier[i] = 1.0
                    
                    self.last_damage_time[i] = current_time
                    player.bullets.remove(bullet)
                    
    def check_game_over(self):
        if self.game_over:
            return
            
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
            self.end_time = pygame.time.get_ticks()
            return
            
        # Vérification de la santé des joueurs
        for i, player in enumerate(self.players):
            if player.health <= 0:
                self.game_over = True
                self.winner = 1 - i  # L'autre joueur gagne
                self.end_time = pygame.time.get_ticks()
                return
                
    def get_match_data(self):
        return {
            'player1_id': self.player_data[0]['id'],
            'player2_id': self.player_data[1]['id'],
            'player1_score': self.scores[0],
            'player2_score': self.scores[1],
            'winner_id': self.player_data[self.winner]['id'] if self.winner >= 0 else None,
            'player1_class': self.players[0].character_class.stats['name'],
            'player2_class': self.players[1].character_class.stats['name'],
            'duration': GAME_DURATION - self.time_remaining
        }
                
    def draw(self, screen):
        # Fond noir
        screen.fill(BLACK)
        
        # Dessin des obstacles
        self.obstacle_manager.draw(screen)
        
        # Dessin des joueurs
        for player in self.players:
            player.draw(screen)
            
        # Affichage du temps restant et des scores
        font = pygame.font.Font(None, 36)
        
        # Temps
        minutes = int(self.time_remaining / 60000)
        seconds = int((self.time_remaining % 60000) / 1000)
        time_text = f"{minutes:02d}:{seconds:02d}"
        time_surface = font.render(time_text, True, WHITE)
        screen.blit(time_surface, (WINDOW_WIDTH/2 - time_surface.get_width()/2, 10))
        
        # Scores et noms des joueurs
        for i, (player, player_data) in enumerate(zip(self.players, self.player_data)):
            score = self.calculate_score(i)
            text = f"{player_data['name']}: {score}"
            color = BLUE if i == 0 else RED
            score_surface = font.render(text, True, color)
            
            if i == 0:  # Joueur 1
                # Score à gauche, cœurs à droite
                x = 10
                score_x = x
                hearts_x = x + score_surface.get_width() + 10
            else:  # Joueur 2
                # Cœurs à gauche, score à droite
                x = WINDOW_WIDTH - score_surface.get_width() - 10
                score_x = x
                hearts_x = x - ((heart_size + 2) * 10) - 10  # Espace pour 10 cœurs
            
            # Affichage du score
            screen.blit(score_surface, (score_x, 10))
            
            # Chargement et affichage des cœurs
            try:
                heart_image = pygame.image.load("assets/coeur.png").convert_alpha()
                heart_size = 20
                heart_image = pygame.transform.scale(heart_image, (heart_size, heart_size))
                
                # Calcul du nombre de cœurs à afficher
                health_percentage = player.health / player.character_class.stats['health']
                num_hearts = int(health_percentage * 10)
                
                # Affichage des cœurs
                heart_x = hearts_x
                heart_y = 10
                for _ in range(num_hearts):
                    screen.blit(heart_image, (heart_x, heart_y))
                    if i == 0:  # Joueur 1: cœurs vers la droite
                        heart_x += heart_size + 2
                    else:  # Joueur 2: cœurs vers la gauche
                        heart_x += heart_size + 2
            except Exception as e:
                print(f"Erreur lors du chargement de l'image du cœur: {e}")
        
        # Affichage du game over
        if self.game_over:
            font = pygame.font.Font(None, 74)
            if self.winner >= 0:
                text = f"{self.player_data[self.winner]['name']} GAGNE!"
            else:
                text = "MATCH NUL!"
            game_over_surface = font.render(text, True, WHITE)
            screen.blit(game_over_surface,
                       (WINDOW_WIDTH/2 - game_over_surface.get_width()/2,
                        WINDOW_HEIGHT/2 - game_over_surface.get_height()/2)) 