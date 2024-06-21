# Tic-Tac-Toe-with-MyCobot-Robotic-Arm


Referencing my lab partner's video:

![Tic-Tac-Toe](https://github.com/SivarajuRanga1002/Tic-Tac-Toe-with-MyCobot-Robotic-Arm/assets/65248651/a09b3b02-6144-4f32-aecd-2a729bd5e877)

https://www.youtube.com/watch?v=fsAbi8Muey8&list=PLVMTVkBf5nwJ27I7ac7mX2-FmtAKAjzNr&index=7&ab_channel=SivarajuYashaswiRanga


Tic Tac Toe with MyCobot Robotic Arm
This project showcases a Tic Tac Toe game played using a 6 DOF MyCobot robotic arm by Elephant Robotics. The game leverages a Raspberry Pi 4B with WiFi modules and an ESP32 with 6 servo motors to control the robotic arm.

How It Works
The robotic arm plays Tic Tac Toe by picking and placing objects on a 3x3 grid. The arm's movements are programmed to respond to user input and AI decisions, making the game interactive and engaging. The AI uses the Alpha-Beta pruning algorithm to determine the best possible moves.

Code Explanation
Importing Libraries
python
Copy code
from pymycobot.mycobot import MyCobot
import pymycobot
from pymycobot import PI_PORT, PI_BAUD 
import time
import os
import sys
from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle, Coord
We start by importing the necessary libraries and modules for controlling the MyCobot arm and other standard libraries.

Defining Positions and Angles
python
Copy code
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
Here, we define the various positions and angles that the robotic arm will use to pick and place objects on the Tic Tac Toe grid.

Tic Class
python
Copy code
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
This class defines the game logic and the robotic arm's movements. It includes methods for initializing the game, checking the game state, making moves, and controlling the robotic arm.

Jay Init
python
Copy code
    def initialize(self):
        self.mc = MyCobot("/dev/ttyACM1", 115200)
        self.mc.sync_send_angles([0, 0, 0, 0, 0, 0], 30, 2)
        time.sleep(2)
The initialize method initializes the MyCobot arm, setting it to its default position.

Show Game Progress
python
Copy code
    def show(self):
        """Print game progress"""
        for element in [self.squares[i: i + 3] for i in range(0, len(self.squares), 3)]:
            print(element)
The show method prints the current state of the game board.

Available Moves
python
Copy code
    def available_moves(self):
        return [k for k, v in enumerate(self.squares) if v is None]
This method returns a list of available moves.

Game Completion and Winner Check
python
Copy code
    def complete(self):
        """Check if game has ended"""
        if None not in [v for v in self.squares]:
            return True
        if self.winner() is not None:
            return True
        return False

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
These methods check if the game is complete and determine the winner.

Making Moves and Controlling the Robotic Arm
python
Copy code
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
The make_move method updates the board with a player's move. The move_cobot method controls the MyCobot arm to execute the move physically, including picking up and placing objects using the suction pump.

AI and Alpha-Beta Pruning
python
Copy code
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
The alphabeta method implements the Alpha-Beta pruning algorithm to determine the best move for the AI.

Determine Best Move for AI
python
Copy code
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
These functions help in determining the best possible move for the AI player.

Main Execution
python
Copy code
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
This is the main loop that initializes the game, takes user input for moves, updates the board, and controls the MyCobot arm to execute the moves.
