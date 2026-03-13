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
from datetime import datetime
import random
from death_proces import plantState, getDeadPlantRefund, harvestDead, ripeDays

# Initialise all pygame modules (display, audio, event system, etc.).
pygame.init()
pygame.mixer.init()

# =============================================================================
# VIRTUAL CANVAS SIZE
# =============================================================================
virtualWidth  = 1920
virtualHeight = 1080
fps           = 60

windowWidth   = 960
windowHeight  = 540

menuRefW = virtualWidth
menuRefH = virtualHeight

# =============================================================================
# DISPLAY SETUP
# =============================================================================
fullscreen = True
info   = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("FermFarm")

clock = pygame.time.Clock()

runStartScreen(screen, fullscreen)

# =============================================================================
# MUSIC SETTINGS
# =============================================================================
musicNormalVol = 0.5
musicDimVol    = 0.2
musicEnabled   = True

# =============================================================================
# ASSET LOADING
# =============================================================================
textures = loadTextures()
initMoneyUi(textures)
crops    = loadCrops(textures)

tekoopTileImg = textures["tekoopTile"]

# =============================================================================
# OFF-SCREEN SURFACES
# =============================================================================
menuSurface = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)
infoSurface = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)

# =============================================================================
# FONTS
# =============================================================================
fontPath = "sprites/babosorry.ttf"
if not os.path.exists(fontPath):
    fontPath = None

saveNameFont  = pygame.font.Font(fontPath, 60)
saveDateFont  = pygame.font.Font(fontPath, 36)
buttonFont    = pygame.font.Font(fontPath, 96)
infoTextFont  = pygame.font.Font(fontPath, 44)
infoTitleFont = pygame.font.Font(fontPath, 72)

# =============================================================================
# SPRITE POSITIONS
# =============================================================================

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

menuSprite         = textures["menuSprite"]
menuSpriteInfo     = textures["menuSpriteInfo"]
closeCrossImg      = textures["closeCross"]
closeCrossClickImg = textures["closeCrossClick"]
doneSparkleImg     = textures["doneSparkle"]

closeCrossX = 1392
closeCrossY = 96

# =============================================================================
# FRUIT & FERMENTED FRUIT TEXTURE LOOKUP TABLES
# =============================================================================

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

# The finished kimchi icon.
kimchiFinishedImg = textures["kichiFerment"]

# =============================================================================
# KIMCHI CONSTANTS
# A pot switches to kimchi mode the moment a second raw fruit is dropped into
# it. All 6 crops must be placed on the SAME game-day — if the day ticks over
# before the recipe is complete the pot resets and the crops are lost.
# The different growth times for each crop (garlic = 5 stages, tomato = 4,
# etc.) make it genuinely hard to get all 6 ripe on the same day.
# =============================================================================
KIMCHI_CROPS        = {"tomato", "carrot", "cucumber", "chili", "cabbage", "garlic"}
KIMCHI_VALUE        = 250   # coins for selling finished kimchi
KIMCHI_FERMENT_DAYS = 4     # days to ferment once all 6 crops are in

# =============================================================================
# FERMENTATION POT STATE
# =============================================================================

shedPotImg = textures["shedPot"]

fermPotLargeRect  = pygame.Rect(fermPotLargeX, fermPotLargeY,
                                fermPotLargeImg.get_width(), fermPotLargeImg.get_height())
fermPotLargePrice = 30

# Where the two shed pots are DRAWN on screen.
shedSlotTop    = (440, 280)
shedSlotBottom = (464, 360)

# Each shed slot dict has these keys for NORMAL fermentation:
#   pot, crop, day_placed, done
#
# When kimchi mode is active, extra keys are added:
#   mode             = "kimchi"
#   kimchi_crops     : set of crop names placed so far
#   kimchi_batch_day : daysPassed when the first crop was dropped (same-day check)
#   kimchi_fermenting: True once all 6 crops are in
#   kimchi_day_started: daysPassed when fermenting began
shedSlots = [None, None]

fermentOffsetX = 17
fermentOffsetY = 25

heldPot   = None
heldFruit = None

fruitCursorSize = 48

shedSlotRects = [
    pygame.Rect(456, 336, 40, 40),
    pygame.Rect(480, 416, 40, 40),
]

shopChestRect  = pygame.Rect(shopChestX, shopChestY,
                             shopChestImg.get_width(), shopChestImg.get_height())
closeCrossRect = pygame.Rect(closeCrossX, closeCrossY,
                             closeCrossImg.get_width(), closeCrossImg.get_height())

