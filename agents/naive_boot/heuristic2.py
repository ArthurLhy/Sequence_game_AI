# import time
from Sequence.sequence_utils import*
from Sequence.sequence_model import *
from collections import defaultdict
from template import Agent
import random
import heapq
import copy

class PriorityQueue:
    """
      Implements a priority queue data structure. Each inserted item
      has a priority associated with it and the client is usually interested
      in quick retrieval of the lowest-priority item in the queue. This
      data structure allows O(1) access to the lowest-priority item.
    """

    def __init__(self):
        self.heap = []
        self.count = 0

    def push(self, item, priority):
        entry = (priority, self.count, item)
        heapq.heappush(self.heap, entry)
        self.count += 1

    def pop(self):
        (_, _, item) = heapq.heappop(self.heap)
        return item

    def isEmpty(self):
        return len(self.heap) == 0

    def update(self, item, priority):
        # If item already in priority queue with higher priority, update its priority and rebuild the heap.
        # If item already in priority queue with equal or lower priority, do nothing.
        # If item not in priority queue, do the same thing as self.push.
        for index, (p, c, i) in enumerate(self.heap):
            if i == item:
                if p <= priority:
                    break
                del self.heap[index]
                self.heap.append((priority, c, item))
                heapq.heapify(self.heap)
                break
        else:
            self.push(item, priority)

