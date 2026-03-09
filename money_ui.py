# =============================================================================
# money_ui.py
# Handles drawing the player's coin balance on screen using a custom
# pixel-art number font stored as a sprite sheet.
#
# The font sheet is one long image with all 10 digit sprites (0-9) lined up
# side by side. We slice out each digit and store it in a dictionary so we
# can look up any digit by its string character ("0", "1", ..., "9").
# =============================================================================

import pygame

# -----------------------------------------------------------------------------
# DIGIT DIMENSIONS
# Each digit in the font sprite sheet occupies an 8x8 tile area, and because
# everything in this game is scaled up by 8, each digit is 64x64 pixels on
# the virtual canvas.
# -----------------------------------------------------------------------------

# Width of one digit sprite in pixels.  8 tiles * 8 pixels/tile = 64.
DIGIT_WIDTH  = 64

# Height of one digit sprite in pixels.  8 tiles * 8 pixels/tile = 64.
DIGIT_HEIGHT = 64

# How many digit characters to always display.
# The balance is zero-padded to this length, e.g. 42 coins -> "00042".
MAX_DIGITS = 5

# This dictionary will be filled by initMoneyUi().
# Keys are string digits "0"-"9", values are pygame.Surface objects
# containing the corresponding sprite cut from the font sheet.
numberFont = {}


def initMoneyUi(textures):
    """
    Slice the font sprite sheet into individual digit surfaces and store them
    in the module-level 'numberFont' dictionary.

    Call this ONCE after loadTextures() at game startup, before the main loop.

    Parameters:
        textures (dict): the texture dictionary from loadTextures().
                         We expect textures["numberFont"] to be the sprite sheet.
    """
    global numberFont

    # Grab the full number-font sprite sheet image.
    fontImg = textures["numberFont"]

    # Loop over each digit 0 through 9.
    for i in range(10):

        # subsurface(x, y, width, height) cuts a rectangular region out of
        # fontImg without copying pixel data — it's efficient.
        # The digits are laid out left-to-right, so digit i starts at
        # x = i * DIGIT_WIDTH on the sheet.
        numberFont[str(i)] = fontImg.subsurface(
            i * DIGIT_WIDTH,    # x: how far along the sheet this digit is
            0,                   # y: always at the top of the sheet
            DIGIT_WIDTH,         # width of one digit
            DIGIT_HEIGHT         # height of one digit
        )


def drawMoney(surface, amount, virtualWidth):
    """
    Draw the player's coin balance in the top-right corner of the screen
    using the custom pixel-art digit font.

    Parameters:
        surface      (pygame.Surface): the virtual canvas to draw onto.
        amount       (int)           : the player's current coin balance.
        virtualWidth (int)           : the full width of the virtual canvas
                                       in pixels, used to right-align the display.
    """

    # Convert the amount to a string and left-pad it with zeros so it always
    # takes up exactly MAX_DIGITS characters.  e.g. 7 -> "00007".
    text = str(amount).zfill(MAX_DIGITS)

    # Calculate the total pixel width of the entire number display.
    totalWidth = MAX_DIGITS * DIGIT_WIDTH   # 5 digits * 64 px = 320 px

    # Place the number 4 tiles (32 px) from the right edge of the canvas,
    # and 4 tiles (32 px) down from the top.
    x = virtualWidth - totalWidth - 32   # right-align with a 32 px margin
    y = 32                               # 32 px from the top

    # Draw each digit character one by one, advancing x by DIGIT_WIDTH each time.
    for i, digit in enumerate(text):
        surface.blit(
            numberFont[digit],                # the sprite for this digit
            (x + i * DIGIT_WIDTH, y)          # position: offset by digit index
        )