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
"""

import logging
import sys
algo = sys.argv[1]
import cube
import neural_network
import numpy as np
import itertools
import threading
import os
import time
import random
from email.message import EmailMessage
#import cv2
from PIL import Image
   
class MainApplication():
    
    colors = {
    "red": 0,
    "blue": 1,
    "yellow": 2,
    "orange": 3,
    "white": 4,
    "green": 5,
        }
    
    solution = np.array([np.tile(i/6+0.01, (3, 3)) for i in range(6)])
    perfect = np.array([np.tile(0, (3, 3)) for i in range(6)])
    
    def __init__(self):
        #creates the robots app only if the platform is Pi
            
        #setting up the cube, working directory, NN
        self.c = cube.rubiks_cube()
        self.open_directory = ""
        #transforming path
        self.path = os.path.realpath(__file__)
        self.path = self.path.replace("main.py", "")
        self.path = self.path.replace("\\", "/")
        self.NN = neural_network.NeuralNetwork()
        self.im_recognition_NN = neural_network.NeuralNetwork()
        #creating threads
        self.t_thread = threading.Thread(target= self.train)
        self.c_thread = threading.Thread(target= self.create_cmd_only)
        self.s_thread = threading.Thread(target= self.save)
        self.l_thread = threading.Thread(target= self.load_cmd_only)
        self.s_a_thread = threading.Thread(target= self.save_as_cmd_only)
        self.solution_thread = threading.Thread(target= self.start_solution_t)
        
        self.tile_location = [(((577, 239, 587, 249), (669, 156, 679, 166), (741, 90, 751, 100)))]
        
        self.moves = []
        
        self.name = ""
        self.shown = False
        self.training = False
    
    def start_solution_t(self):
        if self.solution_thread.is_alive():
            return

        self.solution_thread = threading.Thread(target= self.give_robot_solution)
        self.solution_thread.start()

    #return a list for the robot to eat
    def give_robot_solution(self):
        self.c.mix()
        for i in range(20):
            #turns the cube and saves the outputs of the layers for backpropagation
            output = self.NN.querry(self.converter(self.c.sides))
            self.turn(output) #giving the turn function the last output
            
        print(np.sum(((self.c.sides-self.solution) != 0).astype(int)) / 48)
    
    def start_mix_thread(self):
        if self.mix_thread.is_alive():
            return
        
        self.mix_thread = threading.Thread(target= self.mix)
        self.mix_thread.start()
        
    
    def load_cube_from_picture(self):
        """cam1 = cv2.VideoCapture(0)
        ret, image = cam1.read()
        cv2.imwrite(f"{self.path}/resources/temp.png", image)
        cam1.release()"""
        
        loaded_specs = np.loadtxt(f"{self.path}saves/ImageNet420/specs") #have to first load the specs of the neural network
        loaded_weights = np.load(f"{self.path}saves/ImageNet420/weights.npy", allow_pickle= True)              
        self.im_recognition_NN.load(loaded_specs, loaded_weights) #loading the Neural Network
        
        im = Image.open(f"{self.path}resources/temp.png").convert("RGB")
        for side, lst in enumerate(self.tile_location):
            for i, element in enumerate(lst):
                print(element)
                tempim = im.crop(element)
                rgb = list(tempim.getdata())
                pix_lst = [item for sublist in rgb for item in sublist]
                
                print(pix_lst)
                
                output = self.im_recognition_NN.querry(pix_lst)
                
                val = list(output).index(max(output))
                
                print(val)
                
                self.c.load(val, (side, 0, i))
                
                self.c.update()

    #meh
    def converter(self, arr):
        for i in range(2):
            arr = itertools.chain(*arr)
        return list(arr)
    
    def create_cmd_only(self, specs):
        #transforming the input
        specs = specs.replace(" ", "")
        #splitting it to be read in
        specs = specs.split(",")
        
        #creating the NN
        self.create(specs[0], int(specs[1]), int(specs[2]), int(specs[3]), int(specs[4]), float(specs[5]))
    
    #creates a new neural network
    def create(self, name : str, n_input_nodes : int, n_hidden_layers : int, n_hidden_nodes : int, n_output_nodes : int, l_rate : float):            
        self.NN.create(n_input_nodes, n_hidden_layers, n_hidden_nodes, n_output_nodes, l_rate)
        self.save_as(name,None)
        print("finished creating the NN")
    
    def save_as_cmd_only(self):
        name = input("how do you wanna name your network? \n")
        self.save_as(name, None)
        
    #private saving function
    def save_as(self, name : str, win):
        if name == "":
            return
        os.mkdir(f"{self.path}saves/{name}") #creating the NN directory
        saved = self.save(name, self.NN.whlayers) #passing the weights as a parameter so there wont be any issues with training while saving
        if not win == None:
            win.destroy() #closing the popup
        if not saved: #remove directory when files couldnt be created
            os.rmdir(f"{self.path}saves/{name}")
        self.name = os.path.basename(name)
        
    #saving the weights in specified directory
    def save(self, name, weights): #passing the weights as a parameter so there wont be any issues with training while saving
        if name == "":
            return False
        try: #tries to create files if not returns false and saving process gets terminated
            np.save(f"{self.path}saves/{name}/weights", weights) #creating binary file of weights
            np.savetxt(f"{self.path}saves/{name}/specs", np.array([self.NN.n_inodes, self.NN.n_h_layers, self.NN.n_hnodes, self.NN.n_onodes, self.NN.l_rate, self.NN.steps])) #saving the specs of the Network for easy loading
        except AttributeError:
            return False

        return True
    
    def load_cmd_only(self, name):        
        path = f"{self.path}saves/{name}" #setting the path
        loaded_specs = np.loadtxt(f"{path}/specs") #have to first load the specs of the neural network
        self.load(path, loaded_specs)
    
    def load(self, name, specs):
        try:  
            #getting the directory of the Neural Network
            loaded_weights = np.load(f"{name}/weights.npy", allow_pickle= True)
            self.NN.load(specs, loaded_weights) #loading the Neural Network
            print("loading finished")
            self.open_directory = name #open directory has changed
            self.name = os.path.basename(name)
        except FileNotFoundError:
            print("File not found")
            return

    def train_once(self):
        turned_side = random.randint(0, 11)
        
        expected_output = np.zeros((12, 1))
        expected_output[turned_side] = 1

        self.turn(expected_output)

        if turned_side % 2 == 0:
            expected_output = np.zeros((12, 1))
            expected_output[turned_side + 1] = 1

        else:
            expected_output = np.zeros((12, 1))
            expected_output[turned_side - 1] = 1
        
        #turns the cube and saves the outputs of the layers for backpropagation
        output = self.NN.train(self.converter(self.c.sides))
        self.turn(output[-1]) #giving the turn function the last output
        
        output = np.insert(output, 0, self.converter(self.c.sides))
            
        error = expected_output - output[-1]
            
        #backpropagation
        for i in range(1, self.NN.n_h_layers + 3): #+2 because wih and who is in whlayers now
            #error has to be evenly spread amongst the hidden neurons
            #for that the weights get weighted(how much of the error every one should take)
            weighted_weights = self.NN.whlayers[-i].T / np.sum(self.NN.whlayers[-i], axis= 1)
            self.NN.whlayers[-i] += self.NN.l_rate * np.dot((error * output[-i] * (1-output[-i])), output[-1-i].T)
            error = np.dot(weighted_weights, error)

    def train_20(self):
        
        expected_turns = []
        
        #mixing the cube
        for _ in range(20):
            turned_side = random.randint(0, 11)
        
            expected_output = np.zeros((12, 1))
            expected_output[turned_side] = 1

            self.turn(expected_output)

            if turned_side % 2 == 0:
                expected_output = np.zeros((12, 1))
                expected_output[turned_side + 1] = 1

            else:
                expected_output = np.zeros((12, 1))
                expected_output[turned_side - 1] = 1
                
            expected_turns.append(expected_output)

        for b in range(20):
            #turns the cube and saves the outputs of the layers for backpropagation
            output = self.NN.train(self.converter(self.c.sides))
            self.turn(output[-1]) #giving the turn function the last output
            
            output = np.insert(output, 0, self.converter(self.c.sides))
                
            error = expected_turns[-b] - output[-1]
                
            #backpropagation
            for j in range(1, self.NN.n_h_layers + 3): #+2 because wih and who is in whlayers now
                #error has to be evenly spread amongst the hidden neurons
                #for that the weights get weighted(how much of the error every one should take)
                weighted_weights = self.NN.whlayers[-j].T / np.sum(self.NN.whlayers[-j], axis= 1)
                self.NN.whlayers[-j] += self.NN.l_rate * np.dot((error * output[-j] * (1-output[-j])), output[-1-j].T)
                error = np.dot(weighted_weights, error)
            
            #terminating further turning of the cube because the step was wrong!    
            if list(expected_turns[-b]).index(max(expected_turns[-b])) != list(output[-1]).index(max(output[-1])):
                return b + 1

    def judge_5(self):
        
        self.c.mix()
        
        for _ in range(6):
            
            output : list = []
            
            for _ in range(5):
                #turns the cube and saves the outputs of the layers for backpropagation
                return_val = self.NN.train(self.converter(self.c.sides))
                self.turn(return_val[-1]) #giving the turn function the last output
                return_val = np.insert(return_val, 0, self.converter(self.c.sides))
                output.append(return_val)
                
            output = np.sum(np.array(output).T, axis= 1) / 5

            error = output[-1]
                
            #backpropagation
            for j in range(1, self.NN.n_h_layers + 3): #+2 because wih and who is in whlayers now
                #error has to be evenly spread amongst the hidden neurons
                #for that the weights get weighted(how much of the error every one should take)
                weighted_weights = self.NN.whlayers[-j].T / np.sum(self.NN.whlayers[-j], axis= 1)
                self.NN.whlayers[-j] += self.NN.l_rate * np.dot((error * output[-j] * (1-output[-j])), output[-1-j].T)
                error = np.dot(weighted_weights, error)

    #true training function
    def train(self):
        global algo
        self.b = 0
        start = time.time()
        #strats the training loop
        while self.training:
            self.b += 1
            self.c.reset()
            
            if algo == "once":
                self.train_once()
            
            elif algo == "20":
                steps = self.train_20()
                
            elif algo == "judge_5":
                self.judge_5()

            #debugging
            if self.b % int(40000/(self.NN.n_h_layers + self.NN.n_hnodes)) == 0:
                
                self.save(self.name, self.NN.whlayers)

                logging.basicConfig(filename=f'{self.name}_neuralnetwork.log',
                                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                    datefmt='%H:%M:%S',
                                    level=logging.DEBUG, 
                                    filemode= "a")
                logging.debug(self.b)
                e = np.sum(((self.c.sides-self.solution) != 0).astype(int)) / 48
                logging.debug(f"Error is: {e}")
                if algo == "20":
                    logging.debug(f"Neural Network did: {steps} steps")
                

            if not self.training: #ending the loop
                print("finished training")
                print(f"trained for {self.b} loops")
                print(f"trained for: {(time.time()-start)/60} mins")
                self.c.reset()
                self.save(self.name, self.NN.whlayers)
                    
                break

    #used to turn the cube with the train method
    def turn(self, pred : list):
        #getting the biggest index of the prediction 
        move = list(pred).index(max(pred))
        
        print(move)
        #moving the cube accordingly
        if move == 0:
            self.c.rotate(0,1)
        elif move == 1:
            self.c.rotate(0,-1)
        elif move == 2:
            self.c.rotate(1,1)
        elif move == 3:
            self.c.rotate(1,-1)
        elif move == 4:
            self.c.rotate(2,1)
        elif move == 5:
            self.c.rotate(2,-1)
        elif move == 6:
            self.c.rotate(3,1)
        elif move == 7:
            self.c.rotate(3,-1)
        elif move == 8:
            self.c.rotate(4,1)
        elif move == 9:
            self.c.rotate(4,-1)
        elif move == 10:
            self.c.rotate(5,1)
        elif move == 11:
            self.c.rotate(5,-1)


"""
I'm GoOd At ProGrAMinG
"""
if __name__ == "__main__":
    main = MainApplication()       
    
    print("You are now in console mode")
    time_thread = threading.Thread(target= lambda: update_time)

    #updates the training time
    def update_time(start):
        while main.training:
            sys.stdout.write("\r")
            sys.stdout.write("{} seconds since training was started.".format(round(time.time() - start),0))
            sys.stdout.write(f" Loops done: {main.b}")
            sys.stdout.flush()
            time.sleep(0.25)

            if not main.training:
                break

    #main loop waits for user input
    def mainloop():
        global time_thread
        sys.stdout.flush()
        try:
            user_input = input("")
        except EOFError:
            pass
        if user_input == "help":
            print("commands are:\n - train \n - stop_training \n - load \n - create \n - save \n - save_as \n - solution \n - exit")
        elif user_input == "train":
            if not main.t_thread.is_alive():
                main.training = True
                main.t_thread = threading.Thread(target= main.train)
                main.t_thread.start()
                start = time.time()
                time_thread = threading.Thread(target= lambda: update_time(start))
                time_thread.start()
            else:
                print("already training")
                
        elif user_input == "stop_training":
            main.training = False
            print("started to stop training...")
            main.t_thread.join() #waits for the training thread to finish
            time_thread.join()
            print("finished training")

        elif user_input == "load":
            if not main.l_thread.is_alive():
                name = input("what Neural Network should be loaded? \n")
                main.l_thread = threading.Thread(target= lambda: main.load_cmd_only(name))
                main.l_thread.start()
            else:
                print("already loading")
        
        elif user_input == "create":
            if not main.c_thread.is_alive():
                specs = input("Define the name, n_input_nodes, n_hidden_layers, n_hidden_nodes, n_output_nodes, l_rate (in that order) to create the Neural Network: \n")
                main.c_thread = threading.Thread(target= lambda: main.create_cmd_only(specs))
                main.c_thread.start()
            else:
                print("already creating")
                
        elif user_input == "save":
            if not main.s_thread.is_alive():
                main.s_thread = threading.Thread(target= main.save, args=(main.name, main.NN.whlayers))
                main.s_thread.start()
                main.s_thread.join()
                print("finished saving")
            else:
                print("already saving")
                
        elif user_input == "save_as":
            if not main.s_a_thread.is_alive():
                main.s_a_thread = threading.Thread(target= main.save_as_cmd_only)
                main.s_a_thread.start()
            else:
                print("already saving")
                
        elif user_input == "solution":
            main.give_robot_solution()
        
        elif user_input == "exit":
            exit()
        else:
            print("didnt recognise command. type help to see what commands there are \n")
        
        sys.stdout.flush()
        mainloop()

    mainloop()
    
