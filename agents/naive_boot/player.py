'''
Date: 2021-05-17 18:44:38
LastEditors: Hangyu
LastEditTime: 2021-05-23 18:25:10
FilePath: /comp90054-sequence-group-project-group-22/agents/naive_boot/player.py
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
        
        self.alpha = 0.4
        self.discount_fac = 0.8
        with open("agents/naive_boot/weight.json", "r") as info:
            self.weights = json.load(info)
        self.simulator = Simulator_for_appro.SimulateSquence()
        self.train = False
    
    def select(self, state, actions):
        
        max_action = actions[0]
        max_value = float("-inf")  
        for action in actions: 
            value = self.simulator.getQValue(state, action, self.weights, self.id)
            if value >= max_value:
                max_value = value
                max_action = action
        return max_action      
    
    def SelectAction(self,actions,game_state):
        state = Simulator_for_appro.SimulateState(deepcopy(game_state), self.id)
        action = self.select(state, actions)
        return action
    
 

        