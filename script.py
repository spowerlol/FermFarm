# =============================================================================
# script.py FermFarm Main Entry Point
#
# This is the heart of the game. It:
#   1. Initialises pygame and the display window.
#   2. Runs the title/start screen.
#   3. Loads all assets (textures, crops, fonts, save data).
#   4. Defines all game-state variables (money, grid, calendar, etc.).
#   5. Contains the main game loop which:
#        - Processes input events (clicks, key presses)
#        - Advances the in-game day timer
#        - Renders everything to the screen
# =============================================================================

import pygame
import sys
from texture        import loadTextures
from crop           import loadCrops
from money_ui       import initMoneyUi, drawMoney
from cropHarvesting import CROP_VALUES as cropValues, cropPrice
from ferment        import FERMENT_DATA as fermentData
from startScreen    import runStartScreen
import os
import json
import random
from datetime import datetime
from death_proces import plantState, getDeadPlantRefund, harvestDead, ripeDays

# Initialise all pygame modules (display, audio, event system, etc.).
pygame.init()
pygame.mixer.init()

# =============================================================================
# VIRTUAL CANVAS SIZE
# All game art is drawn at this resolution. The canvas is then scaled to fit
# whatever real display size is available, so the game looks correct on any
# screen. The virtual size is 240 tiles wide and 135 tiles tall; each tile
# is 8 pixels, giving us a 1920 x 1080 virtual canvas (Full HD).
# =============================================================================
virtualWidth  = 1920   #  virtual canvas width in pixels
virtualHeight = 1080   #  virtual canvas height in pixels
fps           = 60     # target frames per second

# Windowed-mode size (used when fullscreen is toggled off).
# We use half the virtual resolution so it fits on most laptop screens.
windowWidth   = 960    # virtualWidth  // 2
windowHeight  = 540    # virtualHeight // 2

# These are used when building the pause menu UI see buildMenuSurface().
menuRefW = virtualWidth   # 1920
menuRefH = virtualHeight  # 1080

# =============================================================================
# DISPLAY SETUP
# We default to true fullscreen. pygame.display.Info() gives us the actual
# monitor resolution so the window fills the screen exactly.
# =============================================================================
fullscreen = True
info   = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("FermFarm")

clock = pygame.time.Clock()

# Show the splash/title screen and wait for the player to dismiss it.
runStartScreen(screen, fullscreen)

# =============================================================================
# MUSIC SETTINGS
# musicNormalVol: volume during normal gameplay.
# musicDimVol   : reduced volume when the pause menu or info screen is open,
#                 so the menu text is easier to read without muting the music.
# musicEnabled  : whether music is playing at all (toggled in the pause menu).
# =============================================================================
musicNormalVol = 0.5   # 50 % volume during gameplay
musicDimVol    = 0.2   # 20 % volume while a menu is open
musicEnabled   = True

# =============================================================================
# ASSET LOADING
# Load all sprites, initialise the money HUD font, and build the crop data.
# =============================================================================
textures = loadTextures()
initMoneyUi(textures)          # slices the number-font sheet into digit surfaces
crops    = loadCrops(textures) # builds the crop-growth dictionary

tekoopTileImg = textures["tekoopTile"]  # "te koop" = Dutch "for sale" overlay on locked tiles

# =============================================================================
# OFF-SCREEN SURFACES
# We draw the pause menu and info screen onto separate transparent surfaces
# (menuSurface / infoSurface) and then blit them over the game world.
# SRCALPHA means each pixel can be fully transparent, semi-transparent, or opaque.
# =============================================================================
menuSurface = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)
infoSurface = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)

# =============================================================================
# FONTS
# We use a custom pixel-art TTF font. If the file is missing we fall back to
# pygame's default font (fontPath = None triggers that fallback).
# The number argument to pygame.font.Font() is the font size in points.
# =============================================================================
fontPath = "sprites/babosorry.ttf"
if not os.path.exists(fontPath):
    fontPath = None

saveNameFont  = pygame.font.Font(fontPath, 60)   # save-slot name in the pause menu
saveDateFont  = pygame.font.Font(fontPath, 36)   # date/time shown in save slots
buttonFont    = pygame.font.Font(fontPath, 96)   # large side-buttons in the pause menu
infoTextFont  = pygame.font.Font(fontPath, 44)   # body text on the info/how-to-play screen
infoTitleFont = pygame.font.Font(fontPath, 72)   # "How to Play" heading on info screen

# =============================================================================
# SPRITE POSITIONS  (all coordinates are design-value * 8 = pixel position)
# =============================================================================

# --- Shed door ---
# The shed door graphic sits at tile (64, 33) in the design.
shedDoorImg = textures["shedDoor"]
shedDoorX   = 512    # 64
shedDoorY   = 264    # 33

# --- Shop shelves ---
# The seed-display shelves start at tile (185, 50).
shopShelvesImg = textures["shopShelves"]
shopShelvesX   = 1480
shopShelvesY   = 400

# --- Shop chest (sell chest) ---
# The sell chest sits at tile (225, 56).
shopChestImg = textures["shopChest"]
shopChestX   = 1800
shopChestY   = 448

# --- Large fermentation pot (shop item, before purchase) ---
# Shown at tile (230, 42) on the shop shelf.
fermPotLargeImg = textures["fermPotLarge"]
fermPotLargeX   = 1840
fermPotLargeY   = 336

# --- Seed bags displayed on shelves ---
# Each seed bag sprite is positioned at its own tile coordinate.
carrotBagImg  = textures["carrotBag"]
carrotBagX    = 1488
carrotBagY    = 432

tomatoBagImg  = textures["tomatoBag"]
tomatoBagX    = 1584
tomatoBagY    = 432

chiliBagImg   = textures["chiliBag"]
chiliBagX     = 1488
chiliBagY     = 536

cucumberBagImg = textures["cucumberBag"]
cucumberBagX   = 1680
cucumberBagY   = 432

cabbageBagImg = textures["cabbageBag"]
cabbageBagX   = 1576
cabbageBagY   = 536

garlicBagImg  = textures["garlicBag"]
garlicBagX    = 1672
garlicBagY    = 536

# --- Menu / UI sprites ---
menuSprite         = textures["menuSprite"]
menuSpriteInfo     = textures["menuSpriteInfo"]
closeCrossImg      = textures["closeCross"]
closeCrossClickImg = textures["closeCrossClick"]
doneSparkleImg     = textures["doneSparkle"]

# The close (X) button in the top-right of the pause menu.
closeCrossX = 1392
closeCrossY = 96

# =============================================================================
# FRUIT & FERMENTED FRUIT TEXTURE LOOKUP TABLES
# Lets us find any crop's icon by name rather than a long if/elif chain.
# =============================================================================

# Raw (un-fermented) fruit icons shown on the cursor while the player
# carries a harvested crop before placing it in a pot or selling it.
fruitImages = {
    "tomato"  : textures["tomato"],
    "carrot"  : textures["carrot"],
    "cucumber": textures["cucumber"],
    "chili"   : textures["chili"],
    "cabbage" : textures["cabbage"],
    "garlic"  : textures["garlic"],
}

# Fermented fruit icons shown inside the shed pot and on the cursor when
# the player picks up a finished fermented product.
fermentImages = {
    "tomato"  : textures["tomatoFerment"],
    "carrot"  : textures["carrotFerment"],
    "cucumber": textures["cucumberFerment"],
    "chili"   : textures["chiliFerment"],
    "cabbage" : textures["cabbageFerment"],
    "garlic"  : textures["garlicFerment"],
}

