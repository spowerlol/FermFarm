import pygame
import sys
from texture import load_textures

VIRTUAL_WIDTH = 240
VIRTUAL_HEIGHT = 135
FPS = 60

def run_start_screen(screen, fullscreen):
    clock = pygame.time.Clock()
    textures = load_textures()

    virtual = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

    # startScreen image is DOUBLE HEIGHT (240 x 270)
    start_image = textures["startScreen"]

    offset_y = 0
    sliding = False
    SLIDE_SPEED = 0.5

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

        # VIEWPORT INTO TALL IMAGE
        viewport = pygame.Rect(
            0,
            offset_y,
            VIRTUAL_WIDTH,
            VIRTUAL_HEIGHT
        )

        virtual.blit(start_image, (0, 0), viewport)

        # scale exactly like the game
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
            x_off = (screen_w - scaled.get_width()) // 2
            y_off = (screen_h - scaled.get_height()) // 2
            screen.fill((0, 0, 0))
            screen.blit(scaled, (x_off, y_off))

        pygame.display.flip()
