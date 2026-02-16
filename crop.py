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
        }}
