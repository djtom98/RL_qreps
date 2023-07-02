# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     custom_cell_magics: kql
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.2
#   kernelspec:
#     display_name: qreps
#     language: python
#     name: python3
# ---

# %% [markdown]
# References: \
# https://github.com/hermesdt/reinforcement-learning/blob/master/a2c \
# https://medium.com/deeplearningmadeeasy/advantage-actor-critic-a2c-implementation-944e98616b \
#

# %%

# %%

# %%
# !python exps/environments/cart_pole/cart_pole_run.py

# %% [markdown]
# # PPO

# %%
#implementation of PPO in cart-pole environment
import numpy as np
import tensorflow as tf

import gym

class ValueNetwork():
    def __init__(self, num_features, hidden_size, learning_rate=.01):
        self.num_features = num_features
        self.hidden_size = hidden_size
        self.tf_graph = tf.Graph()
        with self.tf_graph.as_default():
            self.session = tf.Session()

            self.observations = tf.placeholder(shape=[None, self.num_features], dtype=tf.float32)
            self.W = [
                tf.get_variable("W1", shape=[self.num_features, self.hidden_size]),
                tf.get_variable("W2", shape=[self.hidden_size, 1])
            ]
            self.layer_1 = tf.nn.sigmoid(tf.matmul(self.observations, self.W[0]))
            self.output = tf.reshape(tf.matmul(self.layer_1, self.W[1]), [-1])

            self.rollout = tf.placeholder(shape=[None], dtype=tf.float32)
            self.loss = tf.losses.mean_squared_error(self.output, self.rollout)
            self.grad_optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
            self.minimize = self.grad_optimizer.minimize(self.loss)

            init = tf.global_variables_initializer()
            self.session.run(init)

    def get(self, states):
        value = self.session.run(self.output, feed_dict={self.observations: states})
        return value

    def update(self, states, discounted_rewards):
        _, loss = self.session.run([self.minimize, self.loss], feed_dict={
            self.observations: states, self.rollout: discounted_rewards
        })


class PPOPolicyNetwork():
    def __init__(self, num_features, layer_1_size, layer_2_size, layer_3_size, num_actions, epsilon=.2,
                 learning_rate=9e-4):
        self.tf_graph = tf.Graph()

        with self.tf_graph.as_default():
            self.session = tf.Session()

            self.observations = tf.placeholder(shape=[None, num_features], dtype=tf.float32)
            self.W = [
                tf.get_variable("W1", shape=[num_features, layer_1_size], initializer=tf.contrib.layers.xavier_initializer()),
                tf.get_variable("W2", shape=[layer_1_size, layer_2_size], initializer=tf.contrib.layers.xavier_initializer()),
                tf.get_variable("W3", shape=[layer_2_size, layer_3_size], initializer=tf.contrib.layers.xavier_initializer()),
                tf.get_variable("W4", shape=[layer_3_size, num_actions], initializer=tf.contrib.layers.xavier_initializer())
            ]
            
            self.output = tf.nn.relu(tf.matmul(self.observations, self.W[0]))
            self.output = tf.nn.relu(tf.matmul(self.output, self.W[1]))
            self.output = tf.nn.relu(tf.matmul(self.output, self.W[2]))
            self.output = tf.nn.softmax(tf.matmul(self.output, self.W[3]))

            self.advantages = tf.placeholder(shape=[None], dtype=tf.float32)

            self.chosen_actions = tf.placeholder(shape=[None, num_actions], dtype=tf.float32)
            self.old_probabilities = tf.placeholder(shape=[None, num_actions], dtype=tf.float32)

            self.new_responsible_outputs = tf.reduce_sum(self.chosen_actions*self.output, axis=1)
            self.old_responsible_outputs = tf.reduce_sum(self.chosen_actions*self.old_probabilities, axis=1)

            self.ratio = self.new_responsible_outputs/self.old_responsible_outputs

            self.loss = tf.reshape(
                            tf.minimum(
                                tf.multiply(self.ratio, self.advantages), 
                                tf.multiply(tf.clip_by_value(self.ratio, 1-epsilon, 1+epsilon), self.advantages)),
                            [-1]
                        )
            self.loss = -tf.reduce_mean(self.loss)

            self.W0_grad = tf.placeholder(dtype=tf.float32)
            self.W1_grad = tf.placeholder(dtype=tf.float32)
            self.W2_grad = tf.placeholder(dtype=tf.float32)
            self.W3_grad = tf.placeholder(dtype=tf.float32)

            self.gradient_placeholders = [self.W0_grad, self.W1_grad, self.W2_grad, self.W3_grad]
            self.trainable_vars = self.W
            self.gradients = [(np.zeros(var.get_shape()), var) for var in self.trainable_vars]

            self.optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
            self.get_grad = self.optimizer.compute_gradients(self.loss, self.trainable_vars)
            self.apply_grad = self.optimizer.apply_gradients(zip(self.gradient_placeholders, self.trainable_vars))
            init = tf.global_variables_initializer()
            self.session.run(init)

    def get_dist(self, states):
        dist = self.session.run(self.output, feed_dict={self.observations: states})
        return dist

    def update(self, states, chosen_actions, ep_advantages):
        old_probabilities = self.session.run(self.output, feed_dict={self.observations: states})
        self.session.run(self.apply_grad, feed_dict={
            self.W0_grad: self.gradients[0][0],
            self.W1_grad: self.gradients[1][0],
            self.W2_grad: self.gradients[2][0],
            self.W3_grad: self.gradients[3][0],
        })
        self.gradients, loss = self.session.run([self.get_grad, self.output], feed_dict={
            self.observations: states,
            self.advantages: ep_advantages,
            self.chosen_actions: chosen_actions,
            self.old_probabilities: old_probabilities
        })


