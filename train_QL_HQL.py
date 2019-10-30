import gym
import gym_additions
import json
from agents_core import *
from fancy_agents import *
from utils import save_plot

env_name = 'Cross6-v0'
env = gym.make(env_name)
#print((tuple([s.n for s in env.observation_space]), env.action_space.n))
#agent = QLearning((tuple([s.n for s in env.observation_space]), env.action_space.n),
agent = HQL((tuple([s.n for s in env.observation_space]), env.action_space.n),
            learn_rate=2.5e-4, gamma=1)

def test(agent, env, n_steps, n_episodes=10):
    #print("maxes of Qtable after taining: \n{}".format(np.max(agent.Qtable,axis=-1)))
    # Testing phase
    agent.verbose = True
    # old_eps = agent.epsilon
    # agent.epsilon = 0
    rewards_history = np.empty(n_episodes)
    for ep in range(n_episodes): # everything is deterministic
        obs = env.reset()
        cumreward = 0
        for step in range(n_steps):
            env.render()
            action = agent.act(obs)
            print("Action is {}".format(action))
            obs, reward, done, info = env.step(action)
            cumreward += reward
            if done:
                print("Episode finished after {} timesteps"
                      " with cumulated reward {}".format(step+1, cumreward))
                env.render()
                break
        rewards_history[ep] = cumreward
    env.close()
    agent.verbose = False
    # agent.epsilon = old_eps
    return rewards_history.mean()

#agent.play_around(env, n_steps=20000)

n_episodes = 5*10**4
n_steps = 1500 # virually never
evaluations_history = []
# Training phase
rewards_history = np.empty(n_episodes)
for ep in range(n_episodes):
    if (ep%10000==0):
        print("Episode {}/{}".format(ep+1, n_episodes))
        evaluations_history.append(test(agent, env, n_steps))
        print("Task success rates: {}".format(agent.success_counter/agent.asked_counter))
        print("Current meta policy: {}".format(agent.meta_policy()))

    obs = env.reset()
    cumreward = 0
    for step in range(n_steps):
        action = agent.act(obs)
        old_obs = obs # tuples don't have the copy problem
        obs, reward, done, info = env.step(action)
        cumreward += reward
        agent.learn(old_obs, action, reward, obs, done)
        if done:
            break
    if step>100: print("Step {}".format(step))
    rewards_history[ep] = cumreward

env.close()
print("Evaluations history: {}".format(evaluations_history))

print("Task success rates: {}".format(agent.success_counter/agent.asked_counter))
print("Current meta policy: {}".format(agent.meta_policy()))

# plotting
launch_specs = 'paper'
file_name = "perf_plots/{}/{}/{}".format(env_name, agent.name, launch_specs)
title = "Performance of {} on {} over episodes".format(agent.name, env_name)
title += "\n{}".format(agent.tell_specs())
xlabel = 'Episode'
ylabel = "Performance at {}".format(env_name)
save_plot(rewards_history, file_name, title, xlabel, ylabel,
          smooth_avg=1000, only_avg=True, force_xaxis_0=True)