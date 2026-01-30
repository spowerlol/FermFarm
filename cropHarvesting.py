CROP_VALUES = {
    "tomato": 5,
    # Example: "carrot": 3,
}

def harvest(grid, gx, gy, crops):
    """
    Attempt to harvest the plant at grid[gx][gy].
    Returns the money earned (0 if nothing harvested)
    """
    if 0 <= gx < len(grid) and 0 <= gy < len(grid[0]):
        cell = grid[gx][gy]
        if cell is None:
            return 0  # nothing to harvest

        crop_data = crops[cell["crop"]]
        if cell["stage"] >= crop_data["max_stage"]:
            # fully grown, harvest it
            crop_name = cell["crop"]
            value = CROP_VALUES.get(crop_name, 0)
            grid[gx][gy] = None  # remove plant
            return value

    return 0