class PPO():
    def __init__(self, env, num_features=1, num_actions=1, gamma=.98, lam=1, epsilon=.2,
                 value_network_lr=0.1, policy_network_lr=9e-4, value_network_hidden_size=100,
                 policy_network_hidden_size_1=10, policy_network_hidden_size_2=10, policy_network_hidden_size_3=10):
        
        self.env = env
        self.num_features = num_features
        self.num_actions = num_actions
        self.gamma = gamma
        self.lam = lam
        self.Pi = PPOPolicyNetwork(num_features=num_features, num_actions=num_actions, 
                                   layer_1_size=policy_network_hidden_size_1,
                                   layer_2_size=policy_network_hidden_size_2,
                                   layer_3_size=policy_network_hidden_size_3,
                                   epsilon=epsilon,
                                   learning_rate=policy_network_lr)
        self.V = ValueNetwork(num_features, value_network_hidden_size, learning_rate=value_network_lr)

    def discount_rewards(self, rewards):
        running_total = 0
        discounted = np.zeros_like(rewards)
        for r in reversed(range(len(rewards))):
            running_total = running_total * self.gamma + rewards[r]
            discounted[r] = running_total
        return discounted

    def calculate_advantages(self, rewards, values):
        advantages = np.zeros_like(rewards)
        for t in range(len(rewards)):
            ad = 0
            for l in range(0, len(rewards) - t - 1):
                delta = rewards[t+l] + self.gamma*values[t+l+1] - values[t+l]
                ad += ((self.gamma*self.lam)**l)*(delta)
            ad += ((self.gamma*self.lam)**l)*(rewards[t+l] - values[t+l])
            advantages[t] = ad
        return (advantages - np.mean(advantages))/np.std(advantages)


    def run_model(self):
        episode = 1
        running_reward = []
        step = 0
        render = False
        while(True):
            s0 = self.env.reset()
            is_terminal = False
            ep_rewards = []
            ep_actions = []
            ep_states = []
            score = 0
            while not is_terminal:
                if render:
                    self.env.render()
                action = np.random.choice(range(self.num_actions), p=self.Pi.get_dist(np.array(s0)[np.newaxis, :])[0])
                a_binarized = np.zeros(self.num_actions)
                a_binarized[action] = 1
                s1, r, is_terminal, _ = self.env.step(action)
                score += r
                ep_actions.append(a_binarized)
                ep_rewards.append(r)
                ep_states.append(s0)
                s0 = s1
                if is_terminal:
                    ep_actions = np.vstack(ep_actions)
                    ep_rewards = np.array(ep_rewards, dtype=np.float_)
                    ep_states = np.vstack(ep_states)
                    targets = self.discount_rewards(ep_rewards)
                    for i in range(len(ep_states)):
                        self.V.update([ep_states[i]], [targets[i]])
                    ep_advantages = self.calculate_advantages(ep_rewards, self.V.get(ep_states))
                    vs = self.V.get(ep_states)
                    self.Pi.update(ep_states, ep_actions, ep_advantages)
                    ep_rewards = []
                    ep_actions = []
                    ep_states = []
                    running_reward.append(score)
                    if episode % 25 == 0:
                        avg_score = np.mean(running_reward[-25:])
                        print("Episode: " + str(episode) + " Score: " + str(avg_score))
                        if avg_score >= 500:
                            print("Solved!")
                            render = True
                    episode += 1

env = gym.make('CartPole-v1')
agent = PPO(env, num_features=4, num_actions=2, gamma=.98, lam=1, epsilon=.2,
            value_network_lr=0.001, policy_network_lr=.01, value_network_hidden_size=100,
            policy_network_hidden_size_1=40, policy_network_hidden_size_2=35, policy_network_hidden_size_3=30)
agent.run_model()

# %% [markdown]
# # A2C

