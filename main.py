import pygame
import sys
import random

pygame.init()

screen_width = 320
screen_height = 240
screen_flags = pygame.SCALED | pygame.FULLSCREEN

clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)

near_road_width = 410
number_of_road_segments = 18
horizon_y = int(screen_height * 0.38)
road_height = screen_height - horizon_y
x_center = screen_width / 2

offset = 0
distance_traveled = 0
turn = 0
map_lsit = 20 * [0]

def create_map(map_list):
    for i in range(100):
        road_type=random.randint(1,3)
        if road_type==1:
            turn_sharpnes=-random.randint(0,2)+random.random()
        if road_type==2:
            turn_sharpnes=0
        if road_type==3:
            turn_sharpnes=random.randint(0,2)+random.random()
        road_lenght=random.randint(20,100)
        map_list=map_list+ road_lenght * [turn_sharpnes]
    return map_list

map_lsit=create_map(map_lsit)

scenery_map = {}
for i in range(len(map_lsit)):
    if random.random() < 0.8:  
        side = random.choice([-1, 1])
        distance = random.randint(200, 4000)
        scenery_map[i] = {"type": random.choice(["tree", "stone", "bush"]),"offset": side * distance}

car_x = x_center - 30
car_y = screen_height - 45-30

gear = 1
speed = 0
air_drag_coefficient = 0.010
rolling_friction = 0.0001
braking_force = 0.0025
current_braking = 0.0

test_image = pygame.image.load("car_front.png").convert_alpha()
tree_image = pygame.image.load("tree.png").convert_alpha()
bush_image = pygame.image.load("bush.png").convert_alpha()
stone_image = pygame.image.load("stone.png").convert_alpha()
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
        actual_index = map_index % len(map_lsit)    
        if actual_index in scenery_map:
            object=scenery_map[actual_index]
            if object["type"]=="tree":
                sprite_img=tree_image
                base_w=124
                base_h=151
            elif object["type"]=="bush":
                sprite_img=bush_image
                base_w=124
                base_h=74
            elif object["type"]=="stone":
                sprite_img=stone_image
                base_w=109
                base_h=38
            
            scaled_base_w = int(base_w * scale)
            scaled_base_h = int(base_h * scale)
            if scaled_base_h>0 and scaled_base_w>0:
                scaled_base = pygame.transform.scale(sprite_img, (scaled_base_w, scaled_base_h))
                base_x = final_center + (object["offset"] * scale) - (scaled_base_w / 2)
                base_y = p_1[1] - scaled_base_h
                screen.blit(scaled_base, (base_x, base_y))

        

        


running = True
while running:
    keys = pygame.key.get_pressed()
    current_tile_curve = map_lsit[distance_traveled % len(map_lsit)]

    if keys[pygame.K_w]:
        turn -= current_tile_curve * 0.08
        
        if speed < 0.04 and gear==1:
            engine_force = 0.0017 
        elif speed < 0.08 and gear==2:
            engine_force = 0.0012 
        elif speed < 0.11 and gear==3:
            engine_force = 0.0008 
        elif speed < 0.14 and gear==4:
                engine_force = 0.0006  
        elif speed < 0.18 and gear==5:
                engine_force = 0.0004     
    else:
        engine_force = 0.0

    if speed > 0.04 and gear==1:
            engine_force = 0 
    elif speed > 0.08 and gear==2:
            engine_force = 0
    elif speed > 0.11 and gear==3:
            engine_force = 0
    elif speed > 0.14 and gear==4:
                engine_force = 0
    elif speed > 0.18 and gear==5:
            engine_force = 0

    if keys[pygame.K_s]:
        current_braking = braking_force 
    else:
        current_braking = 0.0

    if keys[pygame.K_a]:
        if speed>0:
            turn -= 0.1  
    if keys[pygame.K_d]:
        if speed>0:
            turn += 0.1 

    
    if speed < 0:
        speed = 0
    if turn < -6:
        turn = -6
        speed = speed * 0.92
        
    if turn > 6:
        turn = 6
        speed = speed * 0.92

    air_drag = air_drag_coefficient * (speed * speed)
    acceleration = engine_force - rolling_friction - air_drag - current_braking
    speed += acceleration
    
    offset += speed

    if offset >= 1.0:
        offset -= 1.0
        distance_traveled += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                if gear < 5:        
                     gear = gear + 1 
                
            elif event.key == pygame.K_LCTRL:
                if gear > 1:        
                    gear = gear - 1 
        

    screen.fill((135, 206, 250))
    kratka_do_wypelnienia = (0, horizon_y+8, 320, 250)

    screen.fill((34, 139, 34), rect=kratka_do_wypelnienia)
    
    font = pygame.font.Font(None, 36)
    speed_surface = font.render(f"Speed: {int(speed*1000)} mph", True, (255, 255, 255))
    screen.blit(speed_surface, (50, 50))

    draw_road(turn)
    
    screen.blit(test_image, (car_x, car_y))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()