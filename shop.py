# shop.py
# Defines the layout of the in-game shop and the data for each purchasable item.
# The actual click-handling lives in script.py; this file provides the data
# that script.py reads so everything about the shop is in one place.

import pygame

# X position of the first shop item on the virtual canvas (pixels).
shopXStart = 1456

# Y position of the first shop item on the virtual canvas (pixels).
shopYStart = 416

# Width of each shop item's clickable area in pixels.
shopItemW = 128

# Height of each shop item's clickable area in pixels.
shopItemH = 128

# Pixel gap between items so they don't look squished together.
shopGap = 16

# Coin cost of a single tomato seed, kept as a named value so it is
# easy to find and change without hunting through the list below.
tomatoSeedPrice = 5

# The list of items the player can buy from the shop shelf.
# Each entry is a dictionary describing one purchasable item:
#   "id"    -> unique name used in game logic
#   "price" -> how many coins it costs
#   "rect"  -> the clickable area on screen as a pygame.Rect
#   "gives" -> what the player receives when they buy it
shopItems = [
    {
        "id"   : "tomatoSeed",
        "price": tomatoSeedPrice,

        # pygame.Rect(x, y, width, height) marks the clickable region.
        "rect" : pygame.Rect(shopXStart, shopYStart, shopItemW, shopItemH),

        # The internal name script.py checks to know which item was bought.
        "gives": "tomatoSeed"
    },
]


def handleShopClick(vx, vy, money, inventory):
    # Check whether the player clicked any shop item.
    # vx, vy    - mouse position in virtual canvas coordinates
    # money     - the player's current coin total (int)
    # inventory - a dictionary of booleans tracking what the player is holding
    #
    # Returns the updated money value. inventory is modified in place.

    for item in shopItems:

        # Check whether the click landed inside this item's clickable area.
        if item["rect"].collidepoint(vx, vy):

            # Only complete the purchase if the player can afford it.
            if money >= item["price"]:
                money -= item["price"]

                # Set the matching inventory flag so script.py knows what to give the player.
                if item["gives"] == "tomatoSeed":
                    inventory["tomatoSeed"] = True
                    inventory["itemHeld"]   = True

            # Stop checking after the first matching item.
            break

    return money