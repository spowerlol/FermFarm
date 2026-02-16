def load_crops(textures):
    return {
        "tomato": {
            "stages": [
                textures["TomaatPlant0"],
                textures["TomaatPlant1"],
                textures["TomaatPlant2"],
                textures["TomaatPlant3"],
            ],
            "growth_days_per_stage": 1,
            "max_stage": 3,
        },

        "carrot": {
            "stages": [
                textures["wortelPlant0"],
                textures["wortelPlant1"],
                textures["wortelPlant2"],
                textures["wortelPlant3"],
            ],
            "growth_days_per_stage": 2,
            "max_stage": 3,
        },

        # Example future crop
        # "carrot": {
        #     "stages": [
        #         textures["Carrot0"],
        #         textures["Carrot1"],
        #         textures["Carrot2"],
        #     ],
        #     "growth_days_per_stage": 2,
        #     "max_stage": 2,
        # },
    }
