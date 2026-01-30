# money_ui.py
import pygame

DIGIT_WIDTH = 8     # MUST match your sprite
DIGIT_HEIGHT = 8
MAX_DIGITS = 5

number_font = {}

def init_money_ui(textures):
    """
    Call once after load_textures()
    """
    global number_font

    font_img = textures["NumberFont"]

    for i in range(10):
        number_font[str(i)] = font_img.subsurface(
            i * DIGIT_WIDTH, 0,
            DIGIT_WIDTH, DIGIT_HEIGHT
        )


def draw_money(surface, amount, virtual_width):
    """
    Draws a fixed 5-digit counter in the top-right
    """
    text = str(amount).zfill(MAX_DIGITS)

    total_width = MAX_DIGITS * DIGIT_WIDTH
    x = virtual_width - total_width - 4
    y = 4

    for i, digit in enumerate(text):
        surface.blit(
            number_font[digit],
            (x + i * DIGIT_WIDTH, y)
        )
