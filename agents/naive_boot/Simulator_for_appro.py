'''
Date: 2021-05-18 14:24:36
LastEditors: Hangyu
LastEditTime: 2021-05-26 23:23:40
FilePath: /comp90054-sequence-group-project-group-22/agents/naive_boot/Simulator_for_appro.py
'''

# The most part of this simulator is modified from 
# the code (sequence_model.py) of COMP90054 subject.

import random
from copy import deepcopy
from collections import defaultdict

BOARD = [['jk','2s','3s','4s','5s','6s','7s','8s','9s','jk'],
         ['6c','5c','4c','3c','2c','ah','kh','qh','th','ts'],
         ['7c','as','2d','3d','4d','5d','6d','7d','9h','qs'],
         ['8c','ks','6c','5c','4c','3c','2c','8d','8h','ks'],
         ['9c','qs','7c','6h','5h','4h','ah','9d','7h','as'],
         ['tc','ts','8c','7h','2h','3h','kh','td','6h','2d'],
         ['qc','9s','9c','8h','9h','th','qh','qd','5h','3d'],
         ['kc','8s','tc','qc','kc','ac','ad','kd','4h','4d'],
         ['ac','7s','6s','5s','4s','3s','2s','2h','3h','5d'],
         ['jk','ad','kd','qd','td','9d','8d','7d','6d','jk']]

#Store dict of cards and their coordinates for fast lookup.
COORDS = defaultdict(list)
for row in range(10):
    for col in range(10):
        COORDS[BOARD[row][col]].append((row,col))

# an simulateState random simulate the situation of otherplayers 
class SimulateState:
   
    def __init__(self, acturalState, target_id):
        self.board = acturalState.board
        self.agents = acturalState.agents
        self.deck = acturalState.deck
        
        for agent in self.agents:
            if agent.id == target_id:
                target_hand = agent.hand
                
        cards = [(r+s) for r in ['2','3','4','5','6','7','8','9','t','j','q','k','a'] for s in ['d','c','h','s']]
        cards = cards*2
        
        cards_known = target_hand + self.deck.discards + self.board.draft
        for card in cards_known:
            if card in cards:
                cards.remove(card)
        
        self.deck.cards = cards
        
        for i in range(4):
            if self.agents[i].id != target_id:
                self.agents[i].hand = self.deal(6)
        
    # a deal function modified from the sequence_model.py
    def deal(self, num_cards=1):
        hand = []
        random.shuffle(self.deck.cards)
        for _ in range(num_cards):
            try:
                hand.append(self.deck.cards.pop())
            except IndexError: #Deck is empty.
                break
        return hand
    
