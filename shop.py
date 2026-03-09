# =============================================================================
# shop.py
# This file defines the layout of the in-game shop and handles what happens
# when the player clicks on a shop item to buy it.
# =============================================================================

# -----------------------------------------------------------------------------
# SHOP COORDINATES
# The game renders everything onto a 240x135 virtual canvas that is then
# scaled up by a factor of 8 before being shown on screen. So every coordinate
# from the original tile-grid design is multiplied by 8 here, giving us the
# actual pixel position on the virtual canvas.
# -----------------------------------------------------------------------------

# Horizontal (X) start position of the first shop item on screen.
# Design value: 182 tiles.  182 * 8 = 1456 pixels.
Shop_x_start = 1456

# Vertical (Y) start position of the first shop item on screen.
# Design value: 52 tiles.  52 * 8 = 416 pixels.
Shop_y_start = 416

# Width of each shop item icon / clickable button, in pixels.
# Design value: 16 tiles.  16 * 8 = 128 pixels.
Shop_Item_w = 128

# Height of each shop item icon / clickable button, in pixels.
# Design value: 16 tiles.  16 * 8 = 128 pixels.
Shop_Item_H = 128

# The empty gap between items so they don't look squished together.
# Design value: 2 tiles.  2 * 8 = 16 pixels.
Shop_gap = 16

# The coin cost of a single tomato seed — kept here as a named constant
# so we never have to hunt for a magic number if we want to change the price.
Tomato_Seed_Price = 5

# -----------------------------------------------------------------------------
# SHOP ITEMS LIST
# A list of dictionaries. Think of each dictionary as a "record card" for
# one purchasable item. Fields:
#   "id"    -> unique string name used in code logic
#   "price" -> coin cost to buy the item
#   "rect"  -> the pygame.Rect (x, y, width, height) defining the clickable
#              area on screen; built from the coordinates above
#   "gives" -> what the player actually receives when they buy the item
# -----------------------------------------------------------------------------
Shop_items = [
    {
        "id"   : "tomato_seed",
        "price": 5,

        # pygame.Rect(x, y, width, height) — marks the clickable region on screen.
        # x and y come from Shop_x_start / Shop_y_start (already scaled × 8).
        # Width and height come from Shop_Item_w / Shop_Item_H (also scaled × 8).
        "rect" : pygame.Rect(Shop_x_start, Shop_y_start, Shop_Item_w, Shop_Item_H),

        # "TomaatZaad" is Dutch for "TomatoSeed". This string is checked below
        # to decide which inventory flag to set after a successful purchase.
        "gives": "TomaatZaad"
    },
]


# =============================================================================
# SHOP CLICK HANDLING
# This block runs when the game detects a click inside the shop area.
# It iterates through every shop item, checks affordability, deducts money,
# and grants the item. In a full event-driven game this would live inside
# the mouse-click event handler; here it is a self-contained snippet.
# =============================================================================

# Start by assuming nothing was clicked — we'll flip this flag inside the loop.
Clicked_Shop = False

# Go through each item in the shop list one by one.
# Using a loop (instead of hard-coding one item) means adding new shop items
# later is as simple as appending another dictionary to Shop_items above.
for item in Shop_items:

    # As soon as we enter the loop body, a shop item was clicked.
    clicked_Shop = True

    # Only proceed with the purchase if the player can actually afford it.
    if money >= item["price"]:

        # Deduct the purchase price from the player's coin wallet.
        money -= item["price"]

        # Figure out WHICH item was bought and give the player the right reward.
        if item["gives"] == "TomaatZaad":

            # Flip this flag to True so the rest of the game knows the player
            # is now carrying a tomato seed and should see the seed cursor.
            TomaatZaad = True

            # This flag tells the cursor-drawing code that the player is
            # holding something, so it should draw an item icon at the mouse.
            itemheld = True

    # Stop after processing the first (and currently only) item.
    # If we ever allow buying multiple items per click we can remove this.
    break

# If we interacted with the shop at all, skip the rest of the current
# game-loop iteration so we don't accidentally trigger other click logic
# (like planting a seed on a tile) in the same frame.
if clicked_Shop:
    continue