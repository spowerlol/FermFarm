# texture.py
# Loads every sprite image used in FermFarm from disk into memory at startup.
# All images live in the "sprites/" folder next to this script.
# Returns one dictionary so every other module can look up sprites by name,
# for example textures["tomato"] instead of reloading files in multiple places.

import pygame
import os

# Folder that contains all sprite PNG files.
assetsPath = "sprites"


def loadTextures():
    # Load every game sprite from disk and return them in a dictionary.
    #
    # .convert()       converts the image to the screen's pixel format for
    #                  fast drawing. Use for fully opaque images.
    # .convert_alpha() same conversion but keeps the transparency channel.
    #                  Use for sprites that have see-through areas.

    textures = {}

    # Backgrounds and UI panels
    textures["background"]    = pygame.image.load(os.path.join(assetsPath, "backgroundconcept.png")).convert()
    textures["startScreen"]   = pygame.image.load(os.path.join(assetsPath, "backgroundconcept+tittlescreen.png")).convert_alpha()
    textures["menuSprite"]    = pygame.image.load(os.path.join(assetsPath, "optionsMenu.png")).convert_alpha()
    textures["menuSpriteInfo"]= pygame.image.load(os.path.join(assetsPath, "optionsMenuInfo.png")).convert_alpha()
    textures["tekoopTile"]    = pygame.image.load(os.path.join(assetsPath, "tekoopTiles.png")).convert_alpha()
    textures["numberFont"]    = pygame.image.load(os.path.join(assetsPath, "Sprite-font.png")).convert_alpha()

    # Gold water bucket (three versions: empty, full, and shop display)
    textures["goldWaterBucket"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-goldwaterbucket.png")).convert_alpha()
    textures["goldWaterBucketFill"] = pygame.image.load(os.path.join(assetsPath, "Sprite-goldwaterbucketfill.png")).convert_alpha()
    textures["goldWaterBucketShop"] = pygame.image.load(os.path.join(assetsPath, "Sprite-goldwaterbucketshop.png")).convert_alpha()

    # Calendar sprites
    textures["calendar"]       = pygame.image.load(os.path.join(assetsPath, "Sprite-Calendar.png")).convert_alpha()
    textures["calendarCircle"] = pygame.image.load(os.path.join(assetsPath, "Sprite-CalendarCircle.png")).convert_alpha()

    # Weather report cards shown on the TV
    textures["weatherReport1"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-WeerBericht1.png")).convert_alpha()
    textures["weatherReport2"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-WeerBericht2.png")).convert_alpha()
    textures["weatherReport3"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-WeerBericht3.png")).convert_alpha()
    textures["rainBackground1"] = pygame.image.load(os.path.join(assetsPath, "Sprite-regenBackground1.png")).convert_alpha()
    textures["rainBackground2"] = pygame.image.load(os.path.join(assetsPath, "Sprite-regenBackground2.png")).convert_alpha()
    textures["rainBackground3"] = pygame.image.load(os.path.join(assetsPath, "Sprite-regenBackground3.png")).convert_alpha()
    textures["rainBackground4"] = pygame.image.load(os.path.join(assetsPath, "Sprite-regenBackground4.png")).convert_alpha()
    textures["rainBackground5"] = pygame.image.load(os.path.join(assetsPath, "Sprite-regenBackground5.png")).convert_alpha()

    # Shop shelves, shed furniture, and selling chest
    textures["shopShelves"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-shopplanken.png")).convert_alpha()
    textures["shedPot"]      = pygame.image.load(os.path.join(assetsPath, "Sprite-shedPot.png")).convert_alpha()
    textures["shedDoor"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-sheddoor.png")).convert_alpha()
    textures["shopChest"]    = pygame.image.load(os.path.join(assetsPath, "Sprite-verkoopKist.png")).convert_alpha()
    textures["kichiFerment"] = pygame.image.load(os.path.join(assetsPath, "Sprite-kimchiFerment.png")).convert_alpha()

    # Watering can (empty and full versions) and the water-drop overlay
    textures["wateringcanEmpty"] = pygame.image.load(os.path.join(assetsPath, "Sprite-waterBucketEmpty.png")).convert_alpha()
    textures["wateringcanFull"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-waterBucketFull.png")).convert_alpha()
    textures["waterDropPlant"]   = pygame.image.load(os.path.join(assetsPath, "Sprite-waterDruppelPlant.png")).convert_alpha()

    # Fermentation pots (small and large sizes)
    textures["fermPotSmall"] = pygame.image.load(os.path.join(assetsPath, "Sprite-fermpot1.png")).convert_alpha()
    textures["fermPotLarge"] = pygame.image.load(os.path.join(assetsPath, "Sprite-fermpot2.png")).convert_alpha()

    # Gnome donation system sprites
    # Big gnome normal version, shown while donations are below the maximum.
    textures["gnomeBig"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-kabouter1.png")).convert_alpha()
    # Big gnome gold version, shown once all 21 donations are complete.
    textures["gnomeBigGold"] = pygame.image.load(os.path.join(assetsPath, "Sprite-goudenKabouter.png")).convert_alpha()
    # Five mini gnomes that appear one by one as donation count rises.
    textures["gnomeMinis"] = [
        pygame.image.load(os.path.join(assetsPath, "Sprite-kabouterMini1.png")).convert_alpha(),
        pygame.image.load(os.path.join(assetsPath, "Sprite-kabouterMini2.png")).convert_alpha(),
        pygame.image.load(os.path.join(assetsPath, "Sprite-kabouterMini3.png")).convert_alpha(),
        pygame.image.load(os.path.join(assetsPath, "Sprite-kabouterMini4.png")).convert_alpha(),
        pygame.image.load(os.path.join(assetsPath, "Sprite-kabouterMini5.png")).convert_alpha(),
    ]

    # Tomato sprites (crop item, fermented version, seed bag, plant stages, dead)
    textures["tomato"]        = pygame.image.load(os.path.join(assetsPath, "Sprite-tomaat.png")).convert_alpha()
    textures["tomatoFerment"] = pygame.image.load(os.path.join(assetsPath, "Sprite-tomaatFerment.png")).convert_alpha()
    textures["tomatoBag"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-tomatenzzak.png")).convert_alpha()
    textures["tomatoPlant0"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-TomaatPlant0.png")).convert_alpha()
    textures["tomatoPlant1"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-TomaatPlant1.png")).convert_alpha()
    textures["tomatoPlant2"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-TomaatPlant2.png")).convert_alpha()
    textures["tomatoPlant3"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-TomaatPlant3.png")).convert_alpha()
    textures["tomatoDeath"]   = pygame.image.load(os.path.join(assetsPath, "Sprite-dodeTomaat.png")).convert_alpha()

    # Carrot sprites
    textures["carrot"]        = pygame.image.load(os.path.join(assetsPath, "Sprite-wortel.png")).convert_alpha()
    textures["carrotFerment"] = pygame.image.load(os.path.join(assetsPath, "Sprite-WortelFerment.png")).convert_alpha()
    textures["carrotBag"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-wortelzzak2.png")).convert_alpha()
    textures["carrotPlant0"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-wortelPlant0.png")).convert_alpha()
    textures["carrotPlant1"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-wortelPlant1.png")).convert_alpha()
    textures["carrotPlant2"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-wortelPlant2.png")).convert_alpha()
    textures["carrotPlant3"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-wortelPlant3.png")).convert_alpha()
    textures["carrotDeath"]   = pygame.image.load(os.path.join(assetsPath, "Sprite-dodeWortel.png")).convert_alpha()

    # Cabbage sprites
    textures["cabbage"]        = pygame.image.load(os.path.join(assetsPath, "Sprite-kool.png")).convert_alpha()
    textures["cabbageFerment"] = pygame.image.load(os.path.join(assetsPath, "Sprite-koolFerment.png")).convert_alpha()
    textures["cabbageBag"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-koolzak.png")).convert_alpha()
    textures["cabbagePlant1"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-colePlant1.png")).convert_alpha()
    textures["cabbagePlant2"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-colePlant2.png")).convert_alpha()
    textures["cabbagePlant3"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-colePlant3.png")).convert_alpha()
    textures["cabbageDeath"]   = pygame.image.load(os.path.join(assetsPath, "Sprite-dodeKool.png")).convert_alpha()

    # Garlic sprites
    textures["garlic"]        = pygame.image.load(os.path.join(assetsPath, "Sprite-knoflook.png")).convert_alpha()
    textures["garlicFerment"] = pygame.image.load(os.path.join(assetsPath, "Sprite-knoflookFerment.png")).convert_alpha()
    textures["garlicBag"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-knoflookzak.png")).convert_alpha()
    textures["garlicPlant1"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-knoflookPlant1.png")).convert_alpha()
    textures["garlicPlant2"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-knoflookPlant2.png")).convert_alpha()
    textures["garlicPlant3"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-knoflookPlant3.png")).convert_alpha()
    textures["garlicPlant4"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-knoflookPlant4.png")).convert_alpha()
    textures["garlicPlant5"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-knoflookPlant5.png")).convert_alpha()
    textures["garlicDeath"]   = pygame.image.load(os.path.join(assetsPath, "Sprite-dodeKnoflook.png")).convert_alpha()

    # Chili sprites
    textures["chili"]        = pygame.image.load(os.path.join(assetsPath, "Sprite-Chili.png")).convert_alpha()
    textures["chiliFerment"] = pygame.image.load(os.path.join(assetsPath, "Sprite-chiliferment.png")).convert_alpha()
    textures["chiliBag"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-chilizzak.png")).convert_alpha()
    textures["chiliPlant1"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-chiliPlant1.png")).convert_alpha()
    textures["chiliPlant2"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-chiliPlant2.png")).convert_alpha()
    textures["chiliPlant3"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-chiliPlant3.png")).convert_alpha()
    textures["chiliPlant4"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-chiliPlant4.png")).convert_alpha()
    textures["chiliDeath"]   = pygame.image.load(os.path.join(assetsPath, "Sprite-dodeChili.png")).convert_alpha()

    # Cucumber sprites
    textures["cucumber"]        = pygame.image.load(os.path.join(assetsPath, "Sprite-komkommer.png")).convert_alpha()
    textures["cucumberFerment"] = pygame.image.load(os.path.join(assetsPath, "Sprite-komkommerFerment.png")).convert_alpha()
    textures["cucumberBag"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-komkommerzak2.png")).convert_alpha()
    textures["cucumberPlant1"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-komkommerPlant1.png")).convert_alpha()
    textures["cucumberPlant2"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-komkommerPlant2.png")).convert_alpha()
    textures["cucumberPlant3"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-komkommerPlant3.png")).convert_alpha()
    textures["cucumberPlant4"]  = pygame.image.load(os.path.join(assetsPath, "Sprite-komkommerPlant4.png")).convert_alpha()
    textures["cucumberDeath"]   = pygame.image.load(os.path.join(assetsPath, "Sprite-dodeKomkommer.png")).convert_alpha()

    # UI buttons
    textures["closeCross"]      = pygame.image.load(os.path.join(assetsPath, "Sprite-closeCross.png")).convert_alpha()
    textures["closeCrossClick"] = pygame.image.load(os.path.join(assetsPath, "Sprite-closeCrossClick.png")).convert_alpha()
    textures["doneSparkle"]     = pygame.image.load(os.path.join(assetsPath, "Sprite-doneSparkle.png")).convert_alpha()

    return textures