# =============================================================================
# SEED BAG CLICK RECTS
# =============================================================================
seedRects = {
    "carrot"  : pygame.Rect(carrotBagX,   carrotBagY,   carrotBagImg.get_width(),   carrotBagImg.get_height()),
    "tomato"  : pygame.Rect(tomatoBagX,   tomatoBagY,   tomatoBagImg.get_width(),   tomatoBagImg.get_height()),
    "chili"   : pygame.Rect(chiliBagX,    chiliBagY,    chiliBagImg.get_width(),    chiliBagImg.get_height()),
    "cucumber": pygame.Rect(cucumberBagX, cucumberBagY, cucumberBagImg.get_width(), cucumberBagImg.get_height()),
    "cabbage" : pygame.Rect(cabbageBagX,  cabbageBagY,  cabbageBagImg.get_width(),  cabbageBagImg.get_height()),
    "garlic"  : pygame.Rect(garlicBagX,   garlicBagY,   garlicBagImg.get_width(),   garlicBagImg.get_height()),
}

selectedSeed = None

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

wateringCanFull  = False
wateringCanHeld  = False

waterRefillRect      = pygame.Rect(887, 416, 90, 90)
wateringCanWorldRect = pygame.Rect(887, 326, 90, 90)

# =============================================================================
# RAIN SYSTEM
# =============================================================================
RAIN_FRAMES       = [textures["rainBackground1"], textures["rainBackground2"],
                     textures["rainBackground3"], textures["rainBackground4"],
                     textures["rainBackground5"]]
RAIN_FRAME_MS     = 120
rainDaysInCycle   = set()
rainCurrentCycle  = -1
rainFrameIndex    = 0
rainLastFrameTime = 0

def getRainDaysForCycle():
    return set(random.sample(range(12), 2))

def isRainingToday():
    return (daysPassed % 12) in rainDaysInCycle

# =============================================================================
# TV WEATHER FORECAST
# =============================================================================
rainForecastImg = textures["weatherReport1"]
sunForecastImg  = textures["weatherReport2"]
tvX, tvY        = 141 * 8, 33 * 8
tvRect          = pygame.Rect(tvX, tvY, 30 * 8, 17 * 8)
tvOn            = False

# =============================================================================
# GOLD WATER BUCKET
# =============================================================================
goldWaterBucketEmptyImg = textures["goldWaterBucket"]
goldWaterBucketFullImg  = textures["goldWaterBucketFill"]
goldWaterBucketShop     = textures["goldWaterBucketShop"]
goldWaterBucketImg      = textures["goldWaterBucketFill"]

goldWaterBucketPrice    = 300
goldWaterBucketMax      = 10

hasGoldWaterBucket      = False
goldWaterBucketHeld     = False
goldWaterBucketUsesLeft = 0

goldWaterBucketx    = 1488
goldWaterBuckety    = 328
goldWaterBucketRect = pygame.Rect(
    goldWaterBucketx,
    goldWaterBuckety,
    goldWaterBucketEmptyImg.get_width(),
    goldWaterBucketEmptyImg.get_height()
)

# =============================================================================
# CORE GAME STATE
# =============================================================================
money          = 600
background     = textures["background"]
calendarSprite = textures["calendar"]
calendarCircle = textures["calendarCircle"]

cellSize   = 128
gridCols   = 7
gridRows   = 3
gridStartX = 0
gridStartY = 696

grid = [[None for _ in range(gridRows)] for _ in range(gridCols)]

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
    owned = [[False for _ in range(gridRows)] for _ in range(gridCols)]
    for col in [5, 6]:
        for row in [0, 1]:
            owned[col][row] = True
    return owned

tileOwned = makeTileOwned()

startX, startY   = 1400, 696
spriteX, spriteY = startX, startY
step          = 128
columns       = 4
rows          = 3
currentColumn = 0
currentRow    = 0

moveInterval = 5_000
lastMoveTime = pygame.time.get_ticks()
daysPassed   = 0

paused   = False
showInfo = True

# =============================================================================
# SAVE / LOAD SYSTEM
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
        pass

# =============================================================================
# PAUSE MENU UI LAYOUT
# =============================================================================
slotWidth   = 400
slotHeight  = 200
slotSpacing = 25

slotStartX  = (virtualWidth  - slotWidth)  // 3.5
slotStartY  = (virtualHeight - (3 * slotHeight + 2 * slotSpacing)) // 2.5
slotBottomY = slotStartY + 3 * slotHeight + 2 * slotSpacing

