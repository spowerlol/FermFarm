import pygame
import sys
import random
from textures import load_textures

# =====================
# INSTELLINGEN
# =====================

GRID_BREEDTE = 8
GRID_HOOGTE = 6
VAKJE_GROOTTE = 64

GROEI_TIJD = 10_000
GROEI_KANS = 0.5
FPS = 60

# =====================
# PYGAME
# =====================

pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Farming Sim")

SCHERM_BREEDTE, SCHERM_HOOGTE = screen.get_size()
clock = pygame.time.Clock()

textures = load_textures(VAKJE_GROOTTE)
font = pygame.font.SysFont(None, 24)
small_font = pygame.font.SysFont(None, 18)

# =====================
# AFMETINGEN
# =====================

FARM_W = GRID_BREEDTE * VAKJE_GROOTTE
FARM_H = GRID_HOOGTE * VAKJE_GROOTTE

RECHTS_X = SCHERM_BREEDTE - 320

# =====================
# POSITIES
# =====================

# Farm
FARM_X = 20
FARM_Y = SCHERM_HOOGTE - FARM_H - 20

# Shed (boven farm, zelfde breedte)
SHED_X = FARM_X
SHED_Y = 20

# Geld
GELD_X = RECHTS_X + 80
GELD_Y = 20
GELD_W = 200
GELD_H = 60

# TV
TV_X = RECHTS_X + 40
TV_Y = 120
TV_W = 240
TV_H = 160

# Shop
SHOP_X = RECHTS_X + 80
SHOP_Y = TV_Y + TV_H + 20
SHOP_W = 200
SHOP_H = 60

# Kalender
CAL_X = RECHTS_X + 20
CAL_Y = SHOP_Y + SHOP_H + 20
CAL_W = 280
CAL_H = 200

# =====================
# DATA
# =====================

grid = [[1 for _ in range(GRID_BREEDTE)] for _ in range(GRID_HOOGTE)]
laatste_groei = pygame.time.get_ticks()
geld = 0

# =====================
# FUNCTIES
# =====================

def box(x, y, w, h, titel=None):
    pygame.draw.rect(screen, (150, 150, 150), (x, y, w, h), border_radius=10)
    pygame.draw.rect(screen, (60, 60, 60), (x, y, w, h), 2, border_radius=10)
    if titel:
        t = font.render(titel, True, (0, 0, 0))
        screen.blit(t, (x + 10, y + 10))

def kalender_tekenen():
    rows, cols = 4, 4
    cel_w = CAL_W // cols
    cel_h = CAL_H // rows

    for r in range(rows):
        for c in range(cols):
            x = CAL_X + c * cel_w
            y = CAL_Y + r * cel_h
            pygame.draw.rect(screen, (200, 200, 200), (x, y, cel_w, cel_h), 1)
            dag = r * cols + c + 1
            txt = small_font.render(str(dag), True, (0, 0, 0))
            screen.blit(txt, (x + 5, y + 5))

# =====================
# HOOFDLOOP
# =====================

running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if (FARM_X <= mx < FARM_X + FARM_W and
                FARM_Y <= my < FARM_Y + FARM_H):

                gx = (mx - FARM_X) // VAKJE_GROOTTE
                gy = (my - FARM_Y) // VAKJE_GROOTTE

                if grid[gy][gx] == 4:
                    grid[gy][gx] = 1
                    geld += 1

    # Groei
    now = pygame.time.get_ticks()
    if now - laatste_groei >= GROEI_TIJD:
        laatste_groei = now
        for y in range(GRID_HOOGTE):
            for x in range(GRID_BREEDTE):
                if grid[y][x] < 4 and random.random() < GROEI_KANS:
                    grid[y][x] += 1

    # =====================
    # TEKENEN
    # =====================

    screen.fill((120, 180, 100))

    # Shed
    box(SHED_X, SHED_Y, FARM_W, FARM_H, "SHED")

    # Farm
    for y in range(GRID_HOOGTE):
        for x in range(GRID_BREEDTE):
            screen.blit(
                textures[grid[y][x]],
                (FARM_X + x * VAKJE_GROOTTE,
                 FARM_Y + y * VAKJE_GROOTTE)
            )

    # Geld
    box(GELD_X, GELD_Y, GELD_W, GELD_H)
    geld_txt = font.render(f"{geld:02}", True, (0, 0, 0))
    screen.blit(geld_txt, (GELD_X + 80, GELD_Y + 15))

    # TV
    box(TV_X, TV_Y, TV_W, TV_H, "TV")

    # Shop
    box(SHOP_X, SHOP_Y, SHOP_W, SHOP_H, "SHOP")

    # Kalender
    box(CAL_X, CAL_Y, CAL_W, CAL_H, "CALENDAR")
    kalender_tekenen()

    pygame.display.flip()

pygame.quit()
sys.exit()
