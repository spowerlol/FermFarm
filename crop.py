# =============================================================================
# crop.py
# Defines every crop type the player can grow in FermFarm.
# Each crop entry stores its growth sprites, how many in-game days it takes
# to advance one growth stage, and how many stages it has in total.
# =============================================================================

def loadCrops(textures):
    """
    Build and return the master crop dictionary.

    Parameters:
        textures (dict): the texture dictionary returned by loadTextures().
                         We look up sprite images from here so each crop
                         knows exactly which image to display per stage.

    Returns:
        dict: keys are crop name strings (e.g. "tomato"), values are dicts
              describing that crop's sprites and growth rules.
    """

    # -------------------------------------------------------------------------
    # HOW THE GROWTH SYSTEM WORKS
    #
    # Every in-game day the grid is ticked. If a plant was watered that day its
    # "watered_days" counter goes up by 1. The current visual stage is then:
    #
    #   stage = watered_days // growth_days_per_stage
    #
    # capped at max_stage. So a crop with growth_days_per_stage=2 needs to be
    # watered on 2 separate days before it advances one sprite stage.
    #
    # "stages" is the list of sprites in order from seedling to fully grown.
    # Index 0 is the freshly planted seedling; the last index is harvest-ready.
    # -------------------------------------------------------------------------

    return {

        # -----------------------------------------------------------------
        # TOMATO
        # Fast grower: advances one sprite stage every 1 watered day.
        # Has 4 sprites (indices 0-3), fully grown at stage 3.
        # -----------------------------------------------------------------
        "tomato": {
            "stages": [
                textures["tomatoPlant0"],   # Stage 0: tiny seedling
                textures["tomatoPlant1"],   # Stage 1: small plant
                textures["tomatoPlant2"],   # Stage 2: flowering
                textures["tomatoPlant3"],   # Stage 3: ripe tomatoes (harvestable)
            ],
            "growth_days_per_stage": 1,   # needs 1 watered day per stage
            "max_stage": 3,               # harvest is available at stage 3
        },

        # -----------------------------------------------------------------
        # CARROT
        # Moderate grower: needs 2 watered days to advance each stage.
        # Has 4 sprites (indices 0-3), fully grown at stage 3.
        # -----------------------------------------------------------------
        "carrot": {
            "stages": [
                textures["carrotPlant0"],   # Stage 0: sprout just poking up
                textures["carrotPlant1"],   # Stage 1: leafy tops visible
                textures["carrotPlant2"],   # Stage 2: carrot bulge showing
                textures["carrotPlant3"],   # Stage 3: fully grown (harvestable)
            ],
            "growth_days_per_stage": 2,   # needs 2 watered days per stage
            "max_stage": 3,
        },

        # -----------------------------------------------------------------
        # GARLIC
        # Slow grower with 5 sprites: needs 3 watered days per stage.
        # Has 5 sprites (indices 0-4), fully grown at stage 4.
        # -----------------------------------------------------------------
        "garlic": {
            "stages": [
                textures["garlicPlant1"],   # Stage 0: first shoot
                textures["garlicPlant2"],   # Stage 1: small leaves
                textures["garlicPlant3"],   # Stage 2: growing well
                textures["garlicPlant4"],   # Stage 3: almost ready
                textures["garlicPlant5"],   # Stage 4: fully grown (harvestable)
            ],
            "growth_days_per_stage": 3,   # needs 3 watered days per stage
            "max_stage": 4,
        },

        # -----------------------------------------------------------------
        # CABBAGE
        # Fast grower with only 3 sprites: advances every 1 watered day.
        # Has 3 sprites (indices 0-2), fully grown at stage 2.
        # -----------------------------------------------------------------
        "cabbage": {
            "stages": [
                textures["cabbagePlant1"],  # Stage 0: tiny cabbage sprout
                textures["cabbagePlant2"],  # Stage 1: leafy head forming
                textures["cabbagePlant3"],  # Stage 2: full cabbage (harvestable)
            ],
            "growth_days_per_stage": 1,   # needs 1 watered day per stage
            "max_stage": 2,
        },

        # -----------------------------------------------------------------
        # CHILI
        # Fast grower with 4 sprites: advances every 1 watered day.
        # Has 4 sprites (indices 0-3), fully grown at stage 3.
        # -----------------------------------------------------------------
        "chili": {
            "stages": [
                textures["chiliPlant1"],    # Stage 0: seedling
                textures["chiliPlant2"],    # Stage 1: leafy plant
                textures["chiliPlant3"],    # Stage 2: small peppers forming
                textures["chiliPlant4"],    # Stage 3: ripe chilis (harvestable)
            ],
            "growth_days_per_stage": 1,   # needs 1 watered day per stage
            "max_stage": 3,
        },

        # -----------------------------------------------------------------
        # CUCUMBER
        # Moderate grower: needs 2 watered days per stage.
        # Has 4 sprites (indices 0-3), fully grown at stage 3.
        # -----------------------------------------------------------------
        "cucumber": {
            "stages": [
                textures["cucumberPlant1"], # Stage 0: seedling
                textures["cucumberPlant2"], # Stage 1: vine starting
                textures["cucumberPlant3"], # Stage 2: cucumbers forming
                textures["cucumberPlant4"], # Stage 3: ripe cucumbers (harvestable)
            ],
            "growth_days_per_stage": 2,   # needs 2 watered days per stage
            "max_stage": 3,
        },
    }