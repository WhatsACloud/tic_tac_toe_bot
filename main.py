import curses

from game import Game
from nnTrainer import Trainer
from program import Program
from badCursesDebugger import output

def better_wrapper(func):
    """wraps curses"""
    try:
        stdscr = curses.initscr()
        curses.filter()
        curses.noecho()
        curses.cbreak()
        #curses.curs_set(False)
        stdscr.keypad(True)
        stdscr.clear()
        return func(stdscr)
    finally:
        curses.nocbreak()
        stdscr.keypad(False)
        curses.echo()
        curses.curs_set(True)
        curses.endwin()
        output()

def main(stdscr):
    'main'
    Program(stdscr, "tic tac toe", {
        "game": {
            "options": {
                "board length": 3,
                "ai": True,
                "ai file": "fileOne",
                "start first": True
            },
            "program_class": Game
        },
        "AI training": {
            "options": {
                "board_length": 3,
                "select file1": "fileOne",
                "select file2": "fileTwo",
                "show training": True,
                "slowAmt": 0,
                "new": True,
                "rounds": 10,
                "start first": True
            },
            "program_class": Trainer
        }
    }).run()

if __name__ == "__main__":
    better_wrapper(main)
