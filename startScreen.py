import pygame
import sys
from texture import load_textures

VIRTUAL_WIDTH  = 240 * 8   # 1920
VIRTUAL_HEIGHT = 135 * 8   # 1080
FPS = 60

def run_start_screen(screen, fullscreen):
    clock = pygame.time.Clock()
    textures = load_textures()

    # startScreen image is DOUBLE HEIGHT (1920 × 2160 after ×8 scale)
    start_image = textures["startScreen"]

    offset_y = 0
    sliding = False
    SLIDE_SPEED = 0.5 * 8   # keep the same visual speed at native res

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                sliding = True

        if sliding:
            offset_y += SLIDE_SPEED
            if offset_y >= VIRTUAL_HEIGHT:
                return

        viewport = pygame.Rect(0, int(offset_y), VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

        screen_w, screen_h = screen.get_size()

        if screen_w == VIRTUAL_WIDTH and screen_h == VIRTUAL_HEIGHT:
            # Screen matches exactly — blit direct
            screen.blit(start_image, (0, 0), viewport)
        else:
            # Draw into intermediate surface, then scale once to fill screen
            buf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            buf.blit(start_image, (0, 0), viewport)
            scaled = pygame.transform.scale(buf, (screen_w, screen_h))
            screen.blit(scaled, (0, 0))

        pygame.display.flip()