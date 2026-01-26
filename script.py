import pygame
import sys
from texture import load_textures

pygame.init()

# =========================================================
# VIRTUAL RESOLUTION
# =========================================================
VIRTUAL_WIDTH = 240
VIRTUAL_HEIGHT = 135
FPS = 60

# =========================================================
# FULLSCREEN WINDOW
# =========================================================
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
# LOAD TEXTURES
# =========================================================
textures = load_textures()

background = pygame.transform.scale(
    textures["background"],
    (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
)

plant_sprite = textures["TomaatPlant1"]
calendar_sprite = textures["CalendarCircle"]

# =========================================================
# GRID (PLANTING)
# =========================================================
CELL_SIZE = 16
GRID_COLS = 7
GRID_ROWS = 3

GRID_START_X = 0
GRID_START_Y = 87

# each cell will store: None or {"seed": str, "sprite": Surface}
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

MOVE_INTERVAL = 60_000
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

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        # -------------------------------------------------
        # PLACE PLANT
        # -------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if TomaatZaad and itemheld:
                mx, my = pygame.mouse.get_pos()

                # screen → virtual coords
                screen_w, screen_h = screen.get_size()
                scale = min(
                    screen_w // VIRTUAL_WIDTH,
                    screen_h // VIRTUAL_HEIGHT
                )

                x_offset = (screen_w - VIRTUAL_WIDTH * scale) // 2
                y_offset = (screen_h - VIRTUAL_HEIGHT * scale) // 2

                vx = (mx - x_offset) // scale
                vy = (my - y_offset) // scale

                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE

                if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                    if grid[gx][gy] is None:
                        grid[gx][gy] = {
                            "seed": "tomato",
                            "sprite": plant_sprite,
                            "day_planted": days_passed
                        }

                        TomaatZaad = False  # consume seed

    # =====================================================
    # CALENDAR TIMED MOVEMENT
    # =====================================================
    now = pygame.time.get_ticks()
    if now - last_move_time >= MOVE_INTERVAL:
        last_move_time = now
        days_passed += 1

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

    # draw plants
    for x in range(GRID_COLS):
        for y in range(GRID_ROWS):
            cell = grid[x][y]
            if cell is not None:
                virtual.blit(
                    cell["sprite"],
                    (
                        GRID_START_X + x * CELL_SIZE,
                        GRID_START_Y + y * CELL_SIZE
                    )
                )

    # draw calendar
    virtual.blit(calendar_sprite, (sprite_x, sprite_y))

    # =====================================================
    # SCALE TO SCREEN
    # =====================================================
    screen_w, screen_h = screen.get_size()
    scale = min(
        screen_w // VIRTUAL_WIDTH,
        screen_h // VIRTUAL_HEIGHT
    )

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
