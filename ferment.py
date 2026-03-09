# =============================================================================
# ferment.py
# Defines the fermentation rules for every crop in FermFarm.
#
# Fermentation is a two-step process:
#   1. The player harvests a ripe crop (right-click on the field).
#   2. They place the harvested fruit into a fermentation pot in the shed.
#   3. After a certain number of in-game days the fruit is "done" and the
#      player can pick it up and sell it for a higher price than raw fruit.
#
# This file stores two numbers per crop:
#   "days"  -> how many in-game days the fruit must sit in the pot before
#              it is finished fermenting.
#   "value" -> how many coins the fermented fruit sells for at the shop chest.
# =============================================================================

FERMENT_DATA = {

    # Tomato: ferments quickly (2 days) but has a modest pay-off.
    # Raw tomato sells for 5 coins; fermented version sells for 18 coins.
    "tomato":   {"days": 2, "value": 18},

    # Carrot: takes a bit longer (3 days) and pays noticeably better.
    # Raw carrot sells for 10 coins; fermented version sells for 28 coins.
    "carrot":   {"days": 3, "value": 28},

    # Cucumber: also 3 days but a bigger reward than carrot.
    # Raw cucumber sells for 20 coins; fermented version sells for 45 coins.
    "cucumber": {"days": 3, "value": 45},

    # Chili: fast ferment (2 days) with a very attractive pay-off.
    # Raw chili sells for 20 coins; fermented version sells for 38 coins.
    "chili":    {"days": 2, "value": 38},

    # Cabbage: slow ferment (4 days) but pays out the best of the mid-tier crops.
    # Raw cabbage sells for 26 coins; fermented version sells for 60 coins.
    "cabbage":  {"days": 4, "value": 60},

    # Garlic: the slowest ferment (5 days) and the most valuable result.
    # Raw garlic sells for 42 coins; fermented version sells for 90 coins.
    "garlic":   {"days": 5, "value": 90},
}