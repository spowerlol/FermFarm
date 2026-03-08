import pygame
import sys
from texture import loadTextures
from crop import loadCrops
from money_ui import initMoneyUi, drawMoney
from cropHarvesting import harvest, CROP_VALUES, cropPrice, inventory
from startScreen import runStartScreen
import os
import json
from datetime import datetime

pygame.init()
pygame.mixer.init()

VIRTUAL_WIDTH  = 240 * 8
VIRTUAL_HEIGHT = 135 * 8
FPS = 60
WINDOW_WIDTH  = VIRTUAL_WIDTH  // 2
WINDOW_HEIGHT = VIRTUAL_HEIGHT // 2
MENU_REF_W = VIRTUAL_WIDTH
MENU_REF_H = VIRTUAL_HEIGHT

fullscreen = True
info = pygame.display.Info()
screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("FermFarm")

clock = pygame.time.Clock()
runStartScreen(screen, fullscreen)

# ── Music ──────────────────────────────────────────────────────────────────────
MUSIC_NORMAL_VOL = 0.5
MUSIC_DIM_VOL    = 0.2
music_enabled    = True
# ──────────────────────────────────────────────────────────────────────────────

textures = loadTextures()
initMoneyUi(textures)
crops = loadCrops(textures)

tekoopTileImg = textures["tekoopTile"]

menuSurface = pygame.Surface((MENU_REF_W, MENU_REF_H), pygame.SRCALPHA)
infoSurface = pygame.Surface((MENU_REF_W, MENU_REF_H), pygame.SRCALPHA)

fontPath = "sprites/babosorry.ttf"
if not os.path.exists(fontPath):
    fontPath = None

saveNameFont  = pygame.font.Font(fontPath, 60)
saveDateFont  = pygame.font.Font(fontPath, 36)
buttonFont    = pygame.font.Font(fontPath, 96)
infoTextFont  = pygame.font.Font(fontPath, 44)
infoTitleFont = pygame.font.Font(fontPath, 72)

shopShelvesImg  = textures["shopShelves"]
shopShelvesX, shopShelvesY = 185*8, 50*8
fermPotSmallImg = textures["fermPotSmall"]
fermPotSmallX, fermPotSmallY = 205*8, 44*8
fermPotLargeImg = textures["fermPotLarge"]
fermPotLargeX, fermPotLargeY = 208*8, 62*8
carrotBagImg    = textures["carrotBag"]
carrotBagX, carrotBagY     = 186*8, 54*8
tomatoBagImg    = textures["tomatoBag"]
tomatoBagX, tomatoBagY     = 198*8, 54*8
chiliBagImg     = textures["chiliBag"]
chiliBagX, chiliBagY       = 186*8, 67*8
cucumberBagImg  = textures["cucumberBag"]
cucumberBagX, cucumberBagY = 210*8, 54*8
cabbageBagImg   = textures["cabbageBag"]
cabbageBagX, cabbageBagY   = 197*8, 67*8
garlicBagImg    = textures["garlicBag"]
garlicBagX, garlicBagY     = 209*8, 67*8
menuSprite = textures["menuSprite"]

seedRects = {
    "carrot":   pygame.Rect(carrotBagX,   carrotBagY,   carrotBagImg.get_width(),   carrotBagImg.get_height()),
    "tomato":   pygame.Rect(tomatoBagX,   tomatoBagY,   tomatoBagImg.get_width(),   tomatoBagImg.get_height()),
    "chili":    pygame.Rect(chiliBagX,    chiliBagY,    chiliBagImg.get_width(),    chiliBagImg.get_height()),
    "cucumber": pygame.Rect(cucumberBagX, cucumberBagY, cucumberBagImg.get_width(), cucumberBagImg.get_height()),
    "cabbage":  pygame.Rect(cabbageBagX,  cabbageBagY,  cabbageBagImg.get_width(),  cabbageBagImg.get_height()),
    "garlic":   pygame.Rect(garlicBagX,   garlicBagY,   garlicBagImg.get_width(),   garlicBagImg.get_height()),
}
selectedSeed = None

