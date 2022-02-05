'Trainer class to train neural network to play tic tac toe'
import math
import random
import time
import pickle as pk
import numpy as np

from nn import HIDDEN_LAYER_AMT, INPUT_LAYER_AMT, LEARNING_RATE, OUTPUT_LAYER_AMT, rand
from nn import NeuralNetwork

from badCursesDebugger import buffer

def relish(file_name, obj):
    'pickles the python object into the provided file'
    if file_name is None:
        return False
    with open(file_name, "wb") as f:
        pk.dump(obj, f)
        return True

def unrelish(file_name):
    'loads the python object from a pickle file'
    if file_name is None:
        return False
    with open(file_name, "rb") as f:
        return pk.load(f)

def rand_weights_n_biases():
    'returns random weights and biases for the neural network'
    return [[rand((INPUT_LAYER_AMT, HIDDEN_LAYER_AMT)), rand((HIDDEN_LAYER_AMT, 1))], \
            [rand((HIDDEN_LAYER_AMT, HIDDEN_LAYER_AMT)), rand((HIDDEN_LAYER_AMT, 1))]], \
            [rand((HIDDEN_LAYER_AMT, OUTPUT_LAYER_AMT)), rand((OUTPUT_LAYER_AMT, 1))]

class Trainer:
    'Trainer class for neural network to play tic tac toe'
    def __init__(self, options, stdscr, game):
        self.file1 = options["select file1"]+".pkl"
        self.file2 = options["select file2"]+".pkl"
        self.original_file2 = options["select file2"]
        self.game = game

        if stdscr is not None:
            self.stdscr = stdscr
        self.show_training = options["show training"]
        self.slow_amt = options["slowAmt"]
        self.new = options["new"]
        self.board_length = options["board_length"]
        self.rounds = options["rounds"]

        self.training = False

        if self.new:
            self.network1 = NeuralNetwork(*rand_weights_n_biases(), self.board_length)
            self.network2 = NeuralNetwork(*rand_weights_n_biases(), self.board_length)
            self.network1.value = options["start first"]
            self.network2.value = not self.network1.value
        else:
            self.network1 = unrelish(self.file1)
            self.network1.value = options["start first"] # determines which network is which
            if self.original_file2 != "":
                self.network2 = unrelish(self.file2)
                self.network2.value = not self.network1.value

    def __del__(self):
        self.save()

    def save(self):
        'saves the neural networks into their pickle files'
        buffer("saving...")
        relish(self.file1, self.network1)
        if self.original_file2 != "":
            relish(self.file2, self.network2)

    def learn(self, network, past_game_pos, y):
        'makes the network learn through back propagation'
        learning_rate = LEARNING_RATE
        change = [{"array": layer.array, "biases": layer.biases} for layer in network.layers]
        for layers in past_game_pos[::-1]:
            learning_rate *= 0.6
            network.input_layer.input = layers[0]["input"].copy()
            for index, layer in enumerate(layers[1::]):
                index += 1
                network.layers[index].array = layer["array"].copy()
                network.layers[index].input = layer["input"].copy()
                network.layers[index].biases = layer["biases"].copy()
            network.back_prop(y, learning_rate)
            for index, layer in enumerate(network.layers[1::]):
                index += 1
                change[index]["array"] += (layer.array - layers[index]["array"])
                change[index]["biases"] += (layer.biases - layers[index]["biases"])
        for index, lay in enumerate(change[1::]):
            index += 1
            network.layers[index].array -= lay["array"] / len(past_game_pos)
            network.layers[index].biases -= lay["biases"] / len(past_game_pos)

    def check(self, game, network, past_game_pos, selected, prev_past_game_pos_len, exists):
        'dishes out "rewards" or "punishments" to the neural network according to how well it performed'
        y = np.ones(self.board_length**2)
        y[selected] = 0

        if self.show_training:
            game.render()
            game.stdscr.refresh()

        if exists:
            layers = []
            for layer in network.layers:
                layers.append(
                    {
                        "array": layer.array,
                        "input": layer.input,
                        "biases": layer.biases
                    }
                )
            past_game_pos.append(layers)
        else:
            new_output = network.output_layer.input.copy()
            new_output[0][selected] = 0
            network.back_prop(new_output, LEARNING_RATE)
        if game.won is not None:
            self.rounds -= 1
            if len(past_game_pos) > prev_past_game_pos_len:
                self.learn(network, past_game_pos, y)
        if game.won in (network.value, 3):
            y = np.zeros(self.board_length**2)
            y[selected] = 1
            self.learn(network, past_game_pos, y)
            game.reset()
        elif game.won == (not network.value):
            self.learn(network, past_game_pos, y)
            game.reset()

    def network_play(self, network, game, past_game_pos, prev_past_game_pos_len):
        'lets the network select which tile to place and makes it learn from its mistakes'
        output = network.forward_prop(np.array(game.board).reshape(self.board_length**2))[0]
        output = np.nan_to_num(output)
        selected = np.where(output == np.amax(output))[0]
        game.ai_last_place = selected
        if len(selected) > 1:
            rand_index = random.randrange(0, len(selected))
            selected = selected[rand_index]
        else:
            selected = selected[0]
        selected = selected.tolist()
        game.cursor_pos = [math.floor(selected / game.length), selected % game.length]
        self.check(game, network, past_game_pos, selected, prev_past_game_pos_len, game.place())

        time.sleep(self.slow_amt / 10)

    def run(self):
        'runs the network Trainer'
        if (self.network1.board_length != self.board_length) or (self.network2.board_length != self.board_length):
            return "Board length does not match the file provided" # error message
        self.training = True
        self.game.training = True
        past_game_pos1 = []
        past_game_pos2 = []
        prev_past_game_pos1_len = 0
        prev_past_game_pos2_len = 0
        start = time.time()
        while self.rounds > 0:
            self.network_play(self.network1, self.game, past_game_pos1, prev_past_game_pos1_len)
            self.network_play(self.network2, self.game, past_game_pos2, prev_past_game_pos2_len)
        end = time.time()
        buffer("elapsed time:", end - start)
        self.save()
        return True
