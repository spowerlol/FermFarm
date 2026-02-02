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

    textures["TomaatPlant0"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-TomaatPlant0.png")
    ).convert_alpha()

    textures["TomaatPlant1"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-TomaatPlant1.png")
    ).convert_alpha()

    textures["TomaatPlant2"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-TomaatPlant2.png")
    ).convert_alpha()

    textures["TomaatPlant3"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-TomaatPlant3.png")
    ).convert_alpha()

    textures["NumberFont"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-font.png")
    ).convert_alpha()

    textures["shopplanken"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-shopplanken.png")
    ).convert_alpha()

    textures["fermpotklein"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-fermpot1.png")
    ).convert_alpha()

    textures["fermpotgroot"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-fermpot2.png")
    ).convert_alpha()

    return textures
