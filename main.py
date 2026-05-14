import pygame
import sys

pygame.init()

screen_width=320
screen_height=240
screen_flags=pygame.SCALED

clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width,screen_height),screen_flags )
#pygame.display.toggle_fullscreen()
running=True

while running:
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()