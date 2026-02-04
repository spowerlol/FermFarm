import pygame
import sys
from texture import load_textures
from crop import load_crops
from money_ui import init_money_ui, draw_money
from cropHarvesting import harvest

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

# =========================================================
# LOAD TEXTURES & CROPS
# =========================================================
textures = load_textures()

#coördinaten van de shopplanken
shopplanken_img = textures["shopplanken"]
shopplanken_x = 185
shopplanken_y = 50

#Coördinaten van fermpot1
fermpotklein_img = textures["fermpotklein"]
fermpotklein_x = 205
fermpotklein_y = 44

#coördinaten van fermpot2
fermpotgroot_img = textures["fermpotgroot"]
fermpotgroot_x = 208
fermpotgroot_y = 62

#coördinaten van wortelzzak
wortelzzak_img = textures["wortelzzak"]
wortelzzak_x = 186
wortelzzak_y = 54

#Coördinaten van tomatenzak
tomatenzak_img = textures["tomatenzak"]
tomatenzak_x = 198
tomatenzak_y = 54

#Coördinaten van chilizak
chilizak_img = textures["chilizak"]
chilizak_x = 186
chilizak_y = 67

#Coördinaten van komkommerzak
komkommerzak_img = textures["komkommerzak"]
komkommerzak_x = 210
komkommerzak_y = 54


init_money_ui(textures)
crops = load_crops(textures)

# =========================================================
# MONEY COUNTER
# =========================================================
money = 0

DIGIT_WIDTH = 8
DIGIT_HEIGHT = 8
MAX_DIGITS = 5

number_font = {}
font_img = textures["NumberFont"]
for i in range(10):
    number_font[str(i)] = font_img.subsurface(
        i * DIGIT_WIDTH, 0,
        DIGIT_WIDTH, DIGIT_HEIGHT
    )

background = pygame.transform.scale(
    textures["background"],
    (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
)
calendar_sprite = textures["CalendarCircle"]

# =========================================================
# GRID (PLANTING)
# =========================================================
CELL_SIZE = 16
GRID_COLS = 7
GRID_ROWS = 3
GRID_START_X = 0
GRID_START_Y = 87
grid = [[None for _ in range(GRID_ROWS)] for _ in range(GRID_COLS)]

# =========================================================
# ITEMS / SEEDS
# =========================================================
TomaatZaad = True
itemheld = True

# =========================================================
# CALENDAR
# =========================================================
START_X = 175
START_Y = 87
sprite_x = START_X
sprite_y = START_Y

STEP = 16
COLUMNS = 4
ROWS = 3

current_column = 0
current_row = 0

MOVE_INTERVAL = 60_000  # 1 day = 60 seconds
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

        # ESC to quit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # F11 to toggle fullscreen/windowed
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

        # Handle window resize in windowed mode
        if event.type == pygame.VIDEORESIZE and not fullscreen:
            screen = pygame.display.set_mode(
                (event.w, event.h),
                pygame.RESIZABLE
            )

        # -------------------------------------------------
        # PLACE PLANT (LEFT CLICK)
        # -------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if TomaatZaad and itemheld:
                mx, my = pygame.mouse.get_pos()
                screen_w, screen_h = screen.get_size()

                if fullscreen:
                    # scale to full screen
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

                if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                    if grid[gx][gy] is None:
                        grid[gx][gy] = {
                            "crop": "tomato",
                            "day_planted": days_passed,
                            "stage": 0
                        }
                        TomaatZaad = False  # consume seed

        # -------------------------------------------------
        # HARVEST PLANT (RIGHT CLICK)
        # -------------------------------------------------
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

            money += harvest(grid, gx, gy, crops)

    # =====================================================
    # CALENDAR TIMED MOVEMENT + PLANT GROWTH
    # =====================================================
    now = pygame.time.get_ticks()
    if now - last_move_time >= MOVE_INTERVAL:
        last_move_time = now
        days_passed += 1

        # grow all plants
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                cell = grid[x][y]
                if cell is not None:
                    crop = crops[cell["crop"]]
                    age = days_passed - cell["day_planted"]
                    stage = age // crop["growth_days_per_stage"]
                    cell["stage"] = min(stage, crop["max_stage"])

        # move calendar
        sprite_x += STEP
        current_column += 1

        if current_column >= COLUMNS:
            current_column = 0
            sprite_x = START_X
            sprite_y += STEP
            current_row += 1

            if current_row >= ROWS:
                current_row = 0
                sprite_x = START_X
                sprite_y = START_Y

    # =====================================================
    # DRAW (VIRTUAL)
    # =====================================================
    virtual.blit(background, (0, 0))

    #Draw shopplanken
    virtual.blit(shopplanken_img, (shopplanken_x, shopplanken_y))

    #Draw fermentatie potten
    virtual.blit(fermpotklein_img, (fermpotklein_x, fermpotklein_y))
    virtual.blit(fermpotgroot_img, (fermpotgroot_x, fermpotgroot_y))

    #Draw zaadjes
    virtual.blit(wortelzzak_img, (wortelzzak_x, wortelzzak_y))
    virtual.blit(tomatenzak_img, (tomatenzak_x, tomatenzak_y))
    virtual.blit(komkommerzak_img, (komkommerzak_x, komkommerzak_y))
    virtual.blit(chilizak_img, (chilizak_x, chilizak_y))

    draw_money(virtual, money, VIRTUAL_WIDTH)

    # draw plants
    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            cell = grid[x][y]
            if cell is not None:
                crop = crops[cell["crop"]]
                virtual.blit(
                    crop["stages"][cell["stage"]],
                    (GRID_START_X + x * CELL_SIZE, GRID_START_Y + y * CELL_SIZE)
                )

    # draw calendar
    virtual.blit(calendar_sprite, (sprite_x, sprite_y))

    # =====================================================
    # SCALE TO SCREEN
    # =====================================================
    screen_w, screen_h = screen.get_size()

    if fullscreen:
        # stretch to fullscreen
        scaled = pygame.transform.scale(virtual, (screen_w, screen_h))
        screen.blit(scaled, (0, 0))
    else:
        # scale with correct aspect ratio
        scale = min(screen_w // VIRTUAL_WIDTH, screen_h // VIRTUAL_HEIGHT)
        scaled_width = VIRTUAL_WIDTH * scale
        scaled_height = VIRTUAL_HEIGHT * scale
        scaled = pygame.transform.scale(virtual, (scaled_width, scaled_height))
        x_offset = (screen_w - scaled_width) // 2
        y_offset = (screen_h - scaled_height) // 2
        screen.fill((0, 0, 0))
        screen.blit(scaled, (x_offset, y_offset))

    pygame.display.flip()

pygame.quit()
sys.exit()
