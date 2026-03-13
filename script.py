# script.py  —  FermFarm main entry point
#
# This is the heart of the game. It:
#   1. Initialises pygame and the display window.
#   2. Runs the title screen.
#   3. Loads all assets (textures, crops, fonts, save data).
#   4. Defines all game-state variables (money, grid, calendar, etc.).
#   5. Runs the main game loop which processes input, advances time,
#      and draws everything to the screen every frame.

import pygame
import sys
from texture        import loadTextures
from crop           import loadCrops
from money_ui       import initMoneyUi, drawMoney
from cropHarvesting import cropValues, cropPrice
from ferment        import fermentData
from startScreen    import runStartScreen
import os
import json
from datetime       import datetime
import random
from death_proces   import plantState, getDeadPlantRefund, harvestDead, ripeDays

pygame.init()
pygame.mixer.init()

# The game renders everything onto a small virtual canvas (1920 x 1080) and
# then scales it up to fill the actual screen. All positions in this file are
# in virtual-canvas pixels, not real screen pixels.
virtualWidth  = 1920
virtualHeight = 1080
fps           = 60

# Window size when running in windowed (non-fullscreen) mode.
windowWidth  = 960
windowHeight = 540

# Used by the menu overlay to know how large to draw itself.
menuRefW = virtualWidth
menuRefH = virtualHeight

# ============================================================
# DISPLAY SETUP
# ============================================================
fullscreen = True
info   = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("FermFarm")

clock = pygame.time.Clock()

# Show the title screen and wait for the player to dismiss it.
runStartScreen(screen, fullscreen)

# ============================================================
# MUSIC SETTINGS
# ============================================================
musicNormalVol = 0.5   # volume during normal gameplay
musicDimVol    = 0.2   # quieter volume while a menu is open
musicEnabled   = True  # the player can toggle music on/off in the menu

# ============================================================
# ASSET LOADING
# ============================================================
textures = loadTextures()
initMoneyUi(textures)
crops    = loadCrops(textures)

tekoopTileImg = textures["tekoopTile"]

# ============================================================
# OFF-SCREEN SURFACES
# pygame.SRCALPHA creates a surface that supports per-pixel transparency.
# These surfaces are used to draw the pause/info overlays with a dark tint.
# ============================================================
menuSurface = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)
infoSurface = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)

# ============================================================
# FONTS
# ============================================================
fontPath = "sprites/babosorry.ttf"
if not os.path.exists(fontPath):
    fontPath = None   # fall back to pygame's default font if the file is missing

saveNameFont  = pygame.font.Font(fontPath, 60)
saveDateFont  = pygame.font.Font(fontPath, 36)
buttonFont    = pygame.font.Font(fontPath, 96)
infoTextFont  = pygame.font.Font(fontPath, 44)
infoTitleFont = pygame.font.Font(fontPath, 72)

# ============================================================
# SPRITE DRAW POSITIONS
# Each variable below is the top-left pixel on the virtual canvas where
# the matching sprite is drawn every frame.
# ============================================================

shedDoorImg = textures["shedDoor"]
shedDoorX   = 512
shedDoorY   = 264

shopShelvesImg = textures["shopShelves"]
shopShelvesX   = 1480
shopShelvesY   = 400

shopChestImg = textures["shopChest"]
shopChestX   = 1800
shopChestY   = 448

fermPotLargeImg = textures["fermPotLarge"]
fermPotLargeX   = 1840
fermPotLargeY   = 336

carrotBagImg   = textures["carrotBag"]
carrotBagX     = 1488
carrotBagY     = 432

tomatoBagImg   = textures["tomatoBag"]
tomatoBagX     = 1584
tomatoBagY     = 432

chiliBagImg    = textures["chiliBag"]
chiliBagX      = 1488
chiliBagY      = 536

cucumberBagImg = textures["cucumberBag"]
cucumberBagX   = 1680
cucumberBagY   = 432

cabbageBagImg  = textures["cabbageBag"]
cabbageBagX    = 1576
cabbageBagY    = 536

garlicBagImg   = textures["garlicBag"]
garlicBagX     = 1672
garlicBagY     = 536

menuSprite         = textures["menuSprite"]
menuSpriteInfo     = textures["menuSpriteInfo"]
closeCrossImg      = textures["closeCross"]
closeCrossClickImg = textures["closeCrossClick"]
doneSparkleImg     = textures["doneSparkle"]

closeCrossX = 1392
closeCrossY = 96

# ============================================================
# FRUIT AND FERMENTED FRUIT IMAGE LOOKUP TABLES
# Dictionaries that map crop name -> the sprite to display.
# fruitImages    -> raw harvested fruit sprite
# fermentImages  -> fermented version of the same fruit
# ============================================================
fruitImages = {
    "tomato"  : textures["tomato"],
    "carrot"  : textures["carrot"],
    "cucumber": textures["cucumber"],
    "chili"   : textures["chili"],
    "cabbage" : textures["cabbage"],
    "garlic"  : textures["garlic"],
}

fermentImages = {
    "tomato"  : textures["tomatoFerment"],
    "carrot"  : textures["carrotFerment"],
    "cucumber": textures["cucumberFerment"],
    "chili"   : textures["chiliFerment"],
    "cabbage" : textures["cabbageFerment"],
    "garlic"  : textures["garlicFerment"],
}

# ============================================================
# FERMENTATION POT STATE
# The shed has two slots where the player can place fermentation pots.
# shedSlots is a list with one entry per slot; each entry is either None
# (no pot placed) or a dictionary describing the pot and what is inside it.
# ============================================================
shedPotImg = textures["shedPot"]

# pygame.Rect defines a rectangle by (x, y, width, height).
# fermPotLargeRect is the clickable area of the shop pot sprite.
fermPotLargeRect  = pygame.Rect(fermPotLargeX, fermPotLargeY,
                                fermPotLargeImg.get_width(), fermPotLargeImg.get_height())
fermPotLargePrice = 30

# Where each shed slot's pot sprite is drawn (top-left pixel positions).
shedSlotTop    = (440, 280)
shedSlotBottom = (464, 360)

# The actual pot-contents data for each slot. None means the slot is empty.
shedSlots = [None, None]

# How many pixels to offset the ferment-fruit sprite from the pot sprite
# so it appears to sit inside the pot.
fermentOffsetX = 17
fermentOffsetY = 25

# heldPot   is the pot the player is currently carrying (None if none).
# heldFruit is a dict {"crop": name, "fermented": bool} for the fruit
#           the player is currently carrying (None if none).
heldPot   = None
heldFruit = None

# How large (in pixels) to draw the fruit sprite when held on the cursor.
fruitCursorSize = 48

# Click areas for each shed slot — separate from the draw positions above
# because click detection and drawing are independent concerns.
shedSlotRects = [
    pygame.Rect(456, 336, 40, 40),
    pygame.Rect(480, 416, 40, 40),
]

# Click area for the sell chest.
shopChestRect  = pygame.Rect(shopChestX, shopChestY,
                             shopChestImg.get_width(), shopChestImg.get_height())
# Click area for the close button on the pause menu.
closeCrossRect = pygame.Rect(closeCrossX, closeCrossY,
                             closeCrossImg.get_width(), closeCrossImg.get_height())

