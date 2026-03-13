# =============================================================================
# texture.py
# Responsible for loading every sprite/image used in FermFarm from disk
# into memory at game startup, storing them in a single dictionary.
#
# All images live in the "sprites/" folder next to this script.
# We return one big "textures" dict so every other module can look up any
# sprite by a readable name like textures["tomato"] instead of re-loading
# files in multiple places.
# =============================================================================

import pygame
import os

# Folder that contains all sprite PNG files.
ASSETS_PATH = "sprites"


def loadTextures():
    """
    Load every game sprite from disk and return them in a dictionary.

    .convert()       - converts the image to the screen's pixel format for
                       fast blitting; use for fully opaque backgrounds.
    .convert_alpha() - same conversion but preserves the alpha (transparency)
                       channel; use for sprites that have transparent areas.

    Returns:
        dict: keys are descriptive string names, values are pygame.Surface objects.
    """
    textures = {}

    # -------------------------------------------------------------------------
    # BACKGROUNDS & UI CHROME
    # -------------------------------------------------------------------------

    # The main game world background (the farm, shop building, fields, etc.).
    textures["background"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "backgroundconcept.png")).convert()

    # The title/splash screen image shown before the game starts.
    textures["startScreen"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "backgroundconcept+tittlescreen.png")).convert_alpha()

    # The pause/options menu overlay sprite.
    textures["menuSprite"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "optionsMenu.png")).convert_alpha()
    # The info/tutorial background
    textures["menuSpriteInfo"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "optionsMenuInfo.png")).convert_alpha()

    # The "For Sale" tile overlay drawn on locked (not yet purchased) grid tiles.
    textures["tekoopTile"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "tekoopTiles.png")).convert_alpha()  # "te koop" = Dutch for "for sale"

    # The custom pixel-art number font sheet used to draw the coin balance.
    # All 10 digits (0-9) are laid out side by side in one image.
    textures["numberFont"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-font.png")).convert_alpha()

    # ---------------------------------------
    # GOLD WATER BUCKET, THE GOLD WATERBUCKET IS AN ITEM YOU CAN BUY IN THE SHOP
    # THIS ITEM WILL NEED A WATERREFILL AFTER EVERY 10 POURS INSTEAD OF AFTER EVERY POUR
    #-----------------------------------------
    textures["goldWaterBucket"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-goldwaterbucket.png")).convert_alpha()
    textures["goldWaterBucketFill"] = pygame.image.load(os.path.join(ASSETS_PATH,"Sprite-goldwaterbucketfill.png")).convert_alpha()
    textures["goldWaterBucketShop"] = pygame.image.load(os.path.join(ASSETS_PATH,"Sprite-goldwaterbucketshop.png")).convert_alpha()

    # -------------------------------------------------------------------------
    # CALENDAR
    # The calendar sprite shows which day of the season it is.
    # The circle sprite is a marker that moves across the calendar each day.
    # -------------------------------------------------------------------------
    textures["calendar"]       = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-Calendar.png")).convert_alpha()
    textures["calendarCircle"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-CalendarCircle.png")).convert_alpha()

    # -------------------------------------------------------------------------
    # WEATHER REPORT
    # Three different weather-report card sprites (one per weather type).
    # -------------------------------------------------------------------------
    textures["weatherReport1"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-WeerBericht1.png")).convert_alpha()
    textures["weatherReport2"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-WeerBericht2.png")).convert_alpha()
    textures["weatherReport3"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-WeerBericht3.png")).convert_alpha()
    textures["rainBackground1"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-regenBackground1.png")).convert_alpha()
    textures["rainBackground2"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-regenBackground2.png")).convert_alpha()
    textures["rainBackground3"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-regenBackground3.png")).convert_alpha()
    textures["rainBackground4"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-regenBackground4.png")).convert_alpha()
    textures["rainBackground5"] = pygame.image.load(
        os.path.join(ASSETS_PATH, "Sprite-regenBackground5.png")).convert_alpha()
    # -------------------------------------------------------------------------
    # SHOP & SHED FURNITURE
    # -------------------------------------------------------------------------
    textures["shopShelves"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-shopplanken.png")).convert_alpha()  # seed display shelves
    textures["shedPot"]     = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-shedPot.png")).convert_alpha()      # fermentation pot inside the shed
    textures["shedDoor"]    = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-sheddoor.png")).convert_alpha()     # the shed door graphic
    textures["shopChest"]   = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-verkoopKist.png")).convert_alpha()  # "verkoop kist" = Dutch for "sell chest"

    # -------------------------------------------------------------------------
    # WATERING CAN & WATER DROP
    # -------------------------------------------------------------------------
    textures["wateringcanEmpty"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-waterBucketEmpty.png")).convert_alpha()
    textures["wateringcanFull"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-waterBucketFull.png")).convert_alpha()
    textures["waterDropPlant"]   = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-waterDruppelPlant.png")).convert_alpha()  # small droplet shown on watered tiles

    # -------------------------------------------------------------------------
    # FERMENTATION POTS (shop items the player can buy and place in the shed)
    # -------------------------------------------------------------------------
    textures["fermPotSmall"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-fermpot1.png")).convert_alpha()
    textures["fermPotLarge"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-fermpot2.png")).convert_alpha()

    # -------------------------------------------------------------------------
    # TOMATO  (raw fruit, fermented fruit, seed bag, and 4 plant growth stages and death stage)
    # -------------------------------------------------------------------------
    textures["tomato"]        = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-tomaat.png")).convert_alpha()           # harvested raw tomato icon
    textures["tomatoFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-tomaatFerment.png")).convert_alpha()    # fermented tomato icon
    textures["tomatoBag"]     = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-tomatenzzak.png")).convert_alpha()      # seed bag on the shop shelf
    textures["tomatoPlant0"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-TomaatPlant0.png")).convert_alpha()     # growth stage 0 (just planted)
    textures["tomatoPlant1"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-TomaatPlant1.png")).convert_alpha()     # growth stage 1
    textures["tomatoPlant2"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-TomaatPlant2.png")).convert_alpha()     # growth stage 2
    textures["tomatoPlant3"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-TomaatPlant3.png")).convert_alpha()     # growth stage 3 (harvestable)
    textures["tomatoDeath"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-dodeTomaat.png")).convert_alpha()
    # -------------------------------------------------------------------------
    # CARROT
    # -------------------------------------------------------------------------
    textures["carrot"]        = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortel.png")).convert_alpha()
    textures["carrotFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-WortelFerment.png")).convert_alpha()
    textures["carrotBag"]     = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelzzak2.png")).convert_alpha()
    textures["carrotPlant0"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelPlant0.png")).convert_alpha()
    textures["carrotPlant1"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelPlant1.png")).convert_alpha()
    textures["carrotPlant2"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelPlant2.png")).convert_alpha()
    textures["carrotPlant3"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-wortelPlant3.png")).convert_alpha()
    textures["carrotDeath"]   = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-dodeWortel.png")).convert_alpha()
    # -------------------------------------------------------------------------
    # CABBAGE  "kool"
    # -------------------------------------------------------------------------
    textures["cabbage"]        = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-kool.png")).convert_alpha()
    textures["cabbageFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-koolFerment.png")).convert_alpha()
    textures["cabbageBag"]     = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-koolzak.png")).convert_alpha()
    textures["cabbagePlant1"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-colePlant1.png")).convert_alpha()
    textures["cabbagePlant2"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-colePlant2.png")).convert_alpha()
    textures["cabbagePlant3"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-colePlant3.png")).convert_alpha()
    textures["cabbageDeath"]   = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-dodeKool.png")).convert_alpha()
    # -------------------------------------------------------------------------
    # GARLIC  "knoflook"
    # -------------------------------------------------------------------------
    textures["garlic"]        = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflook.png")).convert_alpha()
    textures["garlicFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookFerment.png")).convert_alpha()
    textures["garlicBag"]     = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookzak.png")).convert_alpha()
    textures["garlicPlant1"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant1.png")).convert_alpha()  # 5 growth stages for garlic
    textures["garlicPlant2"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant2.png")).convert_alpha()
    textures["garlicPlant3"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant3.png")).convert_alpha()
    textures["garlicPlant4"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant4.png")).convert_alpha()
    textures["garlicPlant5"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-knoflookPlant5.png")).convert_alpha()
    textures["garlicDeath"]   = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-dodeKnoflook.png")).convert_alpha()
    # -------------------------------------------------------------------------
    # CHILI
    # -------------------------------------------------------------------------
    textures["chili"]        = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-Chili.png")).convert_alpha()
    textures["chiliFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliferment.png")).convert_alpha()
    textures["chiliBag"]     = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chilizzak.png")).convert_alpha()
    textures["chiliPlant1"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliPlant1.png")).convert_alpha()
    textures["chiliPlant2"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliPlant2.png")).convert_alpha()
    textures["chiliPlant3"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliPlant3.png")).convert_alpha()
    textures["chiliPlant4"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-chiliPlant4.png")).convert_alpha()
    textures["chiliDeath"]   = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-dodeChili.png")).convert_alpha()
    # -------------------------------------------------------------------------
    # CUCUMBER  ("komkommer")
    # -------------------------------------------------------------------------
    textures["cucumber"]        = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommer.png")).convert_alpha()
    textures["cucumberFerment"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerFerment.png")).convert_alpha()
    textures["cucumberBag"]     = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerzak2.png")).convert_alpha()
    textures["cucumberPlant1"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerPlant1.png")).convert_alpha()
    textures["cucumberPlant2"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerPlant2.png")).convert_alpha()
    textures["cucumberPlant3"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerPlant3.png")).convert_alpha()
    textures["cucumberPlant4"]  = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-komkommerPlant4.png")).convert_alpha()
    textures["cucumberDeath"]   = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-dodeKomkommer.png")).convert_alpha()
    # -------------------------------------------------------------------------
    # UI BUTTONS
    # -------------------------------------------------------------------------
    textures["closeCross"]      = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-closeCross.png")).convert_alpha()       # the X button to close a menu
    textures["closeCrossClick"] = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-closeCrossClick.png")).convert_alpha()  # the X button while being hovered
    textures["doneSparkle"]     = pygame.image.load(os.path.join(ASSETS_PATH, "Sprite-doneSparkle.png")).convert_alpha()      # sparkle shown when fermentation is done

    # Return the complete dictionary to whoever called this function.
    return textures