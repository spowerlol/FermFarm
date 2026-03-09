# =============================================================================
# cropHarvesting.py
# Handles right-click harvesting of fully grown crops on the grid.
#
# Also stores two important price tables used throughout the game:
#   CROP_VALUES -> how many coins the player earns by selling a raw crop
#   cropPrice   -> how many coins the player spends to buy a seed from the shop
# =============================================================================

# -----------------------------------------------------------------------------
# CROP SELL VALUES (raw, un-fermented)
# These are the coin amounts the player receives when they sell a freshly
# harvested crop directly into the shop chest WITHOUT fermenting it first.
# Fermenting always gives a higher value — see ferment.py for those numbers.
# -----------------------------------------------------------------------------
CROP_VALUES = {
    "tomato"  : 5,    # Cheapest to sell raw; best used fermented
    "carrot"  : 10,
    "cucumber": 20,
    "chili"   : 20,
    "cabbage" : 26,
    "garlic"  : 42,   # Most valuable raw crop
}

# -----------------------------------------------------------------------------
# SEED PURCHASE PRICES
# How many coins the player must spend to buy one seed bag from the shop shelf.
# Prices are designed so that buying and growing is always profitable —
# you always sell for more than you spent on the seed.
# -----------------------------------------------------------------------------
cropPrice = {
    "tomato"  : 3,    # Cheapest seed; good for beginners with little money
    "carrot"  : 6,
    "cucumber": 13,
    "chili"   : 18,
    "cabbage" : 23,
    "garlic"  : 28,   # Most expensive seed but highest raw and fermented value
}


def harvest(grid, gx, gy, crops):
    """
    Attempt to harvest the plant at grid position (gx, gy).

    This is called when the player right-clicks on a grid tile. If the plant
    at that position has reached its maximum growth stage, it is removed from
    the grid and the crop name is returned so the player can "hold" the fruit
    (displayed as a cursor icon until they sell or ferment it).

    Parameters:
        grid  (list[list])  : the 2D game grid; each cell is None (empty) or
                              a dict describing the planted crop.
        gx    (int)         : column index of the clicked tile (0 = leftmost).
        gy    (int)         : row index of the clicked tile (0 = top).
        crops (dict)        : the crop definition dictionary from loadCrops(),
                              used to look up each crop's max_stage.

    Returns:
        str | None: the crop name (e.g. "tomato") if a ripe crop was harvested,
                    or None if the tile was empty or the plant is not yet ripe.
    """

    # Make sure the clicked position is actually within the grid boundaries.
    # gx must be a valid column index and gy must be a valid row index.
    if 0 <= gx < len(grid) and 0 <= gy < len(grid[0]):

        # Look up what is planted in this cell.
        cell = grid[gx][gy]

        # If the cell is empty (None) there is nothing to harvest.
        if cell is None:
            return None

        # Get the name of the crop growing here, e.g. "carrot".
        cropName = cell["crop"]

        # Look up the crop's definition so we know its max growth stage.
        cropData = crops[cropName]

        # Check whether the plant has reached its maximum stage (fully ripe).
        # cell["stage"] is updated each day tick based on how many days it
        # was watered; it caps at cropData["max_stage"].
        if cell["stage"] >= cropData["max_stage"]:

            # Remove the plant from the grid — the tile is now empty again.
            grid[gx][gy] = None

            # Return the crop name so the caller knows what was harvested.
            # The main game loop will set heldFruit = {"crop": cropName, ...}
            return cropName

    # Either the indices were out of bounds, the cell was empty,
    # or the plant wasn't ripe yet — nothing was harvested.
    return None