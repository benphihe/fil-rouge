import pygame
import math
from constants import *
from character_class import CharacterClass
from database import Database
from maps import MapManager

class Button:
    def __init__(self, x, y, width, height, text, font_size=36, image_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font_size = font_size
        self.font = pygame.font.Font(None, self.calculate_font_size(width, height, font_size))
        self.color = (30, 30, 30)  # Gris foncé
        self.hover_color = (45, 45, 45)  # Gris un peu plus clair
        self.text_color = WHITE
        self.is_hovered = False
        self.image = None
        self.image_rect = None
        self.original_width = width
        self.original_height = height
        self.hover_scale = 1.1  # Facteur d'agrandissement au survol
        
        # Charger l'image si un chemin est fourni
        if image_path:
            try:
                original_image = pygame.image.load(image_path).convert_alpha()
                # Calculer les dimensions pour préserver le ratio
                img_width, img_height = original_image.get_size()
                ratio = min(width / img_width, height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                # Redimensionner l'image en préservant les proportions
                self.image = pygame.transform.scale(original_image, (new_width, new_height))
                self.original_image = self.image.copy()
                
                # Calculer la position pour centrer l'image dans le bouton
                self.image_rect = self.image.get_rect(center=self.rect.center)
                
                # Préparer l'image agrandie pour le survol
                hover_width = int(new_width * self.hover_scale)
                hover_height = int(new_height * self.hover_scale)
                self.hover_image = pygame.transform.scale(original_image, (hover_width, hover_height))
                self.hover_image_rect = self.hover_image.get_rect(center=self.rect.center)
            except Exception as e:
                print(f"Erreur lors du chargement de l'image: {e}")
                self.image = None

    def calculate_font_size(self, width, height, base_font_size):
        """Calcule une taille de police proportionnelle à la taille du bouton"""
        min_dimension = min(width, height)
        return int(min_dimension * 0.6) if self.text == "+" else int(min_dimension * 0.42)

    def draw(self, screen):
        if self.image:
            # Si on a une image, on dessine uniquement l'image
            if self.is_hovered:
                screen.blit(self.hover_image, self.hover_image_rect)
            else:
                screen.blit(self.image, self.image_rect)
        else:
            # Fallback au bouton classique si pas d'image
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(screen, color, self.rect, border_radius=10)
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Mise à jour de l'état de survol
            if self.image and self.image_rect:
                self.is_hovered = self.image_rect.collidepoint(event.pos)
            else:
                self.is_hovered = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Vérification du clic
            if self.image and self.image_rect:
                return self.image_rect.collidepoint(event.pos)
            else:
                return self.rect.collidepoint(event.pos)
        return False

class TextInput:
    def __init__(self, x, y, width, height, placeholder="", max_length=10):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.max_length = max_length
        self.font = pygame.font.Font(None, 36)
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length and event.unicode.isprintable():
                self.text += event.unicode
        return False
        
    def draw(self, screen):
        # Dessin du fond
        pygame.draw.rect(screen, WHITE, self.rect)
        
        # Préparation du texte à afficher
        text_to_render = self.text if self.text else self.placeholder
        text_color = BLACK if self.text else (128, 128, 128)
        text_surface = self.font.render(text_to_render, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # Affichage du curseur clignotant
        if self.active:
            self.cursor_timer += 1
            if self.cursor_timer // 30 % 2 == 0:
                cursor_x = text_rect.right + 2 if self.text else self.rect.centerx
                pygame.draw.line(screen, BLACK,
                               (cursor_x, self.rect.y + 5),
                               (cursor_x, self.rect.bottom - 5), 2)

class ScrollableList:
    def __init__(self, x, y, width, height, visible_height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible_rect = pygame.Rect(x, y, width, visible_height)
        self.scroll_y = 0
        self.max_scroll = max(0, height - visible_height)
        self.scrollbar_rect = pygame.Rect(x + width - 20, y, 20, visible_height)
        self.scrollbar_height = (visible_height / height) * visible_height if height > 0 else visible_height
        self.scrollbar_pos = y
        self.dragging = False
        self.hover_scrollbar = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Clic gauche
                if self.scrollbar_rect.collidepoint(event.pos):
                    self.dragging = True
                    return True
            elif event.button == 4:  # Molette vers le haut
                self.scroll_y = max(0, self.scroll_y - 30)
                self.update_scrollbar()
                return True
            elif event.button == 5:  # Molette vers le bas
                self.scroll_y = min(self.max_scroll, self.scroll_y + 30)
                self.update_scrollbar()
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            self.hover_scrollbar = self.scrollbar_rect.collidepoint(event.pos)
            if self.dragging:
                relative_y = event.pos[1] - self.visible_rect.y
                scroll_ratio = relative_y / (self.visible_rect.height - self.scrollbar_height)
                self.scroll_y = min(self.max_scroll, max(0, int(scroll_ratio * self.max_scroll)))
                self.update_scrollbar()
                return True
        return False

    def update_scrollbar(self):
        if self.max_scroll > 0:
            scroll_ratio = self.scroll_y / self.max_scroll
            self.scrollbar_pos = self.visible_rect.y + scroll_ratio * (self.visible_rect.height - self.scrollbar_height)
            self.scrollbar_rect.y = self.scrollbar_pos

    def draw(self, screen):
        # Fond de la barre de défilement
        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(self.scrollbar_rect.x, self.visible_rect.y,
                                                         self.scrollbar_rect.width, self.visible_rect.height))
        # Barre de défilement
        scrollbar_color = (150, 150, 150) if self.hover_scrollbar or self.dragging else (100, 100, 100)
        pygame.draw.rect(screen, scrollbar_color, 
                        pygame.Rect(self.scrollbar_rect.x, self.scrollbar_pos,
                                  self.scrollbar_rect.width, self.scrollbar_height))

class Menu:
    def __init__(self, db):
        self.db = db
        self.state = "MAIN"
        self.state_history = ["MAIN"]
        self.settings = self.db.load_settings() or {
            'volume': 0.5,
            'input_mode': 'ARCADE'
        }
        
        # Navigation au clavier
        self.selected_button_index = 0
        self.keyboard_navigation = True
        
        # Chargement de l'image de fond
        try:
            self.background = pygame.image.load("assets/background.png").convert()
            self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except:
            self.background = None
            print("Image de fond non trouvée. Placez une image 'background.png' dans le dossier assets/")
        
        # Initialisation des données de jeu
        self.selected_classes = {0: None, 1: None}
        self.current_player_selecting = 0
        self.player_data = [None, None]
        self.current_player_entering = 0
        self.selected_map = None
        self.maps = MapManager.get_maps()
        self.existing_players_buttons = []
        self.players_list = None
        
        # Création du bouton retour global
        self.back_button = Button(WINDOW_WIDTH*0.05, WINDOW_HEIGHT*0.9, 
                                BUTTON_WIDTH, BUTTON_HEIGHT, "RETOUR", FONT_SIZE_MEDIUM,
                                image_path="assets/retour_button.png")
                                
        # Création des boutons du menu principal
        button_y = WINDOW_HEIGHT * 0.4
        button_spacing = WINDOW_HEIGHT * 0.12
        
        self.main_buttons = [
            Button(WINDOW_WIDTH//2 - BUTTON_WIDTH//2, button_y,
                  BUTTON_WIDTH, BUTTON_HEIGHT, "JOUER", FONT_SIZE_MEDIUM,
                  image_path="assets/play_button.png"),
            Button(WINDOW_WIDTH//2 - BUTTON_WIDTH//2, button_y + button_spacing,
                  BUTTON_WIDTH, BUTTON_HEIGHT, "REGLAGES", FONT_SIZE_MEDIUM,
                  image_path="assets/reglages_button.png"),
            Button(WINDOW_WIDTH//2 - BUTTON_WIDTH//2, button_y + button_spacing * 2,
                  BUTTON_WIDTH, BUTTON_HEIGHT, "REGLES", FONT_SIZE_MEDIUM,
                  image_path="assets/regles_button.png"),
            Button(WINDOW_WIDTH//2 - BUTTON_WIDTH//2, button_y + button_spacing * 3,
                  BUTTON_WIDTH, BUTTON_HEIGHT, "CLASSEMENT", FONT_SIZE_MEDIUM,
                  image_path="assets/classement_button.png")
        ]
        
        # Éléments des réglages
        start_y = WINDOW_HEIGHT * 0.35
        spacing = WINDOW_HEIGHT * 0.12
        
        self.input_button = Button(WINDOW_WIDTH//2 - BUTTON_WIDTH//2, 
                                 start_y, BUTTON_WIDTH, BUTTON_HEIGHT, 
                                 f"INPUT: {self.settings['input_mode']}", FONT_SIZE_MEDIUM)
        
        self.custom_class_button = Button(WINDOW_WIDTH//2 - BUTTON_WIDTH//2,
                                        start_y + spacing, BUTTON_WIDTH, BUTTON_HEIGHT,
                                        "CUSTOM CLASS", FONT_SIZE_MEDIUM)
        
        self.reset_button = Button(WINDOW_WIDTH//2 - BUTTON_WIDTH//2,
                                 start_y + spacing * 2, BUTTON_WIDTH, BUTTON_HEIGHT,
                                 "REINITIALISER SCORES", FONT_SIZE_MEDIUM)
        
        # Boutons de sélection de classe
        self.class_buttons = []
        classes = CharacterClass.get_classes()
        x_start = WINDOW_WIDTH * 0.2
        y_pos = WINDOW_HEIGHT * 0.5
        x_spacing = WINDOW_WIDTH * 0.2
        
        for i, (class_type, class_info) in enumerate(classes.items()):
            self.class_buttons.append({
                'button': Button(x_start + i * x_spacing - BUTTON_WIDTH//2, y_pos + WINDOW_HEIGHT*0.15,
                               BUTTON_WIDTH, BUTTON_HEIGHT, class_info['name'], FONT_SIZE_MEDIUM),
                'type': class_type,
                'preview_pos': (x_start + i * x_spacing, y_pos)
            })
            
        # Boutons de sélection de map
        self.map_buttons = []
        x_start = WINDOW_WIDTH * 0.25
        x_spacing = WINDOW_WIDTH * 0.25
        
        for i, (map_type, map_info) in enumerate(self.maps.items()):
            self.map_buttons.append({
                'button': Button(x_start + i * x_spacing - BUTTON_WIDTH//2, WINDOW_HEIGHT*0.7,
                               BUTTON_WIDTH, BUTTON_HEIGHT, map_info.name, FONT_SIZE_MEDIUM),
                'type': map_type,
                'preview_pos': (x_start + i * x_spacing, WINDOW_HEIGHT*0.4)
            })
            
        # Interface de saisie du nom
        self.player_name_input = TextInput(
            WINDOW_WIDTH//2 - WINDOW_WIDTH*0.15, WINDOW_HEIGHT*0.4,
            WINDOW_WIDTH*0.3, BUTTON_HEIGHT, "Entrez votre nom"
        )
        
        self.validate_button = Button(
            WINDOW_WIDTH//2 - BUTTON_WIDTH//2, WINDOW_HEIGHT*0.6,
            BUTTON_WIDTH, BUTTON_HEIGHT, "VALIDER", FONT_SIZE_MEDIUM
        )

        # Bouton de création de personnage
        self.new_char_button = Button(
            WINDOW_WIDTH*0.25 - (BUTTON_WIDTH * 0.5)/2,
            WINDOW_HEIGHT*0.4,
            BUTTON_WIDTH * 0.5, BUTTON_WIDTH * 0.5,
            "+", FONT_SIZE_LARGE
        )

    def create_existing_players_buttons(self):
        """Crée les boutons pour les personnages existants."""
        players = self.db.get_all_players()
        self.existing_players_buttons = []
        
        if players:
            # Filtrer les joueurs pour exclure celui déjà sélectionné par le joueur 1
            if self.current_player_entering == 1 and self.player_data[0]:
                players = [(pid, name) for pid, name in players if pid != self.player_data[0]['id']]
            
            # Configuration de la liste défilante
            button_spacing = 20
            list_x = WINDOW_WIDTH * 0.7
            list_y = WINDOW_HEIGHT * 0.3
            visible_height = WINDOW_HEIGHT * 0.4
            total_height = len(players) * (BUTTON_HEIGHT + button_spacing)
            
            self.players_list = ScrollableList(list_x, list_y, BUTTON_WIDTH + 20, total_height, visible_height)
            
            for i, (player_id, name) in enumerate(players):
                y = list_y + i * (BUTTON_HEIGHT + button_spacing)
                self.existing_players_buttons.append({
                    'button': Button(list_x, y, BUTTON_WIDTH, BUTTON_HEIGHT, name, FONT_SIZE_MEDIUM),
                    'id': player_id,
                    'name': name
                })

    def draw_main_menu(self, screen):
        # Affichage du fond
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(BLACK)
        
        # Titre simplifié
        title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        title = title_font.render("SPACE DUEL", True, WHITE)  # Changé GOLD pour WHITE
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.2))
        screen.blit(title, title_rect)
        
        # Dessin des boutons
        button_spacing = WINDOW_HEIGHT * 0.12
        for i, button in enumerate(self.main_buttons):
            button.rect.centerx = WINDOW_WIDTH//2
            button.rect.y = WINDOW_HEIGHT * 0.4 + i * button_spacing
            button.draw(screen)

    def draw_settings(self, screen):
        # Fond noir
        screen.fill(BLACK)
        
        # Titre
        title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        title = title_font.render("PARAMETRES", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.2))
        screen.blit(title, title_rect)
        
        # Affichage des éléments de réglages
        start_y = WINDOW_HEIGHT * 0.35
        spacing = WINDOW_HEIGHT * 0.12
        
        # Bouton pour changer de mode d'entrée
        self.input_button.rect.y = start_y
        self.input_button.rect.centerx = WINDOW_WIDTH//2
        self.input_button.draw(screen)
        
        # Bouton custom class
        self.custom_class_button.rect.y = start_y + spacing
        self.custom_class_button.rect.centerx = WINDOW_WIDTH//2
        self.custom_class_button.draw(screen)
        
        # Bouton pour réinitialiser les scores
        self.reset_button.rect.y = start_y + spacing * 2
        self.reset_button.rect.centerx = WINDOW_WIDTH//2
        self.reset_button.draw(screen)
        
        # Bouton retour
        self.back_button.draw(screen)

    def draw_class_select(self, screen):
        # Fond noir
        screen.fill(BLACK)
        
        # Titre
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render(
            f"JOUEUR {self.player_data[self.current_player_selecting]['name']} - CLASSE",
            True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.1))
        
        # Effet de lueur pour le titre
        glow_surf = pygame.Surface((title.get_width() + 20, title.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*GOLD, 64), glow_surf.get_rect(), border_radius=10)
        screen.blit(glow_surf, glow_surf.get_rect(center=title_rect.center))
        screen.blit(title, title_rect)
        
        # Configuration de la grille des classes - Centrage horizontal
        grid_start_x = WINDOW_WIDTH * 0.1  # Réduit de 0.15 à 0.1 pour plus d'espace
        grid_width = WINDOW_WIDTH * 0.8    # Augmenté de 0.7 à 0.8 pour utiliser plus de largeur
        spacing = grid_width / (len(self.class_buttons) - 1)
        
        # Centrage vertical - Déplacé vers le centre de l'écran
        base_y = WINDOW_HEIGHT * 0.45  # Augmenté de 0.35 à 0.45
        
        # Affichage de chaque classe
        for i, class_button in enumerate(self.class_buttons):
            x = grid_start_x + i * spacing
            
            # Zone de prévisualisation - Augmentée en largeur et hauteur
            preview_size = 200  # Augmenté de 160 à 200 pour plus d'espace
            preview_rect = pygame.Rect(x - preview_size//2, base_y - preview_size//2, preview_size, preview_size)
            pygame.draw.rect(screen, (30, 30, 30), preview_rect, border_radius=10)
            pygame.draw.rect(screen, LIGHT_BLUE, preview_rect, width=1, border_radius=10)
            
            # Prévisualisation de la classe
            char_class = CharacterClass(class_button['type'])
            char_class.draw_preview(screen, x, base_y)
            
            # Bouton de sélection - Ajusté pour être plus proche des statistiques
            class_button['button'].rect.centerx = x
            class_button['button'].rect.top = base_y + preview_size//2 + 20  # Ajusté en fonction de la nouvelle taille
            class_button['button'].draw(screen)
        
        # Bouton retour
        self.back_button.draw(screen)

    def draw_map_select(self, screen):
        screen.fill(BLACK)
        
        # Titre avec effet de lueur
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render("SELECTION DE LA MAP", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.1))
        
        # Effet de lueur pour le titre
        glow_surf = pygame.Surface((title.get_width() + 20, title.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*GOLD, 64), glow_surf.get_rect(), border_radius=10)
        screen.blit(glow_surf, glow_surf.get_rect(center=title_rect.center))
        screen.blit(title, title_rect)
        
        # Affichage des maps en carrousel
        for i, map_button in enumerate(self.map_buttons):
            map_type = map_button['type']
            x = WINDOW_WIDTH * (0.25 + i * 0.25)
            y = WINDOW_HEIGHT * 0.4
            
            # Cadre de prévisualisation avec effet de profondeur
            preview_width = WINDOW_WIDTH * 0.2
            preview_height = WINDOW_HEIGHT * 0.2
            preview_rect = pygame.Rect(
                x - preview_width/2,
                y - preview_height/2,
                preview_width, preview_height
            )
            
            # Fond du cadre
            pygame.draw.rect(screen, (30, 30, 30), preview_rect.inflate(20, 20), border_radius=10)
            pygame.draw.rect(screen, LIGHT_BLUE, preview_rect.inflate(20, 20), width=1, border_radius=10)
            
            # Prévisualisation de la map
            self.maps[map_type].draw_preview(screen, preview_rect)
            
            # Description avec fond semi-transparent
            desc_surface = pygame.Surface((preview_width, 30), pygame.SRCALPHA)
            desc_surface.fill((0, 0, 0, 180))
            screen.blit(desc_surface, (preview_rect.x, preview_rect.bottom + 10))
            
            # Texte de description
            font = pygame.font.Font(None, FONT_SIZE_SMALL)
            desc = font.render(self.maps[map_type].description, True, WHITE)
            desc_rect = desc.get_rect(center=(x, preview_rect.bottom + 25))
            screen.blit(desc, desc_rect)
            
            # Positionnement et dessin du bouton
            map_button['button'].rect.centerx = x
            map_button['button'].rect.top = preview_rect.bottom + 50
            map_button['button'].draw(screen)
        
        self.back_button.draw(screen)

    def draw_player_select(self, screen):
        # Fond et titre
        screen.fill(BLACK)
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render(
            "ENTREZ VOTRE NOM", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT*0.2))
        
        # Champ de texte
        self.player_name_input.draw(screen)
        
        # Boutons
        self.validate_button.draw(screen)
        self.back_button.draw(screen)

    def draw_leaderboard(self, screen):
        screen.fill(BLACK)
        
        # Titre avec effet de lueur
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render("CLASSEMENT", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
        
        glow_surf = pygame.Surface((title.get_width() + 20, title.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*GOLD, 64), glow_surf.get_rect(), border_radius=10)
        screen.blit(glow_surf, glow_surf.get_rect(center=title_rect.center))
        screen.blit(title, title_rect)
        
        # Tableau avec effet de profondeur
        table_rect = pygame.Rect(WINDOW_WIDTH*0.1, 120,
                               WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.7)
        pygame.draw.rect(screen, (30, 30, 30), table_rect, border_radius=10)
        pygame.draw.rect(screen, LIGHT_BLUE, table_rect, width=1, border_radius=10)
        
        # En-têtes avec séparateurs
        headers = ["JOUEUR", "PARTIES", "VICTOIRES", "WIN RATE", "MEILLEUR SCORE"]
        header_widths = [0.3, 0.15, 0.15, 0.15, 0.25]  # Proportions relatives
        total_width = table_rect.width * 0.9
        x = table_rect.x + table_rect.width * 0.05
        
        # Barre de séparation des en-têtes
        pygame.draw.line(screen, LIGHT_BLUE,
                        (table_rect.x, 160),
                        (table_rect.right, 160),
                        1)
        
        for header, width in zip(headers, header_widths):
            text = pygame.font.Font(None, FONT_SIZE_MEDIUM).render(header, True, GOLD)
            screen.blit(text, (x, 130))
            x += total_width * width
        
        # Données avec alternance de couleurs
        y = 180
        for rank, (name, games, wins, score, win_rate) in enumerate(self.db.get_leaderboard(), 1):
            # Fond alterné pour une meilleure lisibilité
            if rank % 2 == 0:
                row_rect = pygame.Rect(table_rect.x + 5, y - 5,
                                     table_rect.width - 10, 30)
                pygame.draw.rect(screen, (40, 40, 40), row_rect, border_radius=5)
            
            x = table_rect.x + table_rect.width * 0.05
            color = GOLD if rank == 1 else WHITE
            
            values = [f"{rank}. {name}", str(games), str(wins), f"{win_rate}%", str(score)]
            for value, width in zip(values, header_widths):
                text = pygame.font.Font(None, FONT_SIZE_MEDIUM).render(value, True, color)
                screen.blit(text, (x, y))
                x += total_width * width
            y += 40
        
        self.back_button.draw(screen)

    def draw_rules(self, screen):
        screen.fill(BLACK)
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render("REGLES DU JEU", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT*0.1))

        # Texte des règles
        rules_text = [
            "Bienvenue dans Space Duel !",
            "",
            "- Chaque joueur contrôle un vaisseau spatial",
            "- Utilisez les commandes pour vous déplacer et tirer",
            "- Touchez votre adversaire pour lui infliger des dégâts",
            "- Activez votre bouclier pour vous protéger",
            "- Évitez les obstacles et utilisez-les stratégiquement",
            "- Le premier à éliminer son adversaire gagne la partie",
            "",
            "Contrôles :",
            "Joueur 1: ZQSD pour se déplacer, ESPACE pour tirer, SHIFT pour le bouclier",
            "Joueur 2: Flèches pour se déplacer, ENTER pour tirer, CTRL pour le bouclier"
        ]

        font = pygame.font.Font(None, FONT_SIZE_SMALL)
        y_pos = WINDOW_HEIGHT * 0.25
        for line in rules_text:
            text = font.render(line, True, WHITE)
            screen.blit(text, (WINDOW_WIDTH//2 - text.get_width()//2, y_pos))
            y_pos += FONT_SIZE_SMALL * 0.8

        # Déplacer le bouton retour en bas au milieu
        self.back_button.rect.x = WINDOW_WIDTH//2 - BUTTON_WIDTH//2
        self.back_button.rect.y = WINDOW_HEIGHT * 0.85
        self.back_button.draw(screen)

    def draw_char_select(self, screen):
        screen.fill(BLACK)
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render(
            f"JOUEUR {self.current_player_entering + 1} - SELECTIONNEZ VOTRE PERSONNAGE",
            True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT*0.1))
        
        # Séparateur vertical
        pygame.draw.line(screen, WHITE, 
                        (WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.2),
                        (WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.8),
                        2)
        
        # Titres des sections
        font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
        new_text = font.render("NOUVEAU PERSONNAGE", True, WHITE)
        screen.blit(new_text, (WINDOW_WIDTH * 0.25 - new_text.get_width()/2, WINDOW_HEIGHT * 0.3))
        
        existing_text = font.render("PERSONNAGES EXISTANTS", True, WHITE)
        screen.blit(existing_text, (WINDOW_WIDTH * 0.75 - existing_text.get_width()/2, WINDOW_HEIGHT * 0.2))
        
        # Bouton nouveau personnage (symbole +)
        self.new_char_button.draw(screen)
        
        # Zone de défilement pour les personnages existants
        if self.players_list:
            # Dessiner les boutons avec le décalage de défilement
            for player_button in self.existing_players_buttons:
                button = player_button['button']
                # Ajuster la position en fonction du défilement
                original_y = button.rect.y
                button.rect.y -= self.players_list.scroll_y
                
                # Ne dessiner que si le bouton est dans la zone visible
                if (self.players_list.visible_rect.top <= button.rect.y <= self.players_list.visible_rect.bottom or
                    self.players_list.visible_rect.top <= button.rect.bottom <= self.players_list.visible_rect.bottom):
                    button.draw(screen)
                
                # Restaurer la position originale
                button.rect.y = original_y
            
            # Dessiner la barre de défilement
            self.players_list.draw(screen)
            
        self.back_button.draw(screen)

    def draw_custom_class(self, screen):
        # Fond noir
        screen.fill(BLACK)
        
        # Titre
        title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        title = title_font.render("CUSTOM CLASS", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.2))
        screen.blit(title, title_rect)
        
        # Bouton retour
        self.back_button.draw(screen)

    def draw(self, screen):
        # Appel à la méthode de dessin correspondant à l'état actuel
        draw_methods = {
            "MAIN": self.draw_main_menu,
            "SETTINGS": self.draw_settings,
            "RULES": self.draw_rules,
            "CLASS_SELECT": self.draw_class_select,
            "PLAYER_SELECT": self.draw_player_select,
            "MAP_SELECT": self.draw_map_select,
            "LEADERBOARD": self.draw_leaderboard,
            "CHAR_SELECT": self.draw_char_select,
            "CUSTOM_CLASS": self.draw_custom_class
        }
        
        if self.state in draw_methods:
            draw_methods[self.state](screen)

    def reset_menu_state(self):
        """Réinitialise l'état du menu pour une nouvelle partie."""
        self.state = "MAIN"
        self.selected_classes = {0: None, 1: None}
        self.current_player_selecting = 0
        self.player_data = [None, None]
        self.current_player_entering = 0
        self.selected_map = None
        self.existing_players_buttons = []
        self.players_list = None

    def set_state(self, new_state):
        """Change l'état du menu et effectue les initialisations nécessaires."""
        # Si on retourne au menu principal, on vide l'historique
        if new_state == "MAIN":
            self.reset_menu_state()
            self.state_history = ["MAIN"]
            # Réinitialiser la sélection du bouton
            self.selected_button_index = 0
            if self.main_buttons:
                self.main_buttons[0].is_hovered = True
            return None
        
        # Initialisation spécifique pour chaque état
        if new_state == "CHAR_SELECT":
            self.current_player_entering = 0
            self.player_data = [None, None]
            self.create_existing_players_buttons()
            # Réinitialiser la sélection du bouton
            self.selected_button_index = 0
        elif new_state == "PLAYER_SELECT":
            self.player_name_input.text = ""
            self.player_name_input.active = True
            # Réinitialiser la sélection du bouton
            self.selected_button_index = 0
        elif new_state == "CLASS_SELECT":
            self.current_player_selecting = 0
            # Réinitialiser la sélection du bouton
            self.selected_button_index = 0
            if self.class_buttons:
                self.class_buttons[0]['button'].is_hovered = True
        elif new_state == "MAP_SELECT":
            # Réinitialiser la sélection du bouton
            self.selected_button_index = 0
            if self.map_buttons:
                self.map_buttons[0]['button'].is_hovered = True
        elif new_state == "SETTINGS":
            # Réinitialiser la sélection du bouton
            self.selected_button_index = 0
            self.input_button.is_hovered = True
        elif new_state == "RULES" or new_state == "LEADERBOARD":
            # Dans ces écrans, seul le bouton retour est disponible
            self.selected_button_index = 0
            self.back_button.is_hovered = True
        
        # Ajouter le nouvel état à l'historique
        self.state_history.append(new_state)
        self.state = new_state
        return None

    def get_current_buttons(self):
        """Retourne la liste des boutons disponibles dans l'état actuel."""
        buttons_by_state = {
            "MAIN": self.main_buttons,
            "SETTINGS": [self.input_button, self.custom_class_button, self.reset_button, self.back_button],
            "RULES": [self.back_button],
            "LEADERBOARD": [self.back_button],
            "CLASS_SELECT": [button['button'] for button in self.class_buttons] + [self.back_button],
            "MAP_SELECT": [button['button'] for button in self.map_buttons] + [self.back_button],
            "PLAYER_SELECT": [self.validate_button, self.back_button],
            "CHAR_SELECT": [self.new_char_button, self.back_button] + 
                          ([button['button'] for button in self.existing_players_buttons] if self.existing_players_buttons else []),
            "CUSTOM_CLASS": [self.back_button]
        }
        
        return buttons_by_state.get(self.state, [])

    def get_button_positions(self):
        """Retourne un dictionnaire avec les positions des boutons pour la navigation spatiale."""
        buttons = self.get_current_buttons()
        positions = {}
        
        for i, button in enumerate(buttons):
            positions[i] = {
                'x': button.rect.centerx,
                'y': button.rect.centery,
                'button': button
            }
        
        return positions

    def find_closest_button(self, current_index, direction):
        """Trouve le bouton le plus proche dans la direction spécifiée."""
        positions = self.get_button_positions()
        if not positions or current_index not in positions:
            return 0
        
        current_pos = positions[current_index]
        closest_index = current_index
        min_distance = float('inf')
        
        for index, pos in positions.items():
            if index == current_index:
                continue
                
            # Vérifier si le bouton est dans la direction souhaitée
            is_in_direction = False
            if direction == "UP" and pos['y'] < current_pos['y']:
                is_in_direction = True
            elif direction == "DOWN" and pos['y'] > current_pos['y']:
                is_in_direction = True
            elif direction == "LEFT" and pos['x'] < current_pos['x']:
                is_in_direction = True
            elif direction == "RIGHT" and pos['x'] > current_pos['x']:
                is_in_direction = True
                
            if is_in_direction:
                # Calculer la distance euclidienne
                dx = pos['x'] - current_pos['x']
                dy = pos['y'] - current_pos['y']
                distance = (dx * dx + dy * dy) ** 0.5
                
                # Favoriser les boutons qui sont plus alignés avec la direction
                alignment_factor = 1.0
                if direction in ["UP", "DOWN"]:
                    # Pénaliser les boutons qui sont trop décalés horizontalement
                    alignment_factor = 1.0 + (abs(dx) / (abs(dy) + 1)) * 0.5
                else:  # LEFT, RIGHT
                    # Pénaliser les boutons qui sont trop décalés verticalement
                    alignment_factor = 1.0 + (abs(dy) / (abs(dx) + 1)) * 0.5
                
                adjusted_distance = distance * alignment_factor
                
                if adjusted_distance < min_distance:
                    min_distance = adjusted_distance
                    closest_index = index
        
        # Si aucun bouton n'est trouvé dans la direction, garder le même
        return closest_index if min_distance < float('inf') else current_index

    def update_selected_button(self):
        """Met à jour le bouton sélectionné en fonction de l'index actuel."""
        buttons = self.get_current_buttons()
        
        # Réinitialiser tous les boutons
        for button in buttons:
            button.is_hovered = False
        
        # Sélectionner le bouton actuel
        if buttons and 0 <= self.selected_button_index < len(buttons):
            buttons[self.selected_button_index].is_hovered = True

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "QUIT"

        # Gestion de la touche Échap pour revenir en arrière
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Si on est dans le champ de texte, on le désactive d'abord
            if self.state == "PLAYER_SELECT" and self.player_name_input.active:
                self.player_name_input.active = False
            else:
                # Sinon, on revient à l'état précédent
                return self.go_back()

        # Navigation au clavier
        if event.type == pygame.KEYDOWN:
            buttons = self.get_current_buttons()
            
            # Navigation avec les flèches
            if event.key == pygame.K_UP:
                if self.state == "PLAYER_SELECT" and self.player_name_input.active:
                    # Si on est dans le champ de texte, on le désactive et on sélectionne un bouton
                    self.player_name_input.active = False
                    self.selected_button_index = 0  # Sélectionner le bouton valider
                else:
                    # Naviguer vers le bouton le plus proche vers le haut
                    self.selected_button_index = self.find_closest_button(self.selected_button_index, "UP")
                self.update_selected_button()
                return None
                
            elif event.key == pygame.K_DOWN:
                if self.state == "PLAYER_SELECT" and not self.player_name_input.active and self.selected_button_index == 0:
                    # Si on est sur le bouton valider, on active le champ de texte
                    self.player_name_input.active = True
                else:
                    # Naviguer vers le bouton le plus proche vers le bas
                    self.selected_button_index = self.find_closest_button(self.selected_button_index, "DOWN")
                self.update_selected_button()
                return None
                
            elif event.key == pygame.K_LEFT:
                # Naviguer vers le bouton le plus proche vers la gauche
                self.selected_button_index = self.find_closest_button(self.selected_button_index, "LEFT")
                self.update_selected_button()
                return None
                
            elif event.key == pygame.K_RIGHT:
                # Naviguer vers le bouton le plus proche vers la droite
                self.selected_button_index = self.find_closest_button(self.selected_button_index, "RIGHT")
                self.update_selected_button()
                return None
                
            elif event.key == pygame.K_RETURN:
                # Activer le bouton sélectionné
                if self.state == "PLAYER_SELECT" and self.player_name_input.active:
                    # Si on est dans le champ de texte, valider la saisie
                    if self.player_name_input.text.strip():
                        player_name = self.player_name_input.text.strip()
                        player_id = self.db.add_player(player_name)
                        self.player_data[self.current_player_entering] = {
                            'id': player_id,
                            'name': player_name
                        }
                        
                        if self.current_player_entering == 0:
                            self.current_player_entering = 1
                            self.player_name_input.text = ""
                            return self.set_state("CHAR_SELECT")
                        else:
                            # Les deux joueurs sont enregistrés
                            return self.set_state("CLASS_SELECT")
                else:
                    # Activer le bouton sélectionné
                    if buttons and 0 <= self.selected_button_index < len(buttons):
                        selected_button = buttons[self.selected_button_index]
                        
                        # Traiter l'action en fonction de l'état et du bouton
                        if self.state == "MAIN":
                            if self.selected_button_index == 0:  # JOUER
                                return self.set_state("CHAR_SELECT")
                            elif self.selected_button_index == 1:  # REGLAGES
                                return self.set_state("SETTINGS")
                            elif self.selected_button_index == 2:  # REGLES
                                return self.set_state("RULES")
                            elif self.selected_button_index == 3:  # LEADERBOARD
                                return self.set_state("LEADERBOARD")
                                
                        elif self.state == "SETTINGS":
                            if selected_button == self.input_button:
                                self.settings['input_mode'] = 'PC' if self.settings['input_mode'] == 'ARCADE' else 'ARCADE'
                                self.input_button.text = f"INPUT: {self.settings['input_mode']}"
                                self.db.save_settings(self.settings)
                            elif selected_button == self.custom_class_button:
                                return self.set_state("CUSTOM_CLASS")
                            elif selected_button == self.reset_button:
                                self.db.reset_scores()
                            elif selected_button == self.back_button:
                                return self.go_back()
                                
                        elif self.state == "RULES" or self.state == "LEADERBOARD":
                            if selected_button == self.back_button:
                                return self.go_back()
                                
                        elif self.state == "CLASS_SELECT":
                            if selected_button == self.back_button:
                                if self.current_player_selecting > 0:
                                    self.current_player_selecting -= 1
                                    self.selected_classes[self.current_player_selecting] = None
                                else:
                                    return self.go_back()
                            else:
                                # Trouver l'index du bouton de classe sélectionné
                                for i, class_button in enumerate(self.class_buttons):
                                    if class_button['button'] == selected_button:
                                        self.selected_classes[self.current_player_selecting] = class_button['type']
                                        
                                        if self.current_player_selecting == 0:
                                            self.current_player_selecting = 1
                                        else:
                                            # Les deux joueurs ont choisi leur classe
                                            return self.set_state("MAP_SELECT")
                                        break
                                        
                        elif self.state == "MAP_SELECT":
                            if selected_button == self.back_button:
                                self.current_player_selecting = 1
                                return self.go_back()
                            else:
                                # Trouver l'index du bouton de map sélectionné
                                for i, map_button in enumerate(self.map_buttons):
                                    if map_button['button'] == selected_button:
                                        self.selected_map = map_button['type']
                                        return "START_GAME"
                                        
                        elif self.state == "PLAYER_SELECT":
                            if selected_button == self.back_button:
                                # Désactiver le champ de texte avant de revenir en arrière
                                self.player_name_input.active = False
                                self.player_name_input.text = ""
                                
                                if self.current_player_entering > 0:
                                    self.current_player_entering -= 1
                                    self.player_data[self.current_player_entering] = None
                                    return self.set_state("CHAR_SELECT")
                                else:
                                    return self.go_back()
                            elif selected_button == self.validate_button:
                                if self.player_name_input.text.strip():
                                    player_name = self.player_name_input.text.strip()
                                    player_id = self.db.add_player(player_name)
                                    self.player_data[self.current_player_entering] = {
                                        'id': player_id,
                                        'name': player_name
                                    }
                                    
                                    if self.current_player_entering == 0:
                                        self.current_player_entering = 1
                                        self.player_name_input.text = ""
                                        return self.set_state("CHAR_SELECT")
                                    else:
                                        # Les deux joueurs sont enregistrés
                                        return self.set_state("CLASS_SELECT")
                                        
                        elif self.state == "CHAR_SELECT":
                            if selected_button == self.back_button:
                                if self.current_player_entering > 0:
                                    self.current_player_entering -= 1
                                    self.player_data[self.current_player_entering] = None
                                    return self.set_state("CHAR_SELECT")
                                else:
                                    return self.go_back()
                            elif selected_button == self.new_char_button:
                                return self.set_state("PLAYER_SELECT")
                            else:
                                # Vérifier si c'est un bouton de personnage existant
                                for player_button in self.existing_players_buttons:
                                    if player_button['button'] == selected_button:
                                        self.player_data[self.current_player_entering] = {
                                            'id': player_button['id'],
                                            'name': player_button['name']
                                        }
                                        
                                        if self.current_player_entering == 0:
                                            self.current_player_entering = 1
                                            self.create_existing_players_buttons()
                                        else:
                                            return self.set_state("CLASS_SELECT")
                                        break
                return None

        # Si on utilise la navigation au clavier, on ignore les événements de la souris
        if self.keyboard_navigation:
            # Gérer uniquement les événements du champ de texte en mode clavier
            if self.state == "PLAYER_SELECT" and self.player_name_input.active:
                self.player_name_input.handle_event(event)
            return None

        # Le code existant pour la gestion de la souris reste inchangé mais ne sera pas utilisé
        # si keyboard_navigation est True
        if self.state == "MAIN":
            for i, button in enumerate(self.main_buttons):
                if button.handle_event(event):
                    if i == 0:  # JOUER
                        return self.set_state("CHAR_SELECT")
                    elif i == 1:  # REGLAGES
                        return self.set_state("SETTINGS")
                    elif i == 2:  # REGLES
                        return self.set_state("RULES")
                    elif i == 3:  # LEADERBOARD
                        return self.set_state("LEADERBOARD")

        elif self.state == "SETTINGS":
            if event.key == pygame.K_LEFT:
                self.selected_button_index = (self.selected_button_index - 1) % len(self.get_current_buttons())
                self.update_selected_button()
            elif event.key == pygame.K_RIGHT:
                self.selected_button_index = (self.selected_button_index + 1) % len(self.get_current_buttons())
                self.update_selected_button()
            elif event.key == pygame.K_RETURN:
                buttons = self.get_current_buttons()
                selected_button = buttons[self.selected_button_index]
                
                if selected_button == self.back_button:
                    return self.go_back()
                elif selected_button == self.input_button:
                    self.toggle_input_mode()
                elif selected_button == self.custom_class_button:
                    return self.set_state("CUSTOM_CLASS")
                elif selected_button == self.reset_button:
                    self.db.reset_scores()
                    
        elif self.state == "RULES":
            if self.back_button.handle_event(event):
                return self.go_back()
                
        elif self.state == "CLASS_SELECT":
            if self.back_button.handle_event(event):
                if self.current_player_selecting > 0:
                    self.current_player_selecting -= 1
                    self.selected_classes[self.current_player_selecting] = None
                else:
                    return self.go_back()
                return None
                
            for class_button in self.class_buttons:
                if class_button['button'].handle_event(event):
                    self.selected_classes[self.current_player_selecting] = class_button['type']
                    
                    if self.current_player_selecting == 0:
                        self.current_player_selecting = 1
                    else:
                        # Les deux joueurs ont choisi leur classe
                        return self.set_state("MAP_SELECT")
                        
        elif self.state == "MAP_SELECT":
            if self.back_button.handle_event(event):
                self.current_player_selecting = 1
                return self.go_back()
                
            for map_button in self.map_buttons:
                if map_button['button'].handle_event(event):
                    self.selected_map = map_button['type']
                    return "START_GAME"
                        
        elif self.state == "PLAYER_SELECT":
            if self.back_button.handle_event(event):
                # Désactiver le champ de texte avant de revenir en arrière
                self.player_name_input.active = False
                self.player_name_input.text = ""
                
                if self.current_player_entering > 0:
                    self.current_player_entering -= 1
                    self.player_data[self.current_player_entering] = None
                    return self.set_state("CHAR_SELECT")
                else:
                    return self.go_back()
                
            # Gérer les événements du champ de texte
            self.player_name_input.handle_event(event)
                
            if self.validate_button.handle_event(event) or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.player_name_input.active):
                if self.player_name_input.text.strip():
                    # Enregistrement du joueur dans la base de données
                    player_name = self.player_name_input.text.strip()
                    player_id = self.db.add_player(player_name)
                    self.player_data[self.current_player_entering] = {
                        'id': player_id,
                        'name': player_name
                    }
                    
                    if self.current_player_entering == 0:
                        self.current_player_entering = 1
                        self.player_name_input.text = ""
                        return self.set_state("CHAR_SELECT")
                    else:
                        # Les deux joueurs sont enregistrés
                        return self.set_state("CLASS_SELECT")
                        
        elif self.state == "LEADERBOARD":
            if self.back_button.handle_event(event):
                return self.go_back()
                
        elif self.state == "CHAR_SELECT":
            if self.back_button.handle_event(event):
                if self.current_player_entering > 0:
                    self.current_player_entering -= 1
                    self.player_data[self.current_player_entering] = None
                    return self.set_state("CHAR_SELECT")
                else:
                    return self.go_back()
                
            if self.new_char_button.handle_event(event):
                return self.set_state("PLAYER_SELECT")
                
            # Gérer les événements de la liste défilante
            if self.players_list and self.players_list.handle_event(event):
                return None
                
            # Gérer les clics sur les boutons de personnages
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.players_list and self.players_list.visible_rect.collidepoint(mouse_pos):
                    # Ajuster la position de la souris pour le défilement
                    adjusted_y = mouse_pos[1] + self.players_list.scroll_y
                    adjusted_pos = (mouse_pos[0], adjusted_y)
                    
                    for player_button in self.existing_players_buttons:
                        button = player_button['button']
                        if button.rect.collidepoint(adjusted_pos):
                            self.player_data[self.current_player_entering] = {
                                'id': player_button['id'],
                                'name': player_button['name']
                            }
                            
                            if self.current_player_entering == 0:
                                self.current_player_entering = 1
                                self.create_existing_players_buttons()
                            else:
                                return self.set_state("CLASS_SELECT")
                            return None

        elif self.state == "CUSTOM_CLASS":
            if event.key == pygame.K_LEFT:
                self.selected_button_index = (self.selected_button_index - 1) % len(self.get_current_buttons())
                self.update_selected_button()
            elif event.key == pygame.K_RIGHT:
                self.selected_button_index = (self.selected_button_index + 1) % len(self.get_current_buttons())
                self.update_selected_button()
            elif event.key == pygame.K_RETURN:
                buttons = self.get_current_buttons()
                selected_button = buttons[self.selected_button_index]
                
                if selected_button == self.back_button:
                    return self.go_back()

        return None

    def get_game_settings(self):
        return {
            'player_classes': self.selected_classes,
            'player_data': self.player_data,
            'volume': self.settings['volume'],
            'input_mode': self.settings['input_mode'],
            'map_type': self.selected_map
        }

    def go_back(self):
        """Retourne à l'état précédent dans l'historique."""
        if len(self.state_history) <= 1:
            return self.set_state("MAIN")
            
        # Sauvegarder l'état actuel avant de le modifier
        current_state = self.state
            
        # Retirer l'état actuel
        self.state_history.pop()
        # Récupérer l'état précédent
        previous_state = self.state_history[-1]
        
        # Si on revient au menu principal
        if previous_state == "MAIN":
            return self.set_state("MAIN")
        
        # Gestion spécifique pour certains états
        if current_state == "PLAYER_SELECT":
            # Si on quitte l'écran de saisie du nom
            self.player_name_input.active = False
            self.player_name_input.text = ""
        
        # Mettre à jour l'état actuel
        self.state = previous_state
        
        # Réinitialiser la sélection du bouton
        self.selected_button_index = 0
        
        # Mettre à jour l'état visuel des boutons selon l'état précédent
        button_highlight = {
            "MAIN": lambda: self.main_buttons[0].is_hovered if self.main_buttons else None,
            "SETTINGS": lambda: self.input_button.is_hovered,
            "CLASS_SELECT": lambda: self.class_buttons[0]['button'].is_hovered if self.class_buttons else None,
            "MAP_SELECT": lambda: self.map_buttons[0]['button'].is_hovered if self.map_buttons else None,
            "CHAR_SELECT": lambda: self.new_char_button.is_hovered,
            "RULES": lambda: self.back_button.is_hovered,
            "LEADERBOARD": lambda: self.back_button.is_hovered
        }
        
        if previous_state in button_highlight:
            button_highlight[previous_state]()
        
        # Mettre à jour l'état visuel de tous les boutons
        self.update_selected_button()
        return None 