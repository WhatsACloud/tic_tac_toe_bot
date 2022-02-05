upright = "|"
sideways = "_"
empty = " "

def drawBoard(**kwargs):
    square_length = kwargs.pop("square_length", 5)
    square_height = kwargs.pop("square_height", 3)
    board_length = kwargs.pop("board_length", 5)
    board = []
    true_board_height = board_length*square_height
    true_board_length = board_length*square_length+(board_length-1)
    #print(true_board_height, true_board_length)
    for rowNo in range(true_board_height):
        row = [empty] * true_board_length
        if (rowNo+1) % square_height == 0 and rowNo != true_board_height-1:
            row = [sideways] * true_board_length
        for line in range(board_length-1):
            row[((line+1)*square_length)+line] = upright
        board.append("".join(row))
    return board

if __name__ == "__main__":
    for i in drawBoard():
        print(i)