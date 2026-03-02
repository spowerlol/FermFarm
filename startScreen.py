import pygame
import sys
import os
from texture import load_textures

VIRTUAL_WIDTH  = 240 * 8
VIRTUAL_HEIGHT = 135 * 8
FPS = 60

MUSIC_NORMAL_VOL = 0.5

def run_start_screen(screen, fullscreen):
    clock = pygame.time.Clock()
    textures = load_textures()

    if not pygame.mixer.music.get_busy():
        if os.path.exists("fermfarm theme.mp3"):
            pygame.mixer.music.load("fermfarm theme.mp3")
            pygame.mixer.music.set_volume(MUSIC_NORMAL_VOL)
            pygame.mixer.music.play(-1)

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