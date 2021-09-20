'''
Date: 2021-05-17 18:44:38
LastEditors: Hangyu
LastEditTime: 2021-05-24 23:15:08
FilePath: /comp90054-sequence-group-project-group-22/agents/naive_boot/sequence_q.py
'''
import sys
import json
sys.path.append('agents/naive_boot/')

from template import Agent
from math import sqrt
from collections import defaultdict
import random
from copy import deepcopy
import Simulator_for_appro

class myAgent(Agent):
    
    def __init__(self,_id):
        
        super().__init__(_id)
        
        self.alpha = 0.01
        self.discount_fac = 0.6
        with open("agents/naive_boot/weight.json", "r") as info:
            self.weights = json.load(info)
        self.simulator = Simulator_for_appro.SimulateSquence()
        self.train = True
    
    
    def update(self, state, action, nextState, reward):
        qValue = self.simulator.getQValue(state, action, self.weights, self.id)
        next_actions = self.simulator.getLegalActions(nextState, self.id) 
        max_q_next = 0.0
        if self.simulator.gameEnds(nextState):
            max_q_next = qValue
        else:
            for next_action in next_actions:
                this_q = self.simulator.getQValue(nextState, next_action, self.weights, self.id)
                if this_q > max_q_next:
                    max_q_next = this_q
        print(max_q_next, qValue)
        temp = self.alpha * (10 * reward + self.discount_fac * max_q_next - qValue)
        for feature, value in self.simulator.extractFeatures(state, action, self.id).items():
            weight = self.weights.get(feature, 0.0)
            self.weights[feature] = weight + temp * value
    
    def select(self, state, actions):
        
        max_action = actions[0]
        max_value = float("-inf") 
        r = random.random()
        if r <0.05:
            return random.choice(actions) 
        for action in actions: 
            value = self.simulator.getQValue(state, action, self.weights, self.id)
            if value >= max_value:
                max_value = value
                max_action = action
        return max_action      
    
    def SelectAction(self,actions,game_state):
        if self.train:
            state = Simulator_for_appro.SimulateState(deepcopy(game_state), self.id)
            action = self.select(state, actions)
            next_state, reward = self.simulator.get_nextState(deepcopy(state), action, self.id, self.weights)
            self.update(deepcopy(state), action, next_state, reward)
            with open("agents/naive_boot/weight.json", "w") as info:
                json.dump(self.weights, info)   
        else:
            state = Simulator_for_appro.SimulateState(deepcopy(game_state), self.id)
            action = self.select(state, actions)
        return action
    
 

        