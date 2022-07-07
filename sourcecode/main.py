"""
Copyright 2022, Paul Kleineberg, All rights reserved. This code is for illustrative use only. 
"""

import logging
import sys
#setting it up so the neural network can be used from only the cmd line
if sys.argv[1] == "True":
    cmd_only = True
if sys.argv[1] == "False":
    cmd_only = False

#only load the code for the roboter if we are on a pi
if sys.argv[2] == "Windows":
    Pi = False
if sys.argv[2] == "Pi":
    Pi = True
    import solve

import cube
import neural_network
import numpy as np
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import itertools
import threading
import os
import time
import psutil
import smtplib
from email.message import EmailMessage



class horizontal_Line(tk.Frame):
    
    def __init__(self, master, length : int, padding : tuple, color : str):
        self.master = master
        self.width = length
        self.height = 1
        self.padding = padding
        self.color = color
        
        tk.Frame.__init__(self, self.master, width= self.width, height= self.height, bg= self.color)
        
        self.place(x=self.padding[0], y=self.padding[1])        


class vertical_Line(tk.Frame):
    
    def __init__(self, master, length : int, padding : tuple, color : str):
        self.master = master
        self.width = 1
        self.height = length
        self.padding = padding
        self.color = color
        
        tk.Frame.__init__(self, self.master, width= self.width, height= self.height, bg= self.color)
        
        self.place(x=self.padding[0], y=self.padding[1])        

class container_Frame(tk.Frame):
    
    def __init__(self, master, width : int, height : int, padding : tuple, color : str):
        self.master = master
        self.width = width
        self.height = height
        self.padding = padding
        self.color = color
        
        tk.Frame.__init__(self, self.master, width= self.width, height= self.height, bg= self.color)
        
        self.place(x=self.padding[0], y=self.padding[1])       
        

class Label(tk.Label):
    
    def __init__(self, master, bg_color : str, fg_color : str, font : tuple, padding : tuple, *args, **kwargs):
        self.master = master
        self.bg = bg_color
        self.fg = fg_color
        self.font = font
        self.padding = padding
        
        if "textvariable" in kwargs.keys():
            tk.Label.__init__(self, self.master, bg= self.bg, fg= self.fg, font= self.font, textvariable= kwargs["textvariable"])
            self.textvar = kwargs["textvariable"]
        elif "text" in kwargs.keys():
            tk.Label.__init__(self, self.master, bg= self.bg, fg= self.fg, font= self.font, text= kwargs["text"])
            self.text = kwargs["text"]
        else:
            raise KeyError("text or textvariable have to be passed!")
        
        self.place(x=self.padding[0], y=self.padding[1])
        