# =============================================================================
# FERMENTATION POT STATE
# =============================================================================

shedPotImg = textures["shedPot"]

# Clickable/interactable rect for the large pot on the shop shelf.
# Derived from the pot's draw position and its sprite dimensions.
fermPotLargeRect  = pygame.Rect(fermPotLargeX, fermPotLargeY,
                                fermPotLargeImg.get_width(), fermPotLargeImg.get_height())
fermPotLargePrice = 30   # coins to buy a large fermentation pot

# Where the two shed pots are DRAWN on screen (pixel coordinates).
# These are fixed visual anchor points; the actual click detection uses
# shedSlotRects further below.
shedSlotTop    = (440, 280)    # top    pot draw position (x, y) in pixels
shedSlotBottom = (464, 360)    # bottom pot draw position (x, y) in pixels

# shedSlots[0] = top pot, shedSlots[1] = bottom pot.
# Each slot is either None (no pot placed yet) or a dict:
#   { "pot": "large",
#     "crop": "tomato" | None,   <- what fruit is currently fermenting
#     "day_placed": int | None,  <- which game day the fruit was placed
#     "done": bool               <- True once fermentation is complete
#   }
shedSlots = [None, None]

# Visual offset: when we draw the ferment-fruit icon INSIDE the pot sprite,
# we shift it slightly so it appears to sit inside the pot rather than above it.
fermentOffsetX = 17   # pixels to shift the fruit icon horizontally inside the pot
fermentOffsetY = 25   # pixels to shift the fruit icon vertically inside the pot

# "heldPot"   = "large" while the player is carrying a pot from the shop shelf
#               to a shed slot; None otherwise.
heldPot  = None

# "heldFruit" = a dict {"crop": str, "fermented": bool} while the player is
#               carrying a harvested or fermented crop; None otherwise.
heldFruit = None

# Size in pixels to draw the fruit icon on the cursor while the player holds it.
fruitCursorSize = 48

# Click detection rectangles for the two shed pot slots.
# These are SEPARATE from shedSlotTop / shedSlotBottom because the visual
# sprite and the interactable area don't have to be identical.
shedSlotRects = [
    pygame.Rect(456, 336, 40, 40),   # top    pot clickable area (x, y, w, h)
    pygame.Rect(480, 416, 40, 40),   # bottom pot clickable area (x, y, w, h)
]

# Clickable rect for the sell chest (derived from sprite size).
shopChestRect = pygame.Rect(shopChestX, shopChestY,
                            shopChestImg.get_width(), shopChestImg.get_height())

# Clickable rect for the close (X) button on the pause menu.
closeCrossRect = pygame.Rect(closeCrossX, closeCrossY,
                             closeCrossImg.get_width(), closeCrossImg.get_height())

# =============================================================================
# SEED BAG CLICK RECTS
# One rectangle per crop bag on the shop shelf.
# Derived from each bag's draw position and sprite size.
# =============================================================================
seedRects = {
    "carrot"  : pygame.Rect(carrotBagX,   carrotBagY,   carrotBagImg.get_width(),   carrotBagImg.get_height()),
    "tomato"  : pygame.Rect(tomatoBagX,   tomatoBagY,   tomatoBagImg.get_width(),   tomatoBagImg.get_height()),
    "chili"   : pygame.Rect(chiliBagX,    chiliBagY,    chiliBagImg.get_width(),    chiliBagImg.get_height()),
    "cucumber": pygame.Rect(cucumberBagX, cucumberBagY, cucumberBagImg.get_width(), cucumberBagImg.get_height()),
    "cabbage" : pygame.Rect(cabbageBagX,  cabbageBagY,  cabbageBagImg.get_width(),  cabbageBagImg.get_height()),
    "garlic"  : pygame.Rect(garlicBagX,   garlicBagY,   garlicBagImg.get_width(),   garlicBagImg.get_height()),
}

# Which seed is currently selected (being carried on the cursor ready to plant).
selectedSeed = None

# Quick lookup from crop name to its bag sprite, used when drawing the cursor.
seedBagImages = {
    "carrot"  : textures["carrotBag"],
    "tomato"  : textures["tomatoBag"],
    "chili"   : textures["chiliBag"],
    "cucumber": textures["cucumberBag"],
    "cabbage" : textures["cabbageBag"],
    "garlic"  : textures["garlicBag"],
}

# =============================================================================
# WATERING CAN
# =============================================================================
wateringCanEmptyImg = textures["wateringcanEmpty"]
wateringCanFullImg  = textures["wateringcanFull"]
waterDropImg        = textures["waterDropPlant"]

# Is the can currently full (has water to give to plants)?
wateringCanFull  = False

# Is the player currently holding the watering can (it follows the cursor)?
wateringCanHeld  = False

# The water source / refill point: the well or trough near the farm grid.
# Clicking here when NOT holding a seed refills and picks up the watering can.
waterRefillRect      = pygame.Rect(887, 416, 90, 90)   # clickable area of the water source
wateringCanWorldRect = pygame.Rect(887, 326, 90, 90)   # where the can sprite is drawn when idle  (416 - 90 = 326)


# -------------------------------------------------------------------------------
#RAIN SYSTEM
#--------------------------------------------------------------------------------

RAIN_FRAMES       = [textures["rainBackground1"], textures["rainBackground2"], textures["rainBackground3"], textures["rainBackground4"], textures["rainBackground5"]]
RAIN_FRAME_MS     = 120          # milliseconds per frame (adjust for speed)
rainDaysInCycle   = set()        # which days (mod 12) are rainy this cycle
rainCurrentCycle  = -1           # tracks which 12-day cycle we're in
rainFrameIndex    = 0
rainLastFrameTime = 0

def getRainDaysForCycle():
    # Picks 2 unique rain days out of every 12
    return set(random.sample(range(12), 2))

def isRainingToday():
    return (daysPassed % 12) in rainDaysInCycle


# =============================================================================
# CORE GAME STATE
# =============================================================================
money          = 600               # starting coin balance
background     = textures["background"]
calendarSprite = textures["calendar"]
calendarCircle = textures["calendarCircle"]

# --- Farm grid ---
# The farm is a 7-column × 3-row grid of tiles.
# Each tile is 16 design-tiles wide/tall, which scales to 128 × 128 pixels.
cellSize   = 128    # 16 * 8  size of one farm tile in pixels
gridCols   = 7      # number of columns in the farm grid
gridRows   = 3      # number of rows    in the farm grid
gridStartX = 0      # pixel X where the grid begins (left edge of the screen)
gridStartY = 696    # 87 * 8 pixel Y where the grid begins

# The grid itself: a 2D list indexed as grid[col][row].
# None = empty tile.  dict = planted crop with its state.
grid = [[None for _ in range(gridRows)] for _ in range(gridCols)]

# --- Tile ownership ---
# Players start with the two rightmost columns (5 and 6) and top two rows unlocked.
# All other tiles must be purchased. Prices are higher for tiles on the left
# (further from the shop) to create a natural economic progression.
tileColPrice = {
    6: 3,    # rightmost column cheapest
    5: 5,
    4: 10,
    3: 15,
    2: 20,
    1: 30,
    0: 50,   # leftmost column most expensive
}

