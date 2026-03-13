# money_ui.py
# Draws the player's coin balance on screen using a custom pixel-art digit font.
#
# The font image is one long strip with all 10 digit sprites (0-9) side by side.
# We cut out each digit and store it in a dictionary so any digit can be looked
# up by its character: numberFont["3"] gives the sprite for the number 3.

import pygame

# Each digit in the font image is 64 x 64 pixels on the virtual canvas.
digitWidth  = 64
digitHeight = 64

# Always display this many digit characters, left-padded with zeros.
# For example, 42 coins is shown as "00042".
maxDigits = 5

# This dictionary is filled by initMoneyUi().
# Keys are string characters "0" through "9".
# Values are pygame.Surface objects (the cropped digit sprites).
numberFont = {}


def initMoneyUi(textures):
    # Slice the font image into individual digit surfaces and store them.
    # Call this ONCE at startup, after loadTextures(), before the main loop.
    # textures - the dictionary returned by loadTextures()

    global numberFont

    # The full sprite sheet that contains all 10 digits in a row.
    fontImg = textures["numberFont"]

    # Cut out each digit (0-9) from the strip.
    for i in range(10):
        # subsurface() cuts a rectangle out of fontImg without copying pixels.
        # Digit i starts at x = i * digitWidth along the strip.
        numberFont[str(i)] = fontImg.subsurface(
            i * digitWidth,  # x position of this digit on the strip
            0,               # y is always 0 (only one row of digits)
            digitWidth,
            digitHeight
        )


def drawMoney(surface, amount, virtualWidth):
    # Draw the player's coin total in the top-right corner of the screen.
    # surface      - the virtual canvas surface to draw onto
    # amount       - the player's current coin total
    # virtualWidth - full canvas width in pixels, used to right-align the text

    # Convert the number to a string padded with leading zeros.
    text = str(amount).zfill(maxDigits)

    # Total pixel width of all digits side by side.
    totalWidth = maxDigits * digitWidth

    # Position the number near the top-right corner with a small margin.
    x = virtualWidth - totalWidth - 32
    y = 32

    # Blit each digit sprite one by one, moving right by digitWidth each time.
    for i, digit in enumerate(text):
        surface.blit(
            numberFont[digit],
            (x + i * digitWidth, y)
        )