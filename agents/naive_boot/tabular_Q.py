'''
Date: 2021-05-17 18:44:38
LastEditors: Hangyu
LastEditTime: 2021-05-25 14:45:27
FilePath: /comp90054-sequence-group-project-group-22/agents/naive_boot/reward_shape_Q_agent.py
'''
import sys
import json
sys.path.append('agents/naive_boot/')

from template import Agent
from math import sqrt
from collections import defaultdict
import random
from copy import deepcopy
import SimulateSquence

class myAgent(Agent):
    
    def __init__(self,_id):
        
        super().__init__(_id)
        
        self.alpha = 0.5
        self.discount_fac = 0.8
        with open("agents/naive_boot/Qtable.json", "r") as info:
            self.qtable = json.load(info)
        self.simulator = SimulateSquence.SimulateSquence()
        self.train = False
    
    def get_potential(self, state, next_state, action):

        for agent in state.agents:
            if agent.id == self.id:
                colour = agent.colour
        
        
        if action['type'] == 'trade':
            return 0.0
        
        elif action['type'] == 'remove':
            return 0.0
        
        max_length = self.get_current_max_length(state, self.id)
        next_max_length = 0

        if action['type'] == 'place':
            occupieds = state.board.plr_coords[colour]
            if self.get_max_length(occupieds, action['coords']) == 4:
                next_max_length = 4
            else:
                next_max_length = self.get_current_max_length(next_state, self.id) 
        print(next_max_length, max_length)
        potential = ((next_max_length - max_length) / 4) 
        return potential
    
    def get_current_max_length(self, game_state, agent_id):

        colour = game_state.agents[agent_id].colour
        current_positions = game_state.board.plr_coords[colour]
        current_positions += [(0,0), (9,0), (0,9), (9,9)]
        max_length = 0

        for position in current_positions:
            position_max_length = self.get_max_length(current_positions, position)
            if max_length < position_max_length:
                max_length = position_max_length
        
        return max_length
    
    def get_max_length(self, plr_coords, coord):
        
        x, y = coord
        vertical = 0
        if (x - 1, y) in plr_coords:
            vertical += 1
            if (x - 2, y) in plr_coords:
                vertical += 1
                if (x - 3, y) in plr_coords:
                    vertical += 1
                    if (x - 4, y) in plr_coords:
                        vertical += 1
            if (x + 1, y) in plr_coords:
                vertical += 1
                if (x + 2, y) in plr_coords:
                    vertical += 1
                    if (x + 3, y) in plr_coords:
                        vertical += 1
                        if (x + 4, y) in plr_coords:
                            vertical += 1
        elif (x + 1, y) in plr_coords:
            vertical += 1
            if (x + 2, y) in plr_coords:
                vertical += 1
                if (x + 3, y) in plr_coords:
                    vertical += 1
                    if (x + 4, y) in plr_coords:
                        vertical += 1
            if (x - 1, y) in plr_coords:
                vertical += 1
                if (x - 2, y) in plr_coords:
                    vertical += 1
                    if (x - 3, y) in plr_coords:
                        vertical += 1
                        if (x - 4, y) in plr_coords:
                            vertical += 1
        horizontal = 0
        if (x, y - 1) in plr_coords:
            horizontal += 1
            if (x, y - 2) in plr_coords:
                horizontal += 1
                if (x, y - 3) in plr_coords:
                    horizontal += 1
                    if (x, y - 4) in plr_coords:
                        horizontal += 1
            if (x, y + 1) in plr_coords:
                horizontal += 1
                if (x, y + 2) in plr_coords:
                    horizontal += 1
                    if (x, y + 3) in plr_coords:
                        horizontal += 1
                        if (x, y + 4) in plr_coords:
                            horizontal += 1
        elif (x, y + 1) in plr_coords:
            horizontal += 1
            if (x, y + 2) in plr_coords:
                horizontal += 1
                if (x, y + 3) in plr_coords:
                    horizontal += 1
                    if (x, y + 4) in plr_coords:
                        horizontal += 1
            if (x, y - 1) in plr_coords:
                horizontal += 1
                if (x, y - 2) in plr_coords:
                    horizontal += 1
                    if (x, y - 3) in plr_coords:
                        horizontal += 1
                        if (x, y - 4) in plr_coords:
                            horizontal += 1
        lu = 0
        if (x - 1, y - 1) in plr_coords:
            lu += 1
            if (x - 2, y - 2) in plr_coords:
                lu += 1
                if (x - 3, y - 3) in plr_coords:
                    lu += 1
                    if (x - 4, y - 4) in plr_coords:
                        lu += 1
            if (x + 1, y + 1) in plr_coords:
                lu += 1
                if (x + 2, y + 2) in plr_coords:
                    lu += 1
                    if (x + 3, y + 3) in plr_coords:
                        lu += 1
                        if (x + 4, y + 4) in plr_coords:
                            lu += 1
        elif (x + 1, y + 1) in plr_coords:
            lu += 1
            if (x + 2, y + 2) in plr_coords:
                lu += 1
                if (x + 3, y + 3) in plr_coords:
                    lu += 1
                    if (x + 4, y + 4) in plr_coords:
                        lu += 1
            if (x - 1, y - 1) in plr_coords:
                lu += 1
                if (x - 2, y - 2) in plr_coords:
                    lu += 1
                    if (x - 3, y - 3) in plr_coords:
                        lu += 1
                        if (x - 4, y - 4) in plr_coords:
                            lu += 1
        ld = 0
        if (x + 1, y - 1) in plr_coords:
            ld += 1
            if (x + 2, y - 2) in plr_coords:
                ld += 1
                if (x + 3, y - 3) in plr_coords:
                    ld += 1
                    if (x + 4, y - 4) in plr_coords:
                        ld += 1
            if (x - 1, y + 1) in plr_coords:
                ld += 1
                if (x - 2, y + 2) in plr_coords:
                    ld += 1
                    if (x - 3, y + 3) in plr_coords:
                        ld += 1
                        if (x - 4, y + 4) in plr_coords:
                            ld += 1
        elif (x - 1, y + 1) in plr_coords:
            ld += 1
            if (x - 2, y + 2) in plr_coords:
                ld += 1
                if (x - 3, y + 3) in plr_coords:
                    ld += 1
                    if (x - 4, y + 4) in plr_coords:
                        ld += 1
            if (x + 1, y - 1) in plr_coords:
                ld += 1
                if (x + 2, y - 2) in plr_coords:
                    ld += 1
                    if (x + 3, y - 3) in plr_coords:
                        ld += 1
                        if (x + 4, y - 4) in plr_coords:
                            ld += 1
        return max(vertical, horizontal, lu, ld)
    
    def point_distance(self, p1, p2):
        x, y = p1
        x2, y2 = p2
        
        return abs(x - x2) + abs(y - y2)
        
    def getQValue(self, state, action):
        colour = state.agents[self.id].colour
        occupieds = state.board.plr_coords[colour]
        occ = ''
        for occupied in sorted(occupieds):
            occ += str(occupied)       
        key = occ + "action:" + str(action['type']) + str(action['coords'])
        return self.qtable.get(key, 0.0)
    
    def update(self, state, action, nextState, reward):
        colour = state.agents[self.id].colour
        occupieds = state.board.plr_coords[colour]
        occ = ''
        for occupied in sorted(occupieds):
            occ += str(occupied)  
        qValue = self.getQValue(state, action)
        next_actions = self.simulator.getLegalActions(nextState, self.id) 
        max_q_next = 0.0
        
        if next_actions:
            for next_action in next_actions:
                this_q = self.getQValue(nextState, next_action)
                if this_q > max_q_next:
                    max_q_next = this_q
        state_potential = self.get_potential(state, nextState, action)
        qValue = qValue + self.alpha * (reward + state_potential + self.discount_fac * max_q_next - qValue)
        key = occ + "action:" + str(action['type']) + str(action['coords'])
        self.qtable[key] = qValue
    
    def select(self, state, actions):
        
        max_action = actions[0]
        max_value = float("-inf")  
        r = random.random()
        if r <0.1:
            return random.choice(actions)
        for action in actions:
            if action['type'] == 'trade':
                return random.choice(actions)
            value = self.getQValue(state, action)
            if value >= max_value:
                max_value = value
                max_action = action
        return max_action      
    
    def SelectAction(self,actions,game_state):
        if self.train:
            state = SimulateSquence.SimulateState(game_state, self.id)
            action = self.select(state, actions)
            print(action)
            next_state, reward = self.simulator.get_nextState(deepcopy(state), action, self.id)
            print(next_state)
            self.update(deepcopy(state), action, next_state, reward)
            with open("agents/naive_boot/Qtable.json", "w") as info:
                json.dump(self.qtable, info)   
        else:
            state = SimulateSquence.SimulateState(game_state, self.id)
            action = self.select(state, actions)
        return action
    
 

        