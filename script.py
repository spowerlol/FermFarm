import pygame
import sys
from texture import load_textures
#hello world
pygame.init()
# --- virtual resolution (pixel art size)
VIRTUAL_WIDTH = 240
VIRTUAL_HEIGHT = 135
FPS = 60

# --- fullscreen window
info = pygame.display.Info()
screen = pygame.display.set_mode(
    (info.current_w, info.current_h),
    pygame.FULLSCREEN
)
pygame.display.set_caption("FerFarm")

# --- virtual render surface
virtual = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# --- load textures
textures = load_textures()

# --- force background to exact virtual size
background = pygame.transform.scale(
    textures["background"],
    (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)
)

# --- sprite
sprite = textures["CalendarCircle"]

# --- sprite start position
START_X = 175
START_Y = 87
sprite_x = START_X
sprite_y = START_Y

# --- calendar movement setup
STEP = 16
COLUMNS = 4
ROWS = 3

current_column = 0
current_row = 0

MOVE_INTERVAL = 60_000  # 1 minute = 1 day
last_move_time = pygame.time.get_ticks()

# --- day counter
days_passed = 0

# --- font (pixel-friendly size)
font = pygame.font.Font(None, 14)

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # --- calendar sprite timed movement ---
    now = pygame.time.get_ticks()
    if now - last_move_time >= MOVE_INTERVAL:
        last_move_time = now

        days_passed += 1  # count days

        # move right
        sprite_x += STEP
        current_column += 1

        # end of row
        if current_column >= COLUMNS:
            current_column = 0
            sprite_x = START_X

            sprite_y += STEP
            current_row += 1

            # end of 3rd row -> full visual reset
            if current_row >= ROWS:
                current_row = 0
                sprite_x = START_X
                sprite_y = START_Y

    # --- DRAW ORDER ---
    virtual.blit(background, (0, 0))
    virtual.blit(sprite, (sprite_x, sprite_y))



    # --- integer scaling ---
    screen_w, screen_h = screen.get_size()
    scale = min(
        screen_w // VIRTUAL_WIDTH,
        screen_h // VIRTUAL_HEIGHT
    )

    scaled_surface = pygame.transform.scale(
        virtual,
        (VIRTUAL_WIDTH * scale, VIRTUAL_HEIGHT * scale)
    )

    # --- center with letterboxing ---
    x_offset = (screen_w - scaled_surface.get_width()) // 2
    y_offset = (screen_h - scaled_surface.get_height()) // 2

    screen.fill((0, 0, 0))
    screen.blit(scaled_surface, (x_offset, y_offset))
    pygame.display.flip()

pygame.quit()
sys.exit()
