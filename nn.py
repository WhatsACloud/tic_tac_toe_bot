'neural network'
import warnings
import numpy as np

warnings.filterwarnings('ignore')

BOARD_LENGTH = 3

INPUT_LAYER_AMT = BOARD_LENGTH ** 2
HIDDEN_LAYER_AMT = INPUT_LAYER_AMT + BOARD_LENGTH
OUTPUT_LAYER_AMT = INPUT_LAYER_AMT
EPOCHS = 100
LEARNING_RATE = 1

def sigmoid(z):
    'returns sigmoid of z'
    return 1/(1+np.exp(-z))

def deriv_sigmoid(z):
    'returns the derivative of the sigmoid of z'
    return sigmoid(z)*(1-sigmoid(z))

def rand(shape):
    'returns a numpy array of values -1 to 1 with the given shape'
    return np.random.uniform(-1, 1, shape)

def gradient_descent(layer, prev_layer, y=None, cost=None, learning_rate=1): # i give up
    'performs gradient descent on the layer'
    if cost is None:
        cost = layer.input-y
    dy_yhat = cost
    dz_y = deriv_sigmoid(layer.input)
    dw_z = prev_layer.input.T
    dw_yhat = dy_yhat * dz_y * dw_z
    da_yhat = dy_yhat * dz_y * layer.array.sum(axis=1)[:, np.newaxis]
    da_yhat = da_yhat.sum(axis=1)[:, np.newaxis].T
    layer.array -= (dw_yhat*learning_rate)
    db_yhat = dy_yhat * dz_y
    layer.biases -= (db_yhat.T*learning_rate)
    return da_yhat

class NetworkLayer:
    'layer for NeuralNetwork class'
    def __init__(self, nparray=None, biases=None):
        self.array = nparray
        self.input = None
        self.biases = biases

    def __len__(self):
        return len(self.array)

class NeuralNetwork:
    'makes a neural network'
    def __init__(self, hidden_layers, output_layer, board_length):
        self.input_layer = NetworkLayer(np.array(0))
        self.hidden_layers = [NetworkLayer(hidden[0], hidden[1]) for hidden in hidden_layers]
        self.output_layer = NetworkLayer(output_layer[0], output_layer[1])
        self.layers = [self.input_layer]
        self.value = None
        self.board_length = board_length
        for hidden_layer in self.hidden_layers:
            self.layers.append(hidden_layer)
        self.layers.append(self.output_layer)

    def output(self):
        'outputs the network weights'
        for a in self.layers:
            print(a.array)

    def forward_prop(self, x) -> np.ndarray:
        'Forward propagates the network'
        mult1 = x[:, np.newaxis].T
        mult2 = self.hidden_layers[0].array
        self.input_layer.input = mult1
        for index, network_layer in enumerate(self.layers[1:]):
            dot = mult2 * mult1.T
            add_bias = dot.T.sum(axis=1) + network_layer.biases.T
            mult1 = sigmoid(add_bias)
            network_layer.input = mult1
            if index == len(self.layers)-2:
                break
            mult2 = self.layers[index+2].array
        return mult1

    def back_prop(self, y, learning_rate, da_yhat=None):
        'Back propagates the network'
        if da_yhat is None:
            da_yhat = gradient_descent(
                self.output_layer,
                self.hidden_layers[-1],
                y,
                learning_rate=learning_rate
            )
        for index, layer in reversed(list(enumerate(self.layers[1:-1]))):
            index += 1
            da_yhat = gradient_descent(
                layer,
                self.layers[index-1],
                None,
                da_yhat,
                learning_rate=learning_rate
            )

    def clear_input(self):
        'clears the input from all the layers'
        for layer in self.layers:
            layer.input = None
