# =============================================================================
# startScreen.py
# Shows the title/splash screen when the game first launches.
# The screen slides upward and disappears when the player presses any key
# or clicks the mouse, revealing the main game world underneath.
# =============================================================================

import pygame
import sys
import os
from texture import loadTextures  # Our own module that loads all sprite images

# -----------------------------------------------------------------------------
# SCREEN & TIMING CONSTANTS
# The virtual canvas is 240 tiles wide and 135 tiles tall, each tile being
# 8 pixels, giving a final virtual resolution of 1920 x 1080.
# -----------------------------------------------------------------------------

# Virtual canvas width in pixels.  240 tiles * 8 pixels/tile = 1920.
VIRTUAL_WIDTH  = 1920

# Virtual canvas height in pixels.  135 tiles * 8 pixels/tile = 1080.
VIRTUAL_HEIGHT = 1080

# How many frames we want to draw per second. 60 is standard for smooth motion.
FPS = 60

# The normal background-music volume while the start screen is visible.
# pygame uses a 0.0 (silent) to 1.0 (full volume) scale.
MUSIC_NORMAL_VOL = 0.5


# =============================================================================
# runStartScreen(screen, fullscreen)
# Call this function once at startup. It takes over the display until the
# player dismisses the screen, then returns so the main game loop can begin.
#
# Parameters:
#   screen     - the pygame display Surface to draw onto
#   fullscreen - bool; True if we are running in fullscreen mode
# =============================================================================
def runStartScreen(screen, fullscreen):

    # Create a Clock object. We call clock.tick(FPS) once per frame to cap
    # the frame rate and prevent the game from running absurdly fast.
    clock = pygame.time.Clock()

    # Load all sprite/texture images from disk into a dictionary.
    textures = loadTextures()

    # Start the background music only if it is not already playing.
    # This prevents the track restarting if runStartScreen is called twice.
    if not pygame.mixer.music.get_busy():
        if os.path.exists("fermfarm theme.mp3"):
            pygame.mixer.music.load("fermfarm theme.mp3")
            pygame.mixer.music.set_volume(MUSIC_NORMAL_VOL)
            # play(-1) means loop the track forever until we stop it manually.
            pygame.mixer.music.play(-1)

    # Grab the start-screen image from the texture dictionary.
    startImage = textures["startScreen"]

    # offsetY tracks how many pixels the image has slid upward so far.
    # It starts at 0 (image fully visible) and increases until the whole
    # image has scrolled off the top of the screen.
    offsetY = 0

    # "sliding" becomes True the moment the player presses a key or clicks.
    # Before that the start screen just sits still.
    sliding = False

    # How fast the screen slides up, in pixels per frame.
    # Original design value was 0.5 tiles/frame, scaled by 8 = 4 pixels/frame.
    SLIDE_SPEED = 4

    # -------------------------------------------------------------------------
    # START SCREEN LOOP
    # Keeps running until offsetY reaches the full canvas height, at which
    # point the start image has completely scrolled off the top and we return.
    # -------------------------------------------------------------------------
    while True:
        # Wait long enough to maintain our target frame rate (60 FPS).
        clock.tick(FPS)

        # Process all queued events (keyboard, mouse, window close, etc.).
        for event in pygame.event.get():

            # The player closed the window quit immediately.
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Any key press OR any mouse button click triggers the slide.
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                sliding = True

        # If the slide has been triggered, move the viewport upward each frame.
        if sliding:
            offsetY += SLIDE_SPEED

            # Once the image has scrolled past the full canvas height,
            # the start screen is gone exit this function and return
            # control to the main game loop.
            if offsetY >= VIRTUAL_HEIGHT:
                return

        # ----------------------------------------------------------------
        # RENDERING
        # We only want to show the portion of the start-screen image that
        # has NOT yet scrolled off the top. We do this with a "viewport"
        # rect that moves down the source image as offsetY increases.
        # ----------------------------------------------------------------

        # viewport defines which region of startImage to copy onto the screen.
        # As offsetY grows, we start copying from lower and lower in the image,
        # which makes it look like the image is sliding upward.
        viewport = pygame.Rect(0, int(offsetY), VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

        screenW, screenH = screen.get_size()

        if screenW == VIRTUAL_WIDTH and screenH == VIRTUAL_HEIGHT:
            # The display is exactly the virtual canvas size — blit directly.
            screen.blit(startImage, (0, 0), viewport)
        else:
            # The display is a different size (e.g. windowed or a different
            # monitor resolution). We blit to an intermediate buffer at the
            # virtual resolution, then scale that buffer to fill the screen.
            buf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
            buf.blit(startImage, (0, 0), viewport)
            scaled = pygame.transform.scale(buf, (screenW, screenH))
            screen.blit(scaled, (0, 0))

        # Push everything we just drew to the actual display.
        pygame.display.flip()