# ============================================================
# SEED BAG CLICK RECTS
# Maps each crop name to the pygame.Rect for its seed bag on the shop shelf.
# ============================================================
seedRects = {
    "carrot"  : pygame.Rect(carrotBagX,   carrotBagY,   carrotBagImg.get_width(),   carrotBagImg.get_height()),
    "tomato"  : pygame.Rect(tomatoBagX,   tomatoBagY,   tomatoBagImg.get_width(),   tomatoBagImg.get_height()),
    "chili"   : pygame.Rect(chiliBagX,    chiliBagY,    chiliBagImg.get_width(),    chiliBagImg.get_height()),
    "cucumber": pygame.Rect(cucumberBagX, cucumberBagY, cucumberBagImg.get_width(), cucumberBagImg.get_height()),
    "cabbage" : pygame.Rect(cabbageBagX,  cabbageBagY,  cabbageBagImg.get_width(),  cabbageBagImg.get_height()),
    "garlic"  : pygame.Rect(garlicBagX,   garlicBagY,   garlicBagImg.get_width(),   garlicBagImg.get_height()),
}

# Which seed the player currently has selected (None if they are not holding a seed).
selectedSeed = None

# Maps each crop name to the seed bag sprite, used to draw the cursor icon.
seedBagImages = {
    "carrot"  : textures["carrotBag"],
    "tomato"  : textures["tomatoBag"],
    "chili"   : textures["chiliBag"],
    "cucumber": textures["cucumberBag"],
    "cabbage" : textures["cabbageBag"],
    "garlic"  : textures["garlicBag"],
}

# ============================================================
# WATERING CAN
# ============================================================
wateringCanEmptyImg = textures["wateringcanEmpty"]
wateringCanFullImg  = textures["wateringcanFull"]
waterDropImg        = textures["waterDropPlant"]

wateringCanFull = False   # True when the can has water in it
wateringCanHeld = False   # True when the player is carrying the can

# The area the player clicks to refill the watering can at the water source.
waterRefillRect      = pygame.Rect(887, 416, 90, 90)
# The area where the watering can sits when not being held.
wateringCanWorldRect = pygame.Rect(887, 326, 90, 90)

# ============================================================
# RAIN SYSTEM
# The game picks 2 random days out of every 12-day cycle to be rainy.
# On rainy days all planted crops are watered automatically.
# ============================================================
rainFrames       = [textures["rainBackground1"], textures["rainBackground2"],
                    textures["rainBackground3"], textures["rainBackground4"],
                    textures["rainBackground5"]]
rainFrameMs      = 120   # milliseconds between rain animation frames
rainDaysInCycle  = set() # which days in the current 12-day cycle are rainy
rainCurrentCycle = -1    # which 12-day cycle we are in right now
rainFrameIndex   = 0     # which frame of the rain animation is showing
rainLastFrameTime = 0    # timestamp of the last rain frame change

def getRainDaysForCycle():
    # Pick 2 unique day numbers (0-11) to be rainy in the next 12-day cycle.
    return set(random.sample(range(12), 2))

def isRainingToday():
    # Returns True if today (daysPassed mod 12) is one of the two rainy days.
    return (daysPassed % 12) in rainDaysInCycle

# ============================================================
# TV WEATHER FORECAST
# The player can click the TV to see tomorrow's weather.
# ============================================================
rainForecastImg = textures["weatherReport1"]   # shown when rain is forecast
sunForecastImg  = textures["weatherReport2"]   # shown when sun is forecast
tvX, tvY        = 141 * 8, 33 * 8
tvRect          = pygame.Rect(tvX, tvY, 30 * 8, 17 * 8)
tvOn            = False   # True while the TV forecast is being displayed

# ============================================================
# GOLD WATER BUCKET
# An upgradeable watering tool that can water multiple plants before
# needing a refill. The player buys it once from the shop shelf.
# ============================================================
goldWaterBucketEmptyImg = textures["goldWaterBucket"]
goldWaterBucketFullImg  = textures["goldWaterBucketFill"]
goldWaterBucketShop     = textures["goldWaterBucketShop"]
goldWaterBucketImg      = textures["goldWaterBucketFill"]

goldWaterBucketPrice    = 300   # one-time purchase price in coins
goldWaterBucketMax      = 10    # how many uses per refill

hasGoldWaterBucket      = False   # True once the player has bought it
goldWaterBucketHeld     = False   # True while the player is carrying it
goldWaterBucketUsesLeft = 0       # remaining uses before it needs refilling

goldWaterBucketx    = 1488
goldWaterBuckety    = 328
goldWaterBucketRect = pygame.Rect(
    goldWaterBucketx,
    goldWaterBuckety,
    goldWaterBucketEmptyImg.get_width(),
    goldWaterBucketEmptyImg.get_height()
)

# ============================================================
# GNOME DONATION SYSTEM
# The player can click the big gnome to donate coins.
# Each donation makes in-game days slightly longer (adds 6 seconds per day).
# There are 21 donation levels. After all 21 the big gnome turns gold.
# Mini gnomes appear at donation thresholds 1 / 5 / 9 / 13 / 17.
# Donation price formula: price(n) = 5 + (n-1) * 5
# ============================================================
gnomeMaxDonations = 21

gnomeBigImg     = textures["gnomeBig"]
gnomeBigGoldImg = textures["gnomeBigGold"]
gnomeMiniImgs   = textures["gnomeMinis"]   # list of 5 unique mini-gnome sprites

gnomeBigX = 1045
gnomeBigY = 640

gnomeBigRect = pygame.Rect(
    gnomeBigX,
    gnomeBigY,
    gnomeBigImg.get_width(),
    gnomeBigImg.get_height()
)

# (x, y) draw positions for each of the 5 mini gnomes.
gnomeMiniPositions = [
    (1000, 921),
    ( 968, 724),
    (1059, 564),
    (1268, 636),
    (1292, 828),
]

# gnomeMiniThresholds[i] is the donation count needed before mini gnome i appears.
gnomeMiniThresholds = [1, 5, 9, 13, 17]

gnomeDonations = 0   # current number of completed donations (0 to 21)


def getNextGnomePrice():
    # Returns the coin cost of the next donation.
    # Donation 1 costs 5, donation 2 costs 10, ..., donation 21 costs 105.
    n = gnomeDonations + 1
    return 5 + (n - 1) * 5


def getDayInterval():
    # Returns how many milliseconds one in-game day lasts.
    # Starts at 5 seconds and grows by 6 seconds for every donation made.
    return 5000 + gnomeDonations * 6000


# ============================================================
# CORE GAME STATE
# ============================================================
money          = 600
background     = textures["background"]
calendarSprite = textures["calendar"]
calendarCircle = textures["calendarCircle"]

# Each cell in the grid is either None (empty) or a dictionary describing
# the planted crop. The grid is indexed as grid[column][row].
cellSize   = 128
gridCols   = 7
gridRows   = 3
gridStartX = 0
gridStartY = 696

grid = [[None for _ in range(gridRows)] for _ in range(gridCols)]

# How many coins it costs to buy an unowned tile. Keyed by column index.
# Columns closer to the left (lower index) are more expensive.
tileColPrice = {
    6: 3,
    5: 5,
    4: 10,
    3: 15,
    2: 20,
    1: 30,
    0: 50,
}

def makeTileOwned():
    # Build the starting tile-ownership grid.
    # The player starts with columns 5 and 6, rows 0 and 1 already unlocked.
    owned = [[False for _ in range(gridRows)] for _ in range(gridCols)]
    for col in [5, 6]:
        for row in [0, 1]:
            owned[col][row] = True
    return owned

tileOwned = makeTileOwned()

# Calendar marker position on the grid (updated each day tick).
startX, startY   = 1400, 696
spriteX, spriteY = startX, startY
step          = 128   # pixels the marker moves per day
columns       = 4
rows          = 3
currentColumn = 0
currentRow    = 0

