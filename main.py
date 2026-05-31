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
distance_traveled = 0
turn = 0
map_lsit = 20 * [0] + 30 * [-1] + 100 * [0] + 100 * [1] + 100 * [0]

speed = 0
air_drag_coefficient = 0.010
rolling_friction = 0.0001
braking_force = 0.0025
current_braking = 0.0

test_image = pygame.image.load("car.png").convert()

def width_calc(i, offset, curve_type, current_x_center):
    z_bottom = (number_of_road_segments - i) - offset + 1.0
    z_top = (number_of_road_segments - (i + 1)) - offset + 1.0

    if z_bottom <= 0.1:
        z_bottom = 0.1
    if z_top <= 0.1:
        z_top = 0.1

    scale = 1.0 / z_bottom
    scale_top = 1.0 / z_top

    w = near_road_width * scale
    w_2 = near_road_width * scale_top

    y_bottom = horizon_y + (road_height * scale)
    y_top = horizon_y + (road_height * scale_top)

    left_bottom_x = current_x_center - w / 2
    right_bottom_x = current_x_center + w / 2
    left_top_x = current_x_center - w_2 / 2
    right_top_x = current_x_center + w_2 / 2

    p_1 = (int(left_bottom_x), int(y_bottom))
    p_2 = (int(right_bottom_x), int(y_bottom))
    p_3 = (int(left_top_x), int(y_top))
    p_4 = (int(right_top_x), int(y_top))

    return p_1, p_2, p_3, p_4


def draw_road(turn):
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
        
        
        z = (number_of_road_segments - i) - offset + 1.0
        if z <= 0.1:
            z = 0.1
        scale = 1.0 / z
        
        steering_projection = turn * (scale * 30) 
        
        final_center = centers[i] + steering_projection

        color_1 = (64, 70, 78)
        color_2 = (56, 61, 68)
        color = color_1 if map_index % 4 == 0 else color_2

        p_1, p_2, p_3, p_4 = width_calc(i, offset, curve_type, final_center)
        pos = (p_1, p_2, p_4, p_3)

        pygame.draw.polygon(screen, color, pos)


running = True
while running:
    keys = pygame.key.get_pressed()
    current_tile_curve = map_lsit[distance_traveled % len(map_lsit)]

    if keys[pygame.K_w]:
        turn -= current_tile_curve * 0.08
        if speed < 0.04:
            engine_force = 0.0015 
        elif speed < 0.08:
            engine_force = 0.0010 
        elif speed < 0.11:
            engine_force = 0.0006 
        else:
            engine_force = 0.0004  
    else:
        engine_force = 0.0

    if keys[pygame.K_s]:
        current_braking = braking_force 
    else:
        current_braking = 0.0

    air_drag = air_drag_coefficient * (speed * speed)
    acceleration = engine_force - rolling_friction - air_drag - current_braking
    speed += acceleration
    
    if speed < 0:
        speed = 0

    offset += speed

    if keys[pygame.K_a]:
        if speed>0:
            turn -= 0.1  
    if keys[pygame.K_d]:
        if speed>0:
            turn += 0.1  
    
    

    if turn < -4:
        turn = -4
    if turn > 4:
        turn = 4

    if offset >= 1.0:
        offset -= 1.0
        distance_traveled += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    screen.fill((135, 206, 250))
    kratka_do_wypelnienia = (0, horizon_y+8, 320, 250)

    screen.fill((34, 139, 34), rect=kratka_do_wypelnienia)
    
    draw_road(turn)
    
    screen.blit(test_image, (160-34, 240-26-15))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()