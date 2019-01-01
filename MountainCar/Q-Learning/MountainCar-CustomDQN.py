#Get to the top of the hill

import gym
import random
import numpy as np

from statistics import median, mean
from collections import Counter

import sys
try:
    from CustomDQN_Mar_31 import DQN
except ImportError as e:
    print(e)
    sys.path.append('./../../')
    from CustomDQN_March_18 import DQN

def create_random_samples(init_obs):
    # [state, action, reward, state_new, done]
    training_data = []
    scores = []
    
    # just the scores that met threshold:
    accepted_scores = []
    
    for i in range(initial_games):
        if i % 10 == 0:
            print('Observing random samples: {}%'.format(i*100/initial_games))
            
        score = 0
        game_memory = []
        state = init_obs

        for _ in range(goal_steps):
            action = random.randrange(0, action_space)
            if action == action_space:
                print("FOUND")
            #print("ACTION::::", action, type(action))
            state_new, reward, done, info = env.step(action)
            if observe_random: env.render()
            '''
            #if Lander exceeds height of game screen, end game and add penelty
            if state_new[1] > 600:
                reward -= 200
            '''

            #squash reward 
            reward /= reward_discount
            
            game_memory.append([state, action, reward, state_new, done])
            score += reward
            
            if done: break

        # IF our score >= threshold, we'd like to save [action, obs] pairs
        if score >= score_requirement:
            accepted_scores.append(score)
            
            for data in game_memory:
                training_data.append(data)
                
        init_obs = env.reset()
        scores.append(score)

    training_data_save = np.array(training_data)
    #np.save('lunar_lander_training_data.npy',training_data_save)
    print('Max accepted score:',max(accepted_scores))
    print('Average accepted score:',mean(accepted_scores))
    print('Median score for accepted scores:',median(accepted_scores))
    print("Number of acccepted scores:", len(accepted_scores))
    
    return np.array(training_data)

#~~~~~~~~~~~[  MAIN  ]~~~~~~~~~~~#
gym.envs.register(
    id='MountainCarMyEasyVersion-v0',
    entry_point='gym.envs.classic_control:MountainCarEnv',
    max_episode_steps=1000,      # MountainCar-v0 uses 200
    reward_threshold=-110.0,
)
env = gym.make('MountainCarMyEasyVersion-v0')
#env = gym.make("MountainCar-v0")
goal_steps =  500#2000
score_requirement = -10#-1.5
initial_games = 1000#1000 for "quick" convergance

num_training_games = 1000#>1000
action_space = 3

reward_discount = 50

observe_random = True
observe_training = False

if __name__ == "__main__":
    Agent = DQN(batch_size=64,#64
                memory_size=50000,
                learning_rate=0.005,

                min_action_chance=0.2,
                random_action_decay=0.999,#0.999
                )
                #epsilon_max=0.9,
                #random_action_decay=1000,
                #random_action_chance=0.2)
    
    training_data = create_random_samples(env.reset())
    print("Storing random games data")
    for datum in training_data:
        s, a, r, s_, done = datum
        Agent.store_transition(s, a, r, s_, done)

    Agent.init_model(training_data[0][0].shape, action_space)
    for i in range(25): Agent.train()

    score_length = 1000
    scores = []
    for each_game in range(num_training_games):
        #sample state from env
        #State shape: (1, 1, 8)
        state = env.reset()
        total_reward = 0
        
        for episode in range(goal_steps):
            if observe_training: env.render()

            #ACTION:::: 3
            action = Agent.get_action(state)
            #print("ACTION::::", action)
                  
            state_new, reward, done, info = env.step(action)

            #squash reward 
            #reward /= reward_discount

            Agent.store_transition(state, action, reward, state_new, done)
            Agent.train()
            
            total_reward += reward
            state = state_new
            if done: break
        
        scores.append(total_reward)

        if each_game % 1 == 0:
            if len(scores) > 1000:
                scores = scores[-1000:]
            print("Epochs: {} | {}".format(each_game, num_training_games),
                  "Percent done:", each_game*100/num_training_games,
                  "avg rwd:",round(mean(scores), 3), "last 10 rwd:", round(mean(scores[-10:]), 3))
        

    # Observe Agent after training
    for each_game in range(5):
        state = env.reset()
        for episode in range(goal_steps):
            env.render()
            
            #action = Agent.use_policy(state)
            action = Agent.get_action(state)
            
            state_new, reward, done, info = env.step(action)
            #Agent.store_transition(state, action, reward, state_new, done)      
            state = state_new
            if done: break

    Agent.save_model("./../../saved_models/MountainCar/")
    Agent.display_statisics_to_console()
    print("Score Requirement:",score_requirement)
















