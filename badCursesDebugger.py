'A module for printing outputs after a curses program has ended'
to_print = []

def buffer(*args):
    'adds the provided arguments to be printed later'
    to_print.append(args)

def output():
    'prints everything that was to be printed later'
    for i in to_print:
        if type(i) == tuple:
            print(*i)
        else:
            print(i)