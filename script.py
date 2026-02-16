import pygame
import sys
from texture import load_textures
from crop import load_crops
from money_ui import init_money_ui, draw_money
from cropHarvesting import harvest, CROP_VALUES, Crop_Price, inventory
from startScreen import run_start_screen

pygame.init()

# =========================================================
# VIRTUAL RESOLUTION
# =========================================================
VIRTUAL_WIDTH = 240
VIRTUAL_HEIGHT = 135
FPS = 60

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

# =========================================================
# VIRTUAL SURFACE
# =========================================================
virtual = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
clock = pygame.time.Clock()
run_start_screen(screen, fullscreen)

# =========================================================
# LOAD TEXTURES & CROPS
# =========================================================
textures = load_textures()
init_money_ui(textures)
crops = load_crops(textures)

# =========================================================
# SHOP OBJECTS
# =========================================================
shopPlanken_img = textures["shopPlanken"]
shopPlanken_x, shopPlanken_y = 185, 50

fermpotKlein_img = textures["fermpotKlein"]
fermpotKlein_x, fermpotKlein_y = 205, 44

fermpotGroot_img = textures["fermpotGroot"]
fermpotGroot_x, fermpotGroot_y = 208, 62

wortelzZak_img = textures["wortelzZak"]
wortelzZak_x, wortelzZak_y = 186, 54

tomatenZak_img = textures["tomatenZak"]
tomatenZak_x, tomatenZak_y = 198, 54

chiliZak_img = textures["chiliZak"]
chiliZak_x, chiliZak_y = 186, 67

komkommerZak_img = textures["komkommerZak"]
komkommerZak_x, komkommerZak_y = 210, 54

koolZak_img = textures["koolZak"]
koolZak_x, koolZak_y = 197, 67

knoflookZak_img = textures["knoflookZak"]
knoflookZak_x, knoflookZak_y = 209, 67

# =========================================================
# SEED RECTS (CONSISTENT NAMES)
# =========================================================
seeds_rects = {
    "carrot": pygame.Rect(wortelzZak_x, wortelzZak_y,
                          wortelzZak_img.get_width(), wortelzZak_img.get_height()),
    "tomato": pygame.Rect(tomatenZak_x, tomatenZak_y,
                          tomatenZak_img.get_width(), tomatenZak_img.get_height()),
    "chili": pygame.Rect(chiliZak_x, chiliZak_y,
                         chiliZak_img.get_width(), chiliZak_img.get_height()),
    "cucumber": pygame.Rect(komkommerZak_x, komkommerZak_y,
                            komkommerZak_img.get_width(), komkommerZak_img.get_height()),
    "cabbage": pygame.Rect(koolZak_x, koolZak_y,
                           koolZak_img.get_width(), koolZak_img.get_height()),
    "garlic": pygame.Rect(knoflookZak_x, knoflookZak_y,
                          knoflookZak_img.get_width(), knoflookZak_img.get_height()),
}

selected_seed = None

