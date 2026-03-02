import pygame
import sys
import os
from texture import loadTextures

VIRTUAL_WIDTH  = 240 * 8
VIRTUAL_HEIGHT = 135 * 8
FPS = 60

MUSIC_NORMAL_VOL = 0.5

def runStartScreen(screen, fullscreen):
    clock = pygame.time.Clock()
    textures = loadTextures()

    if not pygame.mixer.music.get_busy():
        if os.path.exists("fermfarm theme.mp3"):
            pygame.mixer.music.load("fermfarm theme.mp3")
            pygame.mixer.music.set_volume(MUSIC_NORMAL_VOL)
            pygame.mixer.music.play(-1)

    startImage = textures["startScreen"]

    offsetY = 0
    sliding = False
    SLIDE_SPEED = 0.5 * 8

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                sliding = True

        if sliding:
            offsetY += SLIDE_SPEED
            if offsetY >= VIRTUAL_HEIGHT:
                return

        viewport = pygame.Rect(0, int(offsetY), VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

        screenW, screenH = screen.get_size()

        if screenW == VIRTUAL_WIDTH and screenH == VIRTUAL_HEIGHT:
            screen.blit(startImage, (0, 0), viewport)
        else:
            buf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            buf.blit(startImage, (0, 0), viewport)
            scaled = pygame.transform.scale(buf, (screenW, screenH))
            screen.blit(scaled, (0, 0))

        pygame.display.flip()