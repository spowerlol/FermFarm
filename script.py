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

#coördinaten van de shopplanken
shopPlanken_img = textures["shopPlanken"]
shopPlanken_x = 185
shopPlanken_y = 50

#Coördinaten van fermpot1
fermpotKlein_img = textures["fermpotKlein"]
fermpotKlein_x = 205
fermpotKlein_y = 44

#coördinaten van fermpot2
fermpotGroot_img = textures["fermpotGroot"]
fermpotGroot_x = 208
fermpotGroot_y = 62

#coördinaten van wortelzzak
wortelzZak_img = textures["wortelzZak"]
wortelzZak_x = 186
wortelzZak_y = 54

#Coördinaten van tomatenzak
tomatenZak_img = textures["tomatenZak"]
tomatenZak_x = 198
tomatenZak_y = 54

#Coördinaten van chilizak
chiliZak_img = textures["chiliZak"]
chiliZak_x = 186
chiliZak_y = 67

#Coördinaten van komkommerzak
komkommerZak_img = textures["komkommerZak"]
komkommerZak_x = 210
komkommerZak_y = 54

#Coördinaten van koolzak
koolZak_img = textures["koolZak"]
koolZak_x = 197
koolZak_y = 67

#Coördinaten van knoflookzak
knoflookZak_img = textures["knoflookZak"]
knoflookZak_x = 209
knoflookZak_y = 67

init_money_ui(textures)
crops = load_crops(textures)

# ------------------------------------------------------------
# ANDERE PLANTEN KUNNEN PLANTEN
# ------------------------------------------------------------

seeds_rects = {
    "carrot": pygame.Rect(wortelzZak_x, wortelzZak_y,
                    wortelzZak_img.get_width(), wortelzZak_img.get_height()),

    "tomato": pygame.Rect(tomatenZak_x, tomatenZak_y,tomatenZak_img.get_width(),
                          tomatenZak_img.get_height()),

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

#======================================
#FERMENTATION
#======================================
fermpotKlein_rect = pygame.Rect(fermpotKlein_x, fermpotKlein_y,
                           fermpotKlein_img.get_width(), fermpotKlein_img.get_height())

fermpotGroot_rect = pygame.Rect(fermpotGroot_x, fermpotGroot_y,
                                fermpotGroot_img.get_width(), fermpotGroot_img.get_height())
# =========================================================
# MONEY COUNTER
# =========================================================
money = 6


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
calendarCircle_sprite = textures["CalendarCircle"]
calendar_sprite = textures["Calendar"]
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

MOVE_INTERVAL = 5_000  # 1 day = 60 seconds
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

            #===================
            # Kleine pot ( 1 stuk)
            #====================
            if fermpotKlein_rect.collidepoint(vx,vy):
                for crop_name in inventory:
                    if inventory[crop_name] > 0:
                        inventory[crop_name] -= 1
                        money +=  CROP_VALUES[crop_name] // 2
                        break
                continue

            #==================
            #Grote pot (2 stuks)
            #===================
            if fermpotGroot_rect.collidepoint(vx,vy):
                fermented_count = 0
                for crop_name in inventory:
                    while inventory[crop_name] > 0 and fermented_count < 2:
                        inventory[crop_name] -= 1
                        money += CROP_VALUES[crop_name] // 2
                        fermented_count += 1
                    if fermented_count >= 2:
                        break
                continue


            #===========================
            # checken of je zaadzak klikt
            #===========================

            clicked_seed = None
            for crop_name, rect in seeds_rects.items():
                if rect.collidepoint(vx, vy):
                    clicked_seed = crop_name
                    break

            #economie
            if clicked_seed == "tomato" and selected_seed is None:
                if money >= Crop_Price["tomato"]:
                    money -= Crop_Price["tomato"]
                    selected_seed = "tomato"

            if clicked_seed == "carrot" and selected_seed is None:
                if money >= Crop_Price["carrot"]:
                    money -= Crop_Price["carrot"]
                    selected_seed = "carrot"

            if clicked_seed == "cucumber" and selected_seed is None:
                if money >= Crop_Price["cucumber"]:
                    money -= Crop_Price["cucumber"]
                    selected_seed = "cucumber"

            if clicked_seed == "chili" and selected_seed is None:
                if money >= Crop_Price["chili"]:
                    money -= Crop_Price["chili"]
                    selected_seed = "chili"



                #planten op grid
            if selected_seed == "tomato":
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE

            if selected_seed == "carrot":
                gx = (vx - GRID_START_X) // CELL_SIZE
                gy = (vy - GRID_START_Y) // CELL_SIZE

                if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                    if grid[gx][gy] is None:
                        grid[gx][gy] = {
                            "crop": "tomato",
                            "day_planted": days_passed,
                            "stage": 0
                        }
                        selected_seed = None

                if 0 <= gx < GRID_COLS and 0 <= gy < GRID_ROWS:
                    if grid[gx][gy] is None:
                        grid[gx][gy] = {
                            "crop": "carrot",
                            "day_planted": days_passed,
                            "stage": 0
                        }
                        selected_seed = None


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

            harvested = harvest(grid,gx,gy,crops)
            if harvested:
                money += CROP_VALUES[harvested]
                inventory[harvested] = inventory.get(harvested, 0) + 1

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
    virtual.blit(shopPlanken_img, (shopPlanken_x, shopPlanken_y))

    #Draw fermentatie potten
    virtual.blit(fermpotKlein_img, (fermpotKlein_x, fermpotKlein_y))
    virtual.blit(fermpotGroot_img, (fermpotGroot_x, fermpotGroot_y))

    #Draw zaadjes
    virtual.blit(wortelzZak_img, (wortelzZak_x, wortelzZak_y))
    virtual.blit(tomatenZak_img, (tomatenZak_x, tomatenZak_y))
    virtual.blit(komkommerZak_img, (komkommerZak_x, komkommerZak_y))
    virtual.blit(chiliZak_img, (chiliZak_x, chiliZak_y))
    virtual.blit(knoflookZak_img, (knoflookZak_x, knoflookZak_y))
    virtual.blit(koolZak_img, (koolZak_x, koolZak_y))

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
    virtual.blit(calendar_sprite, (176,72))
    virtual.blit(calendarCircle_sprite, (sprite_x, sprite_y))

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
