import pygame
import os

ASSETS_PATH = "sprites"

def loadTextures():
    textures = {}

    textures["background"] = pygame.image.load(os.path.join(ASSETS_PATH, "backgroundconcept.png")).convert()
    textures["startScreen"] = pygame.image.load(os.path.join(ASSETS_PATH, "backgroundconcept+tittlescreen.png")).convert_alpha()
    textures["menuSprite"] = pygame.image.load(os.path.join(ASSETS_PATH, "optionsMenu.png")).convert_alpha()
    textures["tekoopTile"] = pygame.image.load(os.path.join(ASSETS_PATH, "tekoopTiles.png")).convert_alpha()
    textures["numberFont"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-font.png")).convert_alpha()

    # Calendar
    textures["calendar"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-Calendar.png")).convert_alpha()
    textures["calendarCircle"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-CalendarCircle.png")).convert_alpha()

    # Weather
    textures["weatherReport1"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-WeerBericht1.png")).convert_alpha()
    textures["weatherReport2"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-WeerBericht2.png")).convert_alpha()
    textures["weatherReport3"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-WeerBericht3.png")).convert_alpha()

    # Shop
    textures["shopShelves"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-shopplanken.png")).convert_alpha()
    textures["shedPot"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-shedPot.png")).convert_alpha()
    textures["shedDoor"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-sheddoor.png")).convert_alpha()

    # Watering
    textures["wateringcanEmpty"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-waterBucketEmpty.png")).convert_alpha()
    textures["wateringcanFull"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-waterBucketFull.png")).convert_alpha()
    textures["waterDropPlant"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-waterDruppelPlant.png")).convert_alpha()

    # Fermentation pots
    textures["fermPotSmall"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-fermpot1.png")).convert_alpha()
    textures["fermPotLarge"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-fermpot2.png")).convert_alpha()

    # Tomato
    textures["tomato"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-tomaat.png")).convert_alpha()
    textures["tomatoFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-tomaatFerment.png")).convert_alpha()
    textures["tomatoBag"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-tomatenzzak.png")).convert_alpha()
    textures["tomatoPlant0"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-TomaatPlant0.png")).convert_alpha()
    textures["tomatoPlant1"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-TomaatPlant1.png")).convert_alpha()
    textures["tomatoPlant2"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-TomaatPlant2.png")).convert_alpha()
    textures["tomatoPlant3"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-TomaatPlant3.png")).convert_alpha()

    # Carrot
    textures["carrot"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortel.png")).convert_alpha()
    textures["carrotFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-WortelFerment.png")).convert_alpha()
    textures["carrotBag"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelzzak2.png")).convert_alpha()
    textures["carrotPlant0"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelPlant0.png")).convert_alpha()
    textures["carrotPlant1"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelPlant1.png")).convert_alpha()
    textures["carrotPlant2"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelPlant2.png")).convert_alpha()
    textures["carrotPlant3"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelPlant3.png")).convert_alpha()

    # Cabbage
    textures["cabbage"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-kool.png")).convert_alpha()
    textures["cabbageFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-koolFerment.png")).convert_alpha()
    textures["cabbageBag"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-koolzak.png")).convert_alpha()
    textures["cabbagePlant1"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-colePlant1.png")).convert_alpha()
    textures["cabbagePlant2"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-colePlant2.png")).convert_alpha()
    textures["cabbagePlant3"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-colePlant3.png")).convert_alpha()

    # Garlic
    textures["garlic"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflook.png")).convert_alpha()
    textures["garlicFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookFerment.png")).convert_alpha()
    textures["garlicBag"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookzak.png")).convert_alpha()
    textures["garlicPlant1"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant1.png")).convert_alpha()
    textures["garlicPlant2"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant2.png")).convert_alpha()
    textures["garlicPlant3"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant3.png")).convert_alpha()
    textures["garlicPlant4"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant4.png")).convert_alpha()
    textures["garlicPlant5"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant5.png")).convert_alpha()

    # Chili
    textures["chili"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-Chili.png")).convert_alpha()
    textures["chiliFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliferment.png")).convert_alpha()
    textures["chiliBag"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chilizzak.png")).convert_alpha()
    textures["chiliPlant1"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliPlant1.png")).convert_alpha()
    textures["chiliPlant2"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliPlant2.png")).convert_alpha()
    textures["chiliPlant3"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliPlant3.png")).convert_alpha()
    textures["chiliPlant4"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliPlant4.png")).convert_alpha()

    # Cucumber
    textures["cucumber"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommer.png")).convert_alpha()
    textures["cucumberFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerFerment.png")).convert_alpha()
    textures["cucumberBag"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerzak2.png")).convert_alpha()
    textures["cucumberPlant1"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerPlant1.png")).convert_alpha()
    textures["cucumberPlant2"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerPlant2.png")).convert_alpha()
    textures["cucumberPlant3"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerPlant3.png")).convert_alpha()
    textures["cucumberPlant4"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerPlant4.png")).convert_alpha()

    return textures