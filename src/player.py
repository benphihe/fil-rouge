import pygame
import math
from constants import *
from character_class import CharacterClass

class Player:
    def __init__(self, player_id, character_class, obstacle_manager):
        self.player_id = player_id
        self.character_class = character_class
        self.obstacle_manager = obstacle_manager
        
        # Position initiale
        self.x, self.y = PLAYER_START_POSITIONS[player_id]
        self.health = self.character_class.stats['health']
        self.rect = pygame.Rect(self.x, self.y, 
                              self.character_class.stats['size'],
                              self.character_class.stats['size'])
        
        # Direction (en radians)
        self.direction = 0 if player_id == 0 else math.pi
        
        # Gestion des tirs
        self.bullets = []
        self.last_shot_time = 0
        
        # Gestion du bouclier
        self.shield_active = False
        self.shield_start_time = 0
        self.last_shield_time = 0
        
        # Chargement de l'image du vaisseau
        try:
            self.original_image = pygame.image.load("assets/vaisseau.png").convert_alpha()
            # Redimensionner l'image à la taille du joueur
            self.original_image = pygame.transform.scale(self.original_image, 
                                                      (self.character_class.stats['size'], 
                                                       self.character_class.stats['size']))
            self.image = self.original_image.copy()
            # Appliquer une teinte à l'image selon la couleur du joueur
            color_surface = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            if player_id == 0:
                color_surface.fill(BLUE)  # Couleur bleue pour le joueur 1
            else:
                color_surface.fill(RED)   # Couleur rouge pour le joueur 2
            self.image.blit(color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image du vaisseau: {e}")
            self.image = None
            
        # Mettre à jour le rectangle de l'image
        if self.image:
            self.image_rect = self.image.get_rect(center=self.rect.center)
        
    def move(self, dx, dy):
        # Normalisation du vecteur de déplacement
        length = math.sqrt(dx*dx + dy*dy)
        if length > 0:
            dx = dx/length
            dy = dy/length
            self.direction = math.atan2(dy, dx)
        
        # Application du modificateur de vitesse des obstacles
        speed_mod_x, speed_mod_y = self.obstacle_manager.get_movement_modifier(self.rect)
        
        # Calcul de la nouvelle position
        move_speed = self.character_class.stats.get('speed', self.character_class.stats['move_speed'])  # Utilise 'speed' s'il existe, sinon 'move_speed'
        new_x = self.x + dx * move_speed * speed_mod_x
        new_y = self.y + dy * move_speed * speed_mod_y
        
        # Test de collision pour X
        test_rect = self.rect.copy()
        test_rect.x = new_x
        if not self.obstacle_manager.check_collision(test_rect):
            self.x = new_x
            
        # Test de collision pour Y
        test_rect = self.rect.copy()
        test_rect.y = new_y
        if not self.obstacle_manager.check_collision(test_rect):
            self.y = new_y
            
        # Mise à jour du rectangle de collision
        self.rect.x = self.x
        self.rect.y = self.y
        
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= BULLET_COOLDOWN:
            # Calcul de la direction du tir
            bullet_dx = math.cos(self.direction)
            bullet_dy = math.sin(self.direction)
            
            # Position de départ du projectile (bout du canon)
            cannon_length = self.character_class.stats['size'] * 0.8
            start_x = self.x + self.character_class.stats['size']/2 + bullet_dx * cannon_length
            start_y = self.y + self.character_class.stats['size']/2 + bullet_dy * cannon_length
            
            # Création du projectile
            bullet = {
                'x': start_x,
                'y': start_y,
                'dx': bullet_dx,
                'dy': bullet_dy,
                'damage': self.character_class.stats['damage'],
                'speed': self.character_class.stats['bullet_speed'],
                'rect': pygame.Rect(
                    start_x - BULLET_SIZE/2,
                    start_y - BULLET_SIZE/2,
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
                
        # Mise à jour de la position du rectangle de l'image
        if hasattr(self, 'image') and self.image:
            self.image_rect.center = self.rect.center
                
        # Mise à jour des projectiles
        for bullet in self.bullets[:]:
            # Mise à jour de la position
            bullet['x'] += bullet['dx'] * bullet['speed']
            bullet['y'] += bullet['dy'] * bullet['speed']
            bullet['rect'].x = bullet['x'] - BULLET_SIZE/2
            bullet['rect'].y = bullet['y'] - BULLET_SIZE/2
            
            # Vérification des collisions avec les obstacles
            if (self.obstacle_manager.check_bullet_collision(bullet['rect']) or
                bullet['x'] < 0 or bullet['x'] > WINDOW_WIDTH or
                bullet['y'] < 0 or bullet['y'] > WINDOW_HEIGHT):
                self.bullets.remove(bullet)
                
    def take_damage(self, damage):
        if not self.shield_active:
            self.health -= damage
            if self.health < 0:
                self.health = 0
                
    def draw(self, screen):
        if self.image:
            # Rotation de l'image selon la direction du joueur
            # Conversion de radians à degrés et ajustement de l'angle pour correspondre à l'orientation de l'image
            angle_deg = -math.degrees(self.direction) + 90  # +90 car l'image est orientée vers le haut par défaut
            rotated_image = pygame.transform.rotate(self.image, angle_deg)
            rotated_rect = rotated_image.get_rect(center=self.rect.center)
            
            # Affichage de l'image du vaisseau
            screen.blit(rotated_image, rotated_rect)
        else:
            # Fallback: Dessin du corps du personnage si l'image n'est pas disponible
            pygame.draw.rect(screen, self.character_class.stats['color'], self.rect)
            
            # Dessin du canon (indicateur de direction)
            center_x = self.x + self.character_class.stats['size']/2
            center_y = self.y + self.character_class.stats['size']/2
            cannon_length = self.character_class.stats['size'] * 0.8
            end_x = center_x + math.cos(self.direction) * cannon_length
            end_y = center_y + math.sin(self.direction) * cannon_length
            pygame.draw.line(screen, WHITE, (center_x, center_y), (end_x, end_y), 4)
        
        # Dessin du bouclier si actif
        if self.shield_active:
            shield_rect = self.rect.inflate(10, 10)
            pygame.draw.rect(screen, GREEN, shield_rect, 2)
        
        # Dessin des projectiles
        for bullet in self.bullets:
            pygame.draw.rect(screen, YELLOW, bullet['rect']) 