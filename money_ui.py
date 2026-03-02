import pygame

DIGIT_WIDTH  = 8 * 8
DIGIT_HEIGHT = 8 * 8
MAX_DIGITS   = 5

numberFont = {}

def initMoneyUi(textures):
    global numberFont

    fontImg = textures["numberFont"]

    for i in range(10):
        numberFont[str(i)] = fontImg.subsurface(
            i * DIGIT_WIDTH, 0,
            DIGIT_WIDTH, DIGIT_HEIGHT
        )


def drawMoney(surface, amount, virtualWidth):
    text = str(amount).zfill(MAX_DIGITS)

    totalWidth = MAX_DIGITS * DIGIT_WIDTH
    x = virtualWidth - totalWidth - 4 * 8
    y = 4 * 8

    for i, digit in enumerate(text):
        surface.blit(
            numberFont[digit],
            (x + i * DIGIT_WIDTH, y)
        )