def makeTileOwned():
    """Return a fresh 7×3 ownership grid with the starting tiles pre-unlocked."""
    owned = [[False for _ in range(gridRows)] for _ in range(gridCols)]
    # Columns 5 and 6, rows 0 and 1 are unlocked at the start of a new game.
    for col in [5, 6]:
        for row in [0, 1]:
            owned[col][row] = True
    return owned

tileOwned = makeTileOwned()

# --- Calendar / day system ---
# The calendar marker (calendarCircle) travels across a 4-column × 3-row path
# that mirrors the calendar sprite graphic. It moves one step per in-game day.
startX, startY = 1400, 696   # 175 * 8, 87 * 8 first calendar marker position
spriteX, spriteY = startX, startY  # current marker position (updated each day tick)
step          = 128    # 16 * 8 pixels per calendar step (one tile)
columns       = 4      # number of columns in the calendar path
rows          = 3      # number of rows    in the calendar path
currentColumn = 0      # which calendar column the marker is currently on (0-3)
currentRow    = 0      # which calendar row    the marker is currently on (0-2)

# How many milliseconds must pass before the next in-game day advances.
# 5000 ms = 5 seconds per day.
moveInterval = 5_000
lastMoveTime = pygame.time.get_ticks()   # timestamp of the last day tick

# Total number of in-game days that have passed since the game started.
daysPassed = 0

# --- UI state flags ---
paused   = False   # True while the pause/options menu is open
showInfo = True    # True while the "How to Play" info screen is open (shown at launch)

# =============================================================================
# SAVE / LOAD SYSTEM
# Saves are stored as a JSON file ("saveslots.json") with 3 slots.
# Each slot holds a name, a date/time string, and a "data" dict with full
# game state, or None if the slot has never been saved.
# =============================================================================
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
        pass   # If the file is corrupt, silently start with empty slots

# =============================================================================
# PAUSE MENU UI LAYOUT
# All button and slot positions for the pause/save menu are calculated here
# so they stay neatly centred even if we change the virtual resolution.
# =============================================================================
slotWidth   = 400    # width  of each save-slot button in pixels
slotHeight  = 200    # height of each save-slot button in pixels
slotSpacing = 25     # vertical gap between save-slot buttons in pixels

# Horizontally centre the slot column at about 1/3.5 of the screen width.
slotStartX = (virtualWidth  - slotWidth)  // 3.5
# Vertically centre the three slots (plus gaps) in the upper portion of the screen.
slotStartY = (virtualHeight - (3 * slotHeight + 2 * slotSpacing)) // 2.5
# The Y coordinate of the bottom edge of the last slot used to size side buttons.
slotBottomY = slotStartY + 3 * slotHeight + 2 * slotSpacing

def getSlotRect(i):
    """Return the pygame.Rect for save-slot button number i (0, 1, or 2)."""
    sy = slotStartY + i * (slotHeight + slotSpacing)
    return pygame.Rect(slotStartX, sy, slotWidth, slotHeight)

# Side buttons (Fullscreen, Info, Audio, Quit) sit to the right of the save slots.
sideBtnW = 380    # width  of each side button in pixels
sideBtnX = int(slotStartX) + slotWidth + 100   # X position of the side button column

# Divide the same vertical space as the slots into 4 equal button areas.
totalBtnArea = slotBottomY - slotStartY
btnSpacing   = 20
btnH4        = (totalBtnArea - 3 * btnSpacing) // 4   # height of each side button

fullscreenBtnRect = pygame.Rect(sideBtnX, int(slotStartY),                            sideBtnW, btnH4)
infoBtnRect       = pygame.Rect(sideBtnX, int(slotStartY + 1 * (btnH4 + btnSpacing)), sideBtnW, btnH4)
audioBtnRect      = pygame.Rect(sideBtnX, int(slotStartY + 2 * (btnH4 + btnSpacing)), sideBtnW, btnH4)
quitBtnRect       = pygame.Rect(sideBtnX, int(slotStartY + 3 * (btnH4 + btnSpacing)), sideBtnW, btnH4)

# =============================================================================
# INFO / HOW-TO-PLAY SCREEN
# Text is loaded from "info.txt", word-wrapped to fit the screen width,
# and rendered with a scroll region so long content can be scrolled.
# =============================================================================
infoPadX         = 160    # horizontal padding in pixels (left and right of text)
infoTopY         = 160    # Y position of the "How to Play" title
infoScrollTop    = 280    # Y where the scrollable text region begins
infoScrollBottom = 920    # Y where the scrollable text region ends
infoScrollH      = infoScrollBottom - infoScrollTop   # 640 px of visible text area

