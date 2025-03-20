# Space Duel

Space Duel est un jeu de combat spatial multijoueur où chaque joueur contrôle un vaisseau spatial. Le but est d'éliminer l'adversaire en utilisant des tirs et des boucliers tout en évitant les obstacles.

## Prérequis

- Python 3.x
- Pygame
- (Optionnel) RPi.GPIO pour les contrôles sur Raspberry Pi

## Installation

1. Installez les dépendances :
   ```bash
   pip install pygame
   ```
   Si vous utilisez un Raspberry Pi, installez également RPi.GPIO :
   ```bash
   sudo apt-get install python3-rpi.gpio
   ```

## Utilisation

1. Lancez le jeu :
   ```bash
   python src/main.py
   ```
2. Utilisez les commandes clavier ou joystick pour naviguer dans le menu et jouer.

## Commandes

- **Joueur 1** :
  - Déplacement : ZQSD
  - Tir : ESPACE
  - Bouclier : SHIFT
  - ou joystick
- **Joueur 2** :
  - Déplacement : Flèches directionnelles
  - Tir : ENTER
  - Bouclier : CTRL
  - ou joystick

## Fonctionnalités

- **Modes de jeu** :
  - Menu principal pour sélectionner les options de jeu.
  - Sélection de personnage et de carte.
- **Multijoueur** :
  - Deux joueurs peuvent s'affronter sur le même écran.
- **Graphismes** :
  - Graphismes 2D avec des effets de rotation et de mise à l'échelle.