class GUI(tk.Frame):
    
    def __init__(self, master, app : object):
        self.app = app
        
        self.master = master
        self.master.state("zoomed")
        self.master.attributes("-fullscreen", True)
        self.master.title("rubikscube solver")
        self.width = self.master.winfo_screenwidth()
        self.height = self.master.winfo_screenheight()

        self.primary_color = "black"
        self.secondary_color = "#E5FFF2"
        self.accent_color = "#A2B5AB"
        
        self.spacer_distance = int(self.height * 0.02)
        self.specs_width = int(self.width * 0.135)
        self.cube_width = int(self.width * 0.156)
        self.sidepanel_height = int(self.height * 0.6)
        self.bottompanel_height = self.height - (self.sidepanel_height + self.spacer_distance * 2 + 16)
        self.create_width = int(self.width * 0.5 - 10)
        
        self.saved = True
        self.sound_on = False
        self.open_save_pop_up = False        

        tk.Frame.__init__(self, master, width= self.width, height= self.height, bg= self.primary_color)

        self.create_GUI()
        
        self.place(x=0, y=0)
        
    
    def create_GUI(self):
        ##############
        #pretty stuff no real use
        self.spacer_line = horizontal_Line(self, self.width - 20, (10,self.spacer_distance), self.accent_color)
        self.spacer_vertical_line = vertical_Line(self, 7, (10,self.spacer_distance - 3), self.accent_color)
        self.spacer_vertical_line2 = vertical_Line(self, 7, (self.specs_width + 9, self.spacer_distance - 3), self.accent_color)
        
        self.spacer_vertical_line3 = vertical_Line(self, 7, (self.width - self.cube_width - 10, self.spacer_distance - 3), self.accent_color)
        self.spacer_vertical_line4 = vertical_Line(self, 7, (self.width - 10, self.spacer_distance - 3), self.accent_color)
        ##############

        #adding close button to the GUI
        self.close_f = container_Frame(self, 40, self.spacer_distance, (self.width - 50, 0), self.primary_color)
        
        self.close_b = tk.Button(self.close_f, command=self.close, text= "X", width= 3, bg= self.primary_color, fg= self.accent_color, relief= tk.FLAT, font= 12)
        self.close_b.place(x=0, y=-5)

        ##############
        #specs section
        self.specs_f = container_Frame(self, self.specs_width, self.sidepanel_height, (10, self.spacer_distance * 2 + 1), self.primary_color)

        #specs info 
        self.pretty_frames = [] #maybe put this into a constant python file
        self.info_labels = []
        self.info_text = {}
        self.texts = ("Name", "Inputnodes", "Hiddenlayers", "Hiddennodes", "Outputnodes", "Learning Rate", "Ram Usage", "CPU Usage")
        for i in range(8):
            #just some frames to make the whole look prettier
            vertical_line1 = vertical_Line(self.specs_f, 7, (0, 80*i), self.accent_color)
            vertical_line2 = vertical_Line(self.specs_f, 7, (self.specs_width-1, 80*i), self.accent_color)
            horizontal_line = horizontal_Line(self.specs_f, self.specs_width, (0, 80*i + 3), self.accent_color)
            self.pretty_frames.append((vertical_line1, vertical_line2, horizontal_line))
            
            #setting up string variables to change the text of the labels
            self.info_text.update({f"info{i}":tk.StringVar(value= "NONE")})
            label = Label(self.specs_f, self.primary_color, self.accent_color, ("MICRAC",12), (5, 80*i + 15), text= self.texts[i])
            label2 = Label(self.specs_f, self.primary_color, self.secondary_color, ("MICRAC",12), (5, 80*i + 40), textvariable= self.info_text[f"info{i}"])
            self.info_labels.append((label,label2))
            
        self.specs_vertical_line1 = vertical_Line(self.specs_f, 7, (0, self.sidepanel_height - 7), self.accent_color)
        self.specs_vertical_line2 = vertical_Line(self.specs_f, 7, (self.specs_width-1, self.sidepanel_height - 7), self.accent_color)
        self.specs_horizontal_line = horizontal_Line(self.specs_f, self.specs_width, (0, self.sidepanel_height - 4), self.accent_color)

        ##############
        #3D cube section
        self.cube_header_f = container_Frame(self, self.cube_width, self.sidepanel_height, (self.width - self.cube_width - 10, self.spacer_distance * 2 + 1), self.primary_color)

        #activate 3D
        self.cube_vertical_line1 = vertical_Line(self.cube_header_f, 7, (0, 0), self.accent_color)
        self.cube_vertical_line2 = vertical_Line(self.cube_header_f, 7, (self.cube_width - 1, 0), self.accent_color)
        self.cube_horizontal_line1 = horizontal_Line(self.cube_header_f, self.cube_width, (0, 3), self.accent_color)
        
        activate_3D_b = tk.Button(self.cube_header_f, command= self.activate_3D, text= "Activate 3D", bg= self.primary_color, foreground= self.secondary_color, width= 18, height= 2, font=("MICRAC",12))
        activate_3D_b.place(x=11, y=15)
        
        self.cube_vertical_line3 = vertical_Line(self.cube_header_f, 7, (0, 67), self.accent_color)
        self.cube_vertical_line4 = vertical_Line(self.cube_header_f, 7, (self.cube_width - 1, 67), self.accent_color)
        self.cube_horizontal_line2 = horizontal_Line(self.cube_header_f, self.cube_width, (0, 70), self.accent_color)
        
        #canvas section
        self.desc_l = Label(self.cube_header_f, self.primary_color, self.secondary_color, ("MICRAC", 12), (5, 71), text= "Virtual environment")

        self.desc_l2 = Label(self.cube_header_f, self.primary_color, self.accent_color, ("MICRAC",12), (5, 101) , text= "Cube")

        self.desc_l3_txt = tk.StringVar(value= "Deactivated")
        self.desc_l3 = Label(self.cube_header_f, self.primary_color, self.accent_color, ("MICRAC",12), (5, 131) ,textvariable= self.desc_l3_txt)

        self.canvas_f = container_Frame(self.cube_header_f, self.cube_width, 300, (0, 161), self.primary_color)

        #3D graph of cube
        self.canvas = FigureCanvasTkAgg(self.app.c.fig, self.canvas_f)
        self.canvas.get_tk_widget().place(x= 0, y= 0) #placing the figure

        self.cube_vertical_line5 = vertical_Line(self.cube_header_f, 7, (0, self.sidepanel_height - 80), self.accent_color)
        self.cube_vertical_line6 = vertical_Line(self.cube_header_f, 7, (self.cube_width - 1, self.sidepanel_height - 80), self.accent_color)
        self.cube_horizontal_line3 = horizontal_Line(self.cube_header_f, self.cube_width, (0, self.sidepanel_height - 77), self.accent_color)
        
        self.solve_r_b = tk.Button(self.cube_header_f, command= self.app.give_robot_solution, text= "Solve", font=("MICRAC", 12), bg= self.primary_color, fg= self.secondary_color, width= 18, height= 2)
        self.solve_r_b.place(x=11, y=self.sidepanel_height - 60)
        
        self.cube_vertical_line5 = vertical_Line(self.cube_header_f, 7, (0, self.sidepanel_height - 7), self.accent_color)
        self.cube_vertical_line6 = vertical_Line(self.cube_header_f, 7, (self.cube_width - 1, self.sidepanel_height - 7), self.accent_color)
        self.cube_horizontal_line3 = horizontal_Line(self.cube_header_f, self.cube_width, (0, self.sidepanel_height - 4), self.accent_color)
        ##############

        ##############
        #camera section
        self.camera_border_f = tk.Frame(self, width= self.width - ((self.specs_width + 10) + (self.cube_width + 10)) - 20, height= self.sidepanel_height, bg=self.accent_color)
        self.camera_border_f.place(x=self.specs_width + 20, y=self.spacer_distance*2 + 1)

        self.camera_f = container_Frame(self.camera_border_f, self.width - ((self.specs_width + 10) + (self.cube_width + 10)) - 22, self.sidepanel_height - 2, (1,1), self.primary_color)
        ##############

        ##############
        #create section
        self.create_f = container_Frame(self, self.create_width * 0.55, self.bottompanel_height, (10, self.sidepanel_height + 2*self.spacer_distance + 16), self.primary_color)

        self.create_vertical_line1 = vertical_Line(self.create_f, 7, (0, 0), self.accent_color)
        self.create_vertical_line2 = vertical_Line(self.create_f, 7, (int(self.create_width *0.55), 0), self.accent_color)
        self.create_horizontal_line1 = horizontal_Line(self.create_f, int(self.create_width *0.55), (0, 3), self.accent_color)

        self.create_labels = []
        self.create_entrys = []
        self.entry_text = {}
        
        #self.texts = ("Name", "Inputnodes", "Hiddenlayers", "Hiddennodes", "Outputnodes", "Learning Rate")
        for i in range(6):
            label = Label(self.create_f, self.primary_color, self.accent_color, ("MICRAC",12), (5, 40 * i + 20), text= self.texts[i])
            self.create_labels.append(label)
            
            self.entry_text.update({f"entry{i}":tk.StringVar()})
            entry = tk.Entry(self.create_f, textvariable= self.entry_text[f"entry{i}"], bg= self.primary_color, fg= self.accent_color, font= ("MICRAC",12), insertbackground= self.accent_color)
            entry.place(x=200, y=40*i + 20)
            self.create_entrys.append(entry)

        self.create_NN_b = tk.Button(self.create_f, command= self.create, text= "Create Neuralnetwork", font= ("MICRAC",12), bg= self.primary_color, fg= self.accent_color)
        self.create_NN_b.place(x=198, y=250)
        
        self.create_vertical_line3 = vertical_Line(self.create_f, 7, (0, self.bottompanel_height - 15), self.accent_color)
        self.create_vertical_line4 = vertical_Line(self.create_f, 7, (int(self.create_width * 0.55), self.bottompanel_height  - 15), self.accent_color)
        self.create_horizontal_line2 = horizontal_Line(self.create_f, int(self.create_width * 0.55), (0, self.bottompanel_height  - 12), self.accent_color)
        
        ###############
        #area for the train buttons
        self.train_f = container_Frame(self, int(self.width * 0.22), self.bottompanel_height, (self.width * 0.275 + 20, self.sidepanel_height + 2*self.spacer_distance + 16), self.primary_color)
        
        self.train_vertical_line1 = vertical_Line(self.train_f, 7, (0, 0), self.accent_color)
        self.train_vertical_line2 = vertical_Line(self.train_f, 7, (int(self.width * 0.22) - 1, 0), self.accent_color)
        self.train_horizontal_line1 = horizontal_Line(self.train_f, int(self.width * 0.22), (0, 3), self.accent_color)
        
        self.train_b = tk.Button(self.train_f, command= self.activate_training, text= "start/stop training", bg= self.primary_color, fg= self.accent_color, font=("MICRAC",12))
        self.train_b.place(x=10, y=15)

        self.loops_txt = tk.StringVar(value= "Loops: 0")
        self.loops_l = tk.Label(self.train_f, textvariable= self.loops_txt, bg= self.primary_color, fg= self.accent_color, font=("MICRAC",12))
        self.loops_l.place(x=10, y=55)
        
        self.sound_b = tk.Button(self.train_f, command= self.turn_sound_on, text= "turn on notifications(Bugged)", bg= self.primary_color, fg= self.accent_color, font=("MICRAC",12))
        self.sound_b.place(x=10, y=95)
        
        self.save_NN_b = tk.Button(self.train_f, command= self.save, text= "save", font= ("MICRAC",12), bg= self.primary_color, fg= self.accent_color)
        self.save_NN_b.place(x=10, y=135)
        
        self.save_as_NN_b = tk.Button(self.train_f, command= self.save_as, text= "save as...", font= ("MICRAC",12), bg= self.primary_color, fg= self.accent_color)
        self.save_as_NN_b.place(x=10, y=175)
        
        self.load_b = tk.Button(self.train_f, command= self.load, text= "load weights", font= ("MICRAC",12), bg= self.primary_color, fg= self.accent_color)
        self.load_b.place(x=10, y=215)
        
        self.train_vertical_line3 = vertical_Line(self.train_f, 7, (0, self.bottompanel_height - 15), self.accent_color)
        self.train_vertical_line4 = vertical_Line(self.train_f, 7, (int(self.width * 0.22) - 1, self.bottompanel_height - 15), self.accent_color)
        self.train_horizontal_line2 = horizontal_Line(self.train_f, int(self.width * 0.22), (0, self.bottompanel_height - 12), self.accent_color)
        
        ###############
        #Terminal action
        self.terminal_f = container_Frame(self, int(self.width * 0.49) - 10, self.bottompanel_height + 5, (self.width * 0.495 + 30, self.sidepanel_height + 2*self.spacer_distance + 1), self.primary_color)
        
        self.terminal = tk.Text(self.terminal_f, font= ("Terminal",11), bg= self.primary_color, fg= self.accent_color, wrap= tk.NONE, width= 185, height= 30)
        self.terminal_scrollbar = tk.Scrollbar(self.terminal_f, command= self.terminal.yview, bg= self.accent_color)
        self.terminal.config(yscrollcommand= self.terminal_scrollbar.set)
        
        self.terminal.place(x=0, y=15)
        self.terminal_scrollbar.place(x= self.width + 100, y=self.height + 100) #placing scrollbar out of bounds so user can only scroll 
    
    #close function    
    def close(self):
        if not self.saved:
            close = messagebox.askyesno("", "You havent saved yet! Do you really want close the Rubikscubesolver?") #asking the user a question returned value gets stored in close
        else:
            close = True #if the user has saved just close the app
        
        #closing the app     
        if close:
            self.master.destroy()
        else: #otherwise just returns from the function
            return
    
    #Function to activate the 3D cube
    def activate_3D(self):
        if not self.app.shown: #if we want to activate the window shown will be False
            self.desc_l3_txt.set("Activated")
            self.app.shown = True
        elif self.app.shown: #removing the buttons
            self.desc_l3_txt.set("Deactivated")
            self.app.shown = False
    
    def create(self):
        self.terminal.insert(tk.END, f"{self.app.path}>create\n")
        if self.app.c_thread.is_alive(): #doesnt start a new thread when its already running
            self.terminal.insert(tk.END, f"{self.app.path}>thread already started\n")
            return
        name = self.entry_text["entry0"].get()
        n_input_nodes = self.entry_text["entry1"].get()
        n_hidden_layers = self.entry_text["entry2"].get()
        n_hidden_nodes = self.entry_text["entry3"].get()
        n_output_nodes = self.entry_text["entry4"].get()
        l_rate = self.entry_text["entry5"].get()
        
        #only creates a new network when there is a value in each box
        if name == "" or n_input_nodes == "" or n_hidden_layers == "" or n_hidden_nodes == "" or n_output_nodes == "" or l_rate == "":
            self.terminal.insert(tk.END, f"{self.app.path}>all entrys have to be filled\n")
            return
        self.app.c_thread = threading.Thread(target= self.app.create, args= (name, int(n_input_nodes), int(n_hidden_layers), int(n_hidden_nodes), int(n_output_nodes), float(l_rate)))
        self.app.c_thread.start() #starting the creating thread
        #updating the info texts
        self.info_text["info0"].set(name)
        self.info_text["info1"].set(n_input_nodes)
        self.info_text["info2"].set(n_hidden_layers)
        self.info_text["info3"].set(n_hidden_nodes)
        self.info_text["info4"].set(n_output_nodes)
        self.info_text["info5"].set(l_rate)
        #clearing the entrys
        self.entry_text["entry0"].set("")
        self.entry_text["entry1"].set("")
        self.entry_text["entry2"].set("")
        self.entry_text["entry3"].set("")
        self.entry_text["entry4"].set("")
        self.entry_text["entry5"].set("")
        self.terminal.insert(tk.END, f"{self.app.path}>creating a new Neural Network...\n")
        
    #putting save into another thread so the window doesnt lag out when saving
    def save(self):
        self.terminal.insert(tk.END, f"{self.app.path}>save\n")
        if not self.app.s_thread.is_alive():
            try:
                self.app.s_thread = threading.Thread(target= self.app.save, args= (self.info_text["info0"].get(), self.app.NN.whlayers))
            except AttributeError:
                self.terminal.insert(tk.END, f"{self.app.path}>Neural Network hasnt been initialized yet\n")
                return
            self.terminal.insert(tk.END, f"{self.app.path}>saving...\n")
            self.app.s_thread.start()
            self.saved = True
        else:
            self.terminal.insert(tk.END, f"{self.app.path}>already saving\n")

    #puttin save_as into another thread so the window doesnt lag out when saving
    def _save_as(self, name : str, win): 
        self.terminal.insert(tk.END, f"{self.app.path}>save as\n")      
        if not self.app.s_a_thread.is_alive():
            self.terminal.insert(tk.END, f"{self.app.path}>saving...\n")
            self.app.s_a_thread = threading.Thread(target= self.app.save_as, args= (name, win))
            self.app.s_a_thread.start()
        else:
            self.terminal.insert(tk.END, f"{self.app.path}>already saving\n")

    #saving function for new neural networks    
    def save_as(self):
        #checks wether or not we are already saving a file
        if self.open_save_pop_up:
            return
        
        self.open_save_pop_up = True
        #creating a pop up window
        top_w = tk.Toplevel(self.master)
        top_w.title("save as...")
        x_coordinate = int(self.master.winfo_width()/2)
        y_coordinate = int(self.master.winfo_height()/2)    
        top_w.geometry("135x55+{}+{}".format(x_coordinate, y_coordinate))
        top_w.resizable(False, False)
        top_w.attributes("-topmost", True)
        top_w.protocol("WM_DELETE_WINDOW", self._pass)
        
        entry_f = tk.Frame(top_w, width= 100, height= 20)
        entry_f.place(x=5,y=5)
        
        save_f = tk.Frame(top_w, width= 100, height= 30)
        save_f.place(x=5, y=26)
        
        name = tk.StringVar()
        e = tk.Entry(entry_f, textvariable= name)
        e.pack()
        
        save_b = tk.Button(save_f, command= lambda: self._save_as(name.get(), top_w), text= "save", width= 5)
        save_b.place(x=40, y=1)

    #show how fcked the system is
    def change_system_utilization(self):
        self.info_text["info6"].set(str(psutil.virtual_memory()[2]))
        self.info_text["info7"].set(str(psutil.cpu_percent()))
        
        self.after(500, self.change_system_utilization)
    
    #turning on sound to get notified if error has been printed
    def turn_sound_on(self):
        if not self.sound_on:
            self.sound_on = True
        else:
            self.sound_on = False
            
    def load(self):
        self.terminal.insert(tk.END, f"{self.app.path}>load\n")
        if not self.app.l_thread.is_alive():
            directory = tk.filedialog.askdirectory(initialdir = f"{self.app.path}saves", title = "select directory\n") #asking the user for the path to the file
            self.terminal.insert(tk.END, f"{self.app.path}>loading weights...\n")
            loaded_specs = np.loadtxt(f"{directory}/specs") #gotta get these to update the info about the network
            self.app.l_thread = threading.Thread(target= self.app.load, args=(directory, loaded_specs))
            self.info_text["info0"].set(f"{os.path.basename(directory)}")
            self.info_text["info1"].set(f"{loaded_specs[0]}")
            self.info_text["info2"].set(f"{loaded_specs[1]}")
            self.info_text["info3"].set(f"{loaded_specs[2]}")
            self.info_text["info4"].set(f"{loaded_specs[3]}")
            self.info_text["info5"].set(f"{loaded_specs[4]}")  
            self.app.l_thread.start()
        else:
            self.terminal.insert(tk.END, f"{self.app.path}>already loading\n")
            
    #train the NN 
    training = False
    def activate_training(self):
        try:
            self.app.NN.whlayers
        except AttributeError:
            self.terminal.insert(tk.END, f"{self.app.path}>Neural Network not initialized yet. Either create or load one\n")
            return
        
        if not self.app.training: #when we want to start, training = False
            self.app.training = True 
            if not self.app.t_thread.is_alive():
                self.saved = False
                self.terminal.insert(tk.END, f"{self.app.path}>train\n")  
                self.app.t_thread = threading.Thread(target= self.app.train)
                self.app.t_thread.start()
                self.terminal.insert(tk.END, f"{self.app.path}>started training\n")
            else:
                self.terminal.insert(tk.END, f"{self.app.path}>already training...\n")
        elif self.app.training:
            self.terminal.insert(tk.END, f"{self.app.path}>stop_training\n")
            self.app.training = False            
        
    #pass
    def _pass():
        pass   

   
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
        if Pi:
            self.robot = solve.app()
            
        #setting up the cube, working directory, NN
        self.c = cube.rubiks_cube()
        self.open_directory = ""
        #transforming path
        self.path = os.path.realpath(__file__)
        self.path = self.path.replace("main.py", "")
        self.path = self.path.replace("\\", "/")
        self.NN = neural_network.NeuralNetwork()
        #creating threads
        self.t_thread = threading.Thread(target= self.train)
        self.c_thread = threading.Thread(target= self.create_cmd_only)
        self.s_thread = threading.Thread(target= self.save)
        self.l_thread = threading.Thread(target= self.load_cmd_only)
        self.s_a_thread = threading.Thread(target= self.save_as_cmd_only)
        
        self.name = ""
        self.shown = False
        self.training = False
    
    #return a list for the robot to eat
    def give_robot_solution(self):
        #somehow get the faces and make the cube that way
        o_lst = []
        #gotta get steps and then plonck them under this in the bracets
        for i in range(100):
            move = self.NN.querry(self.converter(self.c.sides))
            self.turn(move)
            o_lst.append(list(move).index(max(move)))
        if Pi:    
            self.robot.solve_cube(o_lst) #solving the cube
        else:
            print(o_lst)
        

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
            np.savetxt(f"{self.path}saves/{name}/specs", np.array([self.NN.n_inodes, self.NN.n_h_layers, self.NN.n_hnodes, self.NN.n_onodes, self.NN.l_rate])) #saving the specs of the Network for easy loading
        except AttributeError:
            if not cmd_only:
                GUI.terminal.insert(tk.END, f"{self.path}> saving failed")
            return False
        if not cmd_only:
            GUI.terminal.insert(tk.END, f"{self.path}> finished saving")
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
            if not cmd_only:
                GUI.terminal.insert(tk.END, f"{self.path}> loading finished")
            else:
                print("loading finished")
            self.open_directory = name #open directory has changed
            self.name = os.path.basename(name)
        except FileNotFoundError:
            if not cmd_only:
                GUI.terminal.insert(tk.END, f"{self.path}> File not found")
            else:
                print("File not found")
            return

    #true training function
    def train(self):
        n_steps = 100 #would have to relocate this
        self.b = 0
        start = time.time()
        #strats the training loop
        while self.training:
            self.b += 1
            self.c.reset()
            if not cmd_only:
                GUI.loops_txt.set("Loops: " + str(self.b)) #i dont like it but it is the best solution
                self.c.mix(self.shown, GUI.canvas)
            else:
                self.c.mix(self.shown) #mixing cube
            saves = []
            #sides_saves = []
                
            #turns the cube and saves the outputs of the layers for backpropagation
            for i in range(n_steps):
                output = self.NN.train(self.converter(self.c.sides))
                saves.append(output)
                self.turn(output[-1]) #giving the turn function the last output

                #if the cube is visualized we update the sides accordingly
                if self.shown:
                    self.c.update()
                if np.all(self.solution - self.c.sides ==  self.perfect): #checks wether or not we have a perfect solution -> improving steps needed to solve the cube
                    n_steps = i
                    print("Heuryka")
                    msg = EmailMessage()
                    msg.set_content(f"Vallah, BigBertha ist fucking smart! Unser bebe hat den Cube gelöst! (und Paul stinkt)\n Anzahl der Schritte:{n_steps}")
                    msg["Subject"] = "Pardy hard mothafackASS!"
                    msg["From"] = "Robin@BigBertha.de"
                    msg["To"] = ("paul.kleineberg@gmx.de", "mattes.roetschke@web.de", "s.galaxy.a5.j@gmail.com")
                    s = smtplib.SMTP("localhost")
                    s.send_message(msg)
                    s.quit()
                    break
                
                if i % 20 == 0:
                    #error factory
                    e = ((self.c.sides-self.solution) != 0).astype(int) #gets all the wrong tiles
                    E = np.zeros(shape=(len(self.c.sides),1)) #error for each individual side
                    for i in range(len(self.c.sides)):
                        E[i] = np.sum(e[i])
                    E = E/8
                        
                    error = np.zeros(shape=(len(self.c.sides)*2,1)) #creating an empty array for the error to be stored in
                    error[0] = E[0]
                    error[1] = E[0]
                    error[2] = E[1]
                    error[3] = E[1]
                    error[4] = E[2]
                    error[5] = E[2]
                    error[6] = E[3]
                    error[7] = E[3]
                    error[8] = E[4]
                    error[9] = E[4]
                    error[10] = E[5]
                    error[11] = E[5]
                    
                    #backpropagation
                    #because the saves is a list with n_steps length where each element itself is length of whlayer it has to somehow be concatenated to judge the overall movement of the cube
                    np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) #filtering the warning; occures because the output of the output layer isnt the same shape as the ouput of the hidden layers
                    sum_saves = np.sum(saves[i:i*20 + 20], axis= 0)
                    sum_saves = sum_saves/20 #average output of the neurons
                    
                    for i in range(1, self.NN.n_h_layers + 2): #+2 because wih and who is in whlayers now
                        #error has to be evenly spread amongst the hidden neurons
                        #for that the weights get weighted(how much of the error every one should take)
                        self.NN.whlayers[-i] +=  - (self.NN.l_rate / 20) * - np.dot((error * output[-i] * (1-output[-i])),output[-1-i].T)
                        weighted_weights = self.NN.whlayers[-i].T / np.sum(self.NN.whlayers[-i],axis = 1)
                        error = np.dot(weighted_weights,error)

            #error factory
            e = ((self.c.sides-self.solution) != 0).astype(int) #gets all the wrong tiles
            E = np.zeros(shape=(len(self.c.sides),1)) #error for each individual side
            for i in range(len(self.c.sides)):
                E[i] = np.sum(e[i])
            E = E/8
                
            error = np.zeros(shape=(len(self.c.sides)*2,1)) #creating an empty array for the error to be stored in
            error[0] = E[0]
            error[1] = E[0]
            error[2] = E[1]
            error[3] = E[1]
            error[4] = E[2]
            error[5] = E[2]
            error[6] = E[3]
            error[7] = E[3]
            error[8] = E[4]
            error[9] = E[4]
            error[10] = E[5]
            error[11] = E[5]
            
            #backpropagation
            #because the saves is a list with n_steps length where each element itself is length of whlayer it has to somehow be concatenated to judge the overall movement of the cube
            np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning) #filtering the warning; occures because the output of the output layer isnt the same shape as the ouput of the hidden layers
            sum_saves = np.sum(saves, axis= 0)
            sum_saves = sum_saves/n_steps #average output of the neurons
            
            for i in range(1, self.NN.n_h_layers + 2): #+2 because wih and who is in whlayers now
                #error has to be evenly spread amongst the hidden neurons
                #for that the weights get weighted(how much of the error every one should take)
                self.NN.whlayers[-i] +=  - self.NN.l_rate * - np.dot((error * output[-i] * (1-output[-i])),output[-1-i].T)
                weighted_weights = self.NN.whlayers[-i].T / np.sum(self.NN.whlayers[-i],axis = 1)
                error = np.dot(weighted_weights,error)

            #debugging
            if self.b % int(40000/(self.NN.n_h_layers + self.NN.n_hnodes)) == 0:
                
                self.save(self.name, self.NN.whlayers)

                if cmd_only: #if the programm is in cmd only mode the name of the dict will be name which the user inputed
                    logging.basicConfig(filename=f'{self.name}_neuralnetwork.log',
                                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                                        datefmt='%H:%M:%S',
                                        level=logging.DEBUG, 
                                        filemode= "a")
                    logging.debug(self.b)
                    logging.debug(e)
                    logging.debug(E)
                else:
                    GUI.terminal.insert(tk.END, f"{e}\n{self.path}>{E}\n{self.path}>")

            if not self.training: #ending the loop
                if cmd_only:
                    print("finished training")
                    print(f"trained for {self.b} loops")
                    print(f"trained for: {(time.time()-start)/60} mins")
                self.c.reset()
                self.save(self.name, self.NN.whlayers)
                if not cmd_only:
                    GUI.canvas.draw()
                    GUI.terminal.insert(tk.END, f"finished training\n{self.path}>trained for {self.b} loops\n{self.path}>\n{self.path}>trained for: {(time.time()-start)/60} mins\n")
                    
                break

    #used to turn the cube with the train method
    def turn(self, pred):
        #getting the biggest index of the prediction 
        move = list(pred).index(max(pred))
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
    
    if not cmd_only:
        root = tk.Tk()
        GUI = GUI(root, main)
        GUI.after(500, GUI.change_system_utilization)
        GUI.mainloop()
        
    
    if cmd_only:
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
    