class myAgent(Agent):
    def __init__(self, _id):
        super().__init__(_id)

    def checkSeq(self, chips, plr_state, last_coords):
        clr, sclr = plr_state.colour, plr_state.seq_colour
        oc, os = plr_state.opp_colour, plr_state.opp_seq_colour
        seq_type = TRADSEQ
        seq_coords = []
        seq_found = {'vr': 0, 'hz': 0, 'd1': 0, 'd2': 0, 'hb': 0}
        found = False
        nine_chip = lambda x, clr: len(x) == 9 and len(set(x)) == 1 and clr in x
        lr, lc = last_coords
        # All joker spaces become player chips for the purposes of sequence checking.
        for r, c in COORDS['jk']:
            chips[r][c] = clr
        # First, check "heart of the board" (2h, 3h, 4h, 5h). If possessed by one team, the game is over.
        coord_list = [(4, 4), (4, 5), (5, 4), (5, 5)]
        heart_chips = [chips[y][x] for x, y in coord_list]
        if EMPTY not in heart_chips and (clr in heart_chips or sclr in heart_chips) and not (
                oc in heart_chips or os in heart_chips):
            seq_type = HOTBSEQ
            seq_found['hb'] += 2
            seq_coords.append(coord_list)
        # Search vertical, horizontal, and both diagonals.
        vr = [(-4, 0), (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
        hz = [(0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
        d1 = [(-4, -4), (-3, -3), (-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        d2 = [(-4, 4), (-3, 3), (-2, 2), (-1, 1), (0, 0), (1, -1), (2, -2), (3, -3), (4, -4)]
        for seq, seq_name in [(vr, 'vr'), (hz, 'hz'), (d1, 'd1'), (d2, 'd2')]:
            coord_list = [(r + lr, c + lc) for r, c in seq]
            coord_list = [i for i in coord_list if 0 <= min(i) and 9 >= max(i)]  # Sequences must stay on the board.
            chip_str = ''.join([chips[r][c] for r, c in coord_list])
            # Check if there exists 4 player chips either side of new chip (counts as forming 2 sequences).
            if nine_chip(chip_str, clr):
                seq_found[seq_name] += 2
                seq_coords.append(coord_list)
            # If this potential sequence doesn't overlap an established sequence, do fast check.
            if sclr not in chip_str:
                sequence_len = 0
                start_idx = 0
                for i in range(len(chip_str)):
                    if chip_str[i] == clr:
                        sequence_len += 1
                    else:
                        start_idx = i + 1
                        sequence_len = 0
                    if sequence_len >= 5:
                        seq_found[seq_name] += 1
                        seq_coords.append(coord_list[start_idx:start_idx + 5])
                        break
            else:  # Check for sequences of 5 player chips, with a max. 1 chip from an existing sequence.
                for pattern in [clr * 5, clr * 4 + sclr, clr * 3 + sclr + clr, clr * 2 + sclr + clr * 2,
                                clr + sclr + clr * 3, sclr + clr * 4]:
                    for start_idx in range(5):
                        if chip_str[start_idx:start_idx + 5] == pattern:
                            seq_found[seq_name] += 1
                            seq_coords.append(coord_list[start_idx:start_idx + 5])
                            found = True
                            break
                    if found:
                        break
        for r, c in COORDS['jk']:
            chips[r][c] = JOKER  # Joker spaces reset after sequence checking.
        num_seq = sum(seq_found.values())
        if num_seq > 1 and seq_type != HOTBSEQ:
            seq_type = MULTSEQ
        return num_seq

    def get_nearby_chips(self, chips, plr_state, last_coords):
        clr, sclr = plr_state.colour, plr_state.seq_colour
        lr, lc = last_coords
        near_chips = 0
        vr = [(-4, 0), (-3, 0), (-2, 0), (-1, 0), (0, 0), (1, 0), (2, 0), (3, 0), (4, 0)]
        hz = [(0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4)]
        d1 = [(-4, -4), (-3, -3), (-2, -2), (-1, -1), (0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
        d2 = [(-4, 4), (-3, 3), (-2, 2), (-1, 1), (0, 0), (1, -1), (2, -2), (3, -3), (4, -4)]
        for seq, seq_name in [(vr, 'vr'), (hz, 'hz'), (d1, 'd1'), (d2, 'd2')]:
            coord_list = [(r + lr, c + lc) for r, c in seq]
            coord_list = [i for i in coord_list if 0 <= min(i) and 9 >= max(i)]
            chip_str = ''.join([chips[r][c] for r, c in coord_list])
            for chip in chip_str:
                if chip == clr or chip == sclr:
                    near_chips += 1
        return near_chips

    # def get_max_length(self, chips, plr_state, last_coords):

    def get_best_draft(self, game_state, agent_id):
        to_draft = ''
        draft = game_state.board.draft
        colour = game_state.agents[agent_id].colour
        best_seq = 0
        best_near_chips = 0
        draft_near_chips = ''
        current_chips = game_state.board.chips
        for card in draft:
            if card == 'jc' or card == 'jd':
                to_draft = card
                break
            elif card == 'js' or card == 'jh':
                to_draft = card
                break
            else:
                coords = COORDS[card]
                for coord in coords:
                    r, c = coord
                    new_chips = copy.deepcopy(current_chips)
                    if new_chips[r][c] == EMPTY:
                        new_chips[r][c] = colour
                        seq = self.checkSeq(new_chips, game_state.agents[agent_id], coord)
                        near_chips = self.get_nearby_chips(new_chips, game_state.agents[agent_id], coord)
                        if seq > best_seq:
                            best_seq = seq
                            to_draft = card
                        elif near_chips > best_near_chips:
                            best_near_chips = near_chips
                            draft_near_chips = card
        if to_draft == '':
            if draft_near_chips == '':
                to_draft = random.choice(draft)
            else:
                to_draft = draft_near_chips
        return to_draft

    def find_best_dj_position(self, plr_state, chips):
        best_seq = 0
        best_nearby_chips = 0
        best_location = (-1, -1)
        second_location = (-1, -1)
        for r in range(10):
            for c in range(10):
                new_chips = copy.deepcopy(chips)
                if new_chips[r][c] == EMPTY:
                    new_chips[r][c] = plr_state.colour
                    new_seq = self.checkSeq(new_chips, plr_state, (r, c))
                    new_nearby_chips = self.get_nearby_chips(new_chips, plr_state, (r, c))
                    if new_seq > best_seq:
                        best_seq = new_seq
                        best_location = (r, c)
                    elif new_nearby_chips >= best_nearby_chips:
                        best_nearby_chips = new_nearby_chips
                        second_location = (r, c)
        if best_location == (-1, -1):
            return second_location
        return best_location

    def find_best_sj_position(self, plr_state, chips):
        opp_colour = plr_state.opp_colour
        best_seq = 0
        best_nearby_chips = 0
        best_location = (-1,-1)
        second_location = (-1,-1)
        for r in range(10):
            for c in range(10):
                new_chips = copy.deepcopy(chips)
                if new_chips[r][c] == opp_colour:
                    new_chips[r][c] = plr_state.colour
                    new_seq = self.checkSeq(new_chips, plr_state, (r,c))
                    new_nearby_chips = self.get_nearby_chips(new_chips, plr_state, (r,c))
                    if new_seq > best_seq:
                        best_seq = new_seq
                        best_location = (r,c)
                    elif new_nearby_chips >= best_nearby_chips:
                        best_nearby_chips = new_nearby_chips
                        second_location = (r,c)
        if best_location == (-1, -1):
            return second_location
        return best_location

    def isSE(self, card):
        if card == 'js' or card == 'jh':
            return True
        return False

    def isDE(self, card):
        if card == 'jc' or card == 'jd':
            return True
        return False

    def is_our_chip(self, colour, plr_state):
        if colour == plr_state.colour or colour == plr_state.seq_colour:
            return True
        else:
            return False


    def AStartSearch(self, start_state):
        open = PriorityQueue()
        start_node = (start_state, {}, 0, [])
        chips, hand, plr_state = start_state
        initial_h = 5
        if plr_state.last_action:
            initial_h = self.heuristic(start_state, plr_state.last_action, plr_state)
        start_priority = 0 + initial_h
        open.push(start_node, start_priority)
        closed = []
        states = []
        best_g = []
        total_node_expanded = 0
        while open:
            total_node_expanded += 1
            if total_node_expanded < 400:
                node = open.pop()
                state, action, cost, path = node
                chips, hand, plr_state = state
                if state not in states:
                    states.append(state)
                    best_g.append(cost)
                    index = len(states) - 1
                else:
                    index = states.index(state)
                    old_g = best_g[index]
                if state not in closed or cost < old_g:
                    closed.append(state)
                    best_g[index] = cost
                    # is goal?
                    if action:
                        if self.isGoalState(state, action):
                            path = path + [(state, action)]
                            return path[1][-1]
                    #generate succeecors
                    successors = self.findSuccessors(state)
                    for succ_node in successors:
                        succ_state, succ_action, succ_cost = succ_node
                        new_node = (succ_state, succ_action, cost + succ_cost, path+[(succ_state, succ_action)])
                        # print('-------------------------------------------')
                        succ_h = self.heuristic(succ_state, succ_action, plr_state)
                        # print(cost + succ_cost)
                        # print('-------------------------------------------')
                        if succ_h < float('+inf'):
                            succ_priority = succ_h + new_node[2]
                            open.update(new_node, succ_priority)
            else:
                return None


    def isGoalState(self, state, action):
        chips, hand, plr_state = state
        if action['type'] == 'place':
            coord = action['coords']
            num_seq = self.checkSeq(chips, plr_state, coord)
            if num_seq > 0:
                print('goal reached11111111')
                return True
            elif self.is_our_chip(chips[4][4], plr_state) and self.is_our_chip(chips[4][5], plr_state) and self.is_our_chip(chips[5][4], plr_state) and self.is_our_chip(chips[5][5], plr_state):
                    return True
            return False


    def findSuccessors(self, state):
        chips, hand, plr_state = state
        successors = []
        for card in hand:
            potential_coords = COORDS[card]
            for row, col in potential_coords:
                if chips[row][col] == EMPTY:
                    new_hand = copy.deepcopy(hand)
                    new_hand.remove(card)
                    new_chips = copy.deepcopy(chips)
                    new_chips[row][col] = plr_state.colour
                    new_state = (new_chips, new_hand, plr_state)
                    action = {}
                    action['play_card'] = card
                    action['type'] = 'place'
                    action['coords'] = (row, col)
                    cost = 1
                    successors.append((new_state, action, cost))
        return successors


    def heuristic(self, state, action, plr_state):
        chips, hand, plr_state = state
        row, col = action['coords']
        chips[row][col] = plr_state.colour
        max_row = min(9, row+4)
        min_row = max(0, row-4)
        max_col = min(9, col+4)
        min_col = max(0, col-4)
        max_count = 0
        count = 0
        #vertical
        for i in range(min_row, max_row-3):
            count = 0
            if self.is_our_chip(chips[i][col], plr_state):
                count += 1
            if self.is_our_chip(chips[i+1][col], plr_state):
                count += 1
            if self.is_our_chip(chips[i+2][col], plr_state):
                count += 1
            if self.is_our_chip(chips[i+3][col], plr_state):
                count += 1
            if self.is_our_chip(chips[i+4][col], plr_state):
                count += 1
            max_count = max(count, max_count)
        #horizontal
        for i in range(min_col, max_col-3):
            count = 0
            if self.is_our_chip(chips[row][i], plr_state):
                count += 1
            if self.is_our_chip(chips[row][i+1], plr_state):
                count += 1
            if self.is_our_chip(chips[row][i+2], plr_state):
                count += 1
            if self.is_our_chip(chips[row][i+3], plr_state):
                count += 1
            if self.is_our_chip(chips[row][i+4], plr_state):
                count += 1
            max_count = max(count, max_count)
        #lu
        i = 4
        while i >= 0:
            if row - i >= 0 and col - i >= 0:
                break
            i -= 1
        j = 4
        while j >= 0:
            if row + j <= 9 and col + j <= 9:
                break
            j -= 1
        if j+i >= 4:
            for k in range(-i, j-3):
                count = 0
                if self.is_our_chip(chips[row+k][col+k], plr_state):
                    count += 1
                if self.is_our_chip(chips[row+k+1][col+k+1], plr_state):
                    count += 1
                if self.is_our_chip(chips[row+k+2][col+k+2], plr_state):
                    count += 1
                if self.is_our_chip(chips[row+k+3][col+k+3], plr_state):
                    count += 1
                if self.is_our_chip(chips[row+k+4][col+k+4], plr_state):
                    count += 1
                max_count = max(count, max_count)
        #ld
        i = 4
        while i >= 0:
            if row + i <= 9 and col -i >= 0:
                break
            i -= 1
        j = 4
        while j >= 0:
            if row - j >= 0 and col + j <= 9:
                break
            j -= 1
        if j+i >= 4:
            for k in range(-i, j-3):
                count = 0
                if self.is_our_chip(chips[row-k][col+k], plr_state):
                    count += 1
                if self.is_our_chip(chips[row-(k+1)][col+(k+1)], plr_state):
                    count += 1
                if self.is_our_chip(chips[row-(k+2)][col+(k+2)], plr_state):
                    count += 1
                if self.is_our_chip(chips[row-(k+3)][col+(k+3)], plr_state):
                    count += 1
                if self.is_our_chip(chips[row-(k+4)][col+(k+4)], plr_state):
                    count += 1
                max_count = max(count, max_count)
        left = 5 - max_count
        return left

    def SelectAction(self, actions, game_state):
        plr_state = game_state.agents[self.id]
        hand = copy.deepcopy(plr_state.hand)
        score = copy.deepcopy(plr_state.score)
        chips = copy.deepcopy(game_state.board.chips)

        #pick the best draft
        best_draft = self.get_best_draft(game_state, self.id)
        if actions[0]['type'] == 'trade':
            for action in actions:
                if action['draft_card'] == best_draft:
                    return action

        #handle doubleJ & singleJ
        hasDJ = False
        hasSJ = False
        picked_DJ = ""
        picked_SJ = ""
        for card in hand:
            if self.isDE(card):
                hasDJ = True
                picked_DJ = card
                DJ_best_position = self.find_best_dj_position(plr_state, chips)
            elif self.isSE(card):
                hasSJ = True
                picked_SJ = card
                SJ_best_position = self.find_best_sj_position(plr_state, chips)

        #go for j if have
        if hasDJ:
            for action in actions:
                if action['draft_card'] == best_draft:
                    if action['play_card'] == picked_DJ:
                        if action ['coords'] == DJ_best_position:
                            return action
        elif hasSJ:
            for action in actions:
                if action['draft_card'] == best_draft:
                    if action['play_card'] == picked_SJ:
                        if action['coords'] == SJ_best_position:
                            return action
        # start A*!!!!yeah!!!!!!
        else:
            hand_new = copy.deepcopy(hand)
            hand_new.append(best_draft)
            start_state = (chips, hand, plr_state)
            AStarAction = self.AStartSearch(start_state)
            if AStarAction:
                for action in actions:
                    if action['draft_card'] == best_draft:
                        if action['play_card'] == AStarAction['play_card']:
                            if action['coords'] == AStarAction['coords']:
                                if action['type'] == AStarAction['type']:
                                    return action
        max_nearby_chips = 0
        plr_state = game_state.agents[self.id]
        best_coord = (-1, -1)
        best_card = ''
        for card in hand:
            coords = COORDS[card]
            for coord in coords:
                new_nearby_chips = self.get_nearby_chips(chips, plr_state, coord)
                r, c = coord
                if chips[r][c] != EMPTY:
                    continue
                if new_nearby_chips >= max_nearby_chips:
                    max_nearby_chips = new_nearby_chips
                    best_coord = coord
                    best_card = card
        if best_coord == (-1, -1):
            return random.choice(actions)
        best_action = {'play_card': best_card, 'draft_card': best_draft, 'type': 'place', 'coords': best_coord}
        return best_action
