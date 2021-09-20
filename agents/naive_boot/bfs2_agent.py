from template import Agent
import random
from Sequence.sequence_model import *
from Sequence.sequence_utils import *
import copy

# Code for queue is extracted from COMP90054 Assignment 1
class Queue:
    "A container with a first-in-first-out (FIFO) queuing policy."
    def __init__(self):
        self.list = []

    def push(self,item):
        "Enqueue the 'item' into the queue"
        self.list.insert(0,item)

    def pop(self):
        """
          Dequeue the earliest enqueued item still in the queue. This
          operation removes the item from the queue.
        """
        return self.list.pop()

    def isEmpty(self):
        "Returns true if the queue is empty"
        return len(self.list) == 0


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

    def bfs(self, game_state, agent_id, hand_cards):

        my_queue = Queue()
        current_cards = hand_cards
        current_chips = game_state.board.chips
        plr_state = game_state.agents[agent_id]

        my_queue.push((current_chips, [], current_cards))
        total_node_expanded = 0
        while not my_queue.isEmpty():
            if total_node_expanded > 200:
                break
            chips, path, cards = my_queue.pop()
            total_node_expanded += 1
            j_exist = False
            for card in cards:
                if card == 'jc' or card == 'jd':
                    j_exist = True
                    position = self.find_best_dj_position(plr_state, chips)
                    r, c = position
                    new_chips = copy.deepcopy(chips)
                    new_chips[r][c] = plr_state.colour
                    new_cards = copy.deepcopy(cards)
                    new_cards.remove(card)
                    if self.checkSeq(new_chips, plr_state, position) > 0:
                        return path + [(card, position)]
                    my_queue.push((new_chips, path + [(card, position)], new_cards))
                    break

            if j_exist == True:
                continue

            for card in cards:
                if card == 'js' or card == 'jh':
                    j_exist = True
                    opp_colour = plr_state.opp_colour
                    opp_coords = game_state.board.plr_coords[opp_colour]
                    if len(opp_coords) == 0:
                        j_exist = False
                        break
                    position = self.find_best_sj_position(plr_state, chips)
                    r, c = position
                    new_chips = copy.deepcopy(chips)
                    new_chips[r][c] = EMPTY
                    new_cards = copy.deepcopy(cards)
                    new_cards.remove(card)
                    my_queue.push((new_chips, path + [(card, position)], new_cards))
                    break

            if j_exist == True:
                continue

            for card in cards:
                if card == 'js' or card == 'jh':
                    continue
                coords = COORDS[card]
                for coord in coords:
                    r, c = coord
                    new_chips = copy.deepcopy(chips)
                    if new_chips[r][c] == EMPTY:
                        new_chips[r][c] = plr_state.colour
                    else:
                        continue
                    new_cards = copy.deepcopy(cards)
                    new_cards.remove(card)
                    if self.checkSeq(new_chips, plr_state, coord) > 0:
                        return path + [(card, coord)]
                    my_queue.push((new_chips, path + [(card, coord)], new_cards))
        return []


    def SelectAction(self, actions, game_state):

        plr_state = game_state.agents[self.id]
        # If there is trade in actions, just search for the best draft and get the card
        best_draft = self.get_best_draft(game_state, self.id)
        if actions[0]['type'] == 'trade':
            for action in actions:
                if action['draft_card'] == best_draft:
                    return action

        hand_cards = copy.deepcopy(game_state.agents[self.id].hand)
        hand_cards.append(best_draft)
        bfs_action = self.bfs(game_state, self.id, hand_cards)
        if bfs_action:
            play_card = bfs_action[0][0]
            play_position = bfs_action[0][1]
            if play_card != best_draft:
                if play_card == 'js' or play_position == 'jh':
                    return {'play_card': play_card, 'draft_card': best_draft, 'type': 'remove', 'coords': play_position}
                else:
                    return {'play_card': play_card, 'draft_card': best_draft, 'type': 'place', 'coords': play_position}

        current_chips = game_state.board.chips
        current_cards = game_state.agents[self.id].hand
        for card in current_cards:
            if card == 'jc' or card == 'jd':
                position = self.find_best_dj_position(plr_state, current_chips)
                action = {'play_card': card, 'draft_card': best_draft, 'type': 'place', 'coords': position}
                return action
        for card in current_cards:
            if card == 'js' or card == 'jh':
                opp_colour = game_state.agents[self.id].opp_colour
                opp_coords = game_state.board.plr_coords[opp_colour]
                if len(opp_coords) == 0:
                    break
                position = self.find_best_sj_position(plr_state, current_chips)
                action = {'play_card': card, 'draft_card': best_draft, 'type': 'remove', 'coords': position}
                return action

        max_nearby_chips = 0
        plr_state = game_state.agents[self.id]
        best_coord = (-1, -1)
        best_card = ''
        for card in current_cards:
            coords = COORDS[card]
            for coord in coords:
                new_nearby_chips = self.get_nearby_chips(current_chips, plr_state, coord)
                r, c = coord
                if current_chips[r][c] != EMPTY:
                    continue
                if new_nearby_chips >= max_nearby_chips:
                    max_nearby_chips = new_nearby_chips
                    best_coord = coord
                    best_card = card
        if best_coord == (-1, -1):
            return random.choice(actions)
        best_action = {'play_card': best_card, 'draft_card': best_draft, 'type': 'place', 'coords': best_coord}
        return best_action

