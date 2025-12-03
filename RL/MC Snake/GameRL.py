import pygame
import random
import math
import matplotlib.pyplot as plt
import numpy as np
import json

def save_q_table(path="q_table.json"):
    serializable = {
        str(state): actions
        for state, actions in Q.items()
    }
    with open(path, "w") as f:
        json.dump(serializable, f)
    print(f"Q-table saved to {path}")
def load_q_table(path="q_table.json"):
    global Q
    with open(path, "r") as f:
        data = json.load(f)

    # Convert keys back to tuples
    Q = {
        eval(state_str): actions
        for state_str, actions in data.items()
    }
    print(f"Q-table loaded from {path}")

pygame.init()
# RL Variables
FOOD_REWARD  = 20
DEATH_PENALTY = 20
FOOD_RELATIVITY_REWARD = 0.3 
STAGNATION_PENALTY  = 0

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
pygame.display.set_icon(pygame.image.load("icon.png"))

# ===== DEBUGGING SYSTEM =====

class Debugger:
    def __init__(self):
        self.episode_stats = {
            "score": [],
            "reward": [],
            "dist_closer": [],
            "dist_farther": [],
            "food_eaten": [],
            "actions_left": [],
            "actions_forward": [],
            "actions_right": [],
            "q_mean": [],
            "q_max": [],
            "q_min": [],
        }

    def new_episode(self):
        self.dist_closer = 0
        self.dist_farther = 0
        self.food_eaten = 0
        self.act_left = 0
        self.act_forward = 0
        self.act_right = 0

    def log_step(self, state, action, reward, old_dist, new_dist):
        # distance
        if new_dist < old_dist: self.dist_closer += 1
        elif new_dist > old_dist: self.dist_farther += 1

        # action
        if action == -1: self.act_left += 1
        elif action == 0: self.act_forward += 1
        else: self.act_right += 1

        # food eaten
        if reward == FOOD_REWARD: self.food_eaten += 1

    def end_episode(self, score, G, Q):
        self.episode_stats["score"].append(score)
        self.episode_stats["reward"].append(G)
        self.episode_stats["dist_closer"].append(self.dist_closer)
        self.episode_stats["dist_farther"].append(self.dist_farther)
        self.episode_stats["food_eaten"].append(self.food_eaten)
        self.episode_stats["actions_left"].append(self.act_left)
        self.episode_stats["actions_forward"].append(self.act_forward)
        self.episode_stats["actions_right"].append(self.act_right)

        # Q statistics
        all_q = []
        for s in Q.values():
            for v in s.values():
                all_q.append(v)
        if len(all_q):
            self.episode_stats["q_mean"].append(sum(all_q)/len(all_q))
            self.episode_stats["q_max"].append(max(all_q))
            self.episode_stats["q_min"].append(min(all_q))
        else:
            self.episode_stats["q_mean"].append(0)
            self.episode_stats["q_max"].append(0)
            self.episode_stats["q_min"].append(0)


debugger = Debugger()

