from pymycobot.mycobot import MyCobot
import pymycobot
from pymycobot import PI_PORT, PI_BAUD 
import time
import os
import sys
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle, Coord

# Positions and angles for the tic-tac-toe game
DigPos = [[265.9, 63.8, 104.7, -179.02, 2.73, -43.74], 
          [266.1, 8.9, 111.1, 176.67, 6.94, -55.83],
          ...
          [167.6, -38.5, 115.2, -176.4, 3.62, 26.65]]

abovePos = [[265.9, 63.8, 170, -179.02, 2.73, -43.74], 
            ...
            [167.6, -38.5, 170, -176.4, 3.62, 26.65]]
            
DigAngles = [[32.78, -37.96, -100.72, 52.73, -0.7, 10.89],
             ...
             [2.46, -1.66, -152.13, 59.85, 4.65, 13.62]]

XAng = [69.08, -31.28, -113.73, 53.87, 4.21, 11.33]
AirAng = [0.96, -21.35, -54.4, 6.06, -0.52, -20.91]
            
XPos = [142.6, 154.9, 95, 179.08, 1.29, -60.3]
AirPos = [206.3, -12.7, 216.6, 177.34, 7.74, -169.83]

import random

class Tic(object):
    winning_combos = (
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        ...
        [2, 4, 6])
    winners = ('X-win', 'Draw', 'O-win')

    def __init__(self, squares=[]):
        """Initialize either custom or default board"""
        self.mc = None
        if len(squares) == 0:
            self.squares = [None for i in range(9)]
        else:
            self.squares = squares

    def initialize(self):
        self.mc = MyCobot("/dev/ttyACM1", 115200)
        self.mc.sync_send_angles([0, 0, 0, 0, 0, 0], 30, 2)
        time.sleep(2)

    def show(self):
        """Print game progress"""
        for element in [self.squares[i: i + 3] for i in range(0, len(self.squares), 3)]:
            print(element)

    def available_moves(self):
        return [k for k, v in enumerate(self.squares) if v is None]

    def available_combos(self, player):
        return self.available_moves() + self.get_squares(player)

    def complete(self):
        """Check if game has ended"""
        if None not in [v for v in self.squares]:
            return True
        if self.winner() is not None:
            return True
        return False

    def X_won(self):
        return self.winner() == 'X'

    def O_won(self):
        return self.winner() == 'O'

    def tied(self):
        return self.complete() and self.winner() is None

    def winner(self):
        for player in ('X', 'O'):
            positions = self.get_squares(player)
            for combo in self.winning_combos:
                win = True
                for pos in combo:
                    if pos not in positions:
                        win = False
                if win:
                    return player
        return None

    def get_squares(self, player):
        """Returns squares belonging to a player"""
        return [k for k, v in enumerate(self.squares) if v == player]

    def make_move(self, position, player):
        self.squares[position] = player

    def move_cobot(self, position):
        global DigPos, XPos, AirPos, XAng, AirAng
        speeds = 30
        positionInt = int(position)
        
        # Pick position
        self.mc.sync_send_angles(AirAng, speeds, 2)
        print("Air")
        time.sleep(3)

        self.mc.sync_send_coords([115.8, 177.3, 210.6, 178.06, -0.92, -6.11], speeds, 1)
        print("Above Pick")

        self.mc.sync_send_coords(XPos, speeds, 1)
        print("Pick")
        time.sleep(3)

        # Turn on Suction
        self.pump_on()
        time.sleep(3)

        self.mc.sync_send_angles(AirAng, speeds, 2)
        print("Air")
        time.sleep(3)

        self.mc.sync_send_coords(abovePos[positionInt], speeds, 1)
        print("Pos")
        time.sleep(3)

        self.mc.sync_send_coords(DigPos[positionInt], speeds, 1)
        print("Pos")
        time.sleep(3)

        # Turn Off Suction
        self.pump_off()
        time.sleep(4)

    def pump_on(self):
        self.mc.set_basic_output(2, 0)
        self.mc.set_basic_output(5, 0)

    def pump_off(self):
        self.mc.set_basic_output(2, 1)
        self.mc.set_basic_output(5, 1)

    def alphabeta(self, node, player, alpha, beta):
        """Alphabeta algorithm"""
        if node.complete():
            if node.X_won():
                return -1
            elif node.tied():
                return 0
            elif node.O_won():
                return 1

        for move in node.available_moves():
            node.make_move(move, player)
            val = self.alphabeta(node, get_enemy(player), alpha, beta)
            node.make_move(move, None)
            if player == 'O':
                if val > alpha:
                    alpha = val
                if alpha >= beta:
                    return beta
            else:
                if val < beta:
                    beta = val
                if beta <= alpha:
                    return alpha
        return alpha if player == 'O' else beta

def get_enemy(player):
    if player == 'X':
        return 'O'
    return 'X'

def determine(board, player):
    """Determine best possible move"""
    a = -2
    choices = []
    if len(board.available_moves()) == 9:
        return 4
    for move in board.available_moves():
        board.make_move(move, player)
        val = board.alphabeta(board, get_enemy(player), -2, 2)
        board.make_move(move, None)
        if val > a:
            a = val
            choices = [move]
        elif val == a:
            choices.append(move)
    return random.choice(choices)

if __name__ == '__main__':
    board = Tic()
    board.show()
    board.initialize()
    digitSel = 0
    
    while not board.complete():
        player = 'X'
        player_move = int(input('Next Move: ')) - 1
        if player_move not in board.available_moves():
            continue
        board.make_move(player_move, player)
        board.move_cobot(player_move)
        print(DigPos[player_move])
        board.show()

        if board.complete():
            break
        player = get_enemy(player)
        computer_move = determine(board, player)
        board.make_move(computer_move, player)
        board.move_cobot(computer_move)
        print(DigPos[computer_move])
        print(computer_move + 1)
        board.show()
    print('Winner is', board.winner())
