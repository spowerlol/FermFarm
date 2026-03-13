# death_proces.py
# Plants cannot stay in the field forever.
# After a plant becomes ripe it has a limited number of days before it dies.
# A dead plant cannot be harvested normally; the player right-clicks it to
# clear the tile and receive a small refund of the seed price.

from cropHarvesting import cropPrice, harvest

# How many in-game days a ripe plant may sit before it dies.
ripeDays = 2

# How many consecutive un-watered days a plant can survive before it dies.
droughtDays = 2

# What fraction of the seed price the player gets back when clearing a dead plant.
# 0.5 means the player receives half the seed price as a refund.
deadPlantPenalty = 0.5


def plantState(cell):
    # Make sure a planted cell has all the fields the game expects.
    # This is called before reading or writing any cell to avoid KeyError crashes.
    # If the cell is None (empty tile) there is nothing to do.
    if cell is None:
        return None

    # setdefault() adds a key with a default value only if the key is missing.
    # This is safe to call on cells that already have these keys; it does nothing.
    cell.setdefault("watered", False)       # whether the plant was watered today
    cell.setdefault("watered_days", 0)      # total days the plant has been watered
    cell.setdefault("day_ripe", None)       # which game day the plant became ripe
    cell.setdefault("dead", False)          # True if the plant has died
    cell.setdefault("dry_days", 0)          # consecutive days without water
    return cell


def getDeadPlantRefund(cropName):
    # Calculate how many coins the player receives when clearing a dead plant.
    # Rule: refund = seed price * deadPlantPenalty, rounded down, minimum 0.
    return max(0, int(cropPrice[cropName] * deadPlantPenalty))


def harvestDead(grid, gx, gy, crops):
    # Handle a right-click harvest event, checking for dead plants first.
    # If the plant is dead: remove it and return a refund result.
    # If the plant is ripe: run the normal harvest and return a fruit result.
    # Returns None if the tile is empty or the plant is not ready for either.

    # Make sure the column and row are inside the grid boundaries.
    if not (0 <= gx < len(grid) and 0 <= gy < len(grid[0])):
        return None

    cell = grid[gx][gy]

    # Nothing planted here.
    if cell is None:
        return None

    # Ensure the cell has all required fields before reading them.
    plantState(cell)

    if cell.get("dead", False):
        # Plant is dead: remove it from the grid and signal a coin refund.
        cropName = cell["crop"]
        grid[gx][gy] = None
        return {"type": "dead_refund", "crop": cropName}

    # Plant is not dead: attempt the normal harvest (checks if it is ripe).
    harvested = harvest(grid, gx, gy, crops)
    if harvested is not None:
        # harvest() returned the crop name, so the plant was ripe and is now removed.
        return {"type": "fruit", "crop": harvested}

    # Plant was neither dead nor ripe.
    return None