lastMoveTime = pygame.time.get_ticks()   # timestamp of the last day tick
daysPassed   = 0                         # total in-game days elapsed

paused   = False   # True while the pause menu is open
showInfo = True    # True while the how-to-play screen is open

# ============================================================
# SAVE / LOAD SYSTEM
# The game saves to a JSON file with three independent save slots.
# ============================================================
saveFile  = "saveslots.json"
saveSlots = [
    {"name": "Empty", "date": "", "data": None},
    {"name": "Empty", "date": "", "data": None},
    {"name": "Empty", "date": "", "data": None},
]
if os.path.exists(saveFile):
    try:
        with open(saveFile, "r") as f:
            loadedSlots = json.load(f)
            if len(loadedSlots) == 3:
                saveSlots = loadedSlots
    except:
        pass

# ============================================================
# PAUSE MENU UI LAYOUT
# The three save-slot rectangles are stacked vertically in the centre-left
# of the screen. Four side-buttons sit to their right.
# ============================================================
slotWidth   = 400
slotHeight  = 200
slotSpacing = 25

slotStartX  = (virtualWidth  - slotWidth)  // 3.5
slotStartY  = (virtualHeight - (3 * slotHeight + 2 * slotSpacing)) // 2.5
slotBottomY = slotStartY + 3 * slotHeight + 2 * slotSpacing

def getSlotRect(i):
    # Returns the pygame.Rect for save-slot number i (0, 1, or 2).
    sy = slotStartY + i * (slotHeight + slotSpacing)
    return pygame.Rect(slotStartX, sy, slotWidth, slotHeight)

sideBtnW = 380
sideBtnX = int(slotStartX) + slotWidth + 100

totalBtnArea = slotBottomY - slotStartY
btnSpacing   = 20
btnH4        = (totalBtnArea - 3 * btnSpacing) // 4   # height of each side button

fullscreenBtnRect = pygame.Rect(sideBtnX, int(slotStartY),                            sideBtnW, btnH4)
infoBtnRect       = pygame.Rect(sideBtnX, int(slotStartY + 1 * (btnH4 + btnSpacing)), sideBtnW, btnH4)
audioBtnRect      = pygame.Rect(sideBtnX, int(slotStartY + 2 * (btnH4 + btnSpacing)), sideBtnW, btnH4)
quitBtnRect       = pygame.Rect(sideBtnX, int(slotStartY + 3 * (btnH4 + btnSpacing)), sideBtnW, btnH4)

# ============================================================
# INFO / HOW-TO-PLAY SCREEN
# Reads text from info.txt and displays it as a scrollable page.
# ============================================================
infoPadX         = 160
infoTopY         = 160
infoScrollTop    = 280
infoScrollBottom = 920
infoScrollH      = infoScrollBottom - infoScrollTop

