import pygame
import sys
from texture import load_textures
from crop import load_crops
from money_ui import init_money_ui, draw_money
from cropHarvesting import harvest, CROP_VALUES, Crop_Price, inventory
from startScreen import run_start_screen
import os
import json
from datetime import datetime

pygame.init()

# =========================================================
# NATIVE RESOLUTION  — all sprites scaled ×8 manually
# =========================================================
VIRTUAL_WIDTH  = 240 * 8   # 1920
VIRTUAL_HEIGHT = 135 * 8   # 1080
FPS = 60

# =========================================================
# PAUSE MENU REFERENCE RESOLUTION
# =========================================================
MENU_REF_W = VIRTUAL_WIDTH
MENU_REF_H = VIRTUAL_HEIGHT

# =========================================================
# FULLSCREEN / WINDOWED
# =========================================================
fullscreen = True
info = pygame.display.Info()
screen = pygame.display.set_mode(
    (info.current_w, info.current_h),
    pygame.FULLSCREEN
)
pygame.display.set_caption("FermFarm")

clock = pygame.time.Clock()
run_start_screen(screen, fullscreen)

# =========================================================
# LOAD TEXTURES & CROPS
# =========================================================
textures = load_textures()
init_money_ui(textures)
crops = load_crops(textures)

# =========================================================
# PAUSE MENU SURFACE  — native resolution
# =========================================================
menu_surface = pygame.Surface((MENU_REF_W, MENU_REF_H), pygame.SRCALPHA)

font_path = "sprites/babosorry.ttf"
if not os.path.exists(font_path):
    font_path = None

save_name_font = pygame.font.Font(font_path, 60) if font_path else pygame.font.Font(None, 60)
save_date_font = pygame.font.Font(font_path, 36) if font_path else pygame.font.Font(None, 36)

# =========================================================
# SHOP OBJECTS  — original coords × 8
# =========================================================
shopPlanken_img  = textures["shopPlanken"]
shopPlanken_x, shopPlanken_y = 185*8, 50*8

fermpotKlein_img = textures["fermpotKlein"]
fermpotKlein_x, fermpotKlein_y = 205*8, 44*8

fermpotGroot_img = textures["fermpotGroot"]
fermpotGroot_x, fermpotGroot_y = 208*8, 62*8

wortelzZak_img   = textures["wortelzZak"]
wortelzZak_x, wortelzZak_y   = 186*8, 54*8

tomatenZak_img   = textures["tomatenZak"]
tomatenZak_x, tomatenZak_y   = 198*8, 54*8

chiliZak_img     = textures["chiliZak"]
chiliZak_x, chiliZak_y       = 186*8, 67*8

komkommerZak_img = textures["komkommerZak"]
komkommerZak_x, komkommerZak_y = 210*8, 54*8

koolZak_img      = textures["koolZak"]
koolZak_x, koolZak_y         = 197*8, 67*8

knoflookZak_img  = textures["knoflookZak"]
knoflookZak_x, knoflookZak_y = 209*8, 67*8

# =========================================================
# PAUSE MENU SPRITE
# =========================================================
menu_sprite = textures["menuSprite"]

# =========================================================
# SEED RECTS  — native coords
# =========================================================
seeds_rects = {
    "carrot":   pygame.Rect(wortelzZak_x,   wortelzZak_y,   wortelzZak_img.get_width(),   wortelzZak_img.get_height()),
    "tomato":   pygame.Rect(tomatenZak_x,   tomatenZak_y,   tomatenZak_img.get_width(),   tomatenZak_img.get_height()),
    "chili":    pygame.Rect(chiliZak_x,     chiliZak_y,     chiliZak_img.get_width(),     chiliZak_img.get_height()),
    "cucumber": pygame.Rect(komkommerZak_x, komkommerZak_y, komkommerZak_img.get_width(), komkommerZak_img.get_height()),
    "cabbage":  pygame.Rect(koolZak_x,      koolZak_y,      koolZak_img.get_width(),      koolZak_img.get_height()),
    "garlic":   pygame.Rect(knoflookZak_x,  knoflookZak_y,  knoflookZak_img.get_width(),  knoflookZak_img.get_height()),
}
selected_seed = None

