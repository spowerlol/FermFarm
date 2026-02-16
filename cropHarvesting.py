CROP_VALUES = {
    "tomato": 5,
    "carrot": 10,
    "cucumber": 15,
    "chili": 20,
    "cabbage": 25,
    "garlic": 30,

    # Example: "carrot": 3,
}
Crop_Price = {
    "tomato": 3,
    "carrot": 6,
    "cucumber": 13,
    "chili": 18,
    "cabbage": 23,
    "garlic": 28,
}

inventory = {
    "tomato": 0,
    "carrot": 0,
    "cucumber": 0,
    "chili": 0,
    "cabbage": 0,
    "garlic": 0,
}




def harvest(grid, gx, gy, crops):
    """
    Attempt to harvest the plant at grid[gx][gy].
    Returns the money earned (0 if nothing harvested)
    """
    if 0 <= gx < len(grid) and 0 <= gy < len(grid[0]):
        cell = grid[gx][gy]
        if cell is None:
            return None  # nothing to harvest

        crop_name = cell["crop"]
        crop_data = crops[crop_name]

        if cell["stage"] >= crop_data["max_stage"]:
            # fully grown, harvest it
            grid[gx][gy] = None  # remove plant
            return crop_name

    return None
