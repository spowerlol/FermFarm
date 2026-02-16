#========================================================
# SHOP COORDINATES
#========================================================
Shop_x_start = 182
Shop_y_start = 52

Shop_Item_w = 16
Shop_Item_H = 16
Shop_gap = 2

Tomato_Seed_Price = 5

Shop_items = [
    {
        "id" : "tomato_seed",
        "price": 5,
        "rect": pygame.Rect(Shop_x_start, Shop_y_start, Shop_Item_w, Shop_Item_H),
        "gives": "TomaatZaad"
    },
]





# =============================================================
# SHOP VOOR BIJ HET AANKLIKKEN ZAAD
# =============================================================
Clicked_Shop = False
for item in Shop_items:
    clicked_Shop = True
    if money >= item["price"]:
        money -= item["price"]
        if item["gives"] == "TomaatZaad":
            TomaatZaad = True
            itemheld = True
    break
if clicked_Shop:
        continue