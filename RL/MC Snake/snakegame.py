import pygame
import random
import math

pygame.init()

#standard variables
SCREEN_WIDTH,SCREEN_HEIGHT = 1024, 512
PIXEL_WIDTH ,PIXEL_HEIGHT  = 32  , 32
BACKGROUND_COLOR=(122,255,136)
SPEED_INCREASE_CAP=20
BODY=pygame.transform.scale(pygame.image.load("body.png"),(PIXEL_WIDTH,PIXEL_HEIGHT))
HEAD=pygame.transform.scale(pygame.image.load("head.png"),(PIXEL_WIDTH,PIXEL_HEIGHT))
FOOD=pygame.transform.scale(pygame.image.load("food.png"),(PIXEL_WIDTH,PIXEL_HEIGHT))

Directions={
    "Top":(0,-1),
    "Down":(0,1),
    "Left":(-1,0),
    "Right":(1,0),
}

#ingame variables
game: bool      = True
snake: list     = [(8,8),(8,7),(8,6),(8,5),(7,5),(6,5)]
snake_direction: tuple[int,int] = (-1,0)
score: int      = len(snake)
food_coord     : tuple[int,int] = (random.randint(0,SCREEN_WIDTH//PIXEL_WIDTH-1),random.randint(0,SCREEN_HEIGHT//PIXEL_HEIGHT-1))
tick_speed: int = 5

#screen and clock updates
screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
pygame.display.set_icon(pygame.image.load("icon.png"))
clock=pygame.time.Clock()

def _display_snake():
    global snake,snake_direction,game
    for i in range(score):
        if(i==score-1):
            if not (place(HEAD,snake[i],snake_direction)):
                game=False#death reason 1
        else:
            place(BODY,snake[i],(snake[i+1][0]-snake[i][0],snake[i+1][1]-snake[i][1]))


def place(body: pygame.Surface,coord: tuple[int,int],dirn : tuple[int,int] = (1,0)) -> bool:
    if(coord[0] >= SCREEN_WIDTH//PIXEL_WIDTH) or (coord[1]>=SCREEN_HEIGHT//PIXEL_HEIGHT) or coord[0] <0 or coord[1]<0:
        return False
    body=pygame.transform.rotate(body,math.degrees(-math.atan2(dirn[1],dirn[0])))
    screen.blit(body,(coord[0]*PIXEL_WIDTH,coord[1]*PIXEL_HEIGHT))
    return True

def _move_snake():
    global snake_direction,snake,score,game,food_coord,tick_speed
    snake.append((snake[-1][0]+snake_direction[0],snake[-1][1]+snake_direction[1]))
    if snake[-1]!=food_coord:
        snake.pop(0)
    else : 
        if score<SPEED_INCREASE_CAP: tick_speed*=(1+(SPEED_INCREASE_CAP-score)/100)
        while food_coord in snake:
            food_coord=(random.randint(0,SCREEN_WIDTH//PIXEL_WIDTH-1),random.randint(0,SCREEN_HEIGHT//PIXEL_HEIGHT-1))
        print(tick_speed)
    score=len(snake)
    for i in range(score-1):
        if snake[i]==snake[-1]:
            game=False#death reason 2

def _update_game():
    global BODY,food_coord
    screen.fill(BACKGROUND_COLOR)
    _display_snake()
    place(FOOD,food_coord)
    pygame.display.update()


while game:
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            game=False
        if event.type==pygame.KEYDOWN:
            match event.key:
                case pygame.K_SPACE: _move_snake()
                case pygame.K_w    : snake_direction=Directions["Top"]
                case pygame.K_a    : snake_direction=Directions["Left"]
                case pygame.K_s    : snake_direction=Directions["Down"]
                case pygame.K_d    : snake_direction=Directions["Right"]
                case pygame.K_UP   : snake_direction=Directions["Top"]
                case pygame.K_LEFT : snake_direction=Directions["Left"]
                case pygame.K_DOWN : snake_direction=Directions["Down"]
                case pygame.K_RIGHT: snake_direction=Directions["Right"]

    clock.tick(tick_speed)
    _move_snake()
    _update_game()
print(score)
pygame.quit()