class SimulateSquence:
    
    def cardToCoords(self, card):
        return COORDS[card]
    
    def checkSeq(self, chips, plr_state, last_coords):
        clr,sclr   = plr_state.colour, plr_state.seq_colour
        oc,os      = plr_state.opp_colour, plr_state.opp_seq_colour
        seq_type   = 1
        seq_coords = []
        seq_found  = {'vr':0, 'hz':0, 'd1':0, 'd2':0, 'hb':0}
        found      = False
        nine_chip  = lambda x,clr : len(x)==9 and len(set(x))==1 and clr in x
        lr,lc      = last_coords
        
        #All joker spaces become player chips for the purposes of sequence checking.
        for r,c in COORDS['jk']:
            chips[r][c] = clr
        
        #First, check "heart of the board" (2h, 3h, 4h, 5h). If possessed by one team, the game is over.
        coord_list = [(4,4),(4,5),(5,4),(5,5)]
        heart_chips = [chips[y][x] for x,y in coord_list]
        if '_' not in heart_chips and (clr in heart_chips or sclr in heart_chips) and not (oc in heart_chips or os in heart_chips):
            seq_type = 2
            seq_found['hb']+=2
            seq_coords.append(coord_list)
            
        #Search vertical, horizontal, and both diagonals.
        vr = [(-4,0),(-3,0),(-2,0),(-1,0),(0,0),(1,0),(2,0),(3,0),(4,0)]
        hz = [(0,-4),(0,-3),(0,-2),(0,-1),(0,0),(0,1),(0,2),(0,3),(0,4)]
        d1 = [(-4,-4),(-3,-3),(-2,-2),(-1,-1),(0,0),(1,1),(2,2),(3,3),(4,4)]
        d2 = [(-4,4),(-3,3),(-2,2),(-1,1),(0,0),(1,-1),(2,-2),(3,-3),(4,-4)]
        for seq,seq_name in [(vr,'vr'), (hz,'hz'), (d1,'d1'), (d2,'d2')]:
            coord_list = [(r+lr, c+lc) for r,c in seq]
            coord_list = [i for i in coord_list if 0<=min(i) and 9>=max(i)] #Sequences must stay on the board.
            chip_str   = ''.join([chips[r][c] for r,c in coord_list])
            #Check if there exists 4 player chips either side of new chip (counts as forming 2 sequences).
            if nine_chip(chip_str, clr):
                seq_found[seq_name]+=2
                seq_coords.append(coord_list)
            #If this potential sequence doesn't overlap an established sequence, do fast check.
            if sclr not in chip_str:
                sequence_len = 0
                start_idx    = 0
                for i in range(len(chip_str)):
                    if chip_str[i] == clr:
                        sequence_len += 1
                    else:
                        start_idx = i+1
                        sequence_len = 0
                    if sequence_len >= 5:
                        seq_found[seq_name] += 1
                        seq_coords.append(coord_list[start_idx:start_idx+5])    
                        break
            else: #Check for sequences of 5 player chips, with a max. 1 chip from an existing sequence.
                for pattern in [clr*5, clr*4+sclr, clr*3+sclr+clr, clr*2+sclr+clr*2, clr+sclr+clr*3, sclr+clr*4]:
                    for start_idx in range(5):
                        if chip_str[start_idx:start_idx+5] == pattern:
                            seq_found[seq_name]+=1
                            seq_coords.append(coord_list[start_idx:start_idx+5])
                            found = True
                            break
                    if found:
                        break
        
        for r,c in COORDS['jk']:
            chips[r][c] = '#' #Joker spaces reset after sequence checking.
        
        num_seq = sum(seq_found.values())
        if num_seq > 1 and seq_type != 2:
            seq_type = 3
        return ({'num_seq':num_seq, 'orientation':[k for k,v in seq_found.items() if v], 'coords':seq_coords}, seq_type) if num_seq else (None,None)
    
    def checkSeqAndPossible(self, chips, plr_state, last_coords):
        clr,sclr   = plr_state.colour, plr_state.seq_colour
        oc,os      = plr_state.opp_colour, plr_state.opp_seq_colour
        seq_type   = 1
        seq_coords = []
        possible = 0
        seq_found  = {'vr':0, 'hz':0, 'd1':0, 'd2':0, 'hb':0}
        found      = False
        nine_chip  = lambda x,clr : len(x)==9 and len(set(x))==1 and clr in x
        lr,lc      = last_coords
        max_length = 0
        
        #All joker spaces become player chips for the purposes of sequence checking.
        for r,c in COORDS['jk']:
            chips[r][c] = clr
        
        #First, check "heart of the board" (2h, 3h, 4h, 5h). If possessed by one team, the game is over.
        coord_list = [(4,4),(4,5),(5,4),(5,5)]
        heart_chips = [chips[y][x] for x,y in coord_list]
        if '_' not in heart_chips and (clr in heart_chips or sclr in heart_chips) and not (oc in heart_chips or os in heart_chips):
            seq_type = 2
            seq_found['hb']+=2
            seq_coords.append(coord_list)
            
        #Search vertical, horizontal, and both diagonals.
        vr = [(-4,0),(-3,0),(-2,0),(-1,0),(0,0),(1,0),(2,0),(3,0),(4,0)]
        hz = [(0,-4),(0,-3),(0,-2),(0,-1),(0,0),(0,1),(0,2),(0,3),(0,4)]
        d1 = [(-4,-4),(-3,-3),(-2,-2),(-1,-1),(0,0),(1,1),(2,2),(3,3),(4,4)]
        d2 = [(-4,4),(-3,3),(-2,2),(-1,1),(0,0),(1,-1),(2,-2),(3,-3),(4,-4)]
        for seq,seq_name in [(vr,'vr'), (hz,'hz'), (d1,'d1'), (d2,'d2')]:
            coord_list = [(r+lr, c+lc) for r,c in seq]
            coord_list = [i for i in coord_list if 0<=min(i) and 9>=max(i)] #Sequences must stay on the board.
            chip_str   = ''.join([chips[r][c] for r,c in coord_list])
            this_length = 0
            for point in chip_str:
                if point == clr or point == sclr:
                    possible += 1
                    this_length += 1
            if this_length > max_length:
                max_length = this_length                
            #Check if there exists 4 player chips either side of new chip (counts as forming 2 sequences).
            if nine_chip(chip_str, clr):
                seq_found[seq_name]+=2
                seq_coords.append(coord_list)
            #If this potential sequence doesn't overlap an established sequence, do fast check.
            if sclr not in chip_str:
                sequence_len = 0
                start_idx    = 0
                for i in range(len(chip_str)):
                    if chip_str[i] == clr:
                        sequence_len += 1
                    else:
                        start_idx = i+1
                        sequence_len = 0
                    if sequence_len >= 5:
                        seq_found[seq_name] += 1
                        seq_coords.append(coord_list[start_idx:start_idx+5])    
                        break
            else: #Check for sequences of 5 player chips, with a max. 1 chip from an existing sequence.
                for pattern in [clr*5, clr*4+sclr, clr*3+sclr+clr, clr*2+sclr+clr*2, clr+sclr+clr*3, sclr+clr*4]:
                    for start_idx in range(5):
                        if chip_str[start_idx:start_idx+5] == pattern:
                            seq_found[seq_name]+=1
                            seq_coords.append(coord_list[start_idx:start_idx+5])
                            found = True
                            break
                    if found:
                        break
        
        for r,c in COORDS['jk']:
            chips[r][c] = '#' #Joker spaces reset after sequence checking.
        
        num_seq = sum(seq_found.values())
        if num_seq > 1 and seq_type != 2:
            seq_type = 3
            
        return (num_seq, possible, max_length)
    
    # a modified function from sequence_model.py 
    def generateSuccessor(self, state, action, agent_id):
        state.board.new_seq = False
        
        plr_state = state.agents[agent_id]
        plr_state.last_action = action #Record last action such that other agents can make use of this information.
        reward = 0
              
        #Update agent state. Take the card in play from the agent, discard, draw the selected draft, deal a new draft.
        #If agent was allowed to trade but chose not to, there is no card played, and hand remains the same.
        card  = action['play_card']
        draft = action['draft_card']
        if card:
            plr_state.hand.remove(card)                 #Remove card from hand.
            plr_state.discard = card                    #Add card to discard pile.
            state.deck.discards.append(card)            #Add card to global list of discards (some agents might find tracking this helpful).
            state.board.draft.remove(draft)             #Remove draft from draft selection.
            plr_state.hand.append(draft)                #Add draft to player hand.
            state.board.draft.extend(state.deal())      #Replenish draft selection.
        
        #If action was to trade in a dead card, action is complete, and agent gets to play another card.
        if action['type']=='trade':
            plr_state.trade = True #Switch trade flag to prohibit agent performing a second trade this turn.
            plr_state.agent_trace.action_reward.append((action,reward))
            return state

        #Update Sequence board. If action was to place/remove a marker, add/subtract it from the board.
        r,c = action['coords']
        if action['type']=='place':
            state.board.chips[r][c] = plr_state.colour
            state.board.empty_coords.remove(action['coords'])
            state.board.plr_coords[plr_state.colour].append(action['coords'])            
        elif action['type']=='remove':
            state.board.chips[r][c] = '_'
            state.board.empty_coords.append(action['coords'])
        else:
            print("Action unrecognised.")
        
        #Check if a sequence has just been completed. If so, upgrade chips to special sequence chips.
        if action['type']=='place':
            seq,seq_type = self.checkSeq(state.board.chips, plr_state, (r,c))
            if seq:
                reward += seq['num_seq']
                state.board.new_seq = seq_type
                for sequence in seq['coords']:
                    for r,c in sequence:
                        if state.board.chips[r][c] != '#': #Joker spaces stay jokers.
                            state.board.chips[r][c] = plr_state.seq_colour
                            try:
                                state.board.plr_coords[plr_state.colour].remove(action['coords'])
                            except: #Chip coords were already removed with the first sequence.
                                pass
                plr_state.completed_seqs += seq['num_seq']
                plr_state.seq_orientations.extend(seq['orientation'])
        
        plr_state.trade = False #Reset trade flag if agent has completed a full turn.
        plr_state.agent_trace.action_reward.append((action,reward)) #Log this turn's action and any resultant score.
        plr_state.score += reward
        return state
    
    def getLegalActions(self, game_state, agent_id):
        actions = []
        agent_state = game_state.agents[agent_id]
        
        #First, give the agent the option to trade a dead card, if they haven't just done so.
        if not agent_state.trade:
            for card in agent_state.hand:
                if card[0]!='j':
                    free_spaces = 0
                    for r,c in COORDS[card]:
                        if game_state.board.chips[r][c]=='_':
                            free_spaces+=1
                    if not free_spaces: #No option to place, so card is considered dead and can be traded.
                        for draft in game_state.board.draft:
                            actions.append({'play_card':card, 'draft_card':draft, 'type':'trade', 'coords':None})
                        
            if len(actions): #If trade actions available, return those, along with the option to forego the trade.
                actions.append({'play_card':None, 'draft_card':None, 'type':'trade', 'coords':None})
                return actions
                
        #If trade is prohibited, or no trades available, add action/s for each card in player's hand.
        #For each action, add copies corresponding to the various draft cards that could be selected at end of turn.
        for card in agent_state.hand:
            if card in ['jd','jc']: #two-eyed jacks
                for r in range(10):
                    for c in range(10):
                        if game_state.board.chips[r][c]=='_':
                            for draft in game_state.board.draft:
                                actions.append({'play_card':card, 'draft_card':draft, 'type':'place', 'coords':(r,c)})
                            
            elif card in ['jh','js']: #one-eyed jacks
                for r in range(10):
                    for c in range(10):
                        if game_state.board.chips[r][c]==agent_state.opp_colour:
                            for draft in game_state.board.draft:
                                actions.append({'play_card':card, 'draft_card':draft, 'type':'remove', 'coords':(r,c)})
            
            else: #regular cards
                for r,c in COORDS[card]:
                    if game_state.board.chips[r][c]=='_':
                        for draft in game_state.board.draft:
                            actions.append({'play_card':card, 'draft_card':draft, 'type':'place', 'coords':(r,c)})
                    
        return actions
    
    def gameEnds(self, state): 
        scores = {"r":0, "b":0}
        for plr_state in state.agents:
            scores[plr_state.colour] += plr_state.completed_seqs
        return scores["r"]>=2 or scores["b"]>=2 or len(state.board.draft)==0
    
    def extractFeatures(self, state, action, agent_id):

        features = defaultdict(int)
        chips = deepcopy(state.board.chips)
        agent = state.agents[agent_id]
        anti_agent = state.agents[(agent_id % 2) + 1]
        colour = agent.colour
        anti_colour = anti_agent.colour
        double_eye = ['jd','jc']
        single_eye = ['jh','js']
        heart = [(4,4),(4,5),(5,4),(5,5)]
        all_jack = single_eye + double_eye
        coords = []
        hand_coords = []
        rollback = []
        
        #first deal with the draft
        for hand in agent.hand:
            if hand not in all_jack:
                hand_coords += self.cardToCoords(hand)
        for (r,c) in hand_coords:
            if chips[r][c] == '_':
                rollback.append((r,c))
                chips[r][c] = colour
        
        if action['draft_card'] is None:
            return features
        else:
            draft = action['draft_card']
            if draft in single_eye:
                features['draft_single_eye'] = 1
            elif draft in double_eye:
                features['draft_double_eye'] = 1
            else:
                max_numseq = 0
                max_possible = 0
                max_length = 0
                anti_max_numseq = 0
                anti_max_possible = 0
                anti_max_length = 0
                coords = self.cardToCoords(draft)
                for (r,c) in coords:
                    if chips[r][c] == '_':
                        chips[r][c] = colour
                        numseq, possible, length = self.checkSeqAndPossible(chips, agent, (r,c))
                        chips[r][c] = anti_colour
                        anti_num_seq, anti_possible, anti_length = self.checkSeqAndPossible(chips, anti_agent, (r,c))
                        chips[r][c] = '_'
                        if anti_num_seq > anti_max_numseq:
                            anti_max_numseq = anti_num_seq
                        if anti_possible > anti_max_possible:
                            anti_max_possible = anti_possible    
                        if anti_length > anti_max_length:
                            anti_max_length = anti_length
                        if numseq > max_numseq:
                            max_numseq = numseq
                        if possible > max_possible:
                            max_possible = possible
                        if length > max_length:
                            max_length = length
                features['draft_makeseq'] = max_numseq / 4
                features['draft_seq_point'] = max_possible / 36
                features['draft_max_length'] = max_length / 5
                features['draft_harm_seq'] = anti_max_numseq / 4
                features['draft_harm_point'] = anti_max_possible / 36
                features['draft_harm_length'] = anti_max_length / 5
                
            
            for (r,c) in rollback:
                chips[r][c] = '_'
                
            if action['type'] == 'trade':
                return features
            else:
                play = action['play_card']
                if play in double_eye:
                    features['place_double_eye'] = 1 
                heart_play = 0
                (r,c) = action['coords']
                if (r,c) in heart:
                    heart_play = 1
                chips[r][c] = colour
                num_seq, possible, length = self.checkSeqAndPossible(chips, agent, (r,c))
                links = self.linked_dots((r,c), chips, agent)
                chips[r][c] = anti_colour
                anti_links = self.linked_dots((r,c), chips, anti_agent)
                anti_num_seq, anti_possible, anti_length = self.checkSeqAndPossible(chips, anti_agent, (r,c))
                
                if action['type'] == 'place':
                    features['place_around'] = links / 8
                    features['place_anti_around'] = anti_links / 8
                    features['place_heart'] = heart_play
                    features['place_profit_seq'] = num_seq / 4
                    features['place_profit_point'] = possible / 36
                    features['place_harm_seq'] = anti_num_seq / 4
                    features['place_harm_point'] = anti_possible / 36
                    features['place_profit_length'] = length / 5
                    features['place_harm_length'] = anti_length / 5
                    chips[r][c] = '_'
                else:
                    features['remove_around'] = links / 8
                    features['remove_anti_around'] = anti_links / 8
                    features['remove_heart'] = heart_play
                    features['remove_profit_seq'] = num_seq 
                    features['remove_profit_point'] = possible / 36
                    features['remove_profit_length'] = length / 5
                    features['remove_harm_length'] = anti_length / 5
                    features['remove_harm_point'] = anti_possible / 36
                    chips[r][c] = anti_colour
        
        return features
    
    def linked_dots(self, coord, chips, agent):
        (r,c) = coord
        dots = 0
        linked = [(r+1,c),(r-1,c),(r,c+1),(c,c-1),(r-1,c-1),(r+1,c+1),(r-1,c+1),(r+1,c-1)]
        
        for (lr,lc) in linked:
            if lr > 9 or lr < 0 or lc > 9 or lc < 0:
                continue
            if chips[lr][lc] == agent.colour or chips[lr][lc] == agent.seq_colour:
                dots += 1
        return dots
        
    def getQValue(self, state, action, weights, agent_id):
        qValue = 0.0
        features = self.extractFeatures(state, action, agent_id)
        for feature, value in features.items():
            qValue += value * weights.get(feature, 0.0)
        return qValue
    
    def get_nextState(self, state, action, agent_id, weights):
        
        pass_reward = state.agents[agent_id].score     
        new_state = self.generateSuccessor(state, action, agent_id)
        reward = new_state.agents[agent_id].score
        reward = reward - pass_reward
        
        if self.gameEnds(new_state):
            return new_state, reward

        anti_reward = state.agents[(agent_id % 2) + 1].score
        
        rest = [1,2,3]
        if agent_id == 1:
            rest = [2,3,0]
        elif agent_id == 2:
            rest = [3,0,1]
        elif agent_id == 3:
            rest = [0,1,2]
            
        right_anti_reward = 0  

        for rest_id in rest:
            actions = self.getLegalActions(new_state, rest_id)
            max_value = float("-inf")
            new_action = actions[0]
    
            while new_action['type'] == 'trade':
                new_state = self.generateSuccessor(new_state, new_action, rest_id)
                actions = self.getLegalActions(new_state, rest_id)
                new_action = actions[0]
            
            for pos_action in actions:
                if max_value < self.getQValue(new_state, pos_action, weights, rest_id):
                    new_action = pos_action
                
            new_state = self.generateSuccessor(new_state, new_action, rest_id)
            if self.gameEnds(new_state):
                break

        right_anti_reward = new_state.agents[(agent_id % 2) + 1].score - anti_reward
            
            
        reward = reward - right_anti_reward
        
        return new_state, reward
            