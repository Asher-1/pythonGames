"""Convert Alpha doesn't seem to work on OSX

Per surface alpha is slower than per pixel alpha. On Linux it is much quicker.
This results in games running much slower, with lower framerates, and also a number
of unit tests fail.

This file will be testing what is going on.

Conclusions

1. image.convert_alpha() from a png doesn't speed up at all on OSX but does on Linux
2. image.convert() does speed up but doesn't set transparency so you get a black box

"""

import pygame
import time


SPEED_REPEATS = 1000

pygame.init()
pygame.display.set_mode((600, 600), pygame.SRCALPHA | pygame.HWSURFACE)

base_image = pygame.image.load('convert_alpha_test.png')
destination = pygame.Surface(base_image.get_size())
alt_destination = pygame.Surface(base_image.get_size())
destination.fill((255, 0, 0))

# Save the raw image
destination.blit(base_image, (0, 0))
pygame.image.save(destination, 'cat-1.png')
print 'Base image flags', base_image.get_flags()

# Convert alpha on this - per surface alpha
per_surface = base_image.convert()
per_surface.blit(per_surface, (0, 0))
pygame.image.save(destination, 'cat-2.png')
print 'Per surface flags', per_surface.get_flags(), base_image.get_flags()

# Now do some speed tests
# On Linux the first of these tests runs almost ten times quicker than the second

start = time.time()
for i in range(SPEED_REPEATS):
    destination.blit(base_image, (0, 0))
print 'Base image timing', time.time() - start

start = time.time()
for i in range(SPEED_REPEATS):
    destination.blit(per_surface, (0, 0))
print 'Per surface image timing', time.time() - start

# Now try drawing the image to another surface
# On OSX this now suddenly increases the speed to 20X the speed before

destination.blit(per_surface, (0, 0))
start = time.time()
for i in range(SPEED_REPEATS):
    alt_destination.blit(destination, (0, 0))
    if i == 0:
        pygame.image.save(alt_destination, 'cat-3.png')
print 'Re-blitted image timing', time.time() - start

