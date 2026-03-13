# crop.py
# Defines every crop type the player can grow in FermFarm.
# Each crop entry stores its growth sprites, days needed per growth stage,
# and the total number of stages.


def loadCrops(textures):
    # Build and return the master crop dictionary.
    # textures - the dictionary returned by loadTextures()
    # Returns a dict where each key is a crop name (e.g. "tomato") and
    # the value is a dict describing that crop's sprites and growth rules.

    # How the growth system works:
    # Every in-game day, if a plant was watered that day its "watered_days"
    # counter goes up by 1. The current visual stage is calculated as:
    #
    #   stage = watered_days // growthDaysPerStage
    #
    # capped at maxStage. So with growthDaysPerStage = 2 the plant needs to be
    # watered on 2 separate days before it advances one sprite stage.
    #
    # "stages" is a list of sprites ordered from seedling to fully grown.
    # Index 0 is freshly planted; the last index is harvest-ready.

    return {

        # Tomato: advances one stage every 1 watered day, 4 stages total.
        "tomato": {
            "stages": [
                textures["tomatoPlant0"],   # tiny seedling
                textures["tomatoPlant1"],   # small plant
                textures["tomatoPlant2"],   # flowering
                textures["tomatoPlant3"],   # ripe tomatoes, can be harvested
            ],
            "death_sprite"        : textures["tomatoDeath"],
            "growth_days_per_stage": 1,
            "max_stage"           : 3,
        },

        # Carrot: needs 2 watered days to advance each stage, 4 stages total.
        "carrot": {
            "stages": [
                textures["carrotPlant0"],   # sprout just poking up
                textures["carrotPlant1"],   # leafy tops visible
                textures["carrotPlant2"],   # carrot bulge showing
                textures["carrotPlant3"],   # fully grown, can be harvested
            ],
            "death_sprite"        : textures["carrotDeath"],
            "growth_days_per_stage": 2,
            "max_stage"           : 3,
        },

        # Garlic: slow grower, needs 3 watered days per stage, 5 stages total.
        "garlic": {
            "stages": [
                textures["garlicPlant1"],   # first shoot
                textures["garlicPlant2"],   # small leaves
                textures["garlicPlant3"],   # growing well
                textures["garlicPlant4"],   # almost ready
                textures["garlicPlant5"],   # fully grown, can be harvested
            ],
            "death_sprite"        : textures["garlicDeath"],
            "growth_days_per_stage": 3,
            "max_stage"           : 4,
        },

        # Cabbage: fast grower, advances every 1 watered day, 3 stages total.
        "cabbage": {
            "stages": [
                textures["cabbagePlant1"],  # tiny cabbage sprout
                textures["cabbagePlant2"],  # leafy head forming
                textures["cabbagePlant3"],  # full cabbage, can be harvested
            ],
            "death_sprite"        : textures["cabbageDeath"],
            "growth_days_per_stage": 1,
            "max_stage"           : 2,
        },

        # Chili: fast grower, advances every 1 watered day, 4 stages total.
        "chili": {
            "stages": [
                textures["chiliPlant1"],    # seedling
                textures["chiliPlant2"],    # leafy plant
                textures["chiliPlant3"],    # small peppers forming
                textures["chiliPlant4"],    # ripe chilis, can be harvested
            ],
            "death_sprite"        : textures["chiliDeath"],
            "growth_days_per_stage": 1,
            "max_stage"           : 3,
        },

        # Cucumber: needs 2 watered days per stage, 4 stages total.
        "cucumber": {
            "stages": [
                textures["cucumberPlant1"], # seedling
                textures["cucumberPlant2"], # vine starting
                textures["cucumberPlant3"], # cucumbers forming
                textures["cucumberPlant4"], # ripe cucumbers, can be harvested
            ],
            "death_sprite"        : textures["cucumberDeath"],
            "growth_days_per_stage": 2,
            "max_stage"           : 3,
        },
    }