# ── Watering Can ───────────────────────────────────────────────────────────────
wateringCanEmptyImg = textures["wateringcanEmpty"]
wateringCanFullImg  = textures["wateringcanFull"]
waterDropImg     = textures["waterDropPlant"]
wateringCanFull     = False   # starts empty
wateringCanHeld     = False   # player is holding the can

# Refill zone: (887, 416), 90x90 in virtual coords
waterRefillRect = pygame.Rect(887, 416, 90, 90)

# Seed-bag images lookup for cursor rendering
seedBagImages = {
    "carrot":   textures["carrotBag"],
    "tomato":   textures["tomatoBag"],
    "chili":    textures["chiliBag"],
    "cucumber": textures["cucumberBag"],
    "cabbage":  textures["cabbageBag"],
    "garlic":   textures["garlicBag"],
}
# ──────────────────────────────────────────────────────────────────────────────

fermPotSmallRect = pygame.Rect(fermPotSmallX, fermPotSmallY, fermPotSmallImg.get_width(), fermPotSmallImg.get_height())
fermPotLargeRect = pygame.Rect(fermPotLargeX, fermPotLargeY, fermPotLargeImg.get_width(), fermPotLargeImg.get_height())

money = 6
background      = textures["background"]
calendarSprite  = textures["calendar"]
calendarCircle  = textures["calendarCircle"]

# Watering can pickup rect (placed near the refill zone for easy access)
wateringCanWorldRect = pygame.Rect(887, 416 - 90, 90, 90)  # just above refill zone

CELL_SIZE    = 16 * 8
GRID_COLS    = 7
GRID_ROWS    = 3
GRID_START_X = 0
GRID_START_Y = 87 * 8
grid = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

# ── Tile ownership ─────────────────────────────────────────────────────────────
# Prices per column, right to left (col 6 = cheapest, col 0 = most expensive)
TILE_COL_PRICE = {6: 3, 5: 5, 4: 10, 3: 15, 2: 20, 1: 30, 0: 50}

