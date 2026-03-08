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
        "garlic": {
            "stages" : [
                textures["garlicPlant1"],
                textures["garlicPlant2"],
                textures["garlicPlant3"],
                textures["garlicPlant4"],
                textures["garlicPlant5"],
         ],
            "growth_days_per_stage": 3,
            "max_stage": 4,
        },

        "cabbage": {
            "stages": [
                textures["cabbagePlant1"],
                textures["cabbagePlant2"],
                textures["cabbagePlant3"],
            ],
            "growth_days_per_stage": 1,
            "max_stage": 2,
        },
        "chili": {
            "stages": [
                textures["chiliPlant1"],
                textures["chiliPlant2"],
                textures["chiliPlant3"],
                textures["chiliPlant4"],
            ],
            "growth_days_per_stage": 1,
            "max_stage": 3,
        },
        "cucumber": {
            "stages": [
                textures["cucumberPlant1"],
                textures["cucumberPlant2"],
                textures["cucumberPlant3"],
                textures["cucumberPlant4"],
            ],
            "growth_days_per_stage": 2,
            "max_stage": 3,
        },
    }