# =========================================================
# FERMENTATION RECTS  — native coords
# =========================================================
fermpotKlein_rect = pygame.Rect(
    fermpotKlein_x, fermpotKlein_y,
    fermpotKlein_img.get_width(), fermpotKlein_img.get_height()
)
fermpotGroot_rect = pygame.Rect(
    fermpotGroot_x, fermpotGroot_y,
    fermpotGroot_img.get_width(), fermpotGroot_img.get_height()
)

# =========================================================
# MONEY
# =========================================================
money = 6

# =========================================================
# BACKGROUND & UI SPRITES
# =========================================================
background            = textures["background"]
calendar_sprite       = textures["Calendar"]
calendarCircle_sprite = textures["CalendarCircle"]

# =========================================================
# GRID  — original coords × 8, cell size × 8
# =========================================================
CELL_SIZE    = 16 * 8   # 128
GRID_COLS    = 7
GRID_ROWS    = 3
GRID_START_X = 0
GRID_START_Y = 87 * 8
grid = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

# =========================================================
# CALENDAR  — original coords × 8
# =========================================================
START_X, START_Y   = 175*8, 87*8
sprite_x, sprite_y = START_X, START_Y
STEP           = 16 * 8   # 128
COLUMNS        = 4
ROWS           = 3
current_column = 0
current_row    = 0
MOVE_INTERVAL  = 5_000
last_move_time = pygame.time.get_ticks()
days_passed    = 0

# =========================================================
# PAUSE STATE
# =========================================================
paused = False

# =========================================================
# SAVE SLOTS
# =========================================================
SAVE_FILE  = "saveslots.json"
save_slots = [
    {"name": "Empty", "date": "", "data": None},
    {"name": "Empty", "date": "", "data": None},
    {"name": "Empty", "date": "", "data": None},
]

if os.path.exists(SAVE_FILE):
    try:
        with open(SAVE_FILE, "r") as f:
            loaded_slots = json.load(f)
            if len(loaded_slots) == 3:
                save_slots = loaded_slots
    except:
        pass

selected_slot = None

