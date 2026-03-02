def loadCrops(textures):
    return {
        "tomato": {
            "stages": [
                textures["tomatoPlant0"],
                textures["tomatoPlant1"],
                textures["tomatoPlant2"],
                textures["tomatoPlant3"],
            ],
            "growth_days_per_stage": 1,
            "max_stage": 3,
        },
        "carrot": {
            "stages": [
                textures["carrotPlant0"],
                textures["carrotPlant1"],
                textures["carrotPlant2"],
                textures["carrotPlant3"],
            ],
            "growth_days_per_stage": 2,
            "max_stage": 3,
        },
    }