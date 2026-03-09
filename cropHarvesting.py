CROP_VALUES = {
    "tomato": 5,
    "carrot": 10,
    "cucumber": 20,
    "chili": 20,
    "cabbage": 26,
    "garlic": 42,
}

cropPrice = {
    "tomato": 3,
    "carrot": 6,
    "cucumber": 13,
    "chili": 18,
    "cabbage": 23,
    "garlic": 28,
}

def harvest(grid, gx, gy, crops):
    """
    Right-click harvest: if the plant is fully grown, remove it from the grid
    and return the crop name so the player can hold it.
    Returns None if nothing was harvested.
    """
    if 0 <= gx < len(grid) and 0 <= gy < len(grid[0]):
        cell = grid[gx][gy]
        if cell is None:
            return None

        cropName = cell["crop"]
        cropData = crops[cropName]

        if cell["stage"] >= cropData["max_stage"]:
            grid[gx][gy] = None
            return cropName   # caller now holds this fruit

    return None