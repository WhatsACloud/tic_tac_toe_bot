'contains the Game class'
import curses
import math
import time

from badCursesDebugger import buffer
from boardDrawer import drawBoard
from nnTrainer import Trainer

char_map = {
    True: "X",
    False: "0"
}

render_map = {
    True: 1,
    False: 2
}

game_movecursor_map = {
    "KEY_UP": [-1, 0],
    "KEY_DOWN": [1, 0],
    "KEY_LEFT": [0, -1],
    "KEY_RIGHT": [0, 1],
    "w": [-1, 0],
    "s": [1, 0],
    "a": [0, -1],
    "d": [0, 1]
}

def board_val_to_char(num):
    'returns the assigned character of a board value e.g. 1 -> X, 2 -> 0'
    return char_map[{render_map[k]:k for k in render_map}[num]]

SQUARE_LENGTH = 9
SQUARE_HEIGHT = 5
CURSOR_OFFSET = 2
WIN_POS = [5, 0]
WIN_WAIT = 1

class Game:
    'the class for the tic tac toe game'
    def __init__(self, options, stdscr=None):
        self.ai = None
        self.length = options["board length"]
        if options["ai"]:
            self.generate_trainer(options, self.length, stdscr)
            self.training = True
        else:
            self.training = False
        if stdscr is not None:
            self.stdscr = stdscr
            stdscr.clear()
            stdscr.refresh()
        self.running = False
        self.won = None
        if self.length > 4:
            self.match_length = math.ceil(self.length*0.75)
        else:
            self.match_length = 3
        self.true_length = self.length*SQUARE_LENGTH+self.length
        self.board = [[0 for i in range(self.length)] \
                        for j in range(self.length)]
        self.win = None
        self.rendered_board = drawBoard(
            board_length=self.length,
            square_length=SQUARE_LENGTH,
            square_height=SQUARE_HEIGHT
        )
        self.original_rendered_board = self.rendered_board.copy()
        self.turn = options["start first"]
        self.past_game_pos = None
        self.cursor_pos = [0, 0]

    def generate_trainer(self, options, length, stdscr):
        'generates player for ai'
        self.ai_file_name = options["ai file"]
        self.ai = Trainer(
            {
                "board_length": length,
                "select file1": self.ai_file_name,
                "select file2": "",
                "show training": True,
                "start first": options["start first"],
                "slowAmt": 0,
                "new": False,
                "rounds": 1
            },
            stdscr,
            self
        )

    def update_rendered_board(self):
        'updates the rendered board'
        for row_no, row in enumerate(self.board):
            for index in range(len(self.board[row_no])):
                box = row[index]
                if box != 0:
                    box = board_val_to_char(box)
                    true_pos_y = math.ceil(SQUARE_HEIGHT/2) \
                                            + (row_no-1) \
                                            * SQUARE_HEIGHT \
                                            + SQUARE_HEIGHT-1
                    true_pos_x = math.ceil(SQUARE_LENGTH/2) + ((index) * SQUARE_LENGTH) + index-1
                    chars = list(self.rendered_board[true_pos_y])
                    chars[true_pos_x] = box
                    self.rendered_board[true_pos_y] = "".join(chars)

    def render_board(self):
        'renders the board'
        for i,string in enumerate(self.rendered_board):
            self.win.addstr(i,0,string)
        self.win.box()
        self.win.refresh()

    def render_cursor(self):
        'renders the cursor'
        cursor = curses.newwin(3, 5, (
            self.cursor_pos[0]
            * (SQUARE_HEIGHT))
            + round(CURSOR_OFFSET/2)
            + WIN_POS[0],
            (self.cursor_pos[1]
            * (SQUARE_LENGTH+1)
        ) + CURSOR_OFFSET+WIN_POS[1])

        cursor.box()
        if self.get_cursor_selected_val() != 0:
            cursor.move(1,2)

            cursor.addch(board_val_to_char(self.get_cursor_selected_val()))
        cursor.refresh()

    def render(self):
        'combines all the render methods and renders some additional text'
        self.win = curses.newwin(
            self.length*SQUARE_HEIGHT,
            self.true_length,
            WIN_POS[0],
            WIN_POS[1]
        )
        self.update_rendered_board()
        self.render_board()
        self.render_cursor()
        self.stdscr.move(WIN_POS[0]-1, round(WIN_POS[1]+self.true_length/3))
        self.stdscr.addstr(char_map[self.turn]+"'s turn")
        self.stdscr.move(WIN_POS[0]-2, round(WIN_POS[1]+self.true_length/3))
        self.stdscr.addstr("match "+str(self.match_length)+" in a row to win")
        self.stdscr.move(WIN_POS[0]-3, round(WIN_POS[1]+self.true_length/3))
        self.stdscr.addstr(str(self.length)+"x"+str(self.length)+" grid")

    def get_cursor_selected_val(self):
        'returns the value at the selected position'
        return self.board[self.cursor_pos[0]][self.cursor_pos[1]]

    def move_cursor(self, directions):
        'changes cursor_pos according to the direction'
        if (0 <= self.cursor_pos[0] + directions[0] <= self.length-1) \
                and (0 <= self.cursor_pos[1] + directions[1] <= self.length-1):
            self.cursor_pos[0] += directions[0]
            self.cursor_pos[1] += directions[1]

    def has_draw(self):
        'checks if the game has drawn'
        draw = False
        for row in self.board:
            draw = row.count(0) == 0
            if draw is False:
                break
        return draw

    def haswon(self):
        'checks if the game has ended and its outcome'
        current_turn = not self.turn
        if self.has_draw():
            self.won = 3
            return
        for row_no in range(self.length):
            check_list = [
                self.board[row_no], # horizontally
                [self.board[x][row_no] for x in range(self.length)], # vertically
                [self.board[x][x] for x in range(self.length)], # diagonally downwards
                [self.board[x][self.length-x-1] for x in range(self.length)] # diagonally upwards
            ]
            for compre in check_list:
                if compre.count(render_map[current_turn]) == self.match_length:
                    self.won = current_turn
                    return

    def terminate(self, immediate=False):
        'terminates the game object'
        self.stdscr.move(round(self.true_length/3), round(self.true_length/3))
        if self.won != 3:
            self.stdscr.addstr(char_map[self.won]+" has won!")
        else:
            self.stdscr.addstr("Draw!")
        self.stdscr.refresh()
        if not immediate:
            time.sleep(WIN_WAIT)
        self.running = False

    def reset(self):
        'resets the board and everything for playing again'
        if self.ai:
            self.ai.save()
            self.terminate()
            return
        self.board = [[0 for i in range(self.length)] for j in range(self.length)]
        self.turn = True
        self.cursor_pos = [0, 0]
        self.won = None
        self.rendered_board = self.original_rendered_board.copy()

    def place(self):
        'attempts to place x or 0 according to the cursor_pos'
        if self.get_cursor_selected_val() == 0:
            self.board[self.cursor_pos[0]][self.cursor_pos[1]] = render_map[self.turn]
            self.turn = not self.turn
            self.haswon()
            if not self.training:
                self.render()
            if (self.won is not None) and (not self.training):
                self.terminate()
            return True
        return False

    def process_input(self):
        'receives input and makes the game respond accordingly'
        INPUT = self.stdscr.getkey()
        if INPUT in game_movecursor_map:
            directions = game_movecursor_map[INPUT]
            self.move_cursor(directions)
        elif INPUT in (" ", "\n"):
            self.place()
        elif INPUT == "q":
            self.won = not self.turn
            self.terminate(True)

    def run(self):
        'runs the game'
        self.running = True
        if self.ai is not None:
            self.past_game_pos = []
            while self.running:
                self.render()
                if not self.turn:
                    self.ai.network_play(self.ai.network1, self, self.past_game_pos, 500)
                else:
                    self.process_input()
        else:
            while self.running:
                self.render()
                self.process_input()