def getSlotRect(i):
    sy = slotStartY + i * (slotHeight + slotSpacing)
    return pygame.Rect(slotStartX, sy, slotWidth, slotHeight)

sideBtnW = 380
sideBtnX = int(slotStartX) + slotWidth + 100

totalBtnArea = slotBottomY - slotStartY
btnSpacing   = 20
btnH4        = (totalBtnArea - 3 * btnSpacing) // 4

fullscreenBtnRect = pygame.Rect(sideBtnX, int(slotStartY),                            sideBtnW, btnH4)
infoBtnRect       = pygame.Rect(sideBtnX, int(slotStartY + 1 * (btnH4 + btnSpacing)), sideBtnW, btnH4)
audioBtnRect      = pygame.Rect(sideBtnX, int(slotStartY + 2 * (btnH4 + btnSpacing)), sideBtnW, btnH4)
quitBtnRect       = pygame.Rect(sideBtnX, int(slotStartY + 3 * (btnH4 + btnSpacing)), sideBtnW, btnH4)

# =============================================================================
# INFO / HOW-TO-PLAY SCREEN
# =============================================================================
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
infoScrollY     = 0
infoScrollSpeed = 40
infoTotalH      = len(infoLines) * infoLineH


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def setMusicVolume():
    if not musicEnabled:
        pygame.mixer.music.set_volume(0)
    elif paused or showInfo:
        pygame.mixer.music.set_volume(musicDimVol)
    else:
        pygame.mixer.music.set_volume(musicNormalVol)


