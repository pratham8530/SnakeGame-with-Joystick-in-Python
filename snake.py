import pygame
import random
import serial
import time

pygame.init()
pygame.mixer.init()

powerup_sound = pygame.mixer.Sound("sounds/powerup.wav")
food_sound = pygame.mixer.Sound("sounds/food.wav")

ser = serial.Serial('COM9', 9600, timeout=1)
time.sleep(2)

white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
glow_color = (255, 215, 0)
purple = (128, 0, 128)

dis_width = 600
dis_height = 400
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Enhanced Snake Game with Power-Ups')

clock = pygame.time.Clock()

snake_block = 20
snake_speed = 10

font_style = pygame.font.SysFont("bahnschrift", 35)
timer_font = pygame.font.SysFont("bahnschrift", 30)

snake_head_img = pygame.image.load("snake_head.png")
snake_body_img = pygame.image.load("snake_body.png")
apple_img = pygame.image.load("apple.jpg")
powerup_img = pygame.image.load("powerup.png")

snake_head_img = pygame.transform.scale(snake_head_img, (snake_block, snake_block))
snake_body_img = pygame.transform.scale(snake_body_img, (snake_block, snake_block))
apple_img = pygame.transform.scale(apple_img, (snake_block, snake_block))
powerup_img = pygame.transform.scale(powerup_img, (snake_block, snake_block))

def send_score_to_arduino(score1, score2):
    score_data = f"1:{score1},2:{score2}\n"
    ser.write(score_data.encode())

def our_snake(snake_block, snake_list, color):
    for i, segment in enumerate(snake_list):
        if i == len(snake_list) - 1:
            dis.blit(snake_head_img, segment)
        else:
            dis.blit(snake_body_img, segment)

def read_joystick_data():
    if ser.in_waiting > 0:
        try:
            data = ser.readline().decode('utf-8').strip()
            joystick_data = list(map(int, data.split(',')))
            if len(joystick_data) == 4:
                return joystick_data
        except:
            return None
    return None

def control_snakes(snake1_dir, snake2_dir, joystick_data):
    j1_x, j1_y, j2_x, j2_y = joystick_data
    threshold = 100
    if j1_y < 512 - threshold and snake1_dir != [snake_block, 0]:
        snake1_dir = [-snake_block, 0]
    elif j1_y > 512 + threshold and snake1_dir != [-snake_block, 0]:
        snake1_dir = [snake_block, 0]
    elif j1_x < 512 - threshold and snake1_dir != [0, snake_block]:
        snake1_dir = [0, snake_block]
    elif j1_x > 512 + threshold and snake1_dir != [0, -snake_block]:
        snake1_dir = [0, -snake_block]
    if j2_y < 512 - threshold and snake2_dir != [snake_block, 0]:
        snake2_dir = [-snake_block, 0]
    elif j2_y > 512 + threshold and snake2_dir != [-snake_block, 0]:
        snake2_dir = [snake_block, 0]
    elif j2_x < 512 - threshold and snake2_dir != [0, snake_block]:
        snake2_dir = [0, snake_block]
    elif j2_x > 512 + threshold and snake2_dir != [0, -snake_block]:
        snake2_dir = [0, -snake_block]
    return snake1_dir, snake2_dir

def wrap_around(x, y, dis_width, dis_height):
    if x >= dis_width:
        x = 0
    elif x < 0:
        x = dis_width - snake_block
    if y >= dis_height:
        y = 0
    elif y < 0:
        y = dis_height - snake_block
    return x, y

def display_winner(length1, length2):
    dis.fill(blue)
    if length1 > length2:
        message = "Player 1 Wins!"
    elif length2 > length1:
        message = "Player 2 Wins!"
    else:
        message = "It's a Tie!"
    winner_message = font_style.render(message, True, red)
    dis.blit(winner_message, [dis_width / 3, dis_height / 3])
    pygame.display.update()
    time.sleep(2)

def spawn_items(item_count=3):
    items = []
    for _ in range(item_count):
        foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
        foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
        items.append([foodx, foody])
    return items

def blink_power_up(blink_time, current_time, power_up_visible):
    if current_time - blink_time >= 500:
        power_up_visible = not power_up_visible
        blink_time = current_time
    return blink_time, power_up_visible

