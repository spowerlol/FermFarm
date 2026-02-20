import pygame

DIGIT_WIDTH  = 8 * 8   # 64
DIGIT_HEIGHT = 8 * 8   # 64
MAX_DIGITS   = 5

number_font = {}

def init_money_ui(textures):
    global number_font

    font_img = textures["NumberFont"]

    for i in range(10):
        number_font[str(i)] = font_img.subsurface(
            i * DIGIT_WIDTH, 0,
            DIGIT_WIDTH, DIGIT_HEIGHT
        )


def draw_money(surface, amount, virtual_width):
    text = str(amount).zfill(MAX_DIGITS)

    total_width = MAX_DIGITS * DIGIT_WIDTH
    x = virtual_width - total_width - 4 * 8   # 4px margin, scaled
    y = 4 * 8                                  # 4px top margin, scaled

    for i, digit in enumerate(text):
        surface.blit(
            number_font[digit],
            (x + i * DIGIT_WIDTH, y)
        )