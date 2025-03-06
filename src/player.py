import pygame
import math
from constants import *

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.x, self.y = PLAYER_START_POSITIONS[player_id]
        self.color = PLAYER_COLORS[player_id]
        self.health = PLAYER_MAX_HEALTH
        self.rect = pygame.Rect(self.x, self.y, PLAYER_SIZE, PLAYER_SIZE)
        
        # Gestion des tirs
        self.bullets = []
        self.last_shot_time = 0
        
        # Gestion du bouclier
        self.shield_active = False
        self.shield_start_time = 0
        self.last_shield_time = 0
        
        # Direction du joueur (pour les tirs)
        self.direction = 0  # en radians
        
    def move(self, dx, dy):
        # Normalisation du vecteur de déplacement
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx = dx/length
            dy = dy/length
            self.direction = math.atan2(dy, dx)
        
        # Mise à jour de la position
        new_x = self.x + dx * PLAYER_SPEED
        new_y = self.y + dy * PLAYER_SPEED
        
        # Vérification des limites de l'écran
        if 0 <= new_x <= WINDOW_WIDTH - PLAYER_SIZE:
            self.x = new_x
        if 0 <= new_y <= WINDOW_HEIGHT - PLAYER_SIZE:
            self.y = new_y
            
        self.rect.x = self.x
        self.rect.y = self.y
        
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= BULLET_COOLDOWN:
            # Calcul de la direction du tir
            bullet_dx = math.cos(self.direction)
            bullet_dy = math.sin(self.direction)
            
            # Création du projectile
            bullet = {
                'x': self.x + PLAYER_SIZE/2,
                'y': self.y + PLAYER_SIZE/2,
                'dx': bullet_dx,
                'dy': bullet_dy,
                'rect': pygame.Rect(
                    self.x + PLAYER_SIZE/2,
                    self.y + PLAYER_SIZE/2,
                    BULLET_SIZE,
                    BULLET_SIZE
                )
            }
            
            self.bullets.append(bullet)
            self.last_shot_time = current_time
            
    def activate_shield(self):
        current_time = pygame.time.get_ticks()
        if not self.shield_active and current_time - self.last_shield_time >= SHIELD_COOLDOWN:
            self.shield_active = True
            self.shield_start_time = current_time
            self.last_shield_time = current_time
            
    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Mise à jour du bouclier
        if self.shield_active:
            if current_time - self.shield_start_time >= SHIELD_DURATION:
                self.shield_active = False
                
        # Mise à jour des projectiles
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx'] * BULLET_SPEED
            bullet['y'] += bullet['dy'] * BULLET_SPEED
            bullet['rect'].x = bullet['x']
            bullet['rect'].y = bullet['y']
            
            # Suppression des projectiles hors écran
            if (bullet['x'] < 0 or bullet['x'] > WINDOW_WIDTH or
                bullet['y'] < 0 or bullet['y'] > WINDOW_HEIGHT):
                self.bullets.remove(bullet)
                
    def take_damage(self, damage):
        if not self.shield_active:
            self.health -= damage
            if self.health < 0:
                self.health = 0
                
    def draw(self, screen):
        # Dessin du vaisseau
        pygame.draw.rect(screen, self.color, self.rect)
        
        # Dessin du bouclier si actif
        if self.shield_active:
            pygame.draw.rect(screen, GREEN,
                           self.rect.inflate(10, 10), 2)
        
        # Dessin de la barre de vie
        health_width = (PLAYER_SIZE * self.health) / PLAYER_MAX_HEALTH
        health_rect = pygame.Rect(self.x, self.y - 10,
                                health_width, 5)
        pygame.draw.rect(screen, GREEN, health_rect)
        
        # Dessin des projectiles
        for bullet in self.bullets:
            pygame.draw.rect(screen, YELLOW, bullet['rect']) 