def spawn_powerup():
    power_up = [round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0,
                round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0]
    return power_up, pygame.time.get_ticks()

def check_collision_with_food(snake_x, snake_y, food_x, food_y, block_size):
    return abs(snake_x - food_x) < block_size and abs(snake_y - food_y) < block_size

def check_collision_with_powerup(snake_x, snake_y, powerup_x, powerup_y, block_size):
    return abs(snake_x - powerup_x) < block_size and abs(snake_y - powerup_y) < block_size

def gameLoop():
    game_over = False
    game_close = False
    start_time = pygame.time.get_ticks()
    game_duration = 60 * 1000
    x1, y1 = dis_width / 4, dis_height / 2
    x2, y2 = 3 * dis_width / 4, dis_height / 2
    snake1_dir = [snake_block, 0]
    snake2_dir = [snake_block, 0]
    snake1_List = []
    snake2_List = []
    Length_of_snake1 = Length_of_snake2 = 1
    food_items = spawn_items(3)
    power_up, power_up_spawn_time = spawn_powerup()
    power_up_life_duration = 10 * 1000
    blink_time = power_up_spawn_time + 7 * 1000
    power_up_visible = True
    while not game_over:
        while game_close:
            display_winner(Length_of_snake1, Length_of_snake2)
            message = font_style.render("Game Over! Press C-Play Again or Q-Quit", True, red)
            dis.blit(message, [dis_width / 6, dis_height / 2])
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
        joystick_data = read_joystick_data()
        if joystick_data:
            snake1_dir, snake2_dir = control_snakes(snake1_dir, snake2_dir, joystick_data)
        x1 += snake1_dir[0]
        y1 += snake1_dir[1]
        x2 += snake2_dir[0]
        y2 += snake2_dir[1]
        x1, y1 = wrap_around(x1, y1, dis_width, dis_height)
        x2, y2 = wrap_around(x2, y2, dis_width, dis_height)
        snake1_List.append((x1, y1))
        snake2_List.append((x2, y2))
        if len(snake1_List) > Length_of_snake1:
            del snake1_List[0]
        if len(snake2_List) > Length_of_snake2:
            del snake2_List[0]
        for food in food_items:
            foodx, foody = food
            if check_collision_with_food(x1, y1, foodx, foody, snake_block):
                food_items.remove(food)
                food_sound.play()
                Length_of_snake1 += 1
                food_items.append(spawn_items(1)[0])
        for food in food_items:
            foodx, foody = food
            if check_collision_with_food(x2, y2, foodx, foody, snake_block):
                food_items.remove(food)
                food_sound.play()
                Length_of_snake2 += 1
                food_items.append(spawn_items(1)[0])
        if check_collision_with_powerup(x1, y1, power_up[0], power_up[1], snake_block):
            powerup_sound.play()
            Length_of_snake1 += 2
            power_up = None
            power_up_spawn_time = pygame.time.get_ticks()
        if check_collision_with_powerup(x2, y2, power_up[0], power_up[1], snake_block):
            powerup_sound.play()
            Length_of_snake2 += 2
            power_up = None
            power_up_spawn_time = pygame.time.get_ticks()
        current_time = pygame.time.get_ticks()
        if power_up is None or current_time - power_up_spawn_time >= power_up_life_duration:
            power_up, power_up_spawn_time = spawn_powerup()
            blink_time = current_time
            power_up_visible = True
        if power_up is not None:
            blink_time, power_up_visible = blink_power_up(blink_time, current_time, power_up_visible)
            if power_up_visible:
                dis.blit(powerup_img, power_up)
        dis.fill(blue)
        our_snake(snake_block, snake1_List, green)
        our_snake(snake_block, snake2_List, purple)
        for food in food_items:
            foodx, foody = food
            dis.blit(apple_img, (foodx, foody))
        elapsed_time = (current_time - start_time) // 1000
        time_left = max(0, (game_duration // 1000) - elapsed_time)
        timer_text = timer_font.render(f'Time Left: {time_left}', True, white)
        dis.blit(timer_text, [dis_width / 2 - 70, 10])
        if time_left == 0:
            game_close = True
        pygame.display.update()
        send_score_to_arduino(Length_of_snake1, Length_of_snake2)
        clock.tick(snake_speed)
    pygame.quit()
    quit()

gameLoop()
