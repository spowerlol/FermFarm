import pygame
import os

ASSETS_PATH = "sprites"

def load_textures():
    textures = {}

    textures["background"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "backgroundconcept.png")
    ).convert()

    textures["Calendar"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-Calendar.png")
    ).convert_alpha()

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

    textures["wortelPlant0"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-wortelPlant0.png")
    ).convert_alpha()

    textures["wortelPlant1"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-wortelPlant1.png")
    ).convert_alpha()

    textures["wortelPlant2"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-wortelPlant2.png")
    ).convert_alpha()

    textures["wortelPlant3"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-wortelPlant3.png")
    ).convert_alpha()

    textures["NumberFont"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-font.png")
    ).convert_alpha()

    textures["shopPlanken"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-shopplanken.png")
    ).convert_alpha()

    textures["fermpotKlein"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-fermpot1.png")
    ).convert_alpha()

    textures["fermpotGroot"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-fermpot2.png")
    ).convert_alpha()

    textures["wortelzZak"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-wortelzzak2.png")
    ).convert_alpha()

    textures["tomatenZak"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-tomatenzzak.png")
    ).convert_alpha()

    textures["chiliZak"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-chilizzak.png")
    ).convert_alpha()

    textures["komkommerZak"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-komkommerzak2.png")
    ).convert_alpha()
    textures["startScreen"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "backgroundconcept+tittlescreen.png")
    ).convert_alpha()

    textures["knoflookZak"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-knoflookzak.png")
    ).convert_alpha()

    textures["koolZak"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-koolzak.png")
    ).convert_alpha()

    textures["menuSprite"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "optionsMenu.png")
    ).convert_alpha()

    return textures