closeBtnW    = 300
closeBtnH    = 90
closeBtnRect = pygame.Rect((virtualWidth - closeBtnW) // 2, 960, closeBtnW, closeBtnH)

infoFile     = "info.txt"
rawInfoLines = []
if os.path.exists(infoFile):
    try:
        with open(infoFile, "r", encoding="utf-8") as f:
            rawInfoLines = f.read().splitlines()
    except:
        rawInfoLines = ["Could not load info.txt"]

maxTextW = virtualWidth - infoPadX * 2

def wrapLines(rawLines, font, maxW):
    # Break long lines of text so they fit within maxW pixels.
    # Returns a new list of shorter lines.
    wrapped = []
    for raw in rawLines:
        if raw.strip() == "":
            wrapped.append("")
            continue
        words   = raw.split()
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if font.size(test)[0] <= maxW:
                current = test
            else:
                if current:
                    wrapped.append(current)
                current = word
        if current:
            wrapped.append(current)
    return wrapped

infoLines       = wrapLines(rawInfoLines, infoTextFont, maxTextW)
infoLineH       = infoTextFont.get_linesize() + 6
infoScrollY     = 0     # current vertical scroll offset in pixels
infoScrollSpeed = 40    # how many pixels to scroll per mouse wheel tick
infoTotalH      = len(infoLines) * infoLineH


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def setMusicVolume():
    # Adjust the music volume based on the current game state.
    # Muted when disabled, quieter when a menu is open, normal during gameplay.
    if not musicEnabled:
        pygame.mixer.music.set_volume(0)
    elif paused or showInfo:
        pygame.mixer.music.set_volume(musicDimVol)
    else:
        pygame.mixer.music.set_volume(musicNormalVol)


def saveGame(slotIndex, slotName):
    # Write the current game state to the chosen save slot and then to disk.
    global saveSlots
    saveData = {
        "money"                      : money,
        "days_passed"                : daysPassed,
        "grid"                       : grid,
        "current_column"             : currentColumn,
        "current_row"                : currentRow,
        "sprite_x"                   : spriteX,
        "sprite_y"                   : spriteY,
        "tile_owned"                 : tileOwned,
        "shed_slots"                 : shedSlots,
        "has_gold_water_bucket"      : hasGoldWaterBucket,
        "gold_water_bucket_held"     : goldWaterBucketHeld,
        "gold_water_bucket_uses_left": goldWaterBucketUsesLeft,
        "gnome_donations"            : gnomeDonations,
    }
    saveSlots[slotIndex] = {
        "name": slotName,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data": saveData,
    }
    try:
        with open(saveFile, "w") as f:
            json.dump(saveSlots, f)
    except:
        pass


def loadGame(slotIndex):
    # Load a previously saved game from the chosen slot.
    # Returns True on success, False if the slot is empty or data is corrupt.
    global money, daysPassed, grid
    global currentColumn, currentRow, spriteX, spriteY, lastMoveTime, tileOwned
    global shedSlots
    global hasGoldWaterBucket, goldWaterBucketHeld, goldWaterBucketUsesLeft
    global gnomeDonations

    slot = saveSlots[slotIndex]
    if slot["data"] is None:
        return False
    try:
        data          = slot["data"]
        money         = data["money"]
        daysPassed    = data["days_passed"]
        grid          = data["grid"]
        currentColumn = data["current_column"]
        currentRow    = data["current_row"]
        spriteX       = data["sprite_x"]
        spriteY       = data["sprite_y"]
        lastMoveTime  = pygame.time.get_ticks()
        tileOwned     = data.get("tile_owned") or makeTileOwned()
        shedSlots     = data.get("shed_slots") or [None, None]
        hasGoldWaterBucket      = data.get("has_gold_water_bucket", False)
        goldWaterBucketHeld     = data.get("gold_water_bucket_held", False)
        goldWaterBucketUsesLeft = data.get("gold_water_bucket_uses_left", 0)
        # Older saves without gnome_donations default to 0.
        gnomeDonations = data.get("gnome_donations", 0)
        return True
    except:
        return False


def newGame():
    # Reset all game state to starting values for a fresh game.
    global money, daysPassed, grid
    global currentColumn, currentRow, spriteX, spriteY, lastMoveTime, tileOwned
    global shedSlots, heldPot, heldFruit
    global hasGoldWaterBucket, goldWaterBucketHeld, goldWaterBucketUsesLeft
    global gnomeDonations

    money         = 6
    daysPassed    = 0
    grid          = [[None for _ in range(gridRows)] for _ in range(gridCols)]
    currentColumn = 0
    currentRow    = 0
    spriteX       = startX
    spriteY       = startY
    lastMoveTime  = pygame.time.get_ticks()
    tileOwned     = makeTileOwned()
    shedSlots     = [None, None]
    heldPot       = None
    heldFruit     = None
    hasGoldWaterBucket      = False
    goldWaterBucketHeld     = False
    goldWaterBucketUsesLeft = 0
    gnomeDonations          = 0


def screenToVirtual(mx, my):
    # Convert a real screen pixel position to its equivalent virtual canvas position.
    # Needed because the virtual canvas is scaled and centred on the real screen.
    screenW, screenH = screen.get_size()
    if fullscreen:
        vx = mx * virtualWidth  // screenW
        vy = my * virtualHeight // screenH
    else:
        scale   = min(screenW / virtualWidth, screenH / virtualHeight)
        xOffset = (screenW - virtualWidth  * scale) / 2
        yOffset = (screenH - virtualHeight * scale) / 2
        vx = int((mx - xOffset) / scale)
        vy = int((my - yOffset) / scale)
    return vx, vy

def screenToMenuRef(mx, my):
    # Same conversion used specifically for menu elements.
    return screenToVirtual(mx, my)

def toggleFullscreen():
    # Switch between fullscreen and windowed mode.
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((windowWidth, windowHeight), pygame.RESIZABLE)


def drawSideButton(surface, rect, label, hovered=False):
    # Draw one of the side buttons in the pause menu.
    # When hovered the text turns bright yellow with a drop shadow.
    if hovered:
        color      = (255, 245, 190)
        shadowSurf = buttonFont.render(label, False, (70, 40, 5))
        for ox, oy in ((-3, 3), (3, 3), (-3, -3), (3, -3)):
            sx = rect.x + (rect.w - shadowSurf.get_width())  // 2 + ox
            sy = rect.y + (rect.h - shadowSurf.get_height()) // 2 + oy
            surface.blit(shadowSurf, (sx, sy))
    else:
        color = (140, 110, 70)
    textSurf = buttonFont.render(label, False, color)
    tx = rect.x + (rect.w - textSurf.get_width())  // 2
    ty = rect.y + (rect.h - textSurf.get_height()) // 2
    surface.blit(textSurf, (tx, ty))


def buildMenuSurface(mouseVx=0, mouseVy=0):
    # Draw the pause menu onto menuSurface.
    # mouseVx, mouseVy are used to highlight the button the mouse is over.
    menuSurface.fill((0, 0, 0, 0))
    # Semi-transparent black overlay to dim the game behind the menu.
    overlay = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    menuSurface.blit(overlay, (0, 0))
    menuSpriteScaled = pygame.transform.scale(menuSprite, (menuRefW, menuRefH))
    menuSurface.blit(menuSpriteScaled, (0, 0))

    for i in range(3):
        slotRect  = getSlotRect(i)
        isHovered = slotRect.collidepoint(mouseVx, mouseVy)
        hasSave   = saveSlots[i]["data"] is not None

        bgColor     = (75, 55, 40)    if isHovered else (60, 40, 30)
        borderColor = (180, 150, 100) if isHovered else (100, 80, 60)
        pygame.draw.rect(menuSurface, bgColor,     slotRect)
        pygame.draw.rect(menuSurface, borderColor, slotRect, 2)

        # Clip drawing to within the slot rectangle so text can't overflow.
        menuSurface.set_clip(pygame.Rect(slotRect.x+1, slotRect.y+1, slotRect.w-2, slotRect.h-2))
        if hasSave:
            nameSurf = saveNameFont.render(saveSlots[i]["name"], False, (255, 255, 255))
            menuSurface.blit(nameSurf, (slotRect.x + 20, slotRect.y + 20))
            parts    = saveSlots[i]["date"].split(" ")
            dateStr  = parts[0][2:] if parts else ""
            timeStr  = parts[1] if len(parts) > 1 else ""
            dateSurf = saveDateFont.render(dateStr, False, (180, 180, 180))
            timeSurf = saveDateFont.render(timeStr, False, (180, 180, 180))
            menuSurface.blit(dateSurf, (slotRect.x + 20, slotRect.y + 100))
            menuSurface.blit(timeSurf, (slotRect.x + 20, slotRect.y + 148))
        else:
            nameSurf = saveNameFont.render(f"Empty Slot {i + 1}", False, (140, 120, 90))
            menuSurface.blit(nameSurf, (slotRect.x + 20, slotRect.y + 20))
        menuSurface.set_clip(None)

    crossHovered = closeCrossRect.collidepoint(mouseVx, mouseVy)
    crossImg     = closeCrossClickImg if crossHovered else closeCrossImg
    menuSurface.blit(crossImg, (closeCrossX, closeCrossY))

    fsLabel    = "Windowed" if fullscreen else "Fullscreen"
    audioLabel = "Music: ON" if musicEnabled else "Music: OFF"
    drawSideButton(menuSurface, fullscreenBtnRect, fsLabel,    hovered=fullscreenBtnRect.collidepoint(mouseVx, mouseVy))
    drawSideButton(menuSurface, infoBtnRect,       "Info",     hovered=infoBtnRect.collidepoint(mouseVx, mouseVy))
    drawSideButton(menuSurface, quitBtnRect,       "Quit",     hovered=quitBtnRect.collidepoint(mouseVx, mouseVy))
    drawSideButton(menuSurface, audioBtnRect,      audioLabel, hovered=audioBtnRect.collidepoint(mouseVx, mouseVy))


def buildInfoSurface(mouseVx=0, mouseVy=0):
    # Draw the how-to-play info screen onto infoSurface.
    global infoScrollY
    infoSurface.fill((0, 0, 0, 0))
    overlay = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    infoSurface.blit(overlay, (0, 0))
    infoSurface.blit(menuSpriteInfo, (0, 0))

    titleSurf = infoTitleFont.render("How to Play", False, (255, 240, 180))
    infoSurface.blit(titleSurf, ((virtualWidth - titleSurf.get_width()) // 2, infoTopY))

    # Keep the scroll position clamped so the player can't scroll too far.
    maxScroll   = max(0, infoTotalH - infoScrollH)
    infoScrollY = max(0, min(infoScrollY, maxScroll))

    # Only draw text that falls within the visible scroll area.
    scrollClip = pygame.Rect(infoPadX, infoScrollTop, virtualWidth - infoPadX * 2, infoScrollH)
    infoSurface.set_clip(scrollClip)

    y = infoScrollTop - infoScrollY
    for line in infoLines:
        if line == "":
            y += infoLineH // 2
            continue
        lineSurf = infoTextFont.render(line, False, (220, 200, 160))
        infoSurface.blit(lineSurf, (infoPadX, y))
        y += infoLineH

    infoSurface.set_clip(None)

    # Show scroll hint text when there is more content above or below.
    if infoScrollY > 0:
        upSurf = infoTextFont.render("scroll up", False, (160, 130, 80))
        infoSurface.blit(upSurf, ((virtualWidth - upSurf.get_width()) // 2, infoScrollTop + 8))
    if infoScrollY < maxScroll:
        downSurf = infoTextFont.render("scroll down", False, (160, 130, 80))
        infoSurface.blit(downSurf, ((virtualWidth - downSurf.get_width()) // 2, infoScrollBottom - 52))

    drawSideButton(infoSurface, closeBtnRect, "Close", hovered=closeBtnRect.collidepoint(mouseVx, mouseVy))


def getPlantToolTip(cell):
    # Build the tooltip string shown when the player hovers over a planted tile.
    plantState(cell)
    crop = crops[cell["crop"]]

    if cell["dead"]:
        return f"{cell['crop'].capitalize()} is dead"

    if cell["stage"] >= crop["max_stage"]:
        # Plant is ripe — show how many days until it dies.
        if cell["dayRipe"] is not None:
            daysLeftBeforeDeath = max(0, ripeDays - (daysPassed - cell["dayRipe"]))
            return f"{cell['crop'].capitalize()}: Harvest Now! ({daysLeftBeforeDeath}d Left)"
        return f"{cell['crop'].capitalize()}: Harvest Now!"

    # Plant is still growing — show how many more waterings it needs.
    totalWaterNeeded = crop["growth_days_per_stage"] * crop["max_stage"]
    waterDays = cell.get("watered_days", 0)
    if cell.get("watered", False):
        waterDays += 1
    waterLeft = max(0, totalWaterNeeded - waterDays)
    return f"{cell['crop'].capitalize()}: {waterLeft} waterings left"

def potShopPrice(potType):
    # Returns the cost of purchasing a fermentation pot.
    return fermPotLargePrice

def getFruitSellValue(cropName, fermented):
    # Returns how many coins selling this crop earns.
    # fermented=True gives the higher fermented price.
    if fermented:
        return fermentData[cropName]["value"]
    return cropValues[cropName]

def isFermentDone(slot):
    # Returns True if the fruit in this shed slot has finished fermenting.
    if slot is None or slot.get("crop") is None:
        return False
    if slot.get("done", False):
        return True
    daysRequired = fermentData[slot["crop"]]["days"]
    daysIn       = daysPassed - slot.get("day_placed", daysPassed)
    return daysIn >= daysRequired

def tickFermentation():
    # Called once per day tick. Marks any finished fermentation slots as done.
    for slot in shedSlots:
        if slot is not None and slot.get("crop") is not None:
            if not slot.get("done", False):
                daysRequired = fermentData[slot["crop"]]["days"]
                daysIn       = daysPassed - slot.get("day_placed", daysPassed)
                if daysIn >= daysRequired:
                    slot["done"] = True


setMusicVolume()


# ============================================================
# MAIN GAME LOOP
# Everything after this runs repeatedly, once per frame.
# ============================================================
running = True
while running:
    # Wait until enough time has passed to maintain the target frame rate.
    clock.tick(fps)

    # Advance the rain animation when it is raining and the game is not paused.
    if isRainingToday() and not paused and not showInfo:
        nowMs = pygame.time.get_ticks()
        if nowMs - rainLastFrameTime >= rainFrameMs:
            rainLastFrameTime = nowMs
            rainFrameIndex = (rainFrameIndex + 1) % len(rainFrames)

    mx, my           = pygame.mouse.get_pos()
    hoverVx, hoverVy = screenToMenuRef(mx, my)

    # --------------------------------------------------------
    # EVENT PROCESSING
    # pygame puts all input events in a queue each frame.
    # We loop through every event and respond to it.
    # --------------------------------------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if showInfo:
                if event.key == pygame.K_ESCAPE:
                    showInfo = False
                    paused   = True
                    setMusicVolume()
            elif paused:
                if event.key == pygame.K_ESCAPE:
                    paused       = False
                    lastMoveTime = pygame.time.get_ticks()
                    setMusicVolume()
            else:
                if event.key == pygame.K_ESCAPE:
                    # ESC cancels whatever the player is currently holding,
                    # refunding the cost if applicable.
                    if selectedSeed is not None:
                        money += cropPrice[selectedSeed]
                        selectedSeed = None
                    elif wateringCanHeld:
                        wateringCanHeld = False
                    elif goldWaterBucketHeld:
                        goldWaterBucketHeld = False
                    elif heldPot is not None:
                        money  += potShopPrice(heldPot)
                        heldPot = None
                    elif heldFruit is not None:
                        pass   # fruit cannot be refunded, just drop it
                    else:
                        paused = True
                        setMusicVolume()
                if event.key == pygame.K_F11:
                    toggleFullscreen()

        # Mouse wheel scrolls the info page.
        if event.type == pygame.MOUSEWHEEL and showInfo:
            infoScrollY -= event.y * infoScrollSpeed

        if event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # ====================================================
        # LEFT MOUSE BUTTON
        # ====================================================
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            rx, ry = screenToMenuRef(mx, my)

            # Handle clicks when the info screen is open.
            if showInfo:
                if closeBtnRect.collidepoint(rx, ry):
                    showInfo = False
                    paused   = True
                    setMusicVolume()
                continue

            # Handle clicks when the pause menu is open.
            if paused:
                if closeCrossRect.collidepoint(rx, ry):
                    paused       = False
                    lastMoveTime = pygame.time.get_ticks()
                    setMusicVolume()
                    continue
                if fullscreenBtnRect.collidepoint(rx, ry):
                    toggleFullscreen()
                    continue
                if infoBtnRect.collidepoint(rx, ry):
                    showInfo    = True
                    infoScrollY = 0
                    setMusicVolume()
                    continue
                if quitBtnRect.collidepoint(rx, ry):
                    running = False
                    continue
                if audioBtnRect.collidepoint(rx, ry):
                    musicEnabled = not musicEnabled
                    setMusicVolume()
                    continue
                # Left-click a save slot: load it (or start a new game if empty).
                for i in range(3):
                    if getSlotRect(i).collidepoint(rx, ry):
                        if saveSlots[i]["data"] is not None:
                            loadGame(i)
                        else:
                            newGame()
                        paused = False
                        setMusicVolume()
                        break
                continue

            # From here on the game is running normally (not paused, not info).
            vx, vy = screenToVirtual(mx, my)

            # Toggle the TV weather forecast on or off.
            if tvRect.collidepoint(vx, vy):
                tvOn = not tvOn
                continue

            # If the player is holding a fruit, they can sell it or ferment it.
            if heldFruit is not None:
                if shopChestRect.collidepoint(vx, vy):
                    money    += getFruitSellValue(heldFruit["crop"], heldFruit["fermented"])
                    heldFruit = None
                    continue
                for slotIdx, slotRect in enumerate(shedSlotRects):
                    if slotRect.collidepoint(vx, vy):
                        slot = shedSlots[slotIdx]
                        # Place the fruit into the pot only if the slot has a pot but no fruit,
                        # and the fruit is not already fermented.
                        if slot is not None and slot.get("crop") is None and not heldFruit["fermented"]:
                            slot["crop"]       = heldFruit["crop"]
                            slot["day_placed"] = daysPassed
                            slot["done"]       = False
                            heldFruit = None
                        break
                continue

            # If the player is holding a pot, place it into an empty shed slot.
            if heldPot is not None:
                for slotIdx, slotRect in enumerate(shedSlotRects):
                    if slotRect.collidepoint(vx, vy) and shedSlots[slotIdx] is None:
                        shedSlots[slotIdx] = {"pot": heldPot, "crop": None, "day_placed": None, "done": False}
                        heldPot = None
                        break
                continue

            # Clicking the water source refills whichever bucket the player has.
            if waterRefillRect.collidepoint(vx, vy) and not selectedSeed and heldPot is None and heldFruit is None:
                if goldWaterBucketHeld:
                    goldWaterBucketUsesLeft = goldWaterBucketMax
                else:
                    wateringCanHeld = True
                    wateringCanFull = True
                continue

            # Clicking outside the grid while holding a watering tool drops it.
            if wateringCanHeld or goldWaterBucketHeld:
                gx = (vx - gridStartX) // cellSize
                gy = (vy - gridStartY) // cellSize
                if not (0 <= gx < gridCols and 0 <= gy < gridRows):
                    wateringCanHeld     = False
                    goldWaterBucketHeld = False
                    continue

            # Picking up a finished ferment from a shed slot.
            if not wateringCanHeld and selectedSeed is None and heldPot is None and heldFruit is None:
                for slotIdx, slotRect in enumerate(shedSlotRects):
                    if slotRect.collidepoint(vx, vy):
                        slot = shedSlots[slotIdx]
                        if slot is not None and isFermentDone(slot):
                            heldFruit          = {"crop": slot["crop"], "fermented": True}
                            slot["crop"]       = None
                            slot["day_placed"] = None
                            slot["done"]       = False
                        break

            # Buying a fermentation pot from the shop.
            if not wateringCanHeld and selectedSeed is None and heldPot is None and heldFruit is None:
                if fermPotLargeRect.collidepoint(vx, vy):
                    if money >= fermPotLargePrice:
                        money  -= fermPotLargePrice
                        heldPot = "large"
                    continue

            # Buying or picking up the gold water bucket.
            if not wateringCanHeld and not goldWaterBucketHeld and selectedSeed is None and heldPot is None and heldFruit is None:
                if goldWaterBucketRect.collidepoint(vx, vy):
                    if not hasGoldWaterBucket:
                        if money >= goldWaterBucketPrice:
                            money -= goldWaterBucketPrice
                            hasGoldWaterBucket      = True
                            goldWaterBucketHeld     = True
                            goldWaterBucketUsesLeft = goldWaterBucketMax
                            wateringCanHeld = False
                            wateringCanFull = False
                    else:
                        goldWaterBucketHeld = True
                        wateringCanHeld     = True
                        wateringCanFull     = True
                    continue

            # Donating coins to the gnome to extend day length.
            if (not wateringCanHeld and not goldWaterBucketHeld
                    and selectedSeed is None and heldPot is None and heldFruit is None):
                if gnomeBigRect.collidepoint(vx, vy):
                    if gnomeDonations < gnomeMaxDonations:
                        nextPrice = getNextGnomePrice()
                        if money >= nextPrice:
                            money          -= nextPrice
                            gnomeDonations += 1
                    continue

            # Check whether the player clicked a seed bag on the shop shelf.
            clickedSeed = None
            if not wateringCanHeld and heldPot is None and heldFruit is None:
                for cropName, rect in seedRects.items():
                    if rect.collidepoint(vx, vy):
                        clickedSeed = cropName
                        break

            # Buying a locked tile by clicking it.
            if clickedSeed is None and selectedSeed is None and not wateringCanHeld and heldPot is None and heldFruit is None:
                gx = (vx - gridStartX) // cellSize
                gy = (vy - gridStartY) // cellSize
                if 0 <= gx < gridCols and 0 <= gy < gridRows:
                    if not tileOwned[gx][gy]:
                        price = tileColPrice[gx]
                        if money >= price:
                            money -= price
                            tileOwned[gx][gy] = True
                        continue

            # Picking up a seed bag from the shelf.
            if clickedSeed and selectedSeed is None:
                if money >= cropPrice[clickedSeed]:
                    money -= cropPrice[clickedSeed]
                    selectedSeed = clickedSeed
                continue

            # Planting a held seed by clicking an owned empty tile.
            if selectedSeed is not None:
                gx = (vx - gridStartX) // cellSize
                gy = (vy - gridStartY) // cellSize
                if 0 <= gx < gridCols and 0 <= gy < gridRows:
                    if grid[gx][gy] is None and tileOwned[gx][gy]:
                        grid[gx][gy] = {
                            "crop"        : selectedSeed,
                            "day_planted" : daysPassed,
                            "stage"       : 0,
                            "watered"     : False,
                            "watered_days": 0,
                            "dayRipe"     : None,
                            "dead"        : False,
                        }
                        selectedSeed = None
                continue

            # Watering a plant with the gold bucket.
            if goldWaterBucketHeld:
                gx = (vx - gridStartX) // cellSize
                gy = (vy - gridStartY) // cellSize
                if 0 <= gx < gridCols and 0 <= gy < gridRows:
                    cell = grid[gx][gy]
                    if cell is not None:
                        plantState(cell)
                        if not cell["watered"] and not cell["dead"] and goldWaterBucketUsesLeft > 0:
                            cell["watered"] = True
                            goldWaterBucketUsesLeft -= 1
                continue

            # Watering a plant with the normal watering can (waters one plant, then empties).
            if wateringCanHeld and wateringCanFull:
                gx = (vx - gridStartX) // cellSize
                gy = (vy - gridStartY) // cellSize
                if 0 <= gx < gridCols and 0 <= gy < gridRows:
                    cell = grid[gx][gy]
                    if cell is not None:
                        plantState(cell)
                        if not cell["watered"] and not cell["dead"]:
                            cell["watered"] = True
                            wateringCanFull = False

        # ====================================================
        # RIGHT MOUSE BUTTON
        # ====================================================
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            rx, ry = screenToMenuRef(mx, my)

            # Right-click a save slot in the pause menu to overwrite it.
            if paused and not showInfo:
                for i in range(3):
                    if getSlotRect(i).collidepoint(rx, ry):
                        saveGame(i, f"Farm {i + 1}")
                        break

            elif not paused and not showInfo:
                vx, vy = screenToVirtual(mx, my)

                # Right-clicking a fermented fruit re-places it into a free pot slot.
                if heldFruit is not None:
                    if heldFruit["fermented"]:
                        for slot in shedSlots:
                            if slot is not None and slot.get("crop") is None:
                                slot["crop"]       = heldFruit["crop"]
                                slot["day_placed"] = daysPassed
                                slot["done"]       = True
                                heldFruit = None
                                break
                    continue

                # Right-clicking while holding a seed refunds it.
                if selectedSeed is not None:
                    money += cropPrice[selectedSeed]
                    selectedSeed = None
                    continue

                # Right-clicking while holding a pot refunds it.
                if heldPot is not None:
                    money  += potShopPrice(heldPot)
                    heldPot = None
                    continue

                # Right-clicking a grid tile: harvest ripe crop or clear dead plant.
                gx            = (vx - gridStartX) // cellSize
                gy            = (vy - gridStartY) // cellSize
                harvestResult = harvestDead(grid, gx, gy, crops)
                if harvestResult:
                    if harvestResult["type"] == "dead_refund":
                        money += getDeadPlantRefund(harvestResult["crop"])
                    elif harvestResult["type"] == "fruit":
                        heldFruit = {"crop": harvestResult["crop"], "fermented": False}

    # =========================================================
    # DAY TICK
    # When enough real time has passed, advance the in-game day.
    # getDayInterval() gets longer as the player donates to the gnome.
    # =========================================================
    if not paused and not showInfo:
        now = pygame.time.get_ticks()
        if now - lastMoveTime >= getDayInterval():
            lastMoveTime = now
            daysPassed  += 1

            # Every 12 days generate a new set of rainy days.
            cycleIndex = daysPassed // 12
            if cycleIndex != rainCurrentCycle:
                rainCurrentCycle = cycleIndex
                rainDaysInCycle  = getRainDaysForCycle()

            # On rainy days all planted crops are watered automatically.
            if isRainingToday():
                for x in range(gridCols):
                    for y in range(gridRows):
                        if grid[x][y] is not None:
                            grid[x][y]["watered"] = True

            # Update every planted crop.
            for x in range(gridCols):
                for y in range(gridRows):
                    cell = grid[x][y]
                    if not cell:
                        continue

                    plantState(cell)

                    if cell["dead"]:
                        cell["watered"] = False
                        continue

                    # If the plant was watered today, count it as a watered day.
                    if cell.get("watered", False):
                        cell["watered_days"] = cell.get("watered_days", 0) + 1

                    # Reset the watered flag for tomorrow.
                    cell["watered"] = False

                    # Recalculate the plant's visual stage from total watered days.
                    crop        = crops[cell["crop"]]
                    wateredDays = cell.get("watered_days", 0)
                    stage       = wateredDays // crop["growth_days_per_stage"]
                    cell["stage"] = min(stage, crop["max_stage"])

                    # Track when the plant became ripe so we know when it will die.
                    if cell["stage"] >= crop["max_stage"]:
                        if cell["dayRipe"] is None:
                            cell["dayRipe"] = daysPassed
                        elif daysPassed - cell["dayRipe"] >= ripeDays:
                            cell["dead"] = True
                    else:
                        cell["dayRipe"] = None

            tickFermentation()
            tvOn = False   # close the TV forecast at the start of each new day

            # Advance the calendar marker position.
            spriteX       += step
            currentColumn += 1
            if currentColumn >= columns:
                currentColumn = 0
                spriteX       = startX
                spriteY      += step
                currentRow   += 1
                if currentRow >= rows:
                    currentRow       = 0
                    spriteX, spriteY = startX, startY

    # =========================================================
    # RENDERING
    # Draw everything onto the virtual canvas (target), then scale
    # the canvas to fit the actual screen.
    # =========================================================
    screenW, screenH = screen.get_size()
    target = pygame.Surface((virtualWidth, virtualHeight))

    # Background and shop furniture.
    target.blit(background,     (0, 0))
    target.blit(shopShelvesImg, (shopShelvesX, shopShelvesY))
    target.blit(fermPotLargeImg,(fermPotLargeX, fermPotLargeY))
    target.blit(carrotBagImg,   (carrotBagX,   carrotBagY))
    target.blit(tomatoBagImg,   (tomatoBagX,   tomatoBagY))
    target.blit(cucumberBagImg, (cucumberBagX, cucumberBagY))
    target.blit(chiliBagImg,    (chiliBagX,    chiliBagY))
    target.blit(garlicBagImg,   (garlicBagX,   garlicBagY))
    target.blit(cabbageBagImg,  (cabbageBagX,  cabbageBagY))
    target.blit(shopChestImg,   (shopChestX,   shopChestY))

    # Temporary TV hitbox outline (can be replaced with a proper sprite later).
    pygame.draw.rect(target, (255, 0, 0), tvRect, 2)

    # Draw the gold bucket in the shop only when the player is not carrying it.
    if not goldWaterBucketHeld:
        target.blit(goldWaterBucketShop, (goldWaterBucketx, goldWaterBuckety))

    # Draw mini gnomes (behind the big one) then the big gnome on top.
    for i, (miniX, miniY) in enumerate(gnomeMiniPositions):
        if gnomeDonations >= gnomeMiniThresholds[i]:
            target.blit(gnomeMiniImgs[i], (miniX, miniY))

    if gnomeDonations >= gnomeMaxDonations:
        target.blit(gnomeBigGoldImg, (gnomeBigX, gnomeBigY))
    else:
        target.blit(gnomeBigImg,     (gnomeBigX, gnomeBigY))

    # Draw shed fermentation slots.
    shedPositions = [shedSlotTop, shedSlotBottom]
    for slotIdx, slotPos in enumerate(shedPositions):
        slot = shedSlots[slotIdx]
        if slot is None:
            continue
        # Draw the ferment-fruit sprite inside the pot, then the pot on top.
        if slot.get("crop") is not None:
            fermImg = fermentImages[slot["crop"]]
            target.blit(fermImg, (slotPos[0] + fermentOffsetX, slotPos[1] + fermentOffsetY))
        target.blit(shedPotImg, slotPos)
        # Sparkle overlay when fermentation is complete.
        if slot.get("crop") is not None and isFermentDone(slot):
            target.blit(doneSparkleImg, slotPos)

    target.blit(shedDoorImg, (shedDoorX, shedDoorY))
    drawMoney(target, money, virtualWidth)

    # Draw every planted crop on the grid.
    for x in range(gridCols):
        for y in range(gridRows):
            cell = grid[x][y]
            if cell:
                plantState(cell)
                crop = crops[cell["crop"]]
                if cell["dead"]:
                    sprite = crop["death_sprite"]
                else:
                    sprite = crop["stages"][cell["stage"]]
                # Scale the sprite to fit the cell if it is a different size.
                if sprite.get_width() != cellSize or sprite.get_height() != cellSize:
                    sprite = pygame.transform.scale(sprite, (cellSize, cellSize))
                target.blit(sprite, (gridStartX + x * cellSize, gridStartY + y * cellSize))

    # Draw locked-tile overlays and track which one the mouse is hovering over.
    vMouseX, vMouseY  = screenToVirtual(*pygame.mouse.get_pos())
    hoveredLockedTile = None
    tekoopScaled      = pygame.transform.scale(tekoopTileImg, (cellSize, cellSize))
    for x in range(gridCols):
        for y in range(gridRows):
            if not tileOwned[x][y]:
                tx = gridStartX + x * cellSize
                ty = gridStartY + y * cellSize
                target.blit(tekoopScaled, (tx, ty))
                tileRect = pygame.Rect(tx, ty, cellSize, cellSize)
                if tileRect.collidepoint(vMouseX, vMouseY) and not paused and not showInfo:
                    hoveredLockedTile = (x, y)

    # Calendar sprite and the day-marker circle.
    target.blit(calendarSprite, (176*8, 72*8))
    target.blit(calendarCircle, (spriteX, spriteY))

    # Water-drop overlay on each crop that was watered today.
    for x in range(gridCols):
        for y in range(gridRows):
            cell = grid[x][y]
            if cell and cell.get("watered", False):
                druppel = pygame.transform.scale(waterDropImg, (cellSize, cellSize))
                target.blit(druppel, (gridStartX + x * cellSize, gridStartY + y * cellSize))

    # TV weather forecast overlay.
    tvSprite = textures["weatherReport3"]
    target.blit(tvSprite, (1120, 224))
    if tvOn:
        tomorrowDay = (daysPassed + 1) % 12
        forecastImg = rainForecastImg if tomorrowDay in rainDaysInCycle else sunForecastImg
        target.blit(forecastImg, (1120, 224))

    # Rain animation overlay on top of everything when it is raining.
    if isRainingToday() and not paused and not showInfo:
        rainSprite = pygame.transform.scale(rainFrames[rainFrameIndex], (virtualWidth, virtualHeight))
        target.blit(rainSprite, (0, 0))

    # =========================================================
    # CURSOR DRAWING
    # When the player is holding something, hide the system cursor and
    # draw the appropriate item sprite at the mouse position instead.
    # =========================================================
    if heldFruit is not None:
        cursorImg    = fermentImages[heldFruit["crop"]] if heldFruit["fermented"] else fruitImages[heldFruit["crop"]]
        cursorScaled = pygame.transform.scale(cursorImg, (fruitCursorSize, fruitCursorSize))
        target.blit(cursorScaled, (vMouseX - cursorScaled.get_width()  // 2,
                                   vMouseY - cursorScaled.get_height() // 2))
        pygame.mouse.set_visible(False)

    elif heldPot is not None:
        potScaled = pygame.transform.scale(fermPotLargeImg,
                                           (fermPotLargeImg.get_width(), fermPotLargeImg.get_height()))
        target.blit(potScaled, (vMouseX - potScaled.get_width()  // 2,
                                vMouseY - potScaled.get_height() // 2))
        pygame.mouse.set_visible(False)

    elif selectedSeed is not None:
        cursorScaled = pygame.transform.scale(seedBagImages[selectedSeed], (cellSize // 2, cellSize // 2))
        target.blit(cursorScaled, (vMouseX - cursorScaled.get_width()  // 2,
                                   vMouseY - cursorScaled.get_height() // 2))
        pygame.mouse.set_visible(False)

    elif goldWaterBucketHeld:
        bucketImg = goldWaterBucketFullImg if goldWaterBucketUsesLeft > 0 else goldWaterBucketEmptyImg
        target.blit(bucketImg, (vMouseX - bucketImg.get_width() // 2,
                                vMouseY - bucketImg.get_height() // 2))
        pygame.mouse.set_visible(False)

    elif wateringCanHeld:
        canImg    = wateringCanFullImg if wateringCanFull else wateringCanEmptyImg
        canScaled = pygame.transform.scale(canImg, (cellSize // 2, cellSize // 2))
        target.blit(canScaled, (vMouseX - canScaled.get_width() // 2,
                                vMouseY - canScaled.get_height() // 2))
        pygame.mouse.set_visible(False)

    else:
        pygame.mouse.set_visible(True)

    # =========================================================
    # TOOLTIPS
    # Small floating labels that appear when hovering over interactive items.
    # =========================================================
    def drawTooltip(surface, text, cx, cy):
        # Draw a rounded dark box with centred text above the point (cx, cy).
        tooltipSurf = saveDateFont.render(text, True, (255, 240, 160))
        padX, padY  = 16, 10
        tooltipBg   = pygame.Surface((tooltipSurf.get_width()  + padX * 2,
                                      tooltipSurf.get_height() + padY * 2), pygame.SRCALPHA)
        tooltipBg.fill((30, 20, 10, 210))
        tx = max(0, min(cx - tooltipBg.get_width() // 2, virtualWidth - tooltipBg.get_width()))
        ty = max(0, cy - tooltipBg.get_height() - 8)
        surface.blit(tooltipBg,   (tx, ty))
        surface.blit(tooltipSurf, (tx + padX, ty + padY))

    if hoveredLockedTile is not None:
        hx, hy = hoveredLockedTile
        drawTooltip(target, f"Buy: {tileColPrice[hx]} coins",
                    gridStartX + hx * cellSize + cellSize // 2,
                    gridStartY + hy * cellSize)

    if not paused and not showInfo:
        gx = (vMouseX - gridStartX) // cellSize
        gy = (vMouseY - gridStartY) // cellSize
        if 0 <= gx < gridCols and 0 <= gy < gridRows:
            cell = grid[gx][gy]
            if cell is not None:
                tooltipText = getPlantToolTip(cell)
                drawTooltip(target, tooltipText,
                            gridStartX + gx * cellSize + cellSize // 2,
                            gridStartY + gy * cellSize)

    if not paused and not showInfo:
        for cropName, rect in seedRects.items():
            if rect.collidepoint(vMouseX, vMouseY):
                drawTooltip(target, f"{cropName.capitalize()}: {cropPrice[cropName]} coins",
                            rect.centerx, rect.top)
                break

    if not paused and not showInfo and heldPot is None and selectedSeed is None and not wateringCanHeld and heldFruit is None:
        if fermPotLargeRect.collidepoint(vMouseX, vMouseY):
            drawTooltip(target, f"Large pot: {fermPotLargePrice} coins",
                        fermPotLargeRect.centerx, fermPotLargeRect.top)

    if not paused and not showInfo and heldFruit is not None:
        if shopChestRect.collidepoint(vMouseX, vMouseY):
            val    = getFruitSellValue(heldFruit["crop"], heldFruit["fermented"])
            suffix = " (fermented)" if heldFruit["fermented"] else ""
            drawTooltip(target, f"Sell {heldFruit['crop'].capitalize()}{suffix}: {val} coins",
                        shopChestRect.centerx, shopChestRect.top)

    if not paused and not showInfo and not goldWaterBucketHeld and heldFruit is None:
        if goldWaterBucketRect.collidepoint(vMouseX, vMouseY):
            if not hasGoldWaterBucket:
                drawTooltip(target, f"Gold Bucket: {goldWaterBucketPrice} coins",
                            goldWaterBucketRect.centerx, goldWaterBucketRect.top)
            else:
                drawTooltip(target, "Pick up Gold Bucket",
                            goldWaterBucketRect.centerx, goldWaterBucketRect.top)

    if not paused and not showInfo and goldWaterBucketHeld:
        bucketImg = goldWaterBucketFullImg if goldWaterBucketUsesLeft > 0 else goldWaterBucketEmptyImg
        drawTooltip(target, f"uses: {goldWaterBucketUsesLeft} left",
                    vMouseX, vMouseY - bucketImg.get_height() // 2)

    if not paused and not showInfo:
        for slotIdx, slotRect in enumerate(shedSlotRects):
            if slotRect.collidepoint(vMouseX, vMouseY):
                slot = shedSlots[slotIdx]
                if slot is not None and slot.get("crop") is not None:
                    cropName = slot["crop"]
                    if isFermentDone(slot):
                        drawTooltip(target,
                                    f"{cropName.capitalize()} ready! ({fermentData[cropName]['value']} coins)",
                                    slotRect.centerx, slotRect.top)
                    else:
                        daysLeft = fermentData[cropName]["days"] - (daysPassed - slot.get("day_placed", daysPassed))
                        drawTooltip(target, f"Fermenting {cropName}... ({max(0, daysLeft)}d left)",
                                    slotRect.centerx, slotRect.top)
                elif slot is not None:
                    drawTooltip(target, "Empty pot (place a fruit)", slotRect.centerx, slotRect.top)
                break

    # Gnome tooltip: shows donation cost, current progress, and day length preview.
    if (not paused and not showInfo
            and not wateringCanHeld and not goldWaterBucketHeld
            and selectedSeed is None and heldPot is None and heldFruit is None):
        if gnomeBigRect.collidepoint(vMouseX, vMouseY):
            if gnomeDonations >= gnomeMaxDonations:
                drawTooltip(target, "Gnome fully upgraded! Max day length reached.",
                            gnomeBigRect.centerx, gnomeBigRect.top)
            else:
                nextPrice  = getNextGnomePrice()
                daySeconds = getDayInterval() // 1000
                nextDaySec = (getDayInterval() + 6000) // 1000
                drawTooltip(
                    target,
                    f"Donate {nextPrice} coins  [{gnomeDonations}/{gnomeMaxDonations}]"
                    f"  day: {daySeconds}s -> {nextDaySec}s",
                    gnomeBigRect.centerx,
                    gnomeBigRect.top
                )

    # =========================================================
    # OVERLAY MENUS
    # The info and pause menu surfaces are drawn on top of everything else.
    # =========================================================
    if showInfo:
        pygame.mouse.set_visible(True)
        buildInfoSurface(hoverVx, hoverVy)
        target.blit(infoSurface, (0, 0))
    elif paused:
        pygame.mouse.set_visible(True)
        buildMenuSurface(hoverVx, hoverVy)
        target.blit(menuSurface, (0, 0))

    # =========================================================
    # SCALE AND DISPLAY
    # Scale the virtual canvas to fit the real screen, keeping aspect ratio,
    # then centre it on a black background.
    # =========================================================
    scale   = min(screenW / virtualWidth, screenH / virtualHeight)
    scaledW = int(virtualWidth  * scale)
    scaledH = int(virtualHeight * scale)
    scaled  = pygame.transform.scale(target, (scaledW, scaledH))
    screen.fill((0, 0, 0))
    screen.blit(scaled, ((screenW - scaledW) // 2, (screenH - scaledH) // 2))
    pygame.display.flip()

pygame.quit()
sys.exit()