# =========================================================
# FERMENTATION RECTS
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
# BACKGROUND & UI
# =========================================================
background = pygame.transform.scale(
    textures["background"],
    (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
)

calendarCircle_sprite = textures["CalendarCircle"]
calendar_sprite = textures["Calendar"]

# =========================================================
# GRID
# =========================================================
CELL_SIZE = 16
GRID_COLS = 7
GRID_ROWS = 3
GRID_START_X = 0
GRID_START_Y = 87

grid = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

# =========================================================
# CALENDAR
# =========================================================
START_X, START_Y = 175, 87
sprite_x, sprite_y = START_X, START_Y

STEP = 16
COLUMNS = 4
ROWS = 3

current_column = 0
current_row = 0

MOVE_INTERVAL = 5_000
last_move_time = pygame.time.get_ticks()
days_passed = 0

# =========================================================
# MAIN LOOP
# =========================================================
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # ----------------- KEYBOARD -----------------
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            if event.key == pygame.K_F11:
                fullscreen = not fullscreen
                if fullscreen:
                    screen = pygame.display.set_mode(
                        (info.current_w, info.current_h),
                        pygame.FULLSCREEN
                    )
                else:
                    screen = pygame.display.set_mode(
                        (VIRTUAL_WIDTH * 4, VIRTUAL_HEIGHT * 4),
                        pygame.RESIZABLE
                    )

        if event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # ----------------- LEFT CLICK -----------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            mx, my = pygame.mouse.get_pos()
            screen_w, screen_h = screen.get_size()

            if fullscreen:
                vx = mx * VIRTUAL_WIDTH // screen_w
                vy = my * VIRTUAL_HEIGHT // screen_h
            else:
                scale = min(screen_w // VIRTUAL_WIDTH, screen_h // VIRTUAL_HEIGHT)
                x_offset = (screen_w - VIRTUAL_WIDTH * scale) // 2
                y_offset = (screen_h - VIRTUAL_HEIGHT * scale) // 2
                vx = (mx - x_offset) // scale
                vy = (my - y_offset) // scale

            # ---------- FERMENT SMALL ----------
            if fermpotKlein_rect.collidepoint(vx, vy):
                for crop_name in inventory:
                    if inventory[crop_name] > 0:
                        inventory[crop_name] -= 1
                        money += CROP_VALUES[crop_name] // 2
                        break
                continue

            # ---------- FERMENT BIG ----------
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

            # ---------- CLICK SEED ----------
            clicked_seed = None
            for crop_name, rect in seeds_rects.items():
                if rect.collidepoint(vx, vy):
                    clicked_seed = crop_name
                    break

            # BUY SEED
            if clicked_seed and selected_seed is None:
                if money >= Crop_Price[clicked_seed]:
                    money -= Crop_Price[clicked_seed]
                    selected_seed = clicked_seed
                continue

            # ---------- PLANT ----------
            if selected_seed is not None:
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE

                if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                    if grid[gx][gy] is None:
                        grid[gx][gy] = {
                            "crop": selected_seed,
                            "day_planted": days_passed,
                            "stage": 0
                        }
                        selected_seed = None

        # ----------------- RIGHT CLICK HARVEST -----------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:

            mx, my = pygame.mouse.get_pos()
            screen_w, screen_h = screen.get_size()

            if fullscreen:
                vx = mx * VIRTUAL_WIDTH // screen_w
                vy = my * VIRTUAL_HEIGHT // screen_h
            else:
                scale = min(screen_w // VIRTUAL_WIDTH, screen_h // VIRTUAL_HEIGHT)
                x_offset = (screen_w - VIRTUAL_WIDTH * scale) // 2
                y_offset = (screen_h - VIRTUAL_HEIGHT * scale) // 2
                vx = (mx - x_offset) // scale
                vy = (my - y_offset) // scale

            gx = (vx - GRID_START_X) // CELL_SIZE
            gy = (vy - GRID_START_Y) // CELL_SIZE

            harvested = harvest(grid, gx, gy, crops)

            if harvested:
                money += CROP_VALUES[harvested]
                inventory[harvested] = inventory.get(harvested, 0) + 1

    # =====================================================
    # TIME / GROWTH
    # =====================================================
    now = pygame.time.get_ticks()
    if now - last_move_time >= MOVE_INTERVAL:

        last_move_time = now
        days_passed += 1

        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = grid[x][y]
                if cell:
                    crop = crops[cell["crop"]]
                    age = days_passed - cell["day_planted"]
                    stage = age // crop["growth_days_per_stage"]
                    cell["stage"] = min(stage, crop["max_stage"])

        sprite_x += STEP
        current_column += 1

        if current_column >= COLUMNS:
            current_column = 0
            sprite_x = START_X
            sprite_y += STEP
            current_row += 1

            if current_row >= ROWS:
                current_row = 0
                sprite_x, sprite_y = START_X, START_Y

    # =====================================================
    # DRAW
    # =====================================================
    virtual.blit(background, (0, 0))

    virtual.blit(shopPlanken_img, (shopPlanken_x, shopPlanken_y))
    virtual.blit(fermpotKlein_img, (fermpotKlein_x, fermpotKlein_y))
    virtual.blit(fermpotGroot_img, (fermpotGroot_x, fermpotGroot_y))

    virtual.blit(wortelzZak_img, (wortelzZak_x, wortelzZak_y))
    virtual.blit(tomatenZak_img, (tomatenZak_x, tomatenZak_y))
    virtual.blit(komkommerZak_img, (komkommerZak_x, komkommerZak_y))
    virtual.blit(chiliZak_img, (chiliZak_x, chiliZak_y))
    virtual.blit(knoflookZak_img, (knoflookZak_x, knoflookZak_y))
    virtual.blit(koolZak_img, (koolZak_x, koolZak_y))

    draw_money(virtual, money, VIRTUAL_WIDTH)

    # draw crops
    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            cell = grid[x][y]
            if cell:
                crop = crops[cell["crop"]]
                virtual.blit(
                    crop["stages"][cell["stage"]],
                    (GRID_START_X + x * CELL_SIZE,
                     GRID_START_Y + y * CELL_SIZE)
                )

    virtual.blit(calendar_sprite, (176, 72))
    virtual.blit(calendarCircle_sprite, (sprite_x, sprite_y))

    # =====================================================
    # SCALE
    # =====================================================
    screen_w, screen_h = screen.get_size()

    if fullscreen:
        scaled = pygame.transform.scale(virtual, (screen_w, screen_h))
        screen.blit(scaled, (0, 0))
    else:
        scale = min(screen_w // VIRTUAL_WIDTH, screen_h // VIRTUAL_HEIGHT)
        scaled = pygame.transform.scale(
            virtual,
            (VIRTUAL_WIDTH * scale, VIRTUAL_HEIGHT * scale)
        )
        x_offset = (screen_w - scaled.get_width()) // 2
        y_offset = (screen_h - scaled.get_height()) // 2
        screen.fill((0, 0, 0))
        screen.blit(scaled, (x_offset, y_offset))

    pygame.display.flip()

pygame.quit()
sys.exit()