# =========================================================
# SAVE / LOAD
# =========================================================
def save_game(slot_index, slot_name):
    global save_slots
    save_data = {
        "money":          money,
        "days_passed":    days_passed,
        "grid":           grid,
        "inventory":      inventory,
        "current_column": current_column,
        "current_row":    current_row,
        "sprite_x":       sprite_x,
        "sprite_y":       sprite_y,
    }
    save_slots[slot_index] = {
        "name": slot_name,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data": save_data,
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(save_slots, f)
    except:
        pass


def load_game(slot_index):
    global money, days_passed, grid, inventory
    global current_column, current_row, sprite_x, sprite_y, last_move_time
    slot = save_slots[slot_index]
    if slot["data"] is None:
        return False
    try:
        data           = slot["data"]
        money          = data["money"]
        days_passed    = data["days_passed"]
        grid           = data["grid"]
        inventory      = data["inventory"]
        current_column = data["current_column"]
        current_row    = data["current_row"]
        sprite_x       = data["sprite_x"]
        sprite_y       = data["sprite_y"]
        last_move_time = pygame.time.get_ticks()
        return True
    except:
        return False


# =========================================================
# COORDINATE HELPER
# Screen → native game coords (handles windowed letterbox)
# =========================================================
def screen_to_virtual(mx, my):
    screen_w, screen_h = screen.get_size()
    if fullscreen:
        # Screen may not exactly match 1920×1080; map proportionally
        vx = mx * VIRTUAL_WIDTH  // screen_w
        vy = my * VIRTUAL_HEIGHT // screen_h
    else:
        scale    = min(screen_w // VIRTUAL_WIDTH, screen_h // VIRTUAL_HEIGHT)
        if scale < 1: scale = 1
        x_offset = (screen_w - VIRTUAL_WIDTH  * scale) // 2
        y_offset = (screen_h - VIRTUAL_HEIGHT * scale) // 2
        vx = (mx - x_offset) // scale
        vy = (my - y_offset) // scale
    return vx, vy


# In native-res mode the menu reference space == game space
def screen_to_menu_ref(mx, my):
    return screen_to_virtual(mx, my)


# =========================================================
# PAUSE MENU SLOT RECTS  — laid out in 1920×1080 space
# Three slots stacked vertically, centred on screen
# =========================================================
SLOT_WIDTH   = 400
SLOT_HEIGHT  = 200
SLOT_SPACING = 25
SLOT_START_X = (VIRTUAL_WIDTH - SLOT_WIDTH) // 3.5 #horizontal adjust
SLOT_START_Y = (VIRTUAL_HEIGHT - (3 * SLOT_HEIGHT + 2 * SLOT_SPACING)) // 2.5  # vertical adjust


def get_slot_rect(i):
    sy = SLOT_START_Y + i * (SLOT_HEIGHT + SLOT_SPACING)
    return pygame.Rect(SLOT_START_X, sy, SLOT_WIDTH, SLOT_HEIGHT)


def build_menu_surface():
    menu_surface.fill((0, 0, 0, 0))

    overlay = pygame.Surface((MENU_REF_W, MENU_REF_H))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    menu_surface.blit(overlay, (0, 0))

    menu_sprite_scaled = pygame.transform.scale(menu_sprite, (MENU_REF_W, MENU_REF_H))
    menu_surface.blit(menu_sprite_scaled, (0, 0))

    for i in range(3):
        slot_rect = get_slot_rect(i)
        pygame.draw.rect(menu_surface, (60, 40, 30), slot_rect)
        pygame.draw.rect(menu_surface, (100, 80, 60), slot_rect, 1)

        menu_surface.set_clip(pygame.Rect(
            slot_rect.x + 1, slot_rect.y + 1,
            slot_rect.w - 2, slot_rect.h - 2
        ))

        name_surf = save_name_font.render(save_slots[i]["name"], False, (255, 255, 255))
        menu_surface.blit(name_surf, (slot_rect.x + 20, slot_rect.y + 20))

        if save_slots[i]["date"]:
            parts    = save_slots[i]["date"].split(" ")
            date_str = parts[0][2:] if parts else ""
            time_str = parts[1] if len(parts) > 1 else ""
            date_surf = save_date_font.render(date_str, False, (180, 180, 180))
            time_surf = save_date_font.render(time_str, False, (180, 180, 180))
            menu_surface.blit(date_surf, (slot_rect.x + 20, slot_rect.y + 100))
            menu_surface.blit(time_surf, (slot_rect.x + 20, slot_rect.y + 148))

        menu_surface.set_clip(None)


# =========================================================
# MAIN LOOP
# =========================================================
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # ---------- KEYBOARD ----------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = not paused
                if not paused:
                    last_move_time = pygame.time.get_ticks()
            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(
                        (info.current_w, info.current_h), pygame.FULLSCREEN
                    )
                else:
                    screen = pygame.display.set_mode(
                        (VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.RESIZABLE
                    )

        if event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # ---------- LEFT CLICK ----------
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if paused:
                rx, ry = screen_to_menu_ref(mx, my)

                for i in range(3):
                    if get_slot_rect(i).collidepoint(rx, ry):
                        if event.button == 1:
                            if save_slots[i]["data"] is not None:
                                load_game(i)
                                paused = False
                        elif event.button == 3:
                            save_game(i, f"Farm {i + 1}")
                        break

                continue

            vx, vy = screen_to_virtual(mx, my)

            if fermpotKlein_rect.collidepoint(vx, vy):
                for crop_name in inventory:
                    if inventory[crop_name] > 0:
                        inventory[crop_name] -= 1
                        money += CROP_VALUES[crop_name] // 2
                        break
                continue

            if fermpotGroot_rect.collidepoint(vx, vy):
                fermented = 0
                for crop_name in inventory:
                    while inventory[crop_name] > 0 and fermented < 2:
                        inventory[crop_name] -= 1
                        money += CROP_VALUES[crop_name] // 2
                        fermented += 1
                    if fermented >= 2:
                        break
                continue

            clicked_seed = None
            for crop_name, rect in seeds_rects.items():
                if rect.collidepoint(vx, vy):
                    clicked_seed = crop_name
                    break

            if clicked_seed and selected_seed is None:
                if money >= Crop_Price[clicked_seed]:
                    money -= Crop_Price[clicked_seed]
                    selected_seed = clicked_seed
                continue

            if selected_seed is not None:
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE
                if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                    if grid[gx][gy] is None:
                        grid[gx][gy] = {
                            "crop":        selected_seed,
                            "day_planted": days_passed,
                            "stage":       0,
                        }
                        selected_seed = None

        # ---------- RIGHT CLICK (harvest) ----------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            vx, vy = screen_to_virtual(*pygame.mouse.get_pos())
            gx = (vx - GRID_START_X) // CELL_SIZE
            gy = (vy - GRID_START_Y) // CELL_SIZE
            harvested = harvest(grid, gx, gy, crops)
            if harvested:
                money += CROP_VALUES[harvested]
                inventory[harvested] = inventory.get(harvested, 0) + 1

    # =====================================================
    # TIME / GROWTH
    # =====================================================
    if not paused:
        now = pygame.time.get_ticks()
        if now - last_move_time >= MOVE_INTERVAL:
            last_move_time = now
            days_passed += 1

            for x in range(GRID_COLS):
                for y in range(GRID_ROWS):
                    cell = grid[x][y]
                    if cell:
                        crop  = crops[cell["crop"]]
                        age   = days_passed - cell["day_planted"]
                        stage = age // crop["growth_days_per_stage"]
                        cell["stage"] = min(stage, crop["max_stage"])

            sprite_x       += STEP
            current_column += 1
            if current_column >= COLUMNS:
                current_column = 0
                sprite_x       = START_X
                sprite_y      += STEP
                current_row   += 1
                if current_row >= ROWS:
                    current_row        = 0
                    sprite_x, sprite_y = START_X, START_Y

    # =====================================================
    # DRAW
    # =====================================================
    screen_w, screen_h = screen.get_size()

    # If the physical screen differs from 1920×1080 (e.g. ultrawide / 4K),
    # draw into an intermediate surface then scale once.
    if screen_w == VIRTUAL_WIDTH and screen_h == VIRTUAL_HEIGHT:
        target = screen
    else:
        target = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    target.blit(background,      (0, 0))
    target.blit(shopPlanken_img,  (shopPlanken_x,  shopPlanken_y))
    target.blit(fermpotKlein_img, (fermpotKlein_x, fermpotKlein_y))
    target.blit(fermpotGroot_img, (fermpotGroot_x, fermpotGroot_y))
    target.blit(wortelzZak_img,   (wortelzZak_x,   wortelzZak_y))
    target.blit(tomatenZak_img,   (tomatenZak_x,   tomatenZak_y))
    target.blit(komkommerZak_img, (komkommerZak_x, komkommerZak_y))
    target.blit(chiliZak_img,     (chiliZak_x,     chiliZak_y))
    target.blit(knoflookZak_img,  (knoflookZak_x,  knoflookZak_y))
    target.blit(koolZak_img,      (koolZak_x,      koolZak_y))
    draw_money(target, money, VIRTUAL_WIDTH)

    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            cell = grid[x][y]
            if cell:
                crop = crops[cell["crop"]]
                sprite = crop["stages"][cell["stage"]]
                # If the sprite hasn't been pre-scaled to CELL_SIZE, scale it now
                if sprite.get_width() != CELL_SIZE or sprite.get_height() != CELL_SIZE:
                    sprite = pygame.transform.scale(sprite, (CELL_SIZE, CELL_SIZE))
                target.blit(
                    sprite,
                    (GRID_START_X + x * CELL_SIZE, GRID_START_Y + y * CELL_SIZE)
                )

    target.blit(calendar_sprite,       (176*8, 72*8))
    target.blit(calendarCircle_sprite, (sprite_x, sprite_y))

    if paused:
        build_menu_surface()
        target.blit(menu_surface, (0, 0))

    if target is not screen:
        scaled = pygame.transform.scale(target, (screen_w, screen_h))
        screen.blit(scaled, (0, 0))

    pygame.display.flip()

pygame.quit()
sys.exit()