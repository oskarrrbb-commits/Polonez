import pygame
import sys

pygame.init()

screen_width = 320
screen_height = 240
screen_flags = pygame.SCALED | pygame.FULLSCREEN

clock = pygame.time.Clock()

screen = pygame.display.set_mode((screen_width, screen_height), screen_flags)

near_road_width = 330
horizon_road_width = 13
number_of_road_segments = 18
horizon_y = int(screen_height * 0.38)
road_height = screen_height - horizon_y
segment_height = road_height / number_of_road_segments
x_center = screen_width / 2

p_1 = (0, 0)
p_2 = (0, 0)
p_3 = (0, 0)
p_4 = (0, 0)

track_list = []
speed = 0.1
distance_traveled = 0
base_index = 0
offset = 0

start_position = base_index + offset


def place_in_road(speed, distance_traveled, base_index, offset):
    distance_traveled = distance_traveled + speed
    base_index = int(distance_traveled)
    offset = distance_traveled - base_index
    return distance_traveled, base_index, offset


def width_calc(i):
    t = i / number_of_road_segments
    t_2 = (i + 1) / number_of_road_segments

    w = near_road_width + (horizon_road_width - near_road_width) * t
    w_2 = near_road_width + (horizon_road_width - near_road_width) * t_2

    y_bottom = screen_height - (i + offset) * segment_height
    y_top = screen_height - (i + 1 + offset) * segment_height

    left_bottom_x = x_center - w / 2
    right_bottom_x = x_center + w / 2
    left_top_x = x_center - w_2 / 2
    right_top_x = x_center + w_2 / 2

    p_1 = (int(left_bottom_x), int(y_bottom))
    p_2 = (int(right_bottom_x), int(y_bottom))
    p_3 = (int(left_top_x), int(y_top))
    p_4 = (int(right_top_x), int(y_top))

    return p_1, p_2, p_3, p_4


def draw_road():

    for i in range(0, number_of_road_segments - 1):
        color_1 = (128, 128, 128)
        color_2 = (59, 59, 59)

        color = color_1
        if i % 2 == 0:
            color = color_2
        else:
            color = color_1

        p_1, p_2, p_3, p_4 = width_calc(i)
        pos = (p_1, p_2, p_4, p_3)

        pygame.draw.polygon(screen, color, pos)


running = True

while running:
    distance_traveled, base_index, offset = place_in_road(
        speed,
        distance_traveled,
        base_index,
        offset
    )

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((200, 20, 0))
    draw_road()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()