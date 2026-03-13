#============================================
# A PLANT MAY SIT IN THE FIELD FOR A LIMITED AMOUNT OF TIME IN GAME
# AFTER THE INGAME TIME DE PLANT DIES AND IT WONT BE HARVESTED NORMAL
#=============================================
from cropHarvesting import cropPrice, harvest

ripeDays = 2  # number ingame days a plant may remain ripe before death
deadPlantPenalty = 0.5

def plantState(cell):
    "Ensure that a planted cell contains in fields"
    # if the tile = empty the is nothing to change
    if cell is None:
        return None


    cell.setdefault("watered", False)   #ensures cell has a watered boolean
    cell.setdefault("watered_days", 0) #ensures the cell has watereddays counter
    cell.setdefault("day_ripe", None)   # ensures cell knows on wich day it became ripe
    cell.setdefault("dead", False) # ensures has a dead/alive boolean
    return cell

def getDeadPlantRefund(cropName):
    "return the amount of money tge player recieves for clearing plant"
    "rule : refund = seedprice - 2 ----> it never becomes zero"
    "returns: int: refund amount of dead plant"
    return max(0,(int( cropPrice[cropName] * deadPlantPenalty))) # look up seedprice and * penalty + makes sure money >= 0



def harvestDead(grid, gx, gy, crops):
    "handle a right-click harvest without changing the normal harvest right-click"
    "dead plant: - remove the plant from grid and return to result that gives money back"

    if not (0 <= gx < len(grid) and 0 <= gy < len(grid[0])):    # make sure click was in grid
        return None

    cell = grid[gx][gy]     # read click
    if cell is None:        # if tile = empty nothing to do
        return None
    plantState(cell)        # make sure plant state has all required fields

    if cell.get("dead", False):     #if plant = dead --> remove and refund
        cropName = cell["crop"] #store cropname before remove
        grid[gx][gy] = None   # remove plant from grid so tile = empty again
        return{"type": "dead_refund", "crop": cropName} # return result telling script to refund money and look wich croppricerefund

    harvested = harvest(grid, gx,gy,crops) # if plant != dead try normal harvest code
    if harvested is not None: # if harvest() returned cropname, return as normal crop
        return{"type": "fruit", "crop": harvested}

    return None # if not dead removal or harvets, return nothing



