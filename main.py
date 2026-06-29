import pygame
import sys
import random
import numpy as np
import sounddevice as sd
pygame.init()
pygame.mixer.init()

screen_width = 320
screen_height = 240
screen_flags = pygame.SCALED | pygame.FULLSCREEN

pygame.mixer.music.load("assets/intro/intro.mp3")
clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)
sample_rate = 44100
phase_accumulator = 0.0
current_rpm = 0.0  
POLONEZ = {
    "idle": 30.0,        
    "range": 125.0,      
    "base_vol": 0.007,    
    "grit_vol": 0.004,    
    "harmonic": 2.0      
}

current_profile = POLONEZ
def engine_audio_callback(outdata, frames, time, status):
    global phase_accumulator
    
    if game_over or current_rpm == 0:
        outdata.fill(0)  
        return

    target_freq = current_profile["idle"] + (current_rpm / 100.0) * current_profile["range"]
    
    phase_steps = phase_accumulator + np.arange(frames) * (target_freq / sample_rate)
    
    wave = current_profile["base_vol"] * (2.0 * (phase_steps % 1.0) - 1.0)
    
    wave += current_profile["grit_vol"] * (2.0 * ((phase_steps * current_profile["harmonic"]) % 1.0) - 1.0)
    
    phase_accumulator = (phase_accumulator + frames * (target_freq / sample_rate)) % 1.0

    outdata[:, 0] = wave
    outdata[:, 1] = wave
audio_stream = sd.OutputStream(channels=2, callback=engine_audio_callback, samplerate=sample_rate)
audio_stream.start()

near_road_width = 410
number_of_road_segments = 18
horizon_y = int(screen_height * 0.46)
road_height = screen_height - horizon_y
x_center = screen_width / 2

offset = 0
distance_traveled = 0
turn = 0
real_turn = 0
map_lsit = 20 * [0]

time_left = 60.0       
checkpoint_distance = 300
next_checkpoint = checkpoint_distance
game_over = False
skip_intro = False
skip_menu = False

def time_to_go(clock,distance_traveled,game_over,time_left,next_checkpoint):
    dt = clock.get_time() / 1000.0  
    if game_over==False:
        time_left -= dt
        if distance_traveled >= next_checkpoint:
            time_left += 30.0  
            next_checkpoint += checkpoint_distance  
    
        if time_left <= 0:
            time_left = 0
            game_over = True
           
    return time_left,game_over,next_checkpoint


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

map_lsit = create_map(map_lsit)
scenery_map = {} 
for i in range(len(map_lsit)):
    if random.random() < 0.8:  
        side = random.choice([-1, 1])
        distance = random.randint(300, 2000)
        scenery_map[i] = {"type": random.choice(["tree", "stone", "bush"]),"offset": side * distance}

for i in range(len(map_lsit)):
        if i%300==0:
            scenery_map[i] = {"type": "time_sign","offset": 400}   

car_x = x_center - 30
car_y = screen_height - 45-30

gear = 1
speed = 0
air_drag_coefficient = 0.010
rolling_friction = 0.0001
braking_force = 0.0025
current_braking = 0.0
rpm_percent = 0

car_front_image = pygame.image.load("car_front.png").convert_alpha()
car_left_image = pygame.image.load("car_left.png").convert_alpha()
car_right_image = pygame.image.load("car_right.png").convert_alpha()
tree_image = pygame.image.load("tree.png").convert_alpha()
bush_image = pygame.image.load("bush.png").convert_alpha()
stone_image = pygame.image.load("stone.png").convert_alpha()
background_image = pygame.image.load("background.png").convert_alpha()
overlay_image = pygame.image.load("overlay.png").convert_alpha()
time_image = pygame.image.load("time_sign.png").convert_alpha()

background_w=background_image.get_width()
background_image_scaled=pygame.transform.scale(background_image, (background_w, horizon_y))
background_x=0

def draw_background(turn,speed,background_x):

    background_x -= turn * speed * 2
    current_bg_offset = int(background_x) % background_w
    screen.blit(background_image_scaled, (-current_bg_offset, 0))
    screen.blit(background_image_scaled, (background_w - current_bg_offset, 0))    
    return background_x  

def width_calc(i, offset, curve_type, current_x_center):
    z_bottom = (number_of_road_segments - i) - offset + 1.0
    z_top = (number_of_road_segments - (i + 1)) - offset + 1.0

    if z_bottom <= 0.1:
        z_bottom = 0.1
    if z_top <= 0.1:
        z_top = 0.1

    scale = 1.0 / z_bottom
    scale_top = 1.0 / z_top

    scale_min = 1.0 / (number_of_road_segments + 1.0) 
    scale_max = 1.0                                   

    norm_scale = (scale - scale_min) / (scale_max - scale_min)
    norm_scale_top = (scale_top - scale_min) / (scale_max - scale_min)

    w = near_road_width * scale
    w_2 = near_road_width * scale_top

    y_bottom = horizon_y + (road_height * norm_scale)
    y_top = horizon_y + (road_height * norm_scale_top)

    left_bottom_x = current_x_center - w / 2
    right_bottom_x = current_x_center + w / 2
    left_top_x = current_x_center - w_2 / 2
    right_top_x = current_x_center + w_2 / 2

    p_1 = (int(left_bottom_x), int(y_bottom))
    p_2 = (int(right_bottom_x), int(y_bottom))
    p_3 = (int(left_top_x), int(y_top))
    p_4 = (int(right_top_x), int(y_top))

    return p_1, p_2, p_3, p_4
