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
        self.color = (30, 30, 30)
        self.hover_color = (45, 45, 45)
        self.text_color = WHITE
        self.is_hovered = False
        self.image = None
        self.image_rect = None
        self.original_width = width
        self.original_height = height
        self.hover_scale = 1.1
        
        if image_path:
            try:
                original_image = pygame.image.load(image_path).convert_alpha()
                img_width, img_height = original_image.get_size()
                ratio = min(width / img_width, height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                self.image = pygame.transform.scale(original_image, (new_width, new_height))
                self.original_image = self.image.copy()
                
                self.image_rect = self.image.get_rect(center=self.rect.center)
                
                hover_width = int(new_width * self.hover_scale)
                hover_height = int(new_height * self.hover_scale)
                self.hover_image = pygame.transform.scale(original_image, (hover_width, hover_height))
                self.hover_image_rect = self.hover_image.get_rect(center=self.rect.center)
            except Exception as e:
                print(f"Erreur lors du chargement de l'image: {e}")
                self.image = None

    def calculate_font_size(self, width, height, base_font_size):
        min_dimension = min(width, height)
        return int(min_dimension * 0.6) if self.text == "+" else int(min_dimension * 0.42)

    def draw(self, screen):
        if self.image:
            if self.is_hovered:
                screen.blit(self.hover_image, self.hover_image_rect)
            else:
                screen.blit(self.image, self.image_rect)
        else:
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(screen, color, self.rect, border_radius=10)
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.image and self.image_rect:
                self.is_hovered = self.image_rect.collidepoint(event.pos)
            else:
                self.is_hovered = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
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
        pygame.draw.rect(screen, WHITE, self.rect)
        
        text_to_render = self.text if self.text else self.placeholder
        text_color = BLACK if self.text else (128, 128, 128)
        text_surface = self.font.render(text_to_render, True, text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
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
            if event.button == 1:
                if self.scrollbar_rect.collidepoint(event.pos):
                    self.dragging = True
                    return True
            elif event.button == 4:
                self.scroll_y = max(0, self.scroll_y - 30)
                self.update_scrollbar()
                return True
            elif event.button == 5:
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
        pygame.draw.rect(screen, (50, 50, 50), pygame.Rect(self.scrollbar_rect.x, self.visible_rect.y,
                                                         self.scrollbar_rect.width, self.visible_rect.height))
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
        
        self.selected_button_index = 0
        self.keyboard_navigation = True
        
        try:
            self.background = pygame.image.load("assets/background.png").convert()
            self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except:
            self.background = None
            print("Image de fond non trouvée. Placez une image 'background.png' dans le dossier assets/")
        
        self.selected_classes = {0: None, 1: None}
        self.current_player_selecting = 0
        self.player_data = [None, None]
        self.current_player_entering = 0
        self.selected_map = None
        self.maps = MapManager.get_maps()
        self.existing_players_buttons = []
        self.players_list = None
        
        self.back_button = Button(WINDOW_WIDTH*0.05, WINDOW_HEIGHT*0.9, 
                                BUTTON_WIDTH, BUTTON_HEIGHT, "RETOUR", FONT_SIZE_MEDIUM,
                                image_path="assets/retour_button.png")
                                
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
            
        self.player_name_input = TextInput(
            WINDOW_WIDTH//2 - WINDOW_WIDTH*0.15, WINDOW_HEIGHT*0.4,
            WINDOW_WIDTH*0.3, BUTTON_HEIGHT, "Entrez votre nom"
        )
        
        self.validate_button = Button(
            WINDOW_WIDTH//2 - BUTTON_WIDTH//2, WINDOW_HEIGHT*0.6,
            BUTTON_WIDTH, BUTTON_HEIGHT, "VALIDER", FONT_SIZE_MEDIUM
        )

        self.new_char_button = Button(
            WINDOW_WIDTH*0.25 - (BUTTON_WIDTH * 0.5)/2,
            WINDOW_HEIGHT*0.4,
            BUTTON_WIDTH * 0.5, BUTTON_WIDTH * 0.5,
            "+", FONT_SIZE_LARGE
        )

    def create_existing_players_buttons(self):
        players = self.db.get_all_players()
        self.existing_players_buttons = []
        
        if players:
            if self.current_player_entering == 1 and self.player_data[0]:
                players = [(pid, name) for pid, name in players if pid != self.player_data[0]['id']]
            
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
        if self.background:
            screen.blit(self.background, (0, 0))
        else:
            screen.fill(BLACK)
        
        title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        title = title_font.render("SPACE DUEL", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.2))
        screen.blit(title, title_rect)
        
        button_spacing = WINDOW_HEIGHT * 0.12
        for i, button in enumerate(self.main_buttons):
            button.rect.centerx = WINDOW_WIDTH//2
            button.rect.y = WINDOW_HEIGHT * 0.4 + i * button_spacing
            button.draw(screen)

    def draw_settings(self, screen):
        screen.fill(BLACK)
        
        title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        title = title_font.render("PARAMETRES", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.2))
        screen.blit(title, title_rect)
        
        start_y = WINDOW_HEIGHT * 0.35
        spacing = WINDOW_HEIGHT * 0.12
        
        self.input_button.rect.y = start_y
        self.input_button.rect.centerx = WINDOW_WIDTH//2
        self.input_button.draw(screen)
        
        self.custom_class_button.rect.y = start_y + spacing
        self.custom_class_button.rect.centerx = WINDOW_WIDTH//2
        self.custom_class_button.draw(screen)
        
        self.reset_button.rect.y = start_y + spacing * 2
        self.reset_button.rect.centerx = WINDOW_WIDTH//2
        self.reset_button.draw(screen)
        
        self.back_button.draw(screen)

    def draw_class_select(self, screen):
        screen.fill(BLACK)
        
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render(
            f"JOUEUR {self.player_data[self.current_player_selecting]['name']} - CLASSE",
            True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.1))
        
        glow_surf = pygame.Surface((title.get_width() + 20, title.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*GOLD, 64), glow_surf.get_rect(), border_radius=10)
        screen.blit(glow_surf, glow_surf.get_rect(center=title_rect.center))
        screen.blit(title, title_rect)
        
        grid_start_x = WINDOW_WIDTH * 0.1
        grid_width = WINDOW_WIDTH * 0.8
        spacing = grid_width / (len(self.class_buttons) - 1)
        
        base_y = WINDOW_HEIGHT * 0.45
        
        for i, class_button in enumerate(self.class_buttons):
            x = grid_start_x + i * spacing
            
            preview_size = 200
            preview_rect = pygame.Rect(x - preview_size//2, base_y - preview_size//2, preview_size, preview_size)
            pygame.draw.rect(screen, (30, 30, 30), preview_rect, border_radius=10)
            pygame.draw.rect(screen, LIGHT_BLUE, preview_rect, width=1, border_radius=10)
            
            char_class = CharacterClass(class_button['type'])
            char_class.draw_preview(screen, x, base_y)
            
            class_button['button'].rect.centerx = x
            class_button['button'].rect.top = base_y + preview_size//2 + 20
            class_button['button'].draw(screen)
        
        self.back_button.draw(screen)

    def draw_map_select(self, screen):
        screen.fill(BLACK)
        
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render("SELECTION DE LA MAP", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.1))
        
        glow_surf = pygame.Surface((title.get_width() + 20, title.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*GOLD, 64), glow_surf.get_rect(), border_radius=10)
        screen.blit(glow_surf, glow_surf.get_rect(center=title_rect.center))
        screen.blit(title, title_rect)
        
        for i, map_button in enumerate(self.map_buttons):
            map_type = map_button['type']
            x = WINDOW_WIDTH * (0.25 + i * 0.25)
            y = WINDOW_HEIGHT * 0.4
            
            preview_width = WINDOW_WIDTH * 0.2
            preview_height = WINDOW_HEIGHT * 0.2
            preview_rect = pygame.Rect(
                x - preview_width/2,
                y - preview_height/2,
                preview_width, preview_height
            )
            
            pygame.draw.rect(screen, (30, 30, 30), preview_rect.inflate(20, 20), border_radius=10)
            pygame.draw.rect(screen, LIGHT_BLUE, preview_rect.inflate(20, 20), width=1, border_radius=10)
            
            self.maps[map_type].draw_preview(screen, preview_rect)
            
            desc_surface = pygame.Surface((preview_width, 30), pygame.SRCALPHA)
            desc_surface.fill((0, 0, 0, 180))
            screen.blit(desc_surface, (preview_rect.x, preview_rect.bottom + 10))
            
            font = pygame.font.Font(None, FONT_SIZE_SMALL)
            desc = font.render(self.maps[map_type].description, True, WHITE)
            desc_rect = desc.get_rect(center=(x, preview_rect.bottom + 25))
            screen.blit(desc, desc_rect)
            
            map_button['button'].rect.centerx = x
            map_button['button'].rect.top = preview_rect.bottom + 50
            map_button['button'].draw(screen)
        
        self.back_button.draw(screen)

    def draw_player_select(self, screen):
        screen.fill(BLACK)
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render(
            "ENTREZ VOTRE NOM", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT*0.2))
        
        self.player_name_input.draw(screen)
        
        self.validate_button.draw(screen)
        self.back_button.draw(screen)

    def draw_leaderboard(self, screen):
        screen.fill(BLACK)
        
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render("CLASSEMENT", True, GOLD)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, 50))
        
        glow_surf = pygame.Surface((title.get_width() + 20, title.get_height() + 20), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*GOLD, 64), glow_surf.get_rect(), border_radius=10)
        screen.blit(glow_surf, glow_surf.get_rect(center=title_rect.center))
        screen.blit(title, title_rect)
        
        table_rect = pygame.Rect(WINDOW_WIDTH*0.1, 120,
                               WINDOW_WIDTH*0.8, WINDOW_HEIGHT*0.7)
        pygame.draw.rect(screen, (30, 30, 30), table_rect, border_radius=10)
        pygame.draw.rect(screen, LIGHT_BLUE, table_rect, width=1, border_radius=10)
        
        headers = ["JOUEUR", "PARTIES", "VICTOIRES", "WIN RATE", "MEILLEUR SCORE"]
        header_widths = [0.3, 0.15, 0.15, 0.15, 0.25]
        total_width = table_rect.width * 0.9
        x = table_rect.x + table_rect.width * 0.05
        
        pygame.draw.line(screen, LIGHT_BLUE,
                        (table_rect.x, 160),
                        (table_rect.right, 160),
                        1)
        
        for header, width in zip(headers, header_widths):
            text = pygame.font.Font(None, FONT_SIZE_MEDIUM).render(header, True, GOLD)
            screen.blit(text, (x, 130))
            x += total_width * width
        
        y = 180
        for rank, (name, games, wins, score, win_rate) in enumerate(self.db.get_leaderboard(), 1):
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

        self.back_button.rect.x = WINDOW_WIDTH//2 - BUTTON_WIDTH//2
        self.back_button.rect.y = WINDOW_HEIGHT * 0.85
        self.back_button.draw(screen)

    def draw_char_select(self, screen):
        screen.fill(BLACK)
        title = pygame.font.Font(None, FONT_SIZE_LARGE).render(
            f"JOUEUR {self.current_player_entering + 1} - SELECTIONNEZ VOTRE PERSONNAGE",
            True, WHITE)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT*0.1))
        
        pygame.draw.line(screen, WHITE, 
                        (WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.2),
                        (WINDOW_WIDTH * 0.5, WINDOW_HEIGHT * 0.8),
                        2)
        
        font = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        
        new_text = font.render("NOUVEAU PERSONNAGE", True, WHITE)
        screen.blit(new_text, (WINDOW_WIDTH * 0.25 - new_text.get_width()/2, WINDOW_HEIGHT * 0.3))
        
        existing_text = font.render("PERSONNAGES EXISTANTS", True, WHITE)
        screen.blit(existing_text, (WINDOW_WIDTH * 0.75 - existing_text.get_width()/2, WINDOW_HEIGHT * 0.2))
        
        self.new_char_button.draw(screen)
        
        if self.players_list:
            for player_button in self.existing_players_buttons:
                button = player_button['button']
                original_y = button.rect.y
                button.rect.y -= self.players_list.scroll_y
                
                if (self.players_list.visible_rect.top <= button.rect.y <= self.players_list.visible_rect.bottom or
                    self.players_list.visible_rect.top <= button.rect.bottom <= self.players_list.visible_rect.bottom):
                    button.draw(screen)
                
                button.rect.y = original_y
            
            self.players_list.draw(screen)
            
        self.back_button.draw(screen)

    def draw_custom_class(self, screen):
        screen.fill(BLACK)
        
        title_font = pygame.font.Font(None, FONT_SIZE_LARGE)
        title = title_font.render("CUSTOM CLASS", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*0.2))
        screen.blit(title, title_rect)
        
        self.back_button.draw(screen)

    def draw(self, screen):
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
        self.state = "MAIN"
        self.selected_classes = {0: None, 1: None}
        self.current_player_selecting = 0
        self.player_data = [None, None]
        self.current_player_entering = 0
        self.selected_map = None
        self.existing_players_buttons = []
        self.players_list = None

    def set_state(self, new_state):
        if new_state == "MAIN":
            self.reset_menu_state()
            self.state_history = ["MAIN"]
            self.selected_button_index = 0
            if self.main_buttons:
                self.main_buttons[0].is_hovered = True
            return None
        
        if new_state == "CHAR_SELECT":
            self.current_player_entering = 0
            self.player_data = [None, None]
            self.create_existing_players_buttons()
            self.selected_button_index = 0
        elif new_state == "PLAYER_SELECT":
            self.player_name_input.text = ""
            self.player_name_input.active = True
            self.selected_button_index = 0
        elif new_state == "CLASS_SELECT":
            self.current_player_selecting = 0
            self.selected_button_index = 0
            if self.class_buttons:
                self.class_buttons[0]['button'].is_hovered = True
        elif new_state == "MAP_SELECT":
            self.selected_button_index = 0
            if self.map_buttons:
                self.map_buttons[0]['button'].is_hovered = True
        elif new_state == "SETTINGS":
            self.selected_button_index = 0
            self.input_button.is_hovered = True
        elif new_state == "RULES" or new_state == "LEADERBOARD":
            self.selected_button_index = 0
            self.back_button.is_hovered = True
        
        self.state_history.append(new_state)
        self.state = new_state
        return None

    def get_current_buttons(self):
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
        positions = self.get_button_positions()
        if not positions or current_index not in positions:
            return 0
        
        current_pos = positions[current_index]
        closest_index = current_index
        min_distance = float('inf')
        
        for index, pos in positions.items():
            if index == current_index:
                continue
                
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
                dx = pos['x'] - current_pos['x']
                dy = pos['y'] - current_pos['y']
                distance = (dx * dx + dy * dy) ** 0.5
                
                alignment_factor = 1.0
                if direction in ["UP", "DOWN"]:
                    alignment_factor = 1.0 + (abs(dx) / (abs(dy) + 1)) * 0.5
                else:
                    alignment_factor = 1.0 + (abs(dy) / (abs(dx) + 1)) * 0.5
                
                adjusted_distance = distance * alignment_factor
                
                if adjusted_distance < min_distance:
                    min_distance = adjusted_distance
                    closest_index = index
        
        return closest_index if min_distance < float('inf') else current_index

    def update_selected_button(self):
        buttons = self.get_current_buttons()
        
        for button in buttons:
            button.is_hovered = False
        
        if buttons and 0 <= self.selected_button_index < len(buttons):
            buttons[self.selected_button_index].is_hovered = True

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return "QUIT"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.state == "PLAYER_SELECT" and self.player_name_input.active:
                self.player_name_input.active = False
            else:
                return self.go_back()

        if event.type == pygame.KEYDOWN:
            buttons = self.get_current_buttons()
            
            if event.key == pygame.K_UP:
                if self.state == "PLAYER_SELECT" and self.player_name_input.active:
                    self.player_name_input.active = False
                    self.selected_button_index = 0
                else:
                    self.selected_button_index = self.find_closest_button(self.selected_button_index, "UP")
                self.update_selected_button()
                return None
                
            elif event.key == pygame.K_DOWN:
                if self.state == "PLAYER_SELECT" and not self.player_name_input.active and self.selected_button_index == 0:
                    self.player_name_input.active = True
                else:
                    self.selected_button_index = self.find_closest_button(self.selected_button_index, "DOWN")
                self.update_selected_button()
                return None
                
            elif event.key == pygame.K_LEFT:
                self.selected_button_index = self.find_closest_button(self.selected_button_index, "LEFT")
                self.update_selected_button()
                return None
                
            elif event.key == pygame.K_RIGHT:
                self.selected_button_index = self.find_closest_button(self.selected_button_index, "RIGHT")
                self.update_selected_button()
                return None
                
            elif event.key == pygame.K_RETURN:
                if self.state == "PLAYER_SELECT" and self.player_name_input.active:
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
                            return self.set_state("CLASS_SELECT")
                else:
                    if buttons and 0 <= self.selected_button_index < len(buttons):
                        selected_button = buttons[self.selected_button_index]
                        
                        if self.state == "MAIN":
                            if self.selected_button_index == 0:
                                return self.set_state("CHAR_SELECT")
                            elif self.selected_button_index == 1:
                                return self.set_state("SETTINGS")
                            elif self.selected_button_index == 2:
                                return self.set_state("RULES")
                            elif self.selected_button_index == 3:
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
                                for i, class_button in enumerate(self.class_buttons):
                                    if class_button['button'] == selected_button:
                                        self.selected_classes[self.current_player_selecting] = class_button['type']
                                        
                                        if self.current_player_selecting == 0:
                                            self.current_player_selecting = 1
                                        else:
                                            return self.set_state("MAP_SELECT")
                                        break
                                        
                        elif self.state == "MAP_SELECT":
                            if selected_button == self.back_button:
                                self.current_player_selecting = 1
                                return self.go_back()
                            else:
                                for i, map_button in enumerate(self.map_buttons):
                                    if map_button['button'] == selected_button:
                                        self.selected_map = map_button['type']
                                        return "START_GAME"
                                        
                        elif self.state == "PLAYER_SELECT":
                            if selected_button == self.back_button:
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

        if self.keyboard_navigation:
            if self.state == "PLAYER_SELECT" and self.player_name_input.active:
                self.player_name_input.handle_event(event)
            return None

        if self.state == "MAIN":
            for i, button in enumerate(self.main_buttons):
                if button.handle_event(event):
                    if i == 0:
                        return self.set_state("CHAR_SELECT")
                    elif i == 1:
                        return self.set_state("SETTINGS")
                    elif i == 2:
                        return self.set_state("RULES")
                    elif i == 3:
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
                self.player_name_input.active = False
                self.player_name_input.text = ""
                
                if self.current_player_entering > 0:
                    self.current_player_entering -= 1
                    self.player_data[self.current_player_entering] = None
                    return self.set_state("CHAR_SELECT")
                else:
                    return self.go_back()
                
            self.player_name_input.handle_event(event)
                
            if self.validate_button.handle_event(event) or \
               (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and self.player_name_input.active):
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
                
            if self.players_list and self.players_list.handle_event(event):
                return None
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if self.players_list and self.players_list.visible_rect.collidepoint(mouse_pos):
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
        if len(self.state_history) <= 1:
            return self.set_state("MAIN")
            
        current_state = self.state
            
        self.state_history.pop()
        previous_state = self.state_history[-1]
        
        if previous_state == "MAIN":
            return self.set_state("MAIN")
        
        if current_state == "PLAYER_SELECT":
            self.player_name_input.active = False
            self.player_name_input.text = ""
        
        self.state = previous_state
        
        self.selected_button_index = 0
        
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
        
        self.update_selected_button()
        return None 

    def navigate_up(self):
        self.selected_button_index = (self.selected_button_index - 1) % len(self.get_current_buttons())

    def navigate_down(self):
        self.selected_button_index = (self.selected_button_index + 1) % len(self.get_current_buttons())

    def select_option(self):
        buttons = self.get_current_buttons()
        if 0 <= self.selected_button_index < len(buttons):
            return buttons[self.selected_button_index]
        return None 