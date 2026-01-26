import pygame
import os

ASSETS_PATH = "sprites"

def load_textures():
    textures = {}

    textures["background"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "backgroundconcept.png")
    ).convert()

    textures["CalendarCircle"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-CalendarCircle.png")
    ).convert_alpha()

    textures["TomaatPlant1"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-TomaatPlant1.png")
    ).convert_alpha()

    return textures