def border_draw(p_1,p_2,p_3, p_4,i):
    
    color = (255,0,0)
    if i%2==0: color = (255,255,255)

    p_t1=((p_1[0]-int((p_2[0] - p_1[0])*0.2)),p_3[1])
    p_t2=((p_2[0]+int((p_2[0] - p_1[0])*0.2)),p_3[1])
    pos1=p_1,p_3,p_t1
    pos2=p_2,p_4,p_t2
    pygame.draw.polygon(screen, color, pos1)
    pygame.draw.polygon(screen, color, pos2)


def rpm_calc(gear,speed):
    if  gear==1:
        rpm_percent=speed/ 0.04 * 100
        if rpm_percent>100: rpm_percent=100 
        return rpm_percent
    elif  gear==2:
        rpm_percent=speed/ 0.08 * 100
        if rpm_percent>100: rpm_percent=100
        return rpm_percent
    elif  gear==3:
        rpm_percent=speed/ 0.11 * 100
        if rpm_percent>100: rpm_percent=100
        return rpm_percent
    elif  gear==4:
        rpm_percent=speed/ 0.14 * 100
        if rpm_percent>100: rpm_percent=100
        return rpm_percent
    elif  gear==5:
        rpm_percent=speed/ 0.2 * 100
        if rpm_percent>100: rpm_percent=100
        return rpm_percent


def rpm_draw(rpm_percent):
    if rpm_percent>95:
        color = (255,0,0)
    else:
        color = (0,255,0)
     
    pos = (10,220),(10,230),(10+rpm_percent/2,230),(10+rpm_percent/2,220)
    pygame.draw.polygon(screen, color, pos)


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
        border_draw(p_1, p_2, p_3, p_4,map_index)
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
            elif object["type"]=="time_sign":
                sprite_img=time_image
                base_w=100
                base_h=200
            scaled_base_w = int(base_w * scale)
            scaled_base_h = int(base_h * scale)
            if scaled_base_h>0 and scaled_base_w>0:
                scaled_base = pygame.transform.scale(sprite_img, (scaled_base_w, scaled_base_h))
                base_x = final_center + (object["offset"] * scale) - (scaled_base_w / 2)
                base_y = p_1[1] - scaled_base_h
                screen.blit(scaled_base, (base_x, base_y))

        
def fade_in(screen, image, clock, speeedof, base_image=None):
    for alpha in range(0, 256, abs(speeedof)):
        if skip_intro:
            return
        if base_image:
            screen.blit(base_image, (0, 0))
        image.set_alpha(alpha)
        screen.blit(image, (0, 0))
        pygame.display.flip()
        process_intro_events()
        if skip_intro:
            return
        clock.tick(60)

def fade_out(screen, image, clock, speeedof, base_image=None):
    if skip_intro:
        return
    for alpha in range(255, -1, -abs(speeedof)):
        if skip_intro:
            return
        if base_image:
            screen.blit(base_image, (0, 0))
        else:
            screen.fill((0, 0, 0))
        image.set_alpha(alpha)
        screen.blit(image, (0, 0))
        pygame.display.flip()
        process_intro_events()
        if skip_intro:
            return
        clock.tick(60)


def process_intro_events():
    global skip_intro
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                skip_intro = True
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()


