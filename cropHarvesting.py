# cropHarvesting.py
# Handles right-click harvesting of fully grown crops on the grid.
# Also stores the two price tables the rest of the game uses:
#   cropValues -> coins the player earns by selling a raw (un-fermented) crop
#   cropPrice  -> coins the player spends to buy a seed from the shop

# How much money the player gets when selling a freshly harvested crop
# directly into the shop chest, without fermenting it first.
# Fermenting always gives more money; see ferment.py for those numbers.
cropValues = {
    "tomato"  : 5,
    "carrot"  : 10,
    "cucumber": 20,
    "chili"   : 20,
    "cabbage" : 26,
    "garlic"  : 42,
}

# How many coins the player must spend to buy one seed bag from the shop shelf.
# Every crop is designed so that selling the harvest earns back more than the seed cost.
cropPrice = {
    "tomato"  : 3,
    "carrot"  : 6,
    "cucumber": 13,
    "chili"   : 18,
    "cabbage" : 23,
    "garlic"  : 28,
}


def harvest(grid, gx, gy, crops):
    # Try to harvest the plant at grid column gx, row gy.
    # Called when the player right-clicks a tile.
    # If the plant is fully grown it is removed from the grid and the crop
    # name (e.g. "tomato") is returned so the player can hold and sell it.
    # Returns None if the tile is empty or the plant is not ripe yet.

    # Check that the column and row numbers are inside the grid boundaries.
    if 0 <= gx < len(grid) and 0 <= gy < len(grid[0]):

        # Read whatever is planted in this cell (could be None if empty).
        cell = grid[gx][gy]

        # Nothing planted here, nothing to harvest.
        if cell is None:
            return None

        # The name of the crop in this cell, for example "carrot".
        cropName = cell["crop"]

        # Look up this crop's rules (growth stages, max stage, etc.).
        cropData = crops[cropName]

        # A plant is harvestable once its stage number reaches the maximum.
        # stage is updated each game day based on how many days the plant was watered.
        if cell["stage"] >= cropData["max_stage"]:

            # Remove the plant so the tile becomes empty again.
            grid[gx][gy] = None

            # Return the name so the main loop can give it to the player as a held item.
            return cropName

    # Click was out of bounds, tile was empty, or plant is not ripe yet.
    return None