class SnakeEnv:
    def __init__(self):
        # self.screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
        # pygame.display.set_caption("Snake RL")
        self.clock : pygame.time.Clock=pygame.time.Clock()
        self.reset()

    def reset(self):
        self.snake = [(8,8)]
        self.snake_direction: tuple[int,int] = (-1,0)
        self.score = len(self.snake)
        self.tick_speed = 5
        self.game =  True
        self.food_coord  = self._random_food()
        self.food_head_manhattan_dist = abs(self.snake[-1][1]-self.food_coord[1]) + abs(self.snake[-1][0] - self.food_coord[0])
        return self.get_state()
    def _random_food(self):
        while True:
            f = (random.randint(0, SCREEN_WIDTH//PIXEL_WIDTH - 1),
                 random.randint(0, SCREEN_HEIGHT//PIXEL_HEIGHT - 1))
            if f not in self.snake:
                return f

    def get_state(self):
        head = self.snake[-1]
        dirx, diry = self.snake_direction
        fx, fy = self.food_coord
        hx, hy = head

        # ===== 1. Danger (same as before, 3) =====
        left  = (-diry,  dirx)
        front = ( dirx,  diry)
        right = ( diry, -dirx)

        s = [
            self._danger(left),
            self._danger(front),
            self._danger(right),
        ]

        # ===== 2. 2-step danger (3) =====
        def d2(d):
            x = hx + d[0]*2
            y = hy + d[1]*2
            if x < 0 or x >= SCREEN_WIDTH//PIXEL_WIDTH: return 1
            if y < 0 or y >= SCREEN_HEIGHT//PIXEL_HEIGHT: return 1
            return int((x,y) in self.snake)

        s += [
            d2(left),
            d2(front),
            d2(right)
        ]

        # ===== 3. Food direction (3) =====
        dx = fx - hx
        dy = fy - hy
        cross = dx*diry - dy*dirx
        dot   = dx*dirx + dy*diry

        s += [
            int(cross > 0),
            int(dot > 0),
            int(cross < 0)
        ]

        # ===== 4. Food angle bucket (0–7) =====
        angle = (math.atan2(dy, dx) + math.pi) / (2*math.pi)   # 0 to 1
        s.append(int(angle * 8))  # bucket 0–7

        # ===== 5. Head direction bucket (0–3) =====
        # right, down, left, up
        dir_index = { (1,0):0, (0,1):1, (-1,0):2, (0,-1):3 }[self.snake_direction]
        s.append(dir_index)

        # ===== 6. Distance buckets (2) =====
        mdist = abs(dx) + abs(dy)
        dist_bucket = min(5, mdist // 2)
        s.append(dist_bucket)

        # ===== 7. Tail direction (3) =====
        if len(self.snake) > 1:
            tx, ty = self.snake[0]
            tdx = tx - hx
            tdy = ty - hy
            cross_t = tdx*diry - tdy*dirx
            dot_t   = tdx*dirx + tdy*diry
            s += [
                int(cross_t > 0),
                int(dot_t > 0),
                int(cross_t < 0)
            ]
        else:
            s += [0,0,0]

        return tuple(s)



    def _danger(self,dirn):
        n0,n1 = self.snake[-1][0] + dirn[0], self.snake[-1][1] + dirn[1]
        if(n0 >= SCREEN_WIDTH//PIXEL_WIDTH) or (n1>=SCREEN_HEIGHT//PIXEL_HEIGHT) or n0 <0 or n1<0 or ((n0,n1) in self.snake):
            return 1
        return 0
        
    def step(self,action):
        # Do action 
        if (action == -1):
            self.snake_direction = (-self.snake_direction[1],self.snake_direction[0])
        elif (action == 1):
            self.snake_direction = (self.snake_direction[1],-self.snake_direction[0])

        # Update Snake 
        self.snake.append((self.snake[-1][0]+self.snake_direction[0],self.snake[-1][1]+self.snake_direction[1]))
        new_dist = abs(self.snake[-1][1]-self.food_coord[1]) + abs(self.snake[-1][0] - self.food_coord[0])
        reward = ((new_dist > self.food_head_manhattan_dist) - (new_dist < self.food_head_manhattan_dist)) * FOOD_RELATIVITY_REWARD - STAGNATION_PENALTY
        self.food_head_manhattan_dist = new_dist
        if self.snake[-1]!=self.food_coord:
            self.snake.pop(0)
        else:
            reward = FOOD_REWARD
            self.food_coord = self._random_food()
        n0,n1 = self.snake[-1]
        if(n0 >= SCREEN_WIDTH//PIXEL_WIDTH) or (n1>=SCREEN_HEIGHT//PIXEL_HEIGHT) or n0 <0 or n1<0 or ((n0,n1) in self.snake[:-1]):
            self.game = False
            reward -= DEATH_PENALTY
        self.score = len(self.snake)

        return self.get_state(), reward , not self.game

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        self._display_snake()
        self.place(FOOD,self.food_coord)
        pygame.display.update()
        self.clock.tick(30)

    def place(self,body: pygame.Surface,coord: tuple[int,int],dirn : tuple[int,int] = (1,0)) -> bool:
        if(coord[0] >= SCREEN_WIDTH//PIXEL_WIDTH) or (coord[1]>=SCREEN_HEIGHT//PIXEL_HEIGHT) or coord[0] <0 or coord[1]<0:
            return False
        body=pygame.transform.rotate(body,math.degrees(-math.atan2(dirn[1],dirn[0])))
        self.screen.blit(body,(coord[0]*PIXEL_WIDTH,coord[1]*PIXEL_HEIGHT))
        return True

    def _display_snake(self):
        for i in range(self.score):
            if(i==self.score-1):
                if not (self.place(HEAD,self.snake[i],self.snake_direction)):
                    self.game=False#death reason 1
            else:
                self.place(BODY,self.snake[i],(self.snake[i+1][0]-self.snake[i][0],self.snake[i+1][1]-self.snake[i][1]))

# Monte Carlo Implementation 

# we need Q table
Q = {}

# Policy 
# EPSILON_soft
EPSILON = 0.5
EPSILON_DECAY_COEFFICIENT = 0.9999
MAX_STEP_BIAS = 20
MAX_STEP_FACTOR = 10
def get_action(state):
    if state not in Q:
        Q[state] = { -1:0, 0:0, 1:0 }

    if random.random() < EPSILON:
        return random.choice([-1,0,1])
    best_val = max(Q[state].values())
    best_actions = [a for a,v in Q[state].items() if v == best_val]
    return random.choice(best_actions)


def run(Env: SnakeEnv, Stats):
    global EPSILON

    EPSILON *= EPSILON_DECAY_COEFFICIENT

    state = Env.reset()
    episode = []
    step_cnt = 0

    # debugger episode start
    debugger.new_episode()

    while True:
        old_dist = Env.food_head_manhattan_dist
        action = get_action(state)
        next_state, reward, done = Env.step(action)
        new_dist = Env.food_head_manhattan_dist

        # debugger step
        debugger.log_step(state, action, reward, old_dist, new_dist)

        episode.append((state, action, reward))

        if done or step_cnt >= MAX_STEP_BIAS + MAX_STEP_FACTOR * Env.score:
            Stats["score"].append(Env.score)
            break

        step_cnt += 1
        state = next_state

    # Monte Carlo return
    G = 0
    visited = set()

    for state, action, reward in reversed(episode):
        G += reward
        if state not in Q:
            Q[state] = { -1:0, 0:0, 1:0 }
        if action not in Q[state]:
            Q[state][action] = 0
        
        if (state,action) not in visited:
            visited.add((state,action))
            Q[state][action] += 0.1 * (G - Q[state][action])

    debugger.end_episode(Env.score, G, Q)


env = SnakeEnv()
load_q_table()
Stats ={"reward":[],"score":[]}
Stats["checkpoint"] = 100000
for i in range(100000):
    Stats["id"] = i 
    run(env,Stats)
save_q_table()
stats = debugger.episode_stats

plt.figure(figsize=(18, 12))

plt.subplot(2, 3, 1)
plt.title("Score per Episode")
plt.plot(stats["score"])
plt.xlabel("Episodes")
plt.ylabel("Score")

plt.subplot(2, 3, 2)
plt.title("Total Return G")
plt.plot(stats["reward"])
plt.xlabel("Episodes")
plt.ylabel("G")

plt.subplot(2, 3, 3)
plt.title("Distance Trends")
plt.plot(stats["dist_closer"], label="Closer")
plt.plot(stats["dist_farther"], label="Farther")
plt.legend()
plt.xlabel("Episodes")

plt.subplot(2, 3, 4)
plt.title("Action Distribution")
plt.plot(stats["actions_left"], label="left (-1)")
plt.plot(stats["actions_forward"], label="forward (0)")
plt.plot(stats["actions_right"], label="right (1)")
plt.legend()
plt.xlabel("Episodes")

plt.subplot(2, 3, 5)
plt.title("Q Statistics")
plt.plot(stats["q_mean"], label="mean Q")
plt.plot(stats["q_max"], label="max Q")
plt.plot(stats["q_min"], label="min Q")
plt.legend()
plt.xlabel("Episodes")

plt.tight_layout()
plt.show()
