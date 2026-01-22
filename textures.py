import pygame
import os

def load_textures(cell_size: int):
    """Laad PNG-sprites in plaats van gekleurde vlakken.
    Vereist sprites: Sprite-0001.png t/m Sprite-0004.png in map 'sprites/'.
    """
    textures = {}
    for stage in range(1, 5):
        path = os.path.join("sprites", f"Sprite-TomaatPlant{stage}.png")
        if not os.path.exists(path):
            # fallback: maak een gekleurd vlak als sprite ontbreekt
            surf = pygame.Surface((cell_size, cell_size))
            surf.fill((100 + stage*30, 150, 100))
        else:
            surf = pygame.image.load(path).convert_alpha()
            surf = pygame.transform.scale(surf, (cell_size, cell_size))
        textures[stage] = surf
    return textures
