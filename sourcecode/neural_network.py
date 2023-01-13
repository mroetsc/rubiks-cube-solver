"""
MIT License

Copyright (c) 2022 Paul Kleineberg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Code inspiried by Tariq Rashid from the book "Make Your Own Neural Network" (2016)
"""

import numpy as np
from scipy.special import expit

class NeuralNetwork():
    def __init__(self):
        #sigmoid function; expit is the logistic sigmoid for ndarrays from scipy.special
        self.activation_func = lambda x: expit(x)
    
    def create(self, n_input_nodes : int, n_hidden_layers : int, n_hidden_nodes : int, n_output_nodes : int, l_rate : float):        
        #store amount of the nodes so we dont forget later
        self.n_inodes = n_input_nodes
        self.n_hnodes = n_hidden_nodes
        self.n_onodes = n_output_nodes
        self.n_h_layers = n_hidden_layers
        
        #learning rate
        self.l_rate = l_rate
        
        self.steps = 100
        
        #container for the weights
        self.whlayers = []

        #wheights between input and hiddenlayer1
        self.whlayers.append(np.random.normal(0.0, n_hidden_nodes ** -0.5, (n_hidden_nodes, n_input_nodes)))

        #add weights between hiddenlayers
        for i in range(n_hidden_layers):
            self.whlayers.append(np.random.normal(0.0, n_hidden_nodes ** -0.5, (n_hidden_nodes, n_hidden_nodes)))
        
        #weights between last hiddenlayer and output layer
        self.whlayers.append(np.random.normal(0.0, n_output_nodes ** -0.5, (n_output_nodes, n_hidden_nodes)))

    def load(self, specs: list, weights : np.array):
        #store amount of the nodes so we dont forget later
        self.n_inodes = int(specs[0])
        self.n_h_layers = int(specs[1])
        self.n_hnodes = int(specs[2])
        self.n_onodes = int(specs[3])
        
        #learning rate
        self.l_rate = float(specs[4])
        
        self.steps = int(specs[5])
        
        #container for the weights
        self.whlayers = weights

    def train(self, input_list : list):
        #reshaping the list(shape: 1*x aka [1,2,3... ]) into a 2D array with a shape of x*1
        input = np.array(input_list, ndmin=2).T
        
        #calculate the weights of the first hiddenlayer into input
        hidden_input = np.dot(self.whlayers[0], input)
        #emerging signals from first hiddenlayer
        hidden_output = self.activation_func(hidden_input)
        #saving outputs to train
        s_hidden_output = [] 
        s_hidden_output.append(hidden_output)
                
        for i in range(1, self.n_h_layers + 1): #+1 because who and wih just shifted the weights 
            #calculating the other weights
            h_layer_input = np.dot(self.whlayers[i], hidden_output)
            #again calculating emerging signal
            hidden_output = self.activation_func(h_layer_input)
            #saving the outputs to train at
            s_hidden_output.append(hidden_output)

        #calculating the weights into hidden output
        output_input = np.dot(self.whlayers[-1], hidden_output)
        #final signals output with highest signals wins
        final_output = self.activation_func(output_input)
        s_hidden_output.append(final_output)
        return np.array(s_hidden_output, dtype= object)
            
    def querry(self, input_list: list):
        
        #reshaping the list(shape: 1*x aka [1,2,3... ]) into a 2D array with a shape of x*1
        input = np.array(input_list, ndmin=2).T
        
        #calculate the weights of the first hiddenlayer into input
        hidden_input = np.dot(self.whlayers[0], input)
        #emerging signals from first hiddenlayer
        hidden_output = self.activation_func(hidden_input)
        
        for i in range(1, self.n_h_layers + 1):
            #calculating the other weights
            h_layer_input = np.dot(self.whlayers[i], hidden_output)
            #again calculating emerging signal from each layer
            hidden_output = self.activation_func(h_layer_input)

        #calculating the weights into hidden output
        output_input = np.dot(self.whlayers[-1], hidden_output)
        #final signals output with highest signals wins
        final_output = self.activation_func(output_input)
        
        return final_output 

if __name__ == "__main__":
    pass
    
