'program class for terminal ui, used to adjust settings and use different programs'
import curses
from badCursesDebugger import buffer

def space(self):
    'selects object below cursor'
    if self.options is None:
        program_name = list(self.programs.keys())[self.cursor]
        self.options = self.programs[program_name]["options"]
        self.selected_program = program_name
        self.cursor = 0

def down(self):
    'moves the cursor down'
    if self.options is not None:
        if self.cursor+1 < len(self.options.items()):
            self.cursor += 1
        return
    if self.cursor+1 < len(self.programs.items()):
        self.cursor += 1

def up(self):
    'moves the cursor up'
    if self.cursor-1 >= 0:
        self.cursor -= 1

def out(self):
    'exits the scope'
    if self.options:
        self.options = None
        self.selected_program = None
        return
    self.running = False

def enter(self):
    'starts the selected program'
    if self.selected_program is not None:
        program = self.programs[self.selected_program]["program_class"]
        if self.selected_program == "game":
            program(self.options, self.stdscr).run()
        else:
            game = self.programs["game"]["program_class"](
                {
                    "board length": self.options["board_length"],
                    "ai": False,
                    "start first": self.options["start first"]
                },
                self.stdscr
            )
            program(self.options, self.stdscr, game).run()

input_map = {
    " ": space,
    "KEY_UP": up,
    "KEY_DOWN": down,
    "q": out,
    "\n": enter
}

class Program:
    'program class'
    def __init__(self, stdscr, title, programs):
        self.programs = programs
        self.selected_program = None
        self.cursor = 0
        self.options = None
        self.title = title
        self.stdscr = stdscr
        self.win = None
        self.running = True

    def render_options(self, options=None):
        """renders options"""
        self.stdscr.clear()
        self.stdscr.move(1, 0)
        self.stdscr.addstr(self.title)
        if options is None:
            options = list(self.programs.keys())
        self.stdscr.refresh()
        self.win = curses.newwin(len(options)+2, 30, 2, 0)
        self.win.box()
        for index, option in enumerate(options):
            original_value = option
            self.win.move(index+1, 2)
            self.win.addstr(option)
            if isinstance(options, dict):
                self.win.move(index+1, 3+len(option))
                if options[original_value] is not None:
                    self.win.addstr(str(options[original_value]))
        self.stdscr.move(self.cursor+3, 1)
        self.win.refresh()

    def validate_input(self, INPUT):
        'checks if input is valid and passes it into options if so'
        if self.options is not None:
            option_values = list(self.options.values())
            option_keys = list(self.options.keys())
            selected_key = option_keys[self.cursor]

            value = option_values[self.cursor]

            if INPUT == "KEY_BACKSPACE" and not isinstance(value, bool):
                if isinstance(value, str):
                    self.options[selected_key] = value[:-1]
                    return
                if len(str(value)) != 1 and value is not None:
                    self.options[selected_key] = int(str(value)[:-1])
                    return
                self.options[selected_key] = None
                return

            if len(str(value)) > 10:
                return

            if isinstance(value, bool):
                if INPUT in ("KEY_LEFT", "KEY_RIGHT"):
                    self.options[selected_key] = not value
                return

            if (not "KEY" in INPUT) and (INPUT != '\n'):
                if INPUT.isnumeric() or isinstance(INPUT, int):
                    if isinstance(value, int):
                        self.options[selected_key] = int(str(value) + INPUT)
                    elif value is None:
                        self.options[selected_key] = int(INPUT)
                    return
                if isinstance(value, str):
                    self.options[selected_key] = value + INPUT

    def run(self):
        'runs the program'
        while self.running:
            self.render_options(self.options)
            INPUT = self.stdscr.getkey()
            if INPUT in input_map:
                input_map[INPUT](self)
            else:
                self.validate_input(INPUT)
