# startScreen.py
# Shows the title screen when the game first launches.
# The screen slides upward and disappears when the player presses any key
# or clicks the mouse, revealing the main game world underneath.

import pygame
import sys
import os
from texture import loadTextures

# The virtual canvas is 240 tiles wide and 135 tiles tall at 8 pixels per tile,
# giving a final resolution of 1920 x 1080.
virtualWidth  = 1920
virtualHeight = 1080

# How many frames we draw per second. 60 is standard for smooth animation.
fps = 60

# Background music volume during the start screen. pygame uses 0.0 to 1.0.
musicNormalVol = 0.5


def runStartScreen(screen, fullscreen):
    # This function takes over the display until the player dismisses the screen,
    # then returns so the main game loop can begin.
    # screen     - the pygame display surface to draw onto
    # fullscreen - True if running fullscreen, False if windowed

    # pygame.time.Clock lets us limit how fast the loop runs.
    clock = pygame.time.Clock()

    # Load all sprite images from disk into a dictionary.
    textures = loadTextures()

    # Only start the music if it is not already playing.
    # This prevents the track restarting if this function is ever called twice.
    if not pygame.mixer.music.get_busy():
        if os.path.exists("fermfarm theme.mp3"):
            pygame.mixer.music.load("fermfarm theme.mp3")
            pygame.mixer.music.set_volume(musicNormalVol)
            # play(-1) loops the track forever until we stop it manually.
            pygame.mixer.music.play(-1)

    # The big title screen image that fills the whole canvas.
    startImage = textures["startScreen"]

    # offsetY tracks how many pixels the image has slid upward.
    # It starts at 0 (fully visible) and grows until the image is gone.
    offsetY = 0

    # Once the player clicks or presses a key, sliding becomes True.
    sliding = False

    # How many pixels the image moves upward each frame.
    slideSpeed = 4

    # Keep looping until the title image has fully scrolled off the top.
    while True:
        clock.tick(fps)

        # Check every queued event (keyboard, mouse, window close, etc.).
        for event in pygame.event.get():

            # The player closed the window, so quit the whole program.
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Any key press or mouse click starts the slide-away animation.
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                sliding = True

        # If the slide has been triggered, move the image upward each frame.
        if sliding:
            offsetY += slideSpeed

            # Once the image has fully scrolled above the canvas, we are done.
            if offsetY >= virtualHeight:
                return

        # Draw only the part of startImage that has not yet scrolled off.
        # As offsetY increases we copy from lower and lower in the source image,
        # which makes it look like the image is moving upward.
        viewport = pygame.Rect(0, int(offsetY), virtualWidth, virtualHeight)

        screenW, screenH = screen.get_size()

        if screenW == virtualWidth and screenH == virtualHeight:
            # Display exactly matches virtual size, blit directly.
            screen.blit(startImage, (0, 0), viewport)
        else:
            # Display is a different size, so scale the buffer to fill it.
            buf = pygame.Surface((virtualWidth, virtualHeight))
            buf.blit(startImage, (0, 0), viewport)
            scaled = pygame.transform.scale(buf, (screenW, screenH))
            screen.blit(scaled, (0, 0))

        # Push everything we drew to the actual display.
        pygame.display.flip()