def saveGame(slotIndex, slotName):
    global saveSlots
    # kimchi_crops is a set — must convert to list for JSON serialization.
    def serializeSlot(slot):
        if slot is None:
            return None
        s = dict(slot)
        if "kimchi_crops" in s and isinstance(s["kimchi_crops"], set):
            s["kimchi_crops"] = list(s["kimchi_crops"])
        return s
    saveData = {
        "money"          : money,
        "days_passed"    : daysPassed,
        "grid"           : grid,
        "current_column" : currentColumn,
        "current_row"    : currentRow,
        "sprite_x"       : spriteX,
        "sprite_y"       : spriteY,
        "tile_owned"     : tileOwned,
        "shed_slots"     : [serializeSlot(s) for s in shedSlots],
        "has_gold_water_bucket"      : hasGoldWaterBucket,
        "gold_water_bucket_held"     : goldWaterBucketHeld,
        "gold_water_bucket_uses_left": goldWaterBucketUsesLeft,
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
    global money, daysPassed, grid
    global currentColumn, currentRow, spriteX, spriteY, lastMoveTime, tileOwned
    global shedSlots
    global hasGoldWaterBucket, goldWaterBucketHeld, goldWaterBucketUsesLeft
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
        rawSlots      = data.get("shed_slots") or [None, None]
        # Restore kimchi_crops as a set (was serialized as a list).
        shedSlots = []
        for s in rawSlots:
            if s is not None and "kimchi_crops" in s:
                s["kimchi_crops"] = set(s["kimchi_crops"])
            shedSlots.append(s)
        hasGoldWaterBucket      = data.get("has_gold_water_bucket", False)
        goldWaterBucketHeld     = data.get("gold_water_bucket_held", False)
        goldWaterBucketUsesLeft = data.get("gold_water_bucket_uses_left", 0)
        return True
    except:
        return False


def newGame():
    global money, daysPassed, grid
    global currentColumn, currentRow, spriteX, spriteY, lastMoveTime, tileOwned
    global shedSlots, heldPot, heldFruit
    global hasGoldWaterBucket, goldWaterBucketHeld, goldWaterBucketUsesLeft
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


def screenToVirtual(mx, my):
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
    return screenToVirtual(mx, my)

def toggleFullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((windowWidth, windowHeight), pygame.RESIZABLE)


def drawSideButton(surface, rect, label, hovered=False):
    if hovered:
        color = (255, 245, 190)
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
    menuSurface.fill((0, 0, 0, 0))
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
    global infoScrollY
    infoSurface.fill((0, 0, 0, 0))
    overlay = pygame.Surface((menuRefW, menuRefH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    infoSurface.blit(overlay, (0, 0))
    infoSurface.blit(menuSpriteInfo, (0, 0))

    titleSurf = infoTitleFont.render("How to Play", False, (255, 240, 180))
    infoSurface.blit(titleSurf, ((virtualWidth - titleSurf.get_width()) // 2, infoTopY))

    maxScroll   = max(0, infoTotalH - infoScrollH)
    infoScrollY = max(0, min(infoScrollY, maxScroll))

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

    if infoScrollY > 0:
        upSurf = infoTextFont.render("scroll up", False, (160, 130, 80))
        infoSurface.blit(upSurf, ((virtualWidth - upSurf.get_width()) // 2, infoScrollTop + 8))
    if infoScrollY < maxScroll:
        downSurf = infoTextFont.render("scroll down", False, (160, 130, 80))
        infoSurface.blit(downSurf, ((virtualWidth - downSurf.get_width()) // 2, infoScrollBottom - 52))

    drawSideButton(infoSurface, closeBtnRect, "Close", hovered=closeBtnRect.collidepoint(mouseVx, mouseVy))


def getPlantToolTip(cell):
    plantState(cell)
    crop = crops[cell["crop"]]

    if cell["dead"]:
        return f"{cell['crop'].capitalize()} is dead"

    if cell["stage"] >= crop["max_stage"]:
        if cell["dayRipe"] is not None:
            daysLeftBeforDeath = max(0, ripeDays - (daysPassed - cell["dayRipe"]))
            return f"{cell['crop'].capitalize()}: Harvest Now! ({daysLeftBeforDeath}d Left)"
        return f"{cell['crop'].capitalize()}: Harvest Now!"

    totalWaterNeeded = crop["growth_days_per_stage"] * crop["max_stage"]
    waterDays = cell.get("watered_days", 0)
    if cell.get("watered", False):
        waterDays += 1
    waterLeft = max(0, totalWaterNeeded - waterDays)
    return f"{cell['crop'].capitalize()}: {waterLeft} waterings left"

def potShopPrice(potType):
    return fermPotLargePrice

def getFruitSellValue(cropName, fermented):
    if cropName == "kimchi":
        return KIMCHI_VALUE
    if fermented:
        return fermentData[cropName]["value"]
    return cropValues[cropName]

# =============================================================================
# KIMCHI SLOT HELPERS
# =============================================================================

def isSlotKimchi(slot):
    """True if this slot is currently in kimchi mode."""
    return slot is not None and slot.get("mode") == "kimchi"

def isKimchiDone(slot):
    """True when the kimchi in this slot has finished fermenting."""
    if not isSlotKimchi(slot):
        return False
    if slot.get("done", False):
        return True
    if slot.get("kimchi_fermenting", False) and slot.get("kimchi_day_started") is not None:
        return daysPassed - slot["kimchi_day_started"] >= KIMCHI_FERMENT_DAYS
    return False

def isFermentDone(slot):
    """True when a NORMAL (single-crop) slot has finished fermenting."""
    if slot is None or slot.get("crop") is None:
        return False
    if isSlotKimchi(slot):
        return False
    if slot.get("done", False):
        return True
    daysRequired = fermentData[slot["crop"]]["days"]
    daysIn       = daysPassed - slot.get("day_placed", daysPassed)
    return daysIn >= daysRequired

def enterKimchiMode(slot, firstCrop, secondCrop):
    """
    Convert a normal single-crop slot into kimchi mode.
    Called the moment a second raw fruit is dropped onto an occupied pot.
    The crop that was already fermenting becomes the first ingredient.
    """
    slot["mode"]               = "kimchi"
    slot["crop"]               = None       # clear the normal ferment crop field
    slot["day_placed"]         = None
    slot["done"]               = False
    slot["kimchi_crops"]       = {firstCrop, secondCrop}
    slot["kimchi_batch_day"]   = daysPassed
    slot["kimchi_fermenting"]  = False
    slot["kimchi_day_started"] = None

def addCropToKimchiSlot(slot, cropName):
    """
    Add one more crop to a kimchi-mode slot.
    Returns True if accepted, False if rejected (wrong day, duplicate, full, done).
    Automatically starts fermenting once all 6 crops are in.
    """
    if not isSlotKimchi(slot):
        return False
    if slot.get("kimchi_fermenting") or slot.get("done"):
        return False
    if cropName not in KIMCHI_CROPS:
        return False
    if cropName in slot["kimchi_crops"]:
        return False
    # Enforce same-day rule
    if slot.get("kimchi_batch_day") != daysPassed:
        return False
    slot["kimchi_crops"].add(cropName)
    if slot["kimchi_crops"] == KIMCHI_CROPS:
        slot["kimchi_fermenting"]  = True
        slot["kimchi_day_started"] = daysPassed
    return True

def resetKimchiSlotToEmpty(slot):
    """Strip all kimchi keys off a slot, leaving an empty pot."""
    slot["mode"]               = None
    slot["crop"]               = None
    slot["day_placed"]         = None
    slot["done"]               = False
    slot.pop("kimchi_crops",        None)
    slot.pop("kimchi_batch_day",    None)
    slot.pop("kimchi_fermenting",   None)
    slot.pop("kimchi_day_started",  None)

def tickFermentation():
    for slot in shedSlots:
        if slot is None:
            continue
        if isSlotKimchi(slot):
            if slot.get("kimchi_fermenting") and not slot.get("done", False):
                # Advance kimchi ferment timer
                if daysPassed - slot["kimchi_day_started"] >= KIMCHI_FERMENT_DAYS:
                    slot["done"] = True
            elif not slot.get("kimchi_fermenting") and not slot.get("done", False):
                # Incomplete batch: if the day has moved on, reset the pot
                if (slot.get("kimchi_batch_day") is not None
                        and slot["kimchi_batch_day"] < daysPassed):
                    resetKimchiSlotToEmpty(slot)
        else:
            # Normal single-crop ferment tick
            if slot.get("crop") is not None and not slot.get("done", False):
                daysRequired = fermentData[slot["crop"]]["days"]
                daysIn       = daysPassed - slot.get("day_placed", daysPassed)
                if daysIn >= daysRequired:
                    slot["done"] = True


# =============================================================================
# KIMCHI RECIPE DISPLAY
# Drawn above a pot that is in kimchi mode and not yet fermenting.
# Shows all 6 crop icons — green-bordered if already placed, greyed-out if not.
# =============================================================================
KIMCHI_DISPLAY_CROPS = ["tomato", "carrot", "cucumber", "chili", "cabbage", "garlic"]
KIMCHI_ICON_SIZE     = 28
KIMCHI_ICON_PAD      = 4

def drawKimchiRecipe(target, slot, potDrawPos):
    crops_in = slot.get("kimchi_crops", set())
    panelW   = (KIMCHI_ICON_SIZE + KIMCHI_ICON_PAD) * 6 + KIMCHI_ICON_PAD
    panelH   = KIMCHI_ICON_SIZE + KIMCHI_ICON_PAD * 2

    px = potDrawPos[0] - (panelW - shedPotImg.get_width()) // 2
    py = potDrawPos[1] - panelH - 6

    # Semi-transparent dark background
    panelSurf = pygame.Surface((panelW, panelH), pygame.SRCALPHA)
    panelSurf.fill((20, 15, 10, 200))
    target.blit(panelSurf, (px, py))

    for i, cropName in enumerate(KIMCHI_DISPLAY_CROPS):
        icon = pygame.transform.scale(fruitImages[cropName],
                                      (KIMCHI_ICON_SIZE, KIMCHI_ICON_SIZE))
        ix = px + KIMCHI_ICON_PAD + i * (KIMCHI_ICON_SIZE + KIMCHI_ICON_PAD)
        iy = py + KIMCHI_ICON_PAD
        if cropName in crops_in:
            target.blit(icon, (ix, iy))
            # Green border = this ingredient is already in the pot
            pygame.draw.rect(target, (80, 220, 80),
                             pygame.Rect(ix, iy, KIMCHI_ICON_SIZE, KIMCHI_ICON_SIZE), 2)
        else:
            # Greyed-out = still needs to be added today
            grey = icon.copy()
            grey.fill((80, 80, 80, 160), special_flags=pygame.BLEND_RGBA_MULT)
            target.blit(grey, (ix, iy))


setMusicVolume()


# =============================================================================
# MAIN GAME LOOP
# =============================================================================
running = True
while running:
    clock.tick(fps)

    if isRainingToday() and not paused and not showInfo:
        now_ms = pygame.time.get_ticks()
        if now_ms - rainLastFrameTime >= RAIN_FRAME_MS:
            rainLastFrameTime = now_ms
            rainFrameIndex = (rainFrameIndex + 1) % len(RAIN_FRAMES)

    mx, my           = pygame.mouse.get_pos()
    hoverVx, hoverVy = screenToMenuRef(mx, my)

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
                        pass
                    else:
                        paused = True
                        setMusicVolume()
                if event.key == pygame.K_F11:
                    toggleFullscreen()

        if event.type == pygame.MOUSEWHEEL and showInfo:
            infoScrollY -= event.y * infoScrollSpeed

        if event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # =====================================================================
        # LEFT MOUSE BUTTON
        # =====================================================================
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            rx, ry = screenToMenuRef(mx, my)

            if showInfo:
                if closeBtnRect.collidepoint(rx, ry):
                    showInfo = False
                    paused   = True
                    setMusicVolume()
                continue

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

            vx, vy = screenToVirtual(mx, my)

            # --- TV click ---
            if tvRect.collidepoint(vx, vy):
                tvOn = not tvOn
                continue

            # --- Player is holding a fruit ---
            if heldFruit is not None:
                # Sell into chest
                if shopChestRect.collidepoint(vx, vy):
                    money    += getFruitSellValue(heldFruit["crop"], heldFruit["fermented"])
                    heldFruit = None
                    continue

                # Drop into a shed slot
                for slotIdx, slotRect in enumerate(shedSlotRects):
                    if slotRect.collidepoint(vx, vy):
                        slot = shedSlots[slotIdx]
                        if slot is None:
                            break  # no pot here yet

                        if heldFruit["fermented"]:
                            break  # never put a fermented crop back into a pot

                        cropName = heldFruit["crop"]

                        if isSlotKimchi(slot):
                            # Pot is already in kimchi mode — add the next ingredient
                            if addCropToKimchiSlot(slot, cropName):
                                heldFruit = None

                        elif slot.get("crop") is None:
                            # Empty pot — start normal single-crop fermentation
                            slot["crop"]       = cropName
                            slot["day_placed"] = daysPassed
                            slot["done"]       = False
                            heldFruit = None

                        else:
                            # Pot already has ONE crop and has not finished fermenting.
                            # Dropping a SECOND different crop triggers kimchi mode!
                            firstCrop = slot["crop"]
                            if (cropName != firstCrop
                                    and cropName in KIMCHI_CROPS
                                    and firstCrop in KIMCHI_CROPS
                                    and not slot.get("done", False)):
                                enterKimchiMode(slot, firstCrop, cropName)
                                heldFruit = None
                        break
                continue

            # --- Player is carrying a pot ---
            if heldPot is not None:
                for slotIdx, slotRect in enumerate(shedSlotRects):
                    if slotRect.collidepoint(vx, vy) and shedSlots[slotIdx] is None:
                        shedSlots[slotIdx] = {"pot": heldPot, "crop": None, "day_placed": None, "done": False}
                        heldPot = None
                        break
                continue

            # --- Watering can refill ---
            if waterRefillRect.collidepoint(vx, vy) and not selectedSeed and heldPot is None and heldFruit is None:
                if goldWaterBucketHeld:
                    goldWaterBucketUsesLeft = goldWaterBucketMax
                else:
                    wateringCanHeld = True
                    wateringCanFull = True
                continue

            # --- Drop can/bucket if clicking outside grid ---
            if wateringCanHeld or goldWaterBucketHeld:
                gx = (vx - gridStartX) // cellSize
                gy = (vy - gridStartY) // cellSize
                if not (0 <= gx < gridCols and 0 <= gy < gridRows):
                    wateringCanHeld     = False
                    goldWaterBucketHeld = False
                    continue

            # --- Pick up finished kimchi or finished normal ferment ---
            if not wateringCanHeld and selectedSeed is None and heldPot is None and heldFruit is None:
                for slotIdx, slotRect in enumerate(shedSlotRects):
                    if slotRect.collidepoint(vx, vy):
                        slot = shedSlots[slotIdx]
                        if slot is None:
                            break
                        if isKimchiDone(slot):
                            heldFruit = {"crop": "kimchi", "fermented": True}
                            resetKimchiSlotToEmpty(slot)
                        elif isFermentDone(slot):
                            heldFruit          = {"crop": slot["crop"], "fermented": True}
                            slot["crop"]       = None
                            slot["day_placed"] = None
                            slot["done"]       = False
                        break

            # --- Buy a fermentation pot ---
            if not wateringCanHeld and selectedSeed is None and heldPot is None and heldFruit is None:
                if fermPotLargeRect.collidepoint(vx, vy):
                    if money >= fermPotLargePrice:
                        money  -= fermPotLargePrice
                        heldPot = "large"
                    continue

            # --- Gold bucket shop ---
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

            # --- Check seed bag click ---
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

            # --- Purchase a seed ---
            if clickedSeed and selectedSeed is None:
                if money >= cropPrice[clickedSeed]:
                    money -= cropPrice[clickedSeed]
                    selectedSeed = clickedSeed
                continue

            # --- Plant the selected seed ---
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

            # --- Water with gold bucket ---
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

            # --- Water with normal can ---
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

        # =====================================================================
        # RIGHT MOUSE BUTTON
        # =====================================================================
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            rx, ry = screenToMenuRef(mx, my)

            if paused and not showInfo:
                for i in range(3):
                    if getSlotRect(i).collidepoint(rx, ry):
                        saveGame(i, f"Farm {i + 1}")
                        break

            elif not paused and not showInfo:
                vx, vy = screenToVirtual(mx, my)

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

                if selectedSeed is not None:
                    money += cropPrice[selectedSeed]
                    selectedSeed = None
                    continue

                if heldPot is not None:
                    money  += potShopPrice(heldPot)
                    heldPot = None
                    continue

                gx           = (vx - gridStartX) // cellSize
                gy           = (vy - gridStartY) // cellSize
                harvestResult = harvestDead(grid, gx, gy, crops)
                if harvestResult:
                    if harvestResult["type"] == "dead_refund":
                        money += getDeadPlantRefund(harvestResult["crop"])
                    elif harvestResult["type"] == "fruit":
                        heldFruit = {"crop": harvestResult["crop"], "fermented": False}

    # =========================================================================
    # DAY TICK
    # =========================================================================
    if not paused and not showInfo:
        now = pygame.time.get_ticks()
        if now - lastMoveTime >= moveInterval:
            lastMoveTime = now
            daysPassed  += 1

            cycleIndex = daysPassed // 12
            if cycleIndex != rainCurrentCycle:
                rainCurrentCycle = cycleIndex
                rainDaysInCycle  = getRainDaysForCycle()

            if isRainingToday():
                for x in range(gridCols):
                    for y in range(gridRows):
                        if grid[x][y] is not None:
                            grid[x][y]["watered"] = True

            for x in range(gridCols):
                for y in range(gridRows):
                    cell = grid[x][y]
                    if not cell:
                        continue

                    plantState(cell)

                    if cell["dead"]:
                        cell["watered"] = False
                        continue

                    if cell.get("watered", False):
                        cell["watered_days"] = cell.get("watered_days", 0) + 1

                    cell["watered"] = False
                    crop        = crops[cell["crop"]]
                    wateredDays = cell.get("watered_days", 0)
                    stage       = wateredDays // crop["growth_days_per_stage"]
                    cell["stage"] = min(stage, crop["max_stage"])

                    if cell["stage"] >= crop["max_stage"]:
                        if cell["dayRipe"] is None:
                            cell["dayRipe"] = daysPassed
                        elif daysPassed - cell["dayRipe"] >= ripeDays:
                            cell["dead"] = True
                    else:
                        cell["dayRipe"] = None

            tickFermentation()
            tvOn = False
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

    # =========================================================================
    # RENDERING
    # =========================================================================
    screenW, screenH = screen.get_size()
    target = pygame.Surface((virtualWidth, virtualHeight))

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
    pygame.draw.rect(target, (255, 0, 0), tvRect, 2)

    if not goldWaterBucketHeld:
        target.blit(goldWaterBucketShop, (goldWaterBucketx, goldWaterBuckety))

    # --- Shed pots ---
    shedPositions = [shedSlotTop, shedSlotBottom]
    for slotIdx, slotPos in enumerate(shedPositions):
        slot = shedSlots[slotIdx]
        if slot is None:
            continue

        if isSlotKimchi(slot):
            # Draw kimchi sprite inside pot once all 6 crops are placed
            if slot.get("kimchi_fermenting") or slot.get("done"):
                target.blit(kimchiFinishedImg,
                            (slotPos[0] + fermentOffsetX, slotPos[1] + fermentOffsetY))
            target.blit(shedPotImg, slotPos)
            if isKimchiDone(slot):
                target.blit(doneSparkleImg, slotPos)
            elif not slot.get("kimchi_fermenting"):
                # Recipe in progress — show the ingredient checklist above the pot
                drawKimchiRecipe(target, slot, slotPos)
        else:
            # Normal single-crop fermentation
            if slot.get("crop") is not None:
                fermImg = fermentImages[slot["crop"]]
                target.blit(fermImg, (slotPos[0] + fermentOffsetX, slotPos[1] + fermentOffsetY))
            target.blit(shedPotImg, slotPos)
            if slot.get("crop") is not None and isFermentDone(slot):
                target.blit(doneSparkleImg, slotPos)

    target.blit(shedDoorImg, (shedDoorX, shedDoorY))
    drawMoney(target, money, virtualWidth)

    # --- Planted crops ---
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
                if sprite.get_width() != cellSize or sprite.get_height() != cellSize:
                    sprite = pygame.transform.scale(sprite, (cellSize, cellSize))
                target.blit(sprite, (gridStartX + x * cellSize, gridStartY + y * cellSize))

    # --- Locked tile overlays ---
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

    # --- Calendar ---
    target.blit(calendarSprite, (176*8, 72*8))
    target.blit(calendarCircle, (spriteX, spriteY))

    # --- Watered droplets ---
    for x in range(gridCols):
        for y in range(gridRows):
            cell = grid[x][y]
            if cell and cell.get("watered", False):
                druppel = pygame.transform.scale(waterDropImg, (cellSize, cellSize))
                target.blit(druppel, (gridStartX + x * cellSize, gridStartY + y * cellSize))

    # --- TV weather forecast overlay ---
    tvSprite = textures["weatherReport3"]
    target.blit(tvSprite, (1120, 224))
    if tvOn:
        tomorrowDay = (daysPassed + 1) % 12
        forecastImg = rainForecastImg if tomorrowDay in rainDaysInCycle else sunForecastImg
        target.blit(forecastImg, (1120, 224))

    # --- Rain overlay ---
    if isRainingToday() and not paused and not showInfo:
        rainSprite = pygame.transform.scale(RAIN_FRAMES[rainFrameIndex], (virtualWidth, virtualHeight))
        target.blit(rainSprite, (0, 0))

    # =========================================================================
    # CURSOR DRAWING
    # =========================================================================
    if heldFruit is not None:
        if heldFruit["crop"] == "kimchi":
            cursorImg = kimchiFinishedImg
        elif heldFruit["fermented"]:
            cursorImg = fermentImages[heldFruit["crop"]]
        else:
            cursorImg = fruitImages[heldFruit["crop"]]
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

    # =========================================================================
    # TOOLTIPS
    # =========================================================================
    def drawTooltip(surface, text, cx, cy):
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
            val = getFruitSellValue(heldFruit["crop"], heldFruit["fermented"])
            if heldFruit["crop"] == "kimchi":
                drawTooltip(target, f"Sell Kimchi: {val} coins",
                            shopChestRect.centerx, shopChestRect.top)
            else:
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
                if slot is None:
                    break
                if isSlotKimchi(slot):
                    if isKimchiDone(slot):
                        drawTooltip(target, f"Kimchi ready! ({KIMCHI_VALUE} coins)",
                                    slotRect.centerx, slotRect.top)
                    elif slot.get("kimchi_fermenting"):
                        dLeft = max(0, KIMCHI_FERMENT_DAYS - (daysPassed - slot["kimchi_day_started"]))
                        drawTooltip(target, f"Kimchi fermenting... ({dLeft}d left)",
                                    slotRect.centerx, slotRect.top)
                    else:
                        remaining = sorted(KIMCHI_CROPS - slot.get("kimchi_crops", set()))
                        drawTooltip(target, f"Still need: {', '.join(remaining)}",
                                    slotRect.centerx, slotRect.top)
                elif slot.get("crop") is not None:
                    cropName = slot["crop"]
                    if isFermentDone(slot):
                        drawTooltip(target,
                                    f"{cropName.capitalize()} ready! ({fermentData[cropName]['value']} coins)",
                                    slotRect.centerx, slotRect.top)
                    else:
                        daysLeft = fermentData[cropName]["days"] - (daysPassed - slot.get("day_placed", daysPassed))
                        drawTooltip(target, f"Fermenting {cropName}... ({max(0, daysLeft)}d left)",
                                    slotRect.centerx, slotRect.top)
                else:
                    drawTooltip(target, "Empty pot (place a fruit)", slotRect.centerx, slotRect.top)
                break

    # =========================================================================
    # OVERLAY MENUS
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
    # =========================================================================
    scale   = min(screenW / virtualWidth, screenH / virtualHeight)
    scaledW = int(virtualWidth  * scale)
    scaledH = int(virtualHeight * scale)
    scaled  = pygame.transform.scale(target, (scaledW, scaledH))
    screen.fill((0, 0, 0))
    screen.blit(scaled, ((screenW - scaledW) // 2, (screenH - scaledH) // 2))
    pygame.display.flip()

pygame.quit()
sys.exit()