import random
import matplotlib.pyplot as plot
from math import *
ITERATIONS = 2000
STEPS = 1000
N = 10

# Epsilon Greedy and Greedy 
EPSILONS = [0,0.01,0.1]
for EPSILON in EPSILONS:
    AVG_REWARD = [0 for _ in range(STEPS)]
    for _ in range(ITERATIONS):
        total_reward = 0
        q = [random.normalvariate() for _ in range(N)]
        Q = [         0             for _ in range(N)]
        M = [         0             for _ in range(N)]
        for STEP in range(STEPS):
            # Choosing Index
            idx = -1
            if random.uniform(0,1) < EPSILON:
                idx = int(random.uniform(0,N)) 
            else :
                m = max(Q)
                indexes = [i for i, value in enumerate(Q) if value == m]
                idx = random.choices(indexes)[0]
            # Getting Reward
            rew = q[idx] + random.normalvariate()
            Q[idx] = (rew + M[idx] * Q[idx])/(M[idx]+1)
            M[idx] += 1
            # Upgrading stats
            total_reward += rew
            AVG_REWARD[STEP] += total_reward/(STEP+1)
    AVG_REWARD = [x/ITERATIONS for x in AVG_REWARD]
    plot.plot(AVG_REWARD,label=f"Epsilon = {EPSILON}")

# Optimistic Greedy 
AVG_REWARD = [0 for _ in range(STEPS)]
OPTIMISM_FACTOR = 5
for _ in range(ITERATIONS):
    total_reward = 0
    q = [random.normalvariate() for _ in range(N)]
    Q = [   OPTIMISM_FACTOR     for _ in range(N)]
    M = [         0             for _ in range(N)]
    for STEP in range(STEPS):
        # Choosing Index
        m = max(Q)
        indexes = [i for i, value in enumerate(Q) if value == m]
        idx = random.choices(indexes)[0]
        # Getting Reward
        rew = q[idx] + random.normalvariate()
        Q[idx] = (rew + M[idx] * Q[idx])/(M[idx]+1)
        M[idx] += 1
        # Upgrading stats
        total_reward += rew
        AVG_REWARD[STEP] += total_reward/(STEP+1)
AVG_REWARD = [x/ITERATIONS for x in AVG_REWARD]
plot.plot(AVG_REWARD,label=f"Q_0 = {OPTIMISM_FACTOR}")


# UCB 
AVG_REWARD = [0 for _ in range(STEPS)]
EXPLORATION_COEFFICIENT = 1
for _ in range(ITERATIONS):
    total_reward = 0
    q = [random.normalvariate() for _ in range(N)]
    Q = [         0             for _ in range(N)]
    M = [         0             for _ in range(N)]
    for STEP in range(STEPS):
        # Choosing Index
        ucb = [(Q[i] + EXPLORATION_COEFFICIENT * sqrt(log(STEP+1))/M[i]) for i in range(N)]
        m = max(ucb)
        indexes = [i for i, value in enumerate(ucb) if value == m]
        idx = random.choices(indexes)[0]
        # Getting Reward
        rew = q[idx] + random.normalvariate()
        Q[idx] = (rew + M[idx] * Q[idx])/(M[idx]+1)
        M[idx] += 1
        # Upgrading stats
        total_reward += rew
        AVG_REWARD[STEP] += total_reward/(STEP+1)
AVG_REWARD = [x/ITERATIONS for x in AVG_REWARD]
plot.plot(AVG_REWARD,label=f"UCB with c  = {EXPLORATION_COEFFICIENT}")

plot.legend()
plot.show()