# %%
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable
import matplotlib.pyplot as plt
import numpy as np
import math
import random
import os
import gym

# Hyper Parameters
STATE_DIM = 4
ACTION_DIM = 2
STEP = 2000
SAMPLE_NUMS = 30


class ActorNetwork(nn.Module):

    def __init__(self,input_size,hidden_size,action_size):
        super(ActorNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size,hidden_size)
        self.fc2 = nn.Linear(hidden_size,hidden_size)
        self.fc3 = nn.Linear(hidden_size,action_size)

    def forward(self,x):
        out = F.relu(self.fc1(x))
        out = F.relu(self.fc2(out))
        out = F.log_softmax(self.fc3(out))
        return out

class ValueNetwork(nn.Module):

    def __init__(self,input_size,hidden_size,output_size):
        super(ValueNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size,hidden_size)
        self.fc2 = nn.Linear(hidden_size,hidden_size)
        self.fc3 = nn.Linear(hidden_size,output_size)

    def forward(self,x):
        out = F.relu(self.fc1(x))
        out = F.relu(self.fc2(out))
        out = self.fc3(out)
        return out

def roll_out(actor_network,task,sample_nums,value_network,init_state):
    #task.reset()
    states = []
    actions = []
    rewards = []
    is_done = False
    final_r = 0
    state = init_state

    for j in range(sample_nums):
        states.append(state)
        log_softmax_action = actor_network(Variable(torch.Tensor([state])))
        softmax_action = torch.exp(log_softmax_action)
        action = np.random.choice(ACTION_DIM,p=softmax_action.cpu().data.numpy()[0])
        one_hot_action = [int(k == action) for k in range(ACTION_DIM)]
        next_state,reward,done,_ = task.step(action)
        #fix_reward = -10 if done else 1
        actions.append(one_hot_action)
        rewards.append(reward)
        final_state = next_state
        state = next_state
        if done:
            is_done = True
            state = task.reset()
            break
    if not is_done:
        final_r = value_network(Variable(torch.Tensor([final_state]))).cpu().data.numpy()

    return states,actions,rewards,final_r,state

def discount_reward(r, gamma,final_r):
    discounted_r = np.zeros_like(r)
    running_add = final_r
    for t in reversed(range(0, len(r))):
        running_add = running_add * gamma + r[t]
        discounted_r[t] = running_add
    return discounted_r

def main():
    # init a task generator for data fetching
    task = gym.make("CartPole-v1")
    init_state = task.reset()

    # init value network
    value_network = ValueNetwork(input_size = STATE_DIM,hidden_size = 40,output_size = 1)
    value_network_optim = torch.optim.Adam(value_network.parameters(),lr=0.01)

    # init actor network
    actor_network = ActorNetwork(STATE_DIM,40,ACTION_DIM)
    actor_network_optim = torch.optim.Adam(actor_network.parameters(),lr = 0.01)

    steps =[]
    task_episodes =[]
    test_results =[]

    for step in range(STEP):
        states,actions,rewards,final_r,current_state = roll_out(actor_network,task,SAMPLE_NUMS,value_network,init_state)
        init_state = current_state
        actions_var = Variable(torch.Tensor(actions).view(-1,ACTION_DIM))
        states_var = Variable(torch.Tensor(states).view(-1,STATE_DIM))

        # train actor network
        actor_network_optim.zero_grad()
        log_softmax_actions = actor_network(states_var)
        vs = value_network(states_var).detach()
        # calculate qs
        qs = Variable(torch.Tensor(discount_reward(rewards,0.99,final_r)))

        advantages = qs - vs
        actor_network_loss = - torch.mean(torch.sum(log_softmax_actions*actions_var,1)* advantages)
        actor_network_loss.backward()
        torch.nn.utils.clip_grad_norm(actor_network.parameters(),0.5)
        actor_network_optim.step()

        # train value network
        value_network_optim.zero_grad()
        target_values = qs
        values = value_network(states_var)
        criterion = nn.MSELoss()
        value_network_loss = criterion(values,target_values)
        value_network_loss.backward()
        torch.nn.utils.clip_grad_norm(value_network.parameters(),0.5)
        value_network_optim.step()

        # Testing
        if (step + 1) % 50== 0:
                result = 0
                test_task = gym.make("CartPole-v1")
                for test_epi in range(10):
                    state = test_task.reset()
                    for test_step in range(200):
                        softmax_action = torch.exp(actor_network(Variable(torch.Tensor([state]))))
                        #print(softmax_action.data)
                        action = np.argmax(softmax_action.data.numpy()[0])
                        next_state,reward,done,_ = test_task.step(action)
                        result += reward
                        state = next_state
                        if done:
                            break
                print("step:",step+1,"test result:",result/10.0)
                steps.append(step+1)
                test_results.append(result/10)

if __name__ == '__main__':
    main()

