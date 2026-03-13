# ferment.py
# Defines the fermentation rules for every crop in FermFarm.
#
# Fermentation is a two-step process:
#   1. The player harvests a ripe crop by right-clicking the field tile.
#   2. They place the harvested fruit into a fermentation pot in the shed.
#   3. After a set number of in-game days the fruit is ready and can be
#      picked up and sold for more coins than selling it raw.
#
# Each crop entry stores:
#   "days"  -> how many in-game days the fruit must sit before it is done
#   "value" -> how many coins the fermented fruit sells for

fermentData = {

    # Tomato ferments quickly and gives a decent bonus over raw price (5 coins raw).
    "tomato":   {"days": 2, "value": 18},

    # Carrot takes a bit longer but pays noticeably more than raw (10 coins raw).
    "carrot":   {"days": 3, "value": 28},

    # Cucumber also takes 3 days with a bigger reward (20 coins raw).
    "cucumber": {"days": 3, "value": 45},

    # Chili ferments fast with a very attractive pay-off (20 coins raw).
    "chili":    {"days": 2, "value": 38},

    # Cabbage is slow but pays the best of the mid-tier crops (26 coins raw).
    "cabbage":  {"days": 4, "value": 50},

    # Garlic is the slowest ferment and the most valuable result (42 coins raw).
    "garlic":   {"days": 5, "value": 60},
}