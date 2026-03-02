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
run_start_screen(screen, fullscreen)

# ── Music ──────────────────────────────────────────────────────────────────────
MUSIC_NORMAL_VOL = 0.5
MUSIC_DIM_VOL    = 0.2
music_enabled    = True
# ──────────────────────────────────────────────────────────────────────────────

textures = load_textures()
init_money_ui(textures)
crops = load_crops(textures)

menu_surface = pygame.Surface((MENU_REF_W, MENU_REF_H), pygame.SRCALPHA)
info_surface = pygame.Surface((MENU_REF_W, MENU_REF_H), pygame.SRCALPHA)

font_path = "sprites/babosorry.ttf"
if not os.path.exists(font_path):
    font_path = None

save_name_font  = pygame.font.Font(font_path, 60)
save_date_font  = pygame.font.Font(font_path, 36)
button_font     = pygame.font.Font(font_path, 96)
info_text_font  = pygame.font.Font(font_path, 44)
info_title_font = pygame.font.Font(font_path, 72)

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
menu_sprite = textures["menuSprite"]

seeds_rects = {
    "carrot":   pygame.Rect(wortelzZak_x,   wortelzZak_y,   wortelzZak_img.get_width(),   wortelzZak_img.get_height()),
    "tomato":   pygame.Rect(tomatenZak_x,   tomatenZak_y,   tomatenZak_img.get_width(),   tomatenZak_img.get_height()),
    "chili":    pygame.Rect(chiliZak_x,     chiliZak_y,     chiliZak_img.get_width(),     chiliZak_img.get_height()),
    "cucumber": pygame.Rect(komkommerZak_x, komkommerZak_y, komkommerZak_img.get_width(), komkommerZak_img.get_height()),
    "cabbage":  pygame.Rect(koolZak_x,      koolZak_y,      koolZak_img.get_width(),      koolZak_img.get_height()),
    "garlic":   pygame.Rect(knoflookZak_x,  knoflookZak_y,  knoflookZak_img.get_width(),  knoflookZak_img.get_height()),
}
selected_seed = None

fermpotKlein_rect = pygame.Rect(fermpotKlein_x, fermpotKlein_y, fermpotKlein_img.get_width(), fermpotKlein_img.get_height())
fermpotGroot_rect = pygame.Rect(fermpotGroot_x, fermpotGroot_y, fermpotGroot_img.get_width(), fermpotGroot_img.get_height())

money = 6
background            = textures["background"]
calendar_sprite       = textures["Calendar"]
calendarCircle_sprite = textures["CalendarCircle"]

CELL_SIZE    = 16 * 8
GRID_COLS    = 7
GRID_ROWS    = 3
GRID_START_X = 0
GRID_START_Y = 87 * 8
grid = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

START_X, START_Y   = 175*8, 87*8
sprite_x, sprite_y = START_X, START_Y
STEP           = 16 * 8
COLUMNS        = 4
ROWS           = 3
current_column = 0
current_row    = 0
MOVE_INTERVAL  = 5_000
last_move_time = pygame.time.get_ticks()
days_passed    = 0

paused    = False
show_info = True  # open info screen on boot

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

# Slot layout
SLOT_WIDTH   = 400
SLOT_HEIGHT  = 200
SLOT_SPACING = 25
SLOT_START_X = (VIRTUAL_WIDTH - SLOT_WIDTH) // 3.5
SLOT_START_Y = (VIRTUAL_HEIGHT - (3 * SLOT_HEIGHT + 2 * SLOT_SPACING)) // 2.5
SLOT_BOTTOM_Y = SLOT_START_Y + 3 * SLOT_HEIGHT + 2 * SLOT_SPACING

def get_slot_rect(i):
    sy = SLOT_START_Y + i * (SLOT_HEIGHT + SLOT_SPACING)
    return pygame.Rect(SLOT_START_X, sy, SLOT_WIDTH, SLOT_HEIGHT)

# Side buttons
SIDE_BTN_W = 380
SIDE_BTN_H = 100
SIDE_BTN_X = int(SLOT_START_X) + SLOT_WIDTH + 100

# Divide the original 3-slot space evenly across 4 buttons
total_btn_area = SLOT_BOTTOM_Y - SLOT_START_Y
BTN_SPACING = 20
BTN_H_4 = (total_btn_area - 3 * BTN_SPACING) // 4

fullscreen_btn_rect = pygame.Rect(
    SIDE_BTN_X,
    int(SLOT_START_Y),
    SIDE_BTN_W,
    BTN_H_4
)

info_btn_rect = pygame.Rect(
    SIDE_BTN_X,
    int(SLOT_START_Y + 1 * (BTN_H_4 + BTN_SPACING)),
    SIDE_BTN_W,
    BTN_H_4
)

