# Space Duel - Jeu 1v1 pour Raspberry Pi

Un jeu de combat spatial en vue de dessus pour deux joueurs, conçu spécifiquement pour Raspberry Pi.

## Description
Space Duel est un jeu d'arcade en 1v1 où deux joueurs s'affrontent dans une arène spatiale. Chaque joueur contrôle un vaisseau et doit éliminer son adversaire en utilisant des tirs laser tout en évitant les projectiles ennemis.

## Prérequis
- Raspberry Pi (3 ou plus récent recommandé)
- Python 3.7+
- 2 joysticks USB
- 4 boutons (2 par joueur)
- Écran compatible avec Raspberry Pi

## Installation

1. Cloner le repository :
```bash
git clone [URL_DU_REPO]
cd space-duel
```

2. Installer les dépendances :
```bash
pip3 install -r requirements.txt
```

## Configuration des contrôles
- Branchez les joysticks USB avant de lancer le jeu
- Les boutons doivent être connectés aux GPIO du Raspberry Pi :
  - Joueur 1 : GPIO 17 (Tir), GPIO 18 (Action spéciale)
  - Joueur 2 : GPIO 22 (Tir), GPIO 23 (Action spéciale)

## Lancement du jeu
```bash
python3 src/main.py
```

## Contrôles
### Joueur 1
- Joystick : Déplacement du vaisseau
- Bouton 1 : Tir laser
- Bouton 2 : Bouclier temporaire

### Joueur 2
- Joystick : Déplacement du vaisseau
- Bouton 3 : Tir laser
- Bouton 4 : Bouclier temporaire

## Règles du jeu
- Chaque joueur commence avec 100 points de vie
- Les tirs laser infligent 10 points de dégâts
- Le bouclier bloque tous les dégâts pendant 2 secondes
- Le joueur qui élimine son adversaire gagne la partie
- Une partie dure maximum 3 minutes

## Développement
Le jeu est structuré en plusieurs modules :
- `main.py` : Point d'entrée du jeu
- `game.py` : Logique principale du jeu
- `player.py` : Gestion des joueurs
- `bullet.py` : Gestion des projectiles
- `input_handler.py` : Gestion des entrées
- `constants.py` : Configuration du jeu 