def makeTileOwned():
    """Return a fresh 7x3 ownership grid. Free tiles: cols 5-6, rows 0-1."""
    owned = [[False for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
    for col in [5, 6]:
        for row in [0, 1]:
            owned[col][row] = True
    return owned

tileOwned = makeTileOwned()
# ──────────────────────────────────────────────────────────────────────────────

START_X, START_Y   = 175*8, 87*8
spriteX, spriteY   = START_X, START_Y
STEP           = 16 * 8
COLUMNS        = 4
ROWS           = 3
currentColumn  = 0
currentRow     = 0
MOVE_INTERVAL  = 5_000
lastMoveTime   = pygame.time.get_ticks()
daysPassed     = 0

paused   = False
showInfo = True

SAVE_FILE  = "saveslots.json"
saveSlots = [
    {"name": "Empty", "date": "", "data": None},
    {"name": "Empty", "date": "", "data": None},
    {"name": "Empty", "date": "", "data": None},
]
if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, "r") as f:
            loadedSlots = json.load(f)
            if len(loadedSlots) == 3:
                saveSlots = loadedSlots
    except:
        pass

# Slot layout
SLOT_WIDTH    = 400
SLOT_HEIGHT   = 200
SLOT_SPACING  = 25
SLOT_START_X  = (VIRTUAL_WIDTH - SLOT_WIDTH) // 3.5
SLOT_START_Y  = (VIRTUAL_HEIGHT - (3 * SLOT_HEIGHT + 2 * SLOT_SPACING)) // 2.5
SLOT_BOTTOM_Y = SLOT_START_Y + 3 * SLOT_HEIGHT + 2 * SLOT_SPACING

def getSlotRect(i):
    sy = SLOT_START_Y + i * (SLOT_HEIGHT + SLOT_SPACING)
    return pygame.Rect(SLOT_START_X, sy, SLOT_WIDTH, SLOT_HEIGHT)

# Side buttons
SIDE_BTN_W = 380
SIDE_BTN_X = int(SLOT_START_X) + SLOT_WIDTH + 100

totalBtnArea = SLOT_BOTTOM_Y - SLOT_START_Y
BTN_SPACING  = 20
BTN_H_4      = (totalBtnArea - 3 * BTN_SPACING) // 4

fullscreenBtnRect = pygame.Rect(SIDE_BTN_X, int(SLOT_START_Y), SIDE_BTN_W, BTN_H_4)
infoBtnRect       = pygame.Rect(SIDE_BTN_X, int(SLOT_START_Y + 1 * (BTN_H_4 + BTN_SPACING)), SIDE_BTN_W, BTN_H_4)
quitBtnRect       = pygame.Rect(SIDE_BTN_X, int(SLOT_START_Y + 3 * (BTN_H_4 + BTN_SPACING)), SIDE_BTN_W, BTN_H_4)
audioBtnRect      = pygame.Rect(SIDE_BTN_X, int(SLOT_START_Y + 2 * (BTN_H_4 + BTN_SPACING)), SIDE_BTN_W, BTN_H_4)

# Info screen constants
INFO_PAD_X         = 160
INFO_TOP_Y         = 160
INFO_SCROLL_TOP    = 280
INFO_SCROLL_BOTTOM = 920
INFO_SCROLL_H      = INFO_SCROLL_BOTTOM - INFO_SCROLL_TOP

CLOSE_BTN_W = 300
CLOSE_BTN_H = 90
closeBtnRect = pygame.Rect((VIRTUAL_WIDTH - CLOSE_BTN_W) // 2, 960, CLOSE_BTN_W, CLOSE_BTN_H)

INFO_FILE = "info.txt"
rawInfoLines = []
if os.path.exists(INFO_FILE):
    try:
        with open(INFO_FILE, "r", encoding="utf-8") as f:
            rawInfoLines = f.read().splitlines()
    except:
        rawInfoLines = ["Could not load info.txt"]

maxTextW = VIRTUAL_WIDTH - INFO_PAD_X * 2

def wrapLines(rawLines, font, maxW):
    wrapped = []
    for raw in rawLines:
        if raw.strip() == "":
            wrapped.append("")
            continue
        words = raw.split()
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

infoLines      = wrapLines(rawInfoLines, infoTextFont, maxTextW)
INFO_LINE_H    = infoTextFont.get_linesize() + 6
infoScrollY    = 0
infoScrollSpeed = 40
infoTotalH     = len(infoLines) * INFO_LINE_H


# ── Music helpers ──────────────────────────────────────────────────────────────
def setMusicVolume():
    if not music_enabled:
        pygame.mixer.music.set_volume(0)
    elif paused or showInfo:
        pygame.mixer.music.set_volume(MUSIC_DIM_VOL)
    else:
        pygame.mixer.music.set_volume(MUSIC_NORMAL_VOL)
# ──────────────────────────────────────────────────────────────────────────────


def saveGame(slotIndex, slotName):
    global saveSlots
    saveData = {
        "money": money, "days_passed": daysPassed, "grid": grid,
        "inventory": inventory, "current_column": currentColumn,
        "current_row": currentRow, "sprite_x": spriteX, "sprite_y": spriteY,
        "tile_owned": tileOwned,
    }
    saveSlots[slotIndex] = {
        "name": slotName,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data": saveData,
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(saveSlots, f)
    except:
        pass

def loadGame(slotIndex):
    global money, daysPassed, grid, inventory
    global currentColumn, currentRow, spriteX, spriteY, lastMoveTime, tileOwned
    slot = saveSlots[slotIndex]
    if slot["data"] is None:
        return False
    try:
        data = slot["data"]
        money         = data["money"]
        daysPassed    = data["days_passed"]
        grid          = data["grid"]
        inventory     = data["inventory"]
        currentColumn = data["current_column"]
        currentRow    = data["current_row"]
        spriteX       = data["sprite_x"]
        spriteY       = data["sprite_y"]
        lastMoveTime  = pygame.time.get_ticks()
        if "tile_owned" in data:
            tileOwned = data["tile_owned"]
        else:
            tileOwned = makeTileOwned()
        return True
    except:
        return False


def newGame():
    global money, daysPassed, grid, inventory
    global currentColumn, currentRow, spriteX, spriteY, lastMoveTime, tileOwned
    money         = 6
    daysPassed    = 0
    grid          = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]
    inventory     = {k: 0 for k in inventory}
    currentColumn = 0
    currentRow    = 0
    spriteX       = START_X
    spriteY       = START_Y
    lastMoveTime  = pygame.time.get_ticks()
    tileOwned     = makeTileOwned()


def screenToVirtual(mx, my):
    screenW, screenH = screen.get_size()
    if fullscreen:
        vx = mx * VIRTUAL_WIDTH  // screenW
        vy = my * VIRTUAL_HEIGHT // screenH
    else:
        scale   = min(screenW / VIRTUAL_WIDTH, screenH / VIRTUAL_HEIGHT)
        xOffset = (screenW - VIRTUAL_WIDTH  * scale) / 2
        yOffset = (screenH - VIRTUAL_HEIGHT * scale) / 2
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
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

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
    overlay = pygame.Surface((MENU_REF_W, MENU_REF_H))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    menuSurface.blit(overlay, (0, 0))
    menuSpriteScaled = pygame.transform.scale(menuSprite, (MENU_REF_W, MENU_REF_H))
    menuSurface.blit(menuSpriteScaled, (0, 0))

    for i in range(3):
        slotRect = getSlotRect(i)
        isHovered = slotRect.collidepoint(mouseVx, mouseVy)
        hasSave   = saveSlots[i]["data"] is not None

        bgColor = (75, 55, 40) if isHovered else (60, 40, 30)
        pygame.draw.rect(menuSurface, bgColor, slotRect)
        borderColor = (180, 150, 100) if isHovered else (100, 80, 60)
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

    fsLabel = "Windowed" if fullscreen else "Fullscreen"
    drawSideButton(menuSurface, fullscreenBtnRect, fsLabel,   hovered=fullscreenBtnRect.collidepoint(mouseVx, mouseVy))
    drawSideButton(menuSurface, infoBtnRect,       "Info",    hovered=infoBtnRect.collidepoint(mouseVx, mouseVy))
    drawSideButton(menuSurface, quitBtnRect,       "Quit",    hovered=quitBtnRect.collidepoint(mouseVx, mouseVy))
    audioLabel = "Music: ON" if music_enabled else "Music: OFF"
    drawSideButton(menuSurface, audioBtnRect, audioLabel,     hovered=audioBtnRect.collidepoint(mouseVx, mouseVy))


def buildInfoSurface(mouseVx=0, mouseVy=0):
    global infoScrollY
    infoSurface.fill((0, 0, 0, 0))

    overlay = pygame.Surface((MENU_REF_W, MENU_REF_H))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    infoSurface.blit(overlay, (0, 0))
    menuSpriteScaled = pygame.transform.scale(menuSprite, (MENU_REF_W, MENU_REF_H))
    infoSurface.blit(menuSpriteScaled, (0, 0))

    titleSurf = infoTitleFont.render("How to Play", False, (255, 240, 180))
    infoSurface.blit(titleSurf, ((VIRTUAL_WIDTH - titleSurf.get_width()) // 2, INFO_TOP_Y))

    maxScroll  = max(0, infoTotalH - INFO_SCROLL_H)
    infoScrollY = max(0, min(infoScrollY, maxScroll))

    scrollClip = pygame.Rect(INFO_PAD_X, INFO_SCROLL_TOP, VIRTUAL_WIDTH - INFO_PAD_X * 2, INFO_SCROLL_H)
    infoSurface.set_clip(scrollClip)

    y = INFO_SCROLL_TOP - infoScrollY
    for line in infoLines:
        if line == "":
            y += INFO_LINE_H // 2
            continue
        lineSurf = infoTextFont.render(line, False, (220, 200, 160))
        infoSurface.blit(lineSurf, (INFO_PAD_X, y))
        y += INFO_LINE_H

    infoSurface.set_clip(None)

    fadeH = 60
    topFade = pygame.Surface((VIRTUAL_WIDTH - INFO_PAD_X * 2, fadeH), pygame.SRCALPHA)
    for i in range(fadeH):
        alpha = int(200 * (1 - i / fadeH))
        pygame.draw.line(topFade, (20, 12, 5, alpha), (0, i), (topFade.get_width(), i))
    infoSurface.blit(topFade, (INFO_PAD_X, INFO_SCROLL_TOP))

    botFade = pygame.Surface((VIRTUAL_WIDTH - INFO_PAD_X * 2, fadeH), pygame.SRCALPHA)
    for i in range(fadeH):
        alpha = int(200 * (i / fadeH))
        pygame.draw.line(botFade, (20, 12, 5, alpha), (0, i), (botFade.get_width(), i))
    infoSurface.blit(botFade, (INFO_PAD_X, INFO_SCROLL_BOTTOM - fadeH))

    if infoScrollY > 0:
        upSurf = infoTextFont.render("scroll up", False, (160, 130, 80))
        infoSurface.blit(upSurf, ((VIRTUAL_WIDTH - upSurf.get_width()) // 2, INFO_SCROLL_TOP + 8))
    if infoScrollY < maxScroll:
        downSurf = infoTextFont.render("scroll down", False, (160, 130, 80))
        infoSurface.blit(downSurf, ((VIRTUAL_WIDTH - downSurf.get_width()) // 2, INFO_SCROLL_BOTTOM - 52))

    drawSideButton(infoSurface, closeBtnRect, "Close", hovered=closeBtnRect.collidepoint(mouseVx, mouseVy))


# Dim music on startup since info screen opens on boot
setMusicVolume()

# =========================================================
# MAIN LOOP
# =========================================================
running = True
while running:
    clock.tick(FPS)

    mx, my = pygame.mouse.get_pos()
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
                    # Drop held seed or can before pausing
                    if selectedSeed is not None:
                        money += cropPrice[selectedSeed]  # refund
                        selectedSeed = None
                    elif wateringCanHeld:
                        wateringCanHeld = False
                    else:
                        paused = True
                        setMusicVolume()
                if event.key == pygame.K_F11:
                    toggleFullscreen()

        if event.type == pygame.MOUSEWHEEL and showInfo:
            infoScrollY -= event.y * infoScrollSpeed

        if event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

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
                    music_enabled = not music_enabled
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

            # Clicking the refill/water box picks up the can and fills it instantly
            if waterRefillRect.collidepoint(vx, vy) and not selectedSeed:
                wateringCanHeld = True
                wateringCanFull = True
                continue

            if wateringCanHeld:
                # Put down the can (click outside grid)
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE
                if not (0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS):
                    wateringCanHeld = False
                    continue

            if fermPotSmallRect.collidepoint(vx, vy):
                for cropName in inventory:
                    if inventory[cropName] > 0:
                        inventory[cropName] -= 1
                        money += CROP_VALUES[cropName] // 2
                        break
                continue

            if fermPotLargeRect.collidepoint(vx, vy):
                fermented = 0
                for cropName in inventory:
                    while inventory[cropName] > 0 and fermented < 2:
                        inventory[cropName] -= 1
                        money += CROP_VALUES[cropName] // 2
                        fermented += 1
                    if fermented >= 2:
                        break
                continue

            clickedSeed = None
            if not wateringCanHeld:
                for cropName, rect in seedRects.items():
                    if rect.collidepoint(vx, vy):
                        clickedSeed = cropName
                        break

            # Buy a locked tile when clicking it with nothing held
            if clickedSeed is None and selectedSeed is None and not wateringCanHeld:
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE
                if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                    if not tileOwned[gx][gy]:
                        price = TILE_COL_PRICE[gx]
                        if money >= price:
                            money -= price
                            tileOwned[gx][gy] = True
                        continue

            if clickedSeed and selectedSeed is None:
                if money >= cropPrice[clickedSeed]:
                    money -= cropPrice[clickedSeed]
                    selectedSeed = clickedSeed
                continue

            if selectedSeed is not None:
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE
                if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                    if grid[gx][gy] is None and tileOwned[gx][gy]:
                        grid[gx][gy] = {"crop": selectedSeed, "day_planted": daysPassed, "stage": 0, "watered": False, "watered_days": 0}
                        selectedSeed = None
                continue

            # Watering a plant (left-click on grid cell while holding full can)
            if wateringCanHeld and wateringCanFull:
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE
                if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                    cell = grid[gx][gy]
                    if cell is not None and not cell.get("watered", False):
                        cell["watered"] = True
                        wateringCanFull = False

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
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE
                harvested = harvest(grid, gx, gy, crops)
                if harvested:
                    money += CROP_VALUES[harvested]
                    inventory[harvested] = inventory.get(harvested, 0) + 1

    if not paused and not showInfo:
        now = pygame.time.get_ticks()
        if now - lastMoveTime >= MOVE_INTERVAL:
            lastMoveTime = now
            daysPassed  += 1
            for x in range(GRID_COLS):
                for y in range(GRID_ROWS):
                    cell = grid[x][y]
                    if cell:
                        # Only advance growth if plant was watered this day
                        if cell.get("watered", False):
                            cell["watered_days"] = cell.get("watered_days", 0) + 1
                        cell["watered"] = False  # reset watering for new day
                        crop  = crops[cell["crop"]]
                        wateredDays = cell.get("watered_days", 0)
                        stage = wateredDays // crop["growth_days_per_stage"]
                        cell["stage"] = min(stage, crop["max_stage"])
            spriteX       += STEP
            currentColumn += 1
            if currentColumn >= COLUMNS:
                currentColumn = 0
                spriteX       = START_X
                spriteY      += STEP
                currentRow   += 1
                if currentRow >= ROWS:
                    currentRow         = 0
                    spriteX, spriteY   = START_X, START_Y

    screenW, screenH = screen.get_size()
    target = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    target.blit(background,      (0, 0))
    target.blit(shopShelvesImg,  (shopShelvesX,  shopShelvesY))
    target.blit(fermPotSmallImg, (fermPotSmallX, fermPotSmallY))
    target.blit(fermPotLargeImg, (fermPotLargeX, fermPotLargeY))
    target.blit(carrotBagImg,    (carrotBagX,    carrotBagY))
    target.blit(tomatoBagImg,    (tomatoBagX,    tomatoBagY))
    target.blit(cucumberBagImg,  (cucumberBagX,  cucumberBagY))
    target.blit(chiliBagImg,     (chiliBagX,     chiliBagY))
    target.blit(garlicBagImg,    (garlicBagX,    garlicBagY))
    target.blit(cabbageBagImg,   (cabbageBagX,   cabbageBagY))
    drawMoney(target, money, VIRTUAL_WIDTH)

    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            cell = grid[x][y]
            if cell:
                crop   = crops[cell["crop"]]
                sprite = crop["stages"][cell["stage"]]
                if sprite.get_width() != CELL_SIZE or sprite.get_height() != CELL_SIZE:
                    sprite = pygame.transform.scale(sprite, (CELL_SIZE, CELL_SIZE))
                target.blit(sprite, (GRID_START_X + x * CELL_SIZE, GRID_START_Y + y * CELL_SIZE))

    # Draw locked tiles and collect hover info
    vMouseX, vMouseY = screenToVirtual(*pygame.mouse.get_pos())
    hoveredLockedTile = None
    tekoopScaled = pygame.transform.scale(tekoopTileImg, (CELL_SIZE, CELL_SIZE))
    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            if not tileOwned[x][y]:
                tx = GRID_START_X + x * CELL_SIZE
                ty = GRID_START_Y + y * CELL_SIZE
                target.blit(tekoopScaled, (tx, ty))
                # Check hover
                tileRect = pygame.Rect(tx, ty, CELL_SIZE, CELL_SIZE)
                if tileRect.collidepoint(vMouseX, vMouseY) and not paused and not showInfo:
                    hoveredLockedTile = (x, y)

    target.blit(calendarSprite, (176*8, 72*8))
    target.blit(calendarCircle, (spriteX, spriteY))

    # Draw watered indicators on plants using the druppel sprite
    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            cell = grid[x][y]
            if cell and cell.get("watered", False):
                druppel = pygame.transform.scale(waterDropImg, (CELL_SIZE, CELL_SIZE))
                target.blit(druppel, (GRID_START_X + x * CELL_SIZE, GRID_START_Y + y * CELL_SIZE))

    # Draw cursor: seed bag or watering can following mouse
    if selectedSeed is not None:
        cursorImg = seedBagImages[selectedSeed]
        cursorScaled = pygame.transform.scale(cursorImg, (CELL_SIZE // 2, CELL_SIZE // 2))
        target.blit(cursorScaled, (vMouseX - cursorScaled.get_width() // 2, vMouseY - cursorScaled.get_height() // 2))
        pygame.mouse.set_visible(False)
    elif wateringCanHeld:
        canCursor = wateringCanFullImg if wateringCanFull else wateringCanEmptyImg
        canScaled = pygame.transform.scale(canCursor, (CELL_SIZE // 2, CELL_SIZE // 2))
        target.blit(canScaled, (vMouseX - canScaled.get_width() // 2, vMouseY - canScaled.get_height() // 2))
        pygame.mouse.set_visible(False)
    else:
        pygame.mouse.set_visible(True)


    def drawTooltip(surface, text, cx, cy):
        """Draw a small dark tooltip centred at (cx, cy), shifted above that point."""
        tooltipSurf = saveDateFont.render(text, True, (255, 240, 160))
        padX, padY = 16, 10
        tooltipBg = pygame.Surface((tooltipSurf.get_width() + padX * 2, tooltipSurf.get_height() + padY * 2), pygame.SRCALPHA)
        tooltipBg.fill((30, 20, 10, 210))
        tx = cx - tooltipBg.get_width() // 2
        ty = cy - tooltipBg.get_height() - 8
        tx = max(0, min(tx, VIRTUAL_WIDTH - tooltipBg.get_width()))
        ty = max(0, ty)
        surface.blit(tooltipBg, (tx, ty))
        surface.blit(tooltipSurf, (tx + padX, ty + padY))

    # Tooltip: locked tile buy price
    if hoveredLockedTile is not None:
        hx, hy = hoveredLockedTile
        cx = GRID_START_X + hx * CELL_SIZE + CELL_SIZE // 2
        cy = GRID_START_Y + hy * CELL_SIZE
        drawTooltip(target, f"Buy: {TILE_COL_PRICE[hx]} coins", cx, cy)

    # Tooltip: seed bag prices
    if not paused and not showInfo:
        for cropName, rect in seedRects.items():
            if rect.collidepoint(vMouseX, vMouseY):
                cx = rect.centerx
                cy = rect.top
                drawTooltip(target, f"{cropName.capitalize()}: {cropPrice[cropName]} coins", cx, cy)
                break

    if showInfo:
        pygame.mouse.set_visible(True)
        buildInfoSurface(hoverVx, hoverVy)
        target.blit(infoSurface, (0, 0))
    elif paused:
        pygame.mouse.set_visible(True)
        buildMenuSurface(hoverVx, hoverVy)
        target.blit(menuSurface, (0, 0))

    scale    = min(screenW / VIRTUAL_WIDTH, screenH / VIRTUAL_HEIGHT)
    scaledW  = int(VIRTUAL_WIDTH  * scale)
    scaledH  = int(VIRTUAL_HEIGHT * scale)
    scaled   = pygame.transform.scale(target, (scaledW, scaledH))
    screen.fill((0, 0, 0))
    screen.blit(scaled, ((screenW - scaledW) // 2, (screenH - scaledH) // 2))
    pygame.display.flip()

pygame.quit()
sys.exit()