quit_btn_rect = pygame.Rect(
    SIDE_BTN_X,
    int(SLOT_START_Y + 3 * (BTN_H_4 + BTN_SPACING)),
    SIDE_BTN_W,
    BTN_H_4
)

audio_btn_rect = pygame.Rect(
    SIDE_BTN_X,
    int(SLOT_START_Y + 2 * (BTN_H_4 + BTN_SPACING)),
    SIDE_BTN_W,
    BTN_H_4
)

# Info screen constants
INFO_PAD_X         = 160
INFO_TOP_Y         = 160
INFO_SCROLL_TOP    = 280
INFO_SCROLL_BOTTOM = 920
INFO_SCROLL_H      = INFO_SCROLL_BOTTOM - INFO_SCROLL_TOP

CLOSE_BTN_W = 300
CLOSE_BTN_H = 90
close_btn_rect = pygame.Rect((VIRTUAL_WIDTH - CLOSE_BTN_W) // 2, 960, CLOSE_BTN_W, CLOSE_BTN_H)

INFO_FILE = "info.txt"
_raw_info_lines = []
if os.path.exists(INFO_FILE):
    try:
        with open(INFO_FILE, "r", encoding="utf-8") as f:
            _raw_info_lines = f.read().splitlines()
    except:
        _raw_info_lines = ["Could not load info.txt"]

_max_text_w = VIRTUAL_WIDTH - INFO_PAD_X * 2

def _wrap_lines(raw_lines, font, max_w):
    wrapped = []
    for raw in raw_lines:
        if raw.strip() == "":
            wrapped.append("")
            continue
        words = raw.split()
        current = ""
        for word in words:
            test = (current + " " + word).strip()
            if font.size(test)[0] <= max_w:
                current = test
            else:
                if current:
                    wrapped.append(current)
                current = word
        if current:
            wrapped.append(current)
    return wrapped

info_lines        = _wrap_lines(_raw_info_lines, info_text_font, _max_text_w)
INFO_LINE_H       = info_text_font.get_linesize() + 6
info_scroll_y     = 0
info_scroll_speed = 40
_info_total_h     = len(info_lines) * INFO_LINE_H


# ── Music helpers ──────────────────────────────────────────────────────────────
def set_music_volume_for_state():
    """Set the correct volume based on game state and music_enabled toggle."""
    if not music_enabled:
        pygame.mixer.music.set_volume(0)
    elif paused or show_info:
        pygame.mixer.music.set_volume(MUSIC_DIM_VOL)
    else:
        pygame.mixer.music.set_volume(MUSIC_NORMAL_VOL)
# ──────────────────────────────────────────────────────────────────────────────


def save_game(slot_index, slot_name):
    global save_slots
    save_data = {
        "money": money, "days_passed": days_passed, "grid": grid,
        "inventory": inventory, "current_column": current_column,
        "current_row": current_row, "sprite_x": sprite_x, "sprite_y": sprite_y,
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
        data = slot["data"]
        money = data["money"]; days_passed = data["days_passed"]; grid = data["grid"]
        inventory = data["inventory"]; current_column = data["current_column"]
        current_row = data["current_row"]; sprite_x = data["sprite_x"]; sprite_y = data["sprite_y"]
        last_move_time = pygame.time.get_ticks()
        return True
    except:
        return False


def screen_to_virtual(mx, my):
    screen_w, screen_h = screen.get_size()
    if fullscreen:
        vx = mx * VIRTUAL_WIDTH  // screen_w
        vy = my * VIRTUAL_HEIGHT // screen_h
    else:
        scale    = min(screen_w / VIRTUAL_WIDTH, screen_h / VIRTUAL_HEIGHT)
        x_offset = (screen_w - VIRTUAL_WIDTH  * scale) / 2
        y_offset = (screen_h - VIRTUAL_HEIGHT * scale) / 2
        vx = int((mx - x_offset) / scale)
        vy = int((my - y_offset) / scale)
    return vx, vy

def screen_to_menu_ref(mx, my):
    return screen_to_virtual(mx, my)

def toggle_fullscreen():
    global fullscreen, screen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)

def draw_side_button(surface, rect, label, hovered=False):
    if hovered:
        color = (255, 245, 190)
        shadow_surf = button_font.render(label, False, (70, 40, 5))
        for ox, oy in ((-3, 3), (3, 3), (-3, -3), (3, -3)):
            sx = rect.x + (rect.w - shadow_surf.get_width())  // 2 + ox
            sy = rect.y + (rect.h - shadow_surf.get_height()) // 2 + oy
            surface.blit(shadow_surf, (sx, sy))
    else:
        color = (140, 110, 70)
    text_surf = button_font.render(label, False, color)
    tx = rect.x + (rect.w - text_surf.get_width())  // 2
    ty = rect.y + (rect.h - text_surf.get_height()) // 2
    surface.blit(text_surf, (tx, ty))


def build_menu_surface(mouse_vx=0, mouse_vy=0):
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
        menu_surface.set_clip(pygame.Rect(slot_rect.x+1, slot_rect.y+1, slot_rect.w-2, slot_rect.h-2))
        name_surf = save_name_font.render(save_slots[i]["name"], False, (255, 255, 255))
        menu_surface.blit(name_surf, (slot_rect.x + 20, slot_rect.y + 20))
        if save_slots[i]["date"]:
            parts = save_slots[i]["date"].split(" ")
            date_str = parts[0][2:] if parts else ""
            time_str = parts[1] if len(parts) > 1 else ""
            date_surf = save_date_font.render(date_str, False, (180, 180, 180))
            time_surf = save_date_font.render(time_str, False, (180, 180, 180))
            menu_surface.blit(date_surf, (slot_rect.x + 20, slot_rect.y + 100))
            menu_surface.blit(time_surf, (slot_rect.x + 20, slot_rect.y + 148))
        menu_surface.set_clip(None)

    fs_label = "Windowed" if fullscreen else "Fullscreen"
    draw_side_button(menu_surface, fullscreen_btn_rect, fs_label,
                     hovered=fullscreen_btn_rect.collidepoint(mouse_vx, mouse_vy))
    draw_side_button(menu_surface, info_btn_rect, "Info",
                     hovered=info_btn_rect.collidepoint(mouse_vx, mouse_vy))
    draw_side_button(menu_surface, quit_btn_rect, "Quit",
                     hovered=quit_btn_rect.collidepoint(mouse_vx, mouse_vy))

    # Audio toggle button
    audio_label = "Music: ON" if music_enabled else "Music: OFF"
    draw_side_button(menu_surface, audio_btn_rect, audio_label,
                     hovered=audio_btn_rect.collidepoint(mouse_vx, mouse_vy))


def build_info_surface(mouse_vx=0, mouse_vy=0):
    global info_scroll_y
    info_surface.fill((0, 0, 0, 0))

    overlay = pygame.Surface((MENU_REF_W, MENU_REF_H))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    info_surface.blit(overlay, (0, 0))
    menu_sprite_scaled = pygame.transform.scale(menu_sprite, (MENU_REF_W, MENU_REF_H))
    info_surface.blit(menu_sprite_scaled, (0, 0))

    title_surf = info_title_font.render("How to Play", False, (255, 240, 180))
    info_surface.blit(title_surf, ((VIRTUAL_WIDTH - title_surf.get_width()) // 2, INFO_TOP_Y))

    max_scroll = max(0, _info_total_h - INFO_SCROLL_H)
    info_scroll_y = max(0, min(info_scroll_y, max_scroll))

    scroll_clip = pygame.Rect(INFO_PAD_X, INFO_SCROLL_TOP, VIRTUAL_WIDTH - INFO_PAD_X * 2, INFO_SCROLL_H)
    info_surface.set_clip(scroll_clip)

    y = INFO_SCROLL_TOP - info_scroll_y
    for line in info_lines:
        if line == "":
            y += INFO_LINE_H // 2
            continue
        line_surf = info_text_font.render(line, False, (220, 200, 160))
        info_surface.blit(line_surf, (INFO_PAD_X, y))
        y += INFO_LINE_H

    info_surface.set_clip(None)

    fade_h = 60
    top_fade = pygame.Surface((VIRTUAL_WIDTH - INFO_PAD_X * 2, fade_h), pygame.SRCALPHA)
    for i in range(fade_h):
        alpha = int(200 * (1 - i / fade_h))
        pygame.draw.line(top_fade, (20, 12, 5, alpha), (0, i), (top_fade.get_width(), i))
    info_surface.blit(top_fade, (INFO_PAD_X, INFO_SCROLL_TOP))

    bot_fade = pygame.Surface((VIRTUAL_WIDTH - INFO_PAD_X * 2, fade_h), pygame.SRCALPHA)
    for i in range(fade_h):
        alpha = int(200 * (i / fade_h))
        pygame.draw.line(bot_fade, (20, 12, 5, alpha), (0, i), (bot_fade.get_width(), i))
    info_surface.blit(bot_fade, (INFO_PAD_X, INFO_SCROLL_BOTTOM - fade_h))

    if info_scroll_y > 0:
        up_surf = info_text_font.render("scroll up", False, (160, 130, 80))
        info_surface.blit(up_surf, ((VIRTUAL_WIDTH - up_surf.get_width()) // 2, INFO_SCROLL_TOP + 8))
    if info_scroll_y < max_scroll:
        dn_surf = info_text_font.render("scroll down", False, (160, 130, 80))
        info_surface.blit(dn_surf, ((VIRTUAL_WIDTH - dn_surf.get_width()) // 2, INFO_SCROLL_BOTTOM - 52))

    draw_side_button(info_surface, close_btn_rect, "Close",
                     hovered=close_btn_rect.collidepoint(mouse_vx, mouse_vy))


# Dim music on startup since info screen opens on boot
set_music_volume_for_state()

# =========================================================
# MAIN LOOP
# =========================================================
running = True
while running:
    clock.tick(FPS)

    _mx, _my = pygame.mouse.get_pos()
    hover_vx, hover_vy = screen_to_menu_ref(_mx, _my)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if show_info:
                if event.key == pygame.K_ESCAPE:
                    show_info = False
                    paused    = True
                    set_music_volume_for_state()
            elif paused:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    last_move_time = pygame.time.get_ticks()
                    set_music_volume_for_state()
            else:
                if event.key == pygame.K_ESCAPE:
                    paused = True
                    set_music_volume_for_state()
                if event.key == pygame.K_F11:
                    toggle_fullscreen()

        if event.type == pygame.MOUSEWHEEL and show_info:
            info_scroll_y -= event.y * info_scroll_speed

        if event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            rx, ry = screen_to_menu_ref(mx, my)

            if show_info:
                if close_btn_rect.collidepoint(rx, ry):
                    show_info = False
                    paused    = True
                    set_music_volume_for_state()
                continue

            if paused:
                if fullscreen_btn_rect.collidepoint(rx, ry):
                    toggle_fullscreen()
                    continue
                if info_btn_rect.collidepoint(rx, ry):
                    show_info     = True
                    info_scroll_y = 0
                    set_music_volume_for_state()
                    continue
                if quit_btn_rect.collidepoint(rx, ry):
                    running = False
                    continue
                if audio_btn_rect.collidepoint(rx, ry):
                    music_enabled = not music_enabled
                    set_music_volume_for_state()
                    continue
                for i in range(3):
                    if get_slot_rect(i).collidepoint(rx, ry):
                        if save_slots[i]["data"] is not None:
                            load_game(i)
                            paused = False
                            set_music_volume_for_state()
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
                        grid[gx][gy] = {"crop": selected_seed, "day_planted": days_passed, "stage": 0}
                        selected_seed = None

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            mx, my = pygame.mouse.get_pos()
            rx, ry = screen_to_menu_ref(mx, my)
            if paused and not show_info:
                for i in range(3):
                    if get_slot_rect(i).collidepoint(rx, ry):
                        save_game(i, f"Farm {i + 1}")
                        break
            elif not paused and not show_info:
                vx, vy = screen_to_virtual(mx, my)
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE
                harvested = harvest(grid, gx, gy, crops)
                if harvested:
                    money += CROP_VALUES[harvested]
                    inventory[harvested] = inventory.get(harvested, 0) + 1

    if not paused and not show_info:
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

    screen_w, screen_h = screen.get_size()
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
                crop   = crops[cell["crop"]]
                sprite = crop["stages"][cell["stage"]]
                if sprite.get_width() != CELL_SIZE or sprite.get_height() != CELL_SIZE:
                    sprite = pygame.transform.scale(sprite, (CELL_SIZE, CELL_SIZE))
                target.blit(sprite, (GRID_START_X + x * CELL_SIZE, GRID_START_Y + y * CELL_SIZE))

    target.blit(calendar_sprite,       (176*8, 72*8))
    target.blit(calendarCircle_sprite, (sprite_x, sprite_y))

    if show_info:
        build_info_surface(hover_vx, hover_vy)
        target.blit(info_surface, (0, 0))
    elif paused:
        build_menu_surface(hover_vx, hover_vy)
        target.blit(menu_surface, (0, 0))

    scale    = min(screen_w / VIRTUAL_WIDTH, screen_h / VIRTUAL_HEIGHT)
    scaled_w = int(VIRTUAL_WIDTH  * scale)
    scaled_h = int(VIRTUAL_HEIGHT * scale)
    scaled   = pygame.transform.scale(target, (scaled_w, scaled_h))
    screen.fill((0, 0, 0))
    screen.blit(scaled, ((screen_w - scaled_w) // 2, (screen_h - scaled_h) // 2))
    pygame.display.flip()

pygame.quit()
sys.exit()