# "Close" button at the bottom of the info screen.
closeBtnW    = 300
closeBtnH    = 90
closeBtnRect = pygame.Rect((virtualWidth - closeBtnW) // 2, 960, closeBtnW, closeBtnH)

# Load raw lines from info.txt (if it exists).
infoFile     = "info.txt"
rawInfoLines = []
if os.path.exists(infoFile):
    try:
        with open(infoFile, "r", encoding="utf-8") as f:
            rawInfoLines = f.read().splitlines()
    except:
        rawInfoLines = ["Could not load info.txt"]

# Maximum width in pixels that a line of info text may occupy.
maxTextW = virtualWidth - infoPadX * 2   # 1920 - 320 = 1600 px

def wrapLines(rawLines, font, maxW):
    """
    Word-wrap a list of raw text lines to fit within maxW pixels.

    Parameters:
        rawLines (list[str]): lines of text as loaded from info.txt.
        font     (pygame.font.Font): the font used to measure text width.
        maxW     (int): maximum allowed line width in pixels.

    Returns:
        list[str]: new list of lines, each guaranteed to fit within maxW.
    """
    wrapped = []
    for raw in rawLines:
        # Blank lines become empty strings to preserve paragraph spacing.
        if raw.strip() == "":
            wrapped.append("")
            continue
        words   = raw.split()
        current = ""
        for word in words:
            # Try appending the next word and measure the result.
            test = (current + " " + word).strip()
            if font.size(test)[0] <= maxW:
                current = test   # still fits keep building the line
            else:
                if current:
                    wrapped.append(current)   # flush the current line
                current = word                # start a new line with this word
        if current:
            wrapped.append(current)   # flush the final line
    return wrapped

infoLines       = wrapLines(rawInfoLines, infoTextFont, maxTextW)
infoLineH       = infoTextFont.get_linesize() + 6   # line height with a little extra spacing
infoScrollY     = 0     # current scroll offset in pixels (0 = top of text)
infoScrollSpeed = 40    # how many pixels to scroll per mouse-wheel tick
infoTotalH      = len(infoLines) * infoLineH   # total height of all text in pixels


# =============================================================================
# HELPER: setMusicVolume()
# Adjusts the music volume based on the current game state.
# Called whenever paused / showInfo / musicEnabled changes.
# =============================================================================
def setMusicVolume():
    if not musicEnabled:
        pygame.mixer.music.set_volume(0)          # completely silent
    elif paused or showInfo:
        pygame.mixer.music.set_volume(musicDimVol)    # quieter behind menus
    else:
        pygame.mixer.music.set_volume(musicNormalVol) # full volume during gameplay


def saveGame(slotIndex, slotName):
    """
    Serialise the current game state into saveSlots[slotIndex] and write the
    whole saveSlots list to saveslots.json.

    Parameters:
        slotIndex (int): 0, 1, or 2 which save slot to overwrite.
        slotName  (str): the display name to give this save (e.g. "Farm 1").
    """
    global saveSlots
    saveData = {
        "money"         : money,
        "days_passed"   : daysPassed,
        "grid"          : grid,
        "current_column": currentColumn,
        "current_row"   : currentRow,
        "sprite_x"      : spriteX,
        "sprite_y"      : spriteY,
        "tile_owned"    : tileOwned,
        "shed_slots"    : shedSlots,
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
        pass   # Silently skip saving if the file can't be written


def loadGame(slotIndex):
    """
    Restore game state from saveSlots[slotIndex].

    Returns True on success, False if the slot is empty or data is corrupt.
    """
    global money, daysPassed, grid
    global currentColumn, currentRow, spriteX, spriteY, lastMoveTime, tileOwned
    global shedSlots
    slot = saveSlots[slotIndex]
    if slot["data"] is None:
        return False   # slot is empty nothing to load
    try:
        data          = slot["data"]
        money         = data["money"]
        daysPassed    = data["days_passed"]
        grid          = data["grid"]
        currentColumn = data["current_column"]
        currentRow    = data["current_row"]
        spriteX       = data["sprite_x"]
        spriteY       = data["sprite_y"]
        lastMoveTime  = pygame.time.get_ticks()   # reset the timer so we don't skip a day immediately
        tileOwned     = data.get("tile_owned") or makeTileOwned()
        shedSlots     = data.get("shed_slots") or [None, None]
        return True
    except:
        return False   # data was malformed; fail gracefully


def newGame():
    """Reset all game-state variables to their starting values for a fresh game."""
    global money, daysPassed, grid
    global currentColumn, currentRow, spriteX, spriteY, lastMoveTime, tileOwned
    global shedSlots, heldPot, heldFruit
    money         = 6     # players start with very little money to encourage careful spending
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


# =============================================================================
# COORDINATE CONVERSION HELPERS
# The game renders to a virtual canvas (1920×1080) but the display window may
# be any size. These functions convert real screen pixel coordinates (from
# pygame mouse events) into virtual canvas coordinates for hit-testing.
# =============================================================================

def screenToVirtual(mx, my):
    """
    Convert a real-screen mouse position to a virtual-canvas pixel position.
    Uses letter-boxing logic (maintains aspect ratio) in windowed mode, or
    a simple proportional scale in fullscreen mode.
    """
    screenW, screenH = screen.get_size()
    if fullscreen:
        # In fullscreen the canvas fills the screen exactly (possibly stretched).
        vx = mx * virtualWidth  // screenW
        vy = my * virtualHeight // screenH
    else:
        # In windowed mode we keep the aspect ratio, so there may be black bars.
        # Find the largest uniform scale that fits in the window.
        scale   = min(screenW / virtualWidth, screenH / virtualHeight)
        # Calculate the offsets of the black bars.
        xOffset = (screenW - virtualWidth  * scale) / 2
        yOffset = (screenH - virtualHeight * scale) / 2
        # Subtract the bar offsets before dividing by scale.
        vx = int((mx - xOffset) / scale)
        vy = int((my - yOffset) / scale)
    return vx, vy

def screenToMenuRef(mx, my):
    """
    Same as screenToVirtual alias kept for clarity in menu-related code
    to make it obvious we are working in menu-reference (virtual) coordinates.
    """
    return screenToVirtual(mx, my)

def toggleFullscreen():
    """Switch between fullscreen and windowed mode, recreating the display surface."""
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((windowWidth, windowHeight), pygame.RESIZABLE)


# =============================================================================
# MENU DRAW HELPERS
# =============================================================================

def drawSideButton(surface, rect, label, hovered=False):
    """
    Draw a text-only side button (no background box the menu sprite handles
    the background). When hovered the label turns bright yellow with a dark
    drop-shadow; when not hovered it is plain brown/grey.

    Parameters:
        surface (pygame.Surface): the surface to draw onto.
        rect    (pygame.Rect)   : the button's bounding rectangle.
        label   (str)           : the text to show on the button.
        hovered (bool)          : True if the mouse is currently over the button.
    """
    if hovered:
        color = (255, 245, 190)   # warm bright yellow for the hovered state
        # Draw a dark drop-shadow in four diagonal directions for legibility.
        shadowSurf = buttonFont.render(label, False, (70, 40, 5))
        for ox, oy in ((-3, 3), (3, 3), (-3, -3), (3, -3)):
            sx = rect.x + (rect.w - shadowSurf.get_width())  // 2 + ox
            sy = rect.y + (rect.h - shadowSurf.get_height()) // 2 + oy
            surface.blit(shadowSurf, (sx, sy))
    else:
        color = (140, 110, 70)    # muted brown for the idle state
    textSurf = buttonFont.render(label, False, color)
    tx = rect.x + (rect.w - textSurf.get_width())  // 2   # centre horizontally
    ty = rect.y + (rect.h - textSurf.get_height()) // 2   # centre vertically
    surface.blit(textSurf, (tx, ty))


def buildMenuSurface(mouseVx=0, mouseVy=0):
    """
    (Re-)draw the pause / options menu onto menuSurface.
    Called every frame while paused=True so hover effects update in real time.

    Parameters:
        mouseVx, mouseVy (int): current mouse position in virtual coordinates,
                                 used to check which button is being hovered.
    """
    menuSurface.fill((0, 0, 0, 0))   # clear to fully transparent

    # Semi-transparent dark overlay so the game world behind is still faintly visible.
    overlay = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    menuSurface.blit(overlay, (0, 0))

    # Stretch the menu background sprite to fill the virtual canvas.
    menuSpriteScaled = pygame.transform.scale(menuSprite, (menuRefW, menuRefH))
    menuSurface.blit(menuSpriteScaled, (0, 0))

    # Draw the three save-slot buttons.
    for i in range(3):
        slotRect  = getSlotRect(i)
        isHovered = slotRect.collidepoint(mouseVx, mouseVy)
        hasSave   = saveSlots[i]["data"] is not None

        # Slightly lighter background when hovered to give a visual cue.
        bgColor     = (75, 55, 40)    if isHovered else (60, 40, 30)
        borderColor = (180, 150, 100) if isHovered else (100, 80, 60)
        pygame.draw.rect(menuSurface, bgColor,     slotRect)
        pygame.draw.rect(menuSurface, borderColor, slotRect, 2)

        # Clip to the slot area so text never overflows into adjacent slots.
        menuSurface.set_clip(pygame.Rect(slotRect.x+1, slotRect.y+1, slotRect.w-2, slotRect.h-2))
        if hasSave:
            # Show the save name, date, and time for filled slots.
            nameSurf = saveNameFont.render(saveSlots[i]["name"], False, (255, 255, 255))
            menuSurface.blit(nameSurf, (slotRect.x + 20, slotRect.y + 20))
            parts    = saveSlots[i]["date"].split(" ")
            dateStr  = parts[0][2:] if parts else ""        # "YY-MM-DD" (strip century)
            timeStr  = parts[1] if len(parts) > 1 else ""
            dateSurf = saveDateFont.render(dateStr, False, (180, 180, 180))
            timeSurf = saveDateFont.render(timeStr, False, (180, 180, 180))
            menuSurface.blit(dateSurf, (slotRect.x + 20, slotRect.y + 100))
            menuSurface.blit(timeSurf, (slotRect.x + 20, slotRect.y + 148))
        else:
            # Empty slot: show a placeholder label in a dimmer colour.
            nameSurf = saveNameFont.render(f"Empty Slot {i + 1}", False, (140, 120, 90))
            menuSurface.blit(nameSurf, (slotRect.x + 20, slotRect.y + 20))
        menuSurface.set_clip(None)   # remove the clipping region

    # Draw the close (X) button swap to the "clicked" sprite on hover.
    crossHovered = closeCrossRect.collidepoint(mouseVx, mouseVy)
    crossImg     = closeCrossClickImg if crossHovered else closeCrossImg
    menuSurface.blit(crossImg, (closeCrossX, closeCrossY))

    # Draw the four side buttons with hover detection.
    fsLabel    = "Windowed" if fullscreen else "Fullscreen"
    audioLabel = "Music: ON" if musicEnabled else "Music: OFF"
    drawSideButton(menuSurface, fullscreenBtnRect, fsLabel,    hovered=fullscreenBtnRect.collidepoint(mouseVx, mouseVy))
    drawSideButton(menuSurface, infoBtnRect,       "Info",     hovered=infoBtnRect.collidepoint(mouseVx, mouseVy))
    drawSideButton(menuSurface, quitBtnRect,       "Quit",     hovered=quitBtnRect.collidepoint(mouseVx, mouseVy))
    drawSideButton(menuSurface, audioBtnRect,      audioLabel, hovered=audioBtnRect.collidepoint(mouseVx, mouseVy))


def buildInfoSurface(mouseVx=0, mouseVy=0):
    """
    (Re-)draw the "How to Play" info / help screen onto infoSurface.
    Supports mouse-wheel scrolling via the infoScrollY variable.

    Parameters:
        mouseVx, mouseVy (int): current mouse position in virtual coordinates.
    """
    global infoScrollY
    infoSurface.fill((0, 0, 0, 0))   # clear to transparent

    # Same dark overlay and stretched menu background as the pause menu.
    overlay = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    overlay.fill((0, 0, 0, 180))
    infoSurface.blit(overlay, (0, 0))
    menuSpriteScaled = pygame.transform.scale(menuSprite, (menuRefW, menuRefH))
    infoSurface.blit(menuSpriteInfo, (0, 0))

    # Draw the "How to Play" title centred near the top.
    titleSurf = infoTitleFont.render("How to Play", False, (255, 240, 180))
    infoSurface.blit(titleSurf, ((virtualWidth - titleSurf.get_width()) // 2, infoTopY))

    # Clamp scroll so we never scroll past the beginning or end of the text.
    maxScroll   = max(0, infoTotalH - infoScrollH)
    infoScrollY = max(0, min(infoScrollY, maxScroll))

    # Clip rendering to the scroll region so text doesn't appear outside it.
    scrollClip = pygame.Rect(infoPadX, infoScrollTop, virtualWidth - infoPadX * 2, infoScrollH)
    infoSurface.set_clip(scrollClip)

    # Draw each line of text. The starting y is shifted upward by infoScrollY
    # so that scrolling down moves the text upward on screen.
    y = infoScrollTop - infoScrollY
    for line in infoLines:
        if line == "":
            y += infoLineH // 2   # blank lines get half-height spacing
            continue
        lineSurf = infoTextFont.render(line, False, (220, 200, 160))
        infoSurface.blit(lineSurf, (infoPadX, y))
        y += infoLineH

    infoSurface.set_clip(None)   # remove the clip before drawing fade overlays


    # Show "scroll up / scroll down" hints near the edges of the scroll region.
    if infoScrollY > 0:
        upSurf = infoTextFont.render("scroll up", False, (160, 130, 80))
        infoSurface.blit(upSurf, ((virtualWidth - upSurf.get_width()) // 2, infoScrollTop + 8))
    if infoScrollY < maxScroll:
        downSurf = infoTextFont.render("scroll down", False, (160, 130, 80))
        infoSurface.blit(downSurf, ((virtualWidth - downSurf.get_width()) // 2, infoScrollBottom - 52))

    # Draw the "Close" button at the bottom.
    drawSideButton(infoSurface, closeBtnRect, "Close", hovered=closeBtnRect.collidepoint(mouseVx, mouseVy))


# =============================================================================
# GAME LOGIC HELPERS
# =============================================================================

def potShopPrice(potType):
    """Return the coin cost to purchase a fermentation pot of the given type."""
    return fermPotLargePrice   # currently only "large" pots exist


def getFruitSellValue(cropName, fermented):
    """
    Return how many coins the player earns from selling one unit of a crop.

    Parameters:
        cropName (str) : e.g. "tomato", "carrot"
        fermented (bool): True if the crop was fermented before selling

    Returns:
        int: coin value
    """
    if fermented:
        return fermentData[cropName]["value"]   # higher fermented price
    return cropValues[cropName]                 # lower raw price


def isFermentDone(slot):
    """
    Check whether the crop in a shed slot has finished fermenting.

    A slot is considered done if:
      - Its "done" flag was already set True (checked on previous day ticks), OR
      - Enough days have passed since the crop was placed.

    Parameters:
        slot (dict | None): one element of shedSlots

    Returns:
        bool: True if fermentation is complete
    """
    if slot is None or slot.get("crop") is None:
        return False   # empty slot or no crop placed nothing to check
    if slot.get("done", False):
        return True    # already marked done on a previous tick
    daysRequired = fermentData[slot["crop"]]["days"]
    daysIn       = daysPassed - slot.get("day_placed", daysPassed)
    return daysIn >= daysRequired


def tickFermentation():
    """
    Called once per in-game day tick. Checks every shed slot and marks
    any crop whose fermentation time has elapsed as "done".
    """
    for slot in shedSlots:
        if slot is not None and slot.get("crop") is not None:
            if not slot.get("done", False):
                daysRequired = fermentData[slot["crop"]]["days"]
                daysIn       = daysPassed - slot.get("day_placed", daysPassed)
                if daysIn >= daysRequired:
                    slot["done"] = True   # fermentation complete!


# Apply the correct initial music volume before entering the main loop.
setMusicVolume()

# =============================================================================
# MAIN GAME LOOP
# Runs at ~60 FPS. Each iteration:
#   1. Processes input events
#   2. Advances the day timer if enough time has passed
#   3. Renders the world, UI, and cursors to the virtual canvas
#   4. Scales the canvas to the real display and flips the buffer
# =============================================================================
running = True
while running:
    clock.tick(fps)   # cap to target FPS

    # Advance rain animation frame
    if isRainingToday() and not paused and not showInfo:
        now_ms = pygame.time.get_ticks()
        if now_ms - rainLastFrameTime >= RAIN_FRAME_MS:
            rainLastFrameTime = now_ms
            rainFrameIndex = (rainFrameIndex + 1) % len(RAIN_FRAMES)

    # Get the current mouse position and convert to virtual coordinates.
    # We use these for hover-detection on menu buttons every frame.
    mx, my           = pygame.mouse.get_pos()
    hoverVx, hoverVy = screenToMenuRef(mx, my)

    # =========================================================================
    # EVENT HANDLING
    # =========================================================================
    for event in pygame.event.get():

        # --- Window close button ---
        if event.type == pygame.QUIT:
            running = False

        # --- Keyboard ---
        if event.type == pygame.KEYDOWN:

            if showInfo:
                # While the info screen is open, ESC goes back to the pause menu.
                if event.key == pygame.K_ESCAPE:
                    showInfo = False
                    paused   = True
                    setMusicVolume()

            elif paused:
                # While paused, ESC resumes the game.
                if event.key == pygame.K_ESCAPE:
                    paused       = False
                    lastMoveTime = pygame.time.get_ticks()   # don't count paused time
                    setMusicVolume()

            else:
                # During gameplay, ESC cancels whatever the player is holding,
                # or opens the pause menu if hands are empty.
                if event.key == pygame.K_ESCAPE:
                    if selectedSeed is not None:
                        money += cropPrice[selectedSeed]   # refund the seed cost
                        selectedSeed = None
                    elif wateringCanHeld:
                        wateringCanHeld = False
                    elif heldPot is not None:
                        money  += potShopPrice(heldPot)    # refund the pot cost
                        heldPot = None
                    elif heldFruit is not None:
                        pass   # you cannot drop fruit you must sell or ferment it
                    else:
                        paused = True
                        setMusicVolume()

                if event.key == pygame.K_F11:
                    toggleFullscreen()

        # --- Mouse wheel: scroll the info screen ---
        if event.type == pygame.MOUSEWHEEL and showInfo:
            infoScrollY -= event.y * infoScrollSpeed   # negative because scroll up = move text up

        # --- Window resize (windowed mode only) ---
        if event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # =====================================================================
        # LEFT MOUSE BUTTON CLICK
        # =====================================================================
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            rx, ry = screenToMenuRef(mx, my)   # menu/virtual coordinates

            # --- Info screen intercepts all clicks ---
            if showInfo:
                if closeBtnRect.collidepoint(rx, ry):
                    showInfo = False
                    paused   = True
                    setMusicVolume()
                continue   # don't process game-world clicks while info is open

            # --- Pause menu intercepts all clicks ---
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
                    infoScrollY = 0   # always start the info screen scrolled to the top
                    setMusicVolume()
                    continue
                if quitBtnRect.collidepoint(rx, ry):
                    running = False
                    continue
                if audioBtnRect.collidepoint(rx, ry):
                    musicEnabled = not musicEnabled
                    setMusicVolume()
                    continue
                # Save slot clicked: load existing save or start new game.
                for i in range(3):
                    if getSlotRect(i).collidepoint(rx, ry):
                        if saveSlots[i]["data"] is not None:
                            loadGame(i)
                        else:
                            newGame()
                        paused = False
                        setMusicVolume()
                        break
                continue   # done with paused-state clicks

            # For all game-world clicks, convert to virtual coordinates.
            vx, vy = screenToVirtual(mx, my)

            # --- Player is holding a fruit (harvested or fermented) ---
            if heldFruit is not None:
                # Clicking the sell chest sells the fruit immediately.
                if shopChestRect.collidepoint(vx, vy):
                    money    += getFruitSellValue(heldFruit["crop"], heldFruit["fermented"])
                    heldFruit = None
                    continue
                # Clicking a shed slot places the raw fruit into a pot for fermenting.
                for slotIdx, slotRect in enumerate(shedSlotRects):
                    if slotRect.collidepoint(vx, vy):
                        slot = shedSlots[slotIdx]
                        # Can only place un-fermented fruit into an occupied (pot present) empty slot.
                        if slot is not None and slot.get("crop") is None and not heldFruit["fermented"]:
                            slot["crop"]       = heldFruit["crop"]
                            slot["day_placed"] = daysPassed
                            slot["done"]       = False
                            heldFruit = None
                        break
                continue

            # --- Player is carrying a fermentation pot ---
            if heldPot is not None:
                # Clicking an empty shed slot places the pot there.
                for slotIdx, slotRect in enumerate(shedSlotRects):
                    if slotRect.collidepoint(vx, vy) and shedSlots[slotIdx] is None:
                        shedSlots[slotIdx] = {"pot": heldPot, "crop": None, "day_placed": None, "done": False}
                        heldPot = None
                        break
                continue

            # --- Watering can refill ---
            # Clicking the water source (when not carrying a seed) picks up the full can.
            if waterRefillRect.collidepoint(vx, vy) and not selectedSeed:
                wateringCanHeld = True
                wateringCanFull = True
                continue

            # --- Watering can: drop if clicking outside the grid ---
            if wateringCanHeld:
                gx = (vx - gridStartX) // cellSize
                gy = (vy - gridStartY) // cellSize
                if not (0 <= gx < gridCols and 0 <= gy < gridRows):
                    wateringCanHeld = False
                    continue

            # --- Pick up finished fermented fruit from a shed pot ---
            if not wateringCanHeld and selectedSeed is None and heldPot is None and heldFruit is None:
                for slotIdx, slotRect in enumerate(shedSlotRects):
                    if slotRect.collidepoint(vx, vy):
                        slot = shedSlots[slotIdx]
                        if slot is not None and isFermentDone(slot):
                            # Pick up the fermented product.
                            heldFruit          = {"crop": slot["crop"], "fermented": True}
                            # Clear the pot so it can accept a new crop.
                            slot["crop"]       = None
                            slot["day_placed"] = None
                            slot["done"]       = False
                        break

            # --- Buy a fermentation pot from the shop shelf ---
            if not wateringCanHeld and selectedSeed is None and heldPot is None and heldFruit is None:
                if fermPotLargeRect.collidepoint(vx, vy):
                    if money >= fermPotLargePrice:
                        money  -= fermPotLargePrice
                        heldPot = "large"   # player is now carrying the pot
                    continue

            # --- Check if a seed bag was clicked ---
            clickedSeed = None
            if not wateringCanHeld and heldPot is None and heldFruit is None:
                for cropName, rect in seedRects.items():
                    if rect.collidepoint(vx, vy):
                        clickedSeed = cropName
                        break

            # --- Buy a locked tile ---
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

            # --- Purchase a seed and pick it up ---
            if clickedSeed and selectedSeed is None:
                if money >= cropPrice[clickedSeed]:
                    money -= cropPrice[clickedSeed]
                    selectedSeed = clickedSeed
                continue

            # --- Plant the selected seed on a grid tile ---
            if selectedSeed is not None:
                gx = (vx - gridStartX) // cellSize
                gy = (vy - gridStartY) // cellSize
                if 0 <= gx < gridCols and 0 <= gy < gridRows:
                    # Only plant on owned, empty tiles.
                    if grid[gx][gy] is None and tileOwned[gx][gy]:
                        grid[gx][gy] = {
                            "crop"        : selectedSeed,
                            "day_planted" : daysPassed,
                            "stage"       : 0,
                            "watered"     : False,
                            "watered_days": 0,
                            "dayRipe" : None,
                            "dead" : False,
                        }
                        selectedSeed = None   # seed has been planted; hand is empty
                continue

            # --- Water a plant with the watering can ---
            if wateringCanHeld and wateringCanFull:
                gx = (vx - gridStartX) // cellSize
                gy = (vy - gridStartY) // cellSize
                if 0 <= gx < gridCols and 0 <= gy < gridRows:
                    cell = grid[gx][gy]
                    if cell is not None:    # only continue if clicked tile contains plant
                        plantState(cell)    # ensure plant has all required fields
                        if not cell["watered"] and not cell["dead"]:  # deads plants cant be watered
                            cell["watered"] = True    # mark this plant as watered today
                            wateringCanFull = False   # can is now empty; must refill

        # =====================================================================
        # RIGHT MOUSE BUTTON CLICK
        # =====================================================================
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            rx, ry = screenToMenuRef(mx, my)

            if paused and not showInfo:
                # Right-clicking a save slot while paused saves the game there.
                for i in range(3):
                    if getSlotRect(i).collidepoint(rx, ry):
                        saveGame(i, f"Farm {i + 1}")
                        break

            elif not paused and not showInfo:
                vx, vy = screenToVirtual(mx, my)

                # Right-clicking while holding a fermented fruit: put it back in a pot.
                if heldFruit is not None:
                    if heldFruit["fermented"]:
                        for slot in shedSlots:
                            if slot is not None and slot.get("crop") is None:
                                slot["crop"]       = heldFruit["crop"]
                                slot["day_placed"] = daysPassed
                                slot["done"]       = True   # already fermented; mark done
                                heldFruit = None
                                break
                    continue

                # Right-clicking while holding a seed: refund and put it down.
                if selectedSeed is not None:
                    money += cropPrice[selectedSeed]
                    selectedSeed = None
                    continue

                # Right-clicking while holding a pot: refund and put it down.
                if heldPot is not None:
                    money  += potShopPrice(heldPot)
                    heldPot = None
                    continue

                # Right-clicking a fully grown plant: harvest it.
                gx        = (vx - gridStartX) // cellSize
                gy        = (vy - gridStartY) // cellSize
                harvestResult = harvestDead(grid, gx, gy, crops)    # let death-system judge what happens
                if harvestResult:
                    if harvestResult["type"] == "dead_refund":
                        money += getDeadPlantRefund(harvestResult["crop"])  #dead plant give refund instead of cropvalue
                    elif harvestResult["type"] == "fruit":  # otherwise give normal cropvalue
                        heldFruit = {"crop": harvestResult["crop"], "fermented": False}

    # =========================================================================
    # DAY TICK
    # Every moveInterval milliseconds (currently 5 seconds) one in-game day
    # passes. We update crop growth, advance the calendar marker, and tick
    # fermentation.
    # =========================================================================
    if not paused and not showInfo:
        now = pygame.time.get_ticks()
        if now - lastMoveTime >= moveInterval:
            lastMoveTime = now
            daysPassed  += 1

            # Refresh rain schedule at the start of each 12-day cycle
            cycleIndex = daysPassed // 12
            if cycleIndex != rainCurrentCycle:
                rainCurrentCycle = cycleIndex
                rainDaysInCycle = getRainDaysForCycle()

            # Rain auto-waters all the plants
            if isRainingToday():
                for x in range(gridCols):
                    for y in range(gridRows):
                        if grid[x][y] is not None:
                            grid[x][y]["watered"] = True

            # Update every planted crop: increment watered_days if watered,
            # then reset the "watered today" flag for the new day.
            for x in range(gridCols):
                for y in range(gridRows):
                    cell = grid[x][y]
                    if not cell:
                        continue

                    plantState(cell)   # ensure older save data also has new death-systme field

                    if cell["dead"]:        # dead pplants remain dead and don't grow
                        cell["watered"] = False # reset water  boolean
                        continue

                    if cell.get("watered", False): # if watered increase counter
                        cell["watered_days"] = cell.get("watered_days", 0) + 1

                    cell["watered"] = False   # reset; must water again tomorrow
                    crop        = crops[cell["crop"]]
                    wateredDays = cell.get("watered_days", 0)
                    # Advance stage based on total watered days, capped at max.
                    stage       = wateredDays // crop["growth_days_per_stage"]
                    cell["stage"] = min(stage, crop["max_stage"])

                    #check if plant = ripe
                    if cell["stage"] >= crop["max_stage"]:  #if crop ripe track how long its ripe
                        if cell["dayRipe"] is None: # if this is the first ripe day store the day
                            cell["dayRipe"] = daysPassed

                        elif daysPassed - cell["dayRipe"] >= ripeDays:    # if plant stays too long mark it dead
                            cell["dead"] = True
                    else:                   # if the plant is no longer considered ripe clear ripe day
                        cell["dayRipe"] = None

            # Check fermentation pots and mark any finished crops.
            tickFermentation()

            # Move the calendar circle marker one step along its 4×3 path.
            spriteX       += step
            currentColumn += 1
            if currentColumn >= columns:
                currentColumn = 0
                spriteX       = startX
                spriteY      += step
                currentRow   += 1
                if currentRow >= rows:
                    # Completed a full calendar cycle wrap back to the start.
                    currentRow       = 0
                    spriteX, spriteY = startX, startY

    # =========================================================================
    # RENDERING
    # All drawing goes onto "target" (the virtual canvas) first, then "target"
    # is scaled to the real display size and blitted once per frame.
    # =========================================================================
    screenW, screenH = screen.get_size()
    target = pygame.Surface((virtualWidth, virtualHeight))

    # --- Background and shop furniture ---
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

    # --- Shed pots: draw ferment contents first, then the pot on top ---
    # We draw ferment contents behind the pot sprite so they look like they're
    # sitting inside the pot rather than floating above it.
    shedPositions = [shedSlotTop, shedSlotBottom]
    for slotIdx, slotPos in enumerate(shedPositions):
        slot = shedSlots[slotIdx]
        if slot is None:
            continue   # no pot placed in this slot; skip it
        if slot.get("crop") is not None:
            # Draw the ferment-fruit icon slightly inset so it looks inside the pot.
            fermImg = fermentImages[slot["crop"]]
            target.blit(fermImg, (slotPos[0] + fermentOffsetX, slotPos[1] + fermentOffsetY))
        # Draw the pot sprite on top of the fruit (pot rim covers the fruit edges).
        target.blit(shedPotImg, slotPos)
        # If fermentation is complete, draw a sparkle over the pot.
        if slot.get("crop") is not None and isFermentDone(slot):
            target.blit(doneSparkleImg, slotPos)

    target.blit(shedDoorImg, (shedDoorX, shedDoorY))
    drawMoney(target, money, virtualWidth)

    # --- Draw planted crops on the farm grid ---
    for x in range(gridCols):
        for y in range(gridRows):
            cell = grid[x][y]
            if cell:
                plantState(cell)    # ensure the cell contains all keys
                crop   = crops[cell["crop"]]    #look up crop data for plant

                if cell["dead"]:        #choose correct sprite - dead foor deadsprite, moral stage sprite for living
                    sprite = crop["death_sprite"]
                else:
                    sprite = crop["stages"][cell["stage"]]
                # Scale the crop sprite to exactly fill one grid cell if needed.
                if sprite.get_width() != cellSize or sprite.get_height() != cellSize:
                    sprite = pygame.transform.scale(sprite, (cellSize, cellSize))
                target.blit(sprite, (gridStartX + x * cellSize, gridStartY + y * cellSize))

    # --- Draw locked (for-sale) tile overlays ---
    vMouseX, vMouseY  = screenToVirtual(*pygame.mouse.get_pos())
    hoveredLockedTile = None   # track which locked tile (if any) the mouse is over for the tooltip
    tekoopScaled      = pygame.transform.scale(tekoopTileImg, (cellSize, cellSize))
    for x in range(gridCols):
        for y in range(gridRows):
            if not tileOwned[x][y]:
                tx = gridStartX + x * cellSize
                ty = gridStartY + y * cellSize
                target.blit(tekoopScaled, (tx, ty))
                tileRect = pygame.Rect(tx, ty, cellSize, cellSize)
                if tileRect.collidepoint(vMouseX, vMouseY) and not paused and not showInfo:
                    hoveredLockedTile = (x, y)   # remember for tooltip below

    # --- Calendar: background sprite and the moving day-marker circle ---
    target.blit(calendarSprite, (176*8, 72*8))   # 1408, 576
    target.blit(calendarCircle, (spriteX, spriteY))

    # --- Draw watered-today indicator droplets on watered tiles ---
    for x in range(gridCols):
        for y in range(gridRows):
            cell = grid[x][y]
            if cell and cell.get("watered", False):
                druppel = pygame.transform.scale(waterDropImg, (cellSize, cellSize))
                target.blit(druppel, (gridStartX + x * cellSize, gridStartY + y * cellSize))

    # =========================================================================
    # CURSOR DRAWING
    # The system cursor is hidden while the player is holding something.
    # We draw a custom sprite at the mouse position instead.
    # =========================================================================
    if heldFruit is not None:
        # Show the fruit or fermented-fruit icon at the mouse cursor.
        cursorImg    = fermentImages[heldFruit["crop"]] if heldFruit["fermented"] else fruitImages[heldFruit["crop"]]
        cursorScaled = pygame.transform.scale(cursorImg, (fruitCursorSize, fruitCursorSize))
        target.blit(cursorScaled, (vMouseX - cursorScaled.get_width()  // 2,
                                   vMouseY - cursorScaled.get_height() // 2))
        pygame.mouse.set_visible(False)

    elif heldPot is not None:
        # Show the fermentation pot sprite at the cursor (full size).
        potScaled = pygame.transform.scale(fermPotLargeImg,
                                           (fermPotLargeImg.get_width(), fermPotLargeImg.get_height()))
        target.blit(potScaled, (vMouseX - potScaled.get_width()  // 2,
                                vMouseY - potScaled.get_height() // 2))
        pygame.mouse.set_visible(False)

    elif selectedSeed is not None:
        # Show the seed bag at half a cell size at the cursor.
        cursorScaled = pygame.transform.scale(seedBagImages[selectedSeed], (cellSize // 2, cellSize // 2))
        target.blit(cursorScaled, (vMouseX - cursorScaled.get_width()  // 2,
                                   vMouseY - cursorScaled.get_height() // 2))
        pygame.mouse.set_visible(False)

    elif wateringCanHeld:
        # Show the correct watering can (full or empty) at the cursor.
        canImg = wateringCanFullImg if wateringCanFull else wateringCanEmptyImg
        canScaled = pygame.transform.scale(canImg, (cellSize // 2, cellSize // 2))
        target.blit(canScaled, (vMouseX - canScaled.get_width() // 2,
                                vMouseY - canScaled.get_height() // 2))
        pygame.mouse.set_visible(False)

    else:
        # Nothing held show the normal OS mouse cursor.
        pygame.mouse.set_visible(True)

    # --- Draw rain overlay ---
    if isRainingToday() and not paused and not showInfo:
        rainSprite = pygame.transform.scale(RAIN_FRAMES[rainFrameIndex], (virtualWidth, virtualHeight))
        target.blit(rainSprite, (0, 0))

    # =========================================================================
    # TOOLTIPS
    # =========================================================================
        # Small pop-up labels that appear near the mouse when hovering over
        # interactive objects, showing their name and price.

    def drawTooltip(surface, text, cx, cy):
        """
               Draw a small rounded tooltip box with the given text.

               Parameters:
                   surface (pygame.Surface): canvas to draw on.
                   text    (str)           : the text to display.
                   cx      (int)           : desired horizontal centre of the tooltip.
                   cy      (int)           : Y position of the bottom edge of the tooltip.
               """

        tooltipSurf = saveDateFont.render(text, True, (255, 240, 160))
        padX, padY = 16, 10
        tooltipBg = pygame.Surface((tooltipSurf.get_width() + padX * 2,
                                    tooltipSurf.get_height() + padY * 2), pygame.SRCALPHA)
        tooltipBg.fill((30, 20, 10, 210)) # dark semi-transparent background
        # Clamp so the tooltip never goes off the left or right edge.
        tx = max(0, min(cx - tooltipBg.get_width() // 2, virtualWidth - tooltipBg.get_width()))
        ty = max(0, cy - tooltipBg.get_height() - 8)
        surface.blit(tooltipBg, (tx, ty))
        surface.blit(tooltipSurf, (tx + padX, ty + padY))


    # Tooltip: locked tile purchase price.
    if hoveredLockedTile is not None:
        hx, hy = hoveredLockedTile
        drawTooltip(target, f"Buy: {tileColPrice[hx]} coins",
                    gridStartX + hx * cellSize + cellSize // 2,
                    gridStartY + hy * cellSize)

    # Tooltip: seed bag price.
    if not paused and not showInfo:
        for cropName, rect in seedRects.items():
            if rect.collidepoint(vMouseX, vMouseY):
                drawTooltip(target, f"{cropName.capitalize()}: {cropPrice[cropName]} coins",
                            rect.centerx, rect.top)
                break

    # Tooltip: fermentation pot price.
    if not paused and not showInfo and heldPot is None and selectedSeed is None and not wateringCanHeld and heldFruit is None:
        if fermPotLargeRect.collidepoint(vMouseX, vMouseY):
            drawTooltip(target, f"Large pot: {fermPotLargePrice} coins",
                        fermPotLargeRect.centerx, fermPotLargeRect.top)

    # Tooltip: sell-chest value for the fruit being held.
    if not paused and not showInfo and heldFruit is not None:
        if shopChestRect.collidepoint(vMouseX, vMouseY):
            val    = getFruitSellValue(heldFruit["crop"], heldFruit["fermented"])
            suffix = " (fermented)" if heldFruit["fermented"] else ""
            drawTooltip(target, f"Sell {heldFruit['crop'].capitalize()}{suffix}: {val} coins",
                        shopChestRect.centerx, shopChestRect.top)

    # Tooltip: fermentation pot status (time remaining / ready).
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

    # =========================================================================
    # OVERLAY MENUS (drawn last so they appear on top of everything)
    # =========================================================================
    if showInfo:
        pygame.mouse.set_visible(True)
        buildInfoSurface(hoverVx, hoverVy)
        target.blit(infoSurface, (0, 0))
    elif paused:
        pygame.mouse.set_visible(True)
        buildMenuSurface(hoverVx, hoverVy)
        target.blit(menuSurface, (0, 0))

    # =========================================================================
    # SCALE & DISPLAY
    # Scale the virtual canvas to fit the real window (preserving aspect ratio),
    # centre it on a black background, and flip the display buffer.
    # =========================================================================
    scale   = min(screenW / virtualWidth, screenH / virtualHeight)
    scaledW = int(virtualWidth  * scale)
    scaledH = int(virtualHeight * scale)
    scaled  = pygame.transform.scale(target, (scaledW, scaledH))
    screen.fill((0, 0, 0))   # fill with black so letterbox bars are black
    screen.blit(scaled, ((screenW - scaledW) // 2, (screenH - scaledH) // 2))
    pygame.display.flip()   # swap the back buffer to the screen

# Cleanly shut down pygame and exit Python when the main loop ends.
pygame.quit()
sys.exit()