def show_menu():
    menu_running = True
    while menu_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    menu_running = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        screen.blit(img7, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def wait_with_skip(milliseconds):
    start = pygame.time.get_ticks()
    while not skip_intro and pygame.time.get_ticks() - start < milliseconds:
        process_intro_events()
        clock.tick(60)

img1 = pygame.image.load("assets/intro/polonez_logo.png")
img2 = pygame.image.load("assets/intro/polonez_1.png")
img3 = pygame.image.load("assets/intro/polonez_2.png")
img4 = pygame.image.load("assets/intro/polonez_3.png")
img5 = pygame.image.load("assets/intro/sunrise.png")
img6 = pygame.image.load("assets/intro/car_front.png")
img7 = pygame.image.load("assets/intro/menu.png")

black_img = pygame.Surface(screen.get_size())
black_img.fill((0, 0, 0))

pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(0)

screen.blit(black_img, (0, 0))
pygame.display.flip()
wait_with_skip(4000)
fade_in(screen, img1, clock, 8)
wait_with_skip(6500)
fade_out(screen, img1, clock, 8)
screen.blit(black_img, (0, 0))
pygame.display.flip()
wait_with_skip(3500)

screen.blit(black_img, (0, 0))
pygame.display.flip()
fade_in(screen, img2, clock, 8)
wait_with_skip(7000)

fade_in(screen, img3, clock, 20, base_image=img2)
fade_out(screen, img3, clock, 20, base_image=img2)
wait_with_skip(400)
fade_in(screen, img3, clock, 20, base_image=img2)
fade_out(screen, img3, clock, 20, base_image=img2)
wait_with_skip(2640)

fade_out(screen, img2, clock, 8)
screen.blit(black_img, (0, 0))
pygame.display.flip()
wait_with_skip(4000)
fade_in(screen, img4, clock, 8)
wait_with_skip(7000)
fade_out(screen, img4, clock, 8)

screen.blit(black_img, (0, 0))
pygame.display.flip()
wait_with_skip(8200)

fade_in(screen, img6, clock, 8)
wait_with_skip(6500)
fade_out(screen, img6, clock, 8)
screen.blit(black_img, (0, 0))
pygame.display.flip()
wait_with_skip(6500)

fade_in(screen, img5, clock, 8)
wait_with_skip(10200)
fade_out(screen, img5, clock, 8)

fade_in(screen, img6, clock, 8)
wait_with_skip(10200)
fade_in(screen, img7, clock, 8)

menu_running = True
while menu_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                menu_running = False
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
    screen.blit(img7, (0, 0))
    pygame.display.flip()
    clock.tick(60)

running = True
while running:
    keys = pygame.key.get_pressed()
    current_tile_curve = map_lsit[distance_traveled % len(map_lsit)]

    if keys[pygame.K_w]:
        turn -= current_tile_curve * 0.08
        
        if speed < 0.04 and gear==1:
            engine_force = 0.00055 
        elif speed < 0.08 and gear==2:
            engine_force = 0.0005 
        elif speed < 0.11 and gear==3:
            engine_force = 0.00045
        elif speed < 0.14 and gear==4:
                engine_force = 0.0004  
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

    real_turn = 0
    if keys[pygame.K_a]:
        if speed>0:
            real_turn = -1
            turn -= 0.1  
    if keys[pygame.K_d]:
        if speed>0:
            real_turn = 1
            turn += 0.1 
    if turn < -6:
        turn = -6
        speed = speed * 0.92
        
    if turn > 6:
        turn = 6
        speed = speed * 0.92

    if game_over==True:
         engine_force=0

    air_drag = air_drag_coefficient * (speed * speed)
    acceleration = engine_force - rolling_friction - air_drag - current_braking
    speed += acceleration

    if speed < 0:
        speed = 0

    rpm_percent=rpm_calc(gear,speed)
    
    current_rpm = rpm_percent if speed > 0 else 0.0
    if game_over:
        current_rpm = 0.0

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
        
    
    background_x = draw_background(real_turn,speed,background_x)
    
    grass = (0, horizon_y, 320, 250)
    screen.fill((34, 139, 34), rect=grass)

    

    draw_road(turn)

    screen.blit(overlay_image,(0,0))

    font = pygame.font.Font(None, 24)
    speed_surface = font.render(f"{int(speed*1000)}", True, (0, 0, 0))
    gear_surface = font.render(f"{int(gear)}", True, (0, 0, 0))
    time_surface = font.render(f"{int(time_left)}", True, (0, 0, 0))
    screen.blit(speed_surface, (17, 180))
    screen.blit(gear_surface, (278, 220))
    screen.blit(time_surface, (270, 183))
    if real_turn == 0:
         car_image = car_front_image
    elif real_turn > 0:
         car_image = car_right_image
    elif real_turn < 0:
         car_image = car_left_image
    screen.blit(car_image, (car_x, car_y))
    rpm_draw(rpm_percent)
    time_left,game_over,next_checkpoint=time_to_go(clock,distance_traveled,game_over,time_left,next_checkpoint)
    if game_over:
        over_start = pygame.time.get_ticks()
        score_font = pygame.font.Font(None, 28)
        while pygame.time.get_ticks() - over_start < 2000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            screen.fill((0, 0, 0))
            score_surface = score_font.render(f"Score: {distance_traveled}", True, (255, 255, 255))
            label_surface = score_font.render("Returning to menu...", True, (255, 255, 255))
            screen.blit(score_surface, (80, 100))
            screen.blit(label_surface, (40, 130))
            pygame.display.flip()
            clock.tick(400)
        show_menu()
        distance_traveled = 0
        offset = 0
        speed = 0
        gear = 1
        current_braking = 0.0
        rpm_percent = 0
        time_left = 60.0
        next_checkpoint = checkpoint_distance
        game_over = False
        continue
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()