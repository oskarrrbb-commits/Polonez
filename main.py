import pygame
import sys

pygame.init()

screen_width = 320
screen_height = 240
screen_flags = pygame.SCALED | pygame.FULLSCREEN

clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)

near_road_width = 330
number_of_road_segments = 18
horizon_y = int(screen_height * 0.38)
road_height = screen_height - horizon_y
x_center = screen_width / 2

offset = 0
distance_traveled=0

map_lsit = 20 * [0] + 30 * [-1] + 100 * [0] + 100 * [1] + 100 * [0]
def width_calc(i, offset,curve_type,current_x_center):
    
    
    
    z_bottom = (number_of_road_segments - i) - offset + 1.0
    z_top = (number_of_road_segments - (i + 1)) - offset + 1.0

    if z_bottom<=0.1:
        z_bottom=0.1
    if z_top<=0.1:
        z_top=0.1

    scale = 1.0 / z_bottom
    scale_top = 1.0 / z_top

    w = near_road_width * scale
    w_2 = near_road_width * scale_top

    y_bottom = horizon_y + (road_height * scale)
    y_top = horizon_y + (road_height * scale_top)

    left_bottom_x = current_x_center - w / 2
    right_bottom_x =  current_x_center + w / 2
    left_top_x =  current_x_center - w_2 / 2
    right_top_x =  current_x_center + w_2 / 2

    p_1 = (int(left_bottom_x), int(y_bottom))
    p_2 = (int(right_bottom_x), int(y_bottom))
    p_3 = (int(left_top_x), int(y_top))
    p_4 = (int(right_top_x), int(y_top))

    return p_1, p_2, p_3, p_4


def draw_road():
    
    centers = [0] * number_of_road_segments
    
    current_x = x_center
    dx = 0  

    
    for i in range(number_of_road_segments - 1, -1, -1):
        
        
        map_index = distance_traveled + (number_of_road_segments - 1 - i)
        curve_type = map_lsit[map_index % len(map_lsit)]
        
        
        dx += curve_type * 0.4    
        current_x += dx           
        
        centers[i] = current_x

    
    for i in range(number_of_road_segments):
        
        map_index = distance_traveled + (number_of_road_segments - 1 - i)
        curve_type = map_lsit[map_index % len(map_lsit)]
        
        color_1 = (128, 128, 128)
        color_2 = (59, 59, 59)
        color = color_1 if map_index % 2 == 0 else color_2

        p_1, p_2, p_3, p_4 = width_calc(i, offset, curve_type, centers[i])
        pos = (p_1, p_2, p_4, p_3)

        pygame.draw.polygon(screen, color, pos)

running = True

while running:

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        offset += 0.09  

    if offset >= 1.0:
        offset -= 1.0
        distance_traveled=distance_traveled+1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    screen.fill((200, 20, 0))  
    draw_road()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()