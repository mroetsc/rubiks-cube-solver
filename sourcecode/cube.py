"""
Copyright 2022, Paul Kleineberg, Julian Schaeffer and Mattes Roetschke, All rights reserved. This code is for illustrative use only. 
"""

from random import choice
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.pyplot as plt
import numpy as np

class rubiks_cube():
    color_dic = {
    "0": [1,0,0,1],
    "1": [0,0,1,1],
    "2": [1,1,0,1],
    "3": [1,0.5,0,1],
    "4": [0.9,0.9,0.9,1],
    "5": [0,1,0,1]
            }
    
    fig = plt.Figure(figsize=(3,3),dpi=100,facecolor= "black")
    ax = fig.add_subplot(1,1,1,projection="3d")
    ax.autoscale(enable= False, axis= "both")
    ax.set_xbound(-3, +3)
    ax.set_ybound(-3, +3)
    ax.set_zbound(-3, +3)
    ax.set_facecolor("black")
    ax.set_axis_off()
    ax.set_visible(True)
    plt.ion()
    
    save = []
    
    def __init__(self):
        #the sides of the cube get stored here
        #self.sides = np.array([([np.array([1,2,3]),np.array([4,i,6]),np.array([7,8,9])]) for i in range(6)])
        #self.sides = np.array([np.array([np.array([1,2,3]),np.array([4,5,6]),np.array([7,8,9])]),np.array([np.array([10,11,12]),np.array([13,14,15]),np.array([16,17,18])]),np.array([np.array([19,20,21]),np.array([22,23,24]),np.array([25,26,27])]),np.array([np.array([28,29,30]),np.array([31,32,33]),np.array([34,35,36])]),np.array([np.array([37,38,39]),np.array([40,41,42]),np.array([43,44,45])]),np.array([np.array([46,47,48]),np.array([49,50,51]),np.array([52,53,54])])])
        self.sides = np.array([np.tile(i/6+0.01, (3, 3)) for i in range(6)])
        self.side_dic = {}
        self.render()
        
    def rotate(self, side ,direction):
        #rotates ndarray(side) by the direction given 1=counterclockwise, -1=clockwise
        self.sides[side] = np.rot90(self.sides[side], k=direction)
        #bad solutions dont like it but easiest
        #hard coding the sides into the programm
        
        #red    
        if side == 0:
            right = [self.sides[4][i][0] for i in range(3)] #right
            top = [self.sides[1][2][i] for i in range(3)] #top 
            left = [self.sides[2][i][2] for i in range(3)] #left
            bottom = [self.sides[5][2][i] for i in range(3)] #bottom           
            
            if direction == 1:
                top.reverse() #reversing the lists so the cube turns the right way; 7th element of the top face has to be put into the 9th on the right face
                left.reverse() 
                self.sides[1][2] = np.array(right) #right goes into top
                for i in range(3):
                    self.sides[2][i][2] = top[i] #top into left
                    self.sides[4][i][0] = bottom[i] #bottom into right
                self.sides[5][2] = np.array(left) #left into bottom
            
            elif direction == -1:
                left.reverse()
                bottom.reverse()
                self.sides[5][2] = np.array(right)
                for i in range(3):
                    self.sides[2][i][2] = bottom[i]
                    self.sides[4][i][0] = top[i]
                self.sides[1][2] = np.array(left)

        #blue            
        elif side == 1:
            right = [self.sides[4][0][i] for i in range(3)] #right
            top = [self.sides[3][0][i] for i in range(3)] #top 
            left = [self.sides[2][0][i] for i in range(3)] #left
            bottom = [self.sides[0][0][i] for i in range(3)] #bottom           
            
            if direction == 1:
                self.sides[3][0] = np.array(right)
                self.sides[2][0] = np.array(top)
                self.sides[0][0] = np.array(left)
                self.sides[4][0] = np.array(bottom)
            
            elif direction == -1:
                self.sides[3][0] = np.array(left)
                self.sides[2][0] = np.array(bottom)
                self.sides[0][0] = np.array(right)
                self.sides[4][0] = np.array(top)
        
        #yellow            
        elif side == 2:
            right = [self.sides[0][i][0] for i in range(3)] #right
            top = [self.sides[1][i][0] for i in range(3)] #top 
            left = [self.sides[3][i][2] for i in range(3)] #left
            bottom = [self.sides[5][i][2] for i in range(3)] #bottom           
            
            if direction == 1:
                top.reverse()
                bottom.reverse()
                for i in range(3):
                    self.sides[1][i][0] = right[i]
                    self.sides[3][i][2] = top[i]
                    self.sides[5][i][2] = left[i]
                    self.sides[0][i][0] = bottom[i]
                
            elif direction == -1:
                right.reverse()
                left.reverse()
                for i in range(3):
                    self.sides[1][i][0] = left[i]
                    self.sides[3][i][2] = bottom[i]
                    self.sides[5][i][2] = right[i]
                    self.sides[0][i][0] = top[i]
        
        #orange
        elif side == 3:
            right = [self.sides[2][i][0] for i in range(3)] #right
            top = [self.sides[1][0][i] for i in range(3)] #top 
            left = [self.sides[4][i][2] for i in range(3)] #left
            bottom = [self.sides[5][0][i] for i in range(3)] #bottom         
            
            if direction == 1:
                right.reverse() 
                bottom.reverse() 
                self.sides[1][0] = np.array(right)
                for i in range(3):
                    self.sides[4][i][2] = top[i]
                    self.sides[2][i][0] = bottom[i]
                self.sides[5][0] = np.array(left)                    
            
            elif direction == -1:
                right.reverse()
                top.reverse()  
                self.sides[5][0] = np.array(right)
                for i in range(3):
                    self.sides[4][i][2] = bottom[i]
                    self.sides[2][i][0] = top[i]
                self.sides[1][0] = np.array(left)
        
        #white
        elif side == 4:
            right = [self.sides[3][i][0] for i in range(3)] #right
            top = [self.sides[1][i][2] for i in range(3)] #top 
            left = [self.sides[0][i][2] for i in range(3)] #left
            bottom = [self.sides[5][i][0] for i in range(3)] #bottom           
            
            if direction == 1:
                right.reverse() 
                left.reverse() 
                for i in range(3):
                    self.sides[1][i][2] = right[i]
                    self.sides[0][i][2] = top[i]
                    self.sides[5][i][0] = left[i]
                    self.sides[3][i][0] = bottom[i]
            
            elif direction == -1:
                bottom.reverse()
                top.reverse()
                for i in range(3):
                    self.sides[1][i][2] = left[i]
                    self.sides[0][i][2] = bottom[i]
                    self.sides[5][i][0] = right[i]
                    self.sides[3][i][0] = top[i]
        
        #green
        elif side == 5:
            right = [self.sides[4][2][i] for i in range(3)] #right
            top = [self.sides[0][2][i] for i in range(3)] #top 
            left = [self.sides[2][2][i] for i in range(3)] #left
            bottom = [self.sides[3][2][i] for i in range(3)] #bottom           
            
            if direction == 1:
                self.sides[0][2] = np.array(right)
                self.sides[2][2] = np.array(top)
                self.sides[3][2] = np.array(left)
                self.sides[4][2] = np.array(bottom)
            
            elif direction == -1:
                self.sides[3][2] = np.array(right)
                self.sides[2][2] = np.array(bottom)
                self.sides[0][2] = np.array(left)
                self.sides[4][2] = np.array(top)
        
        del right
        del top
        del left
        del bottom    
            
    def mix(self, *args):
        #the name speaks for it self right?
        for i in range(np.random.randint(70,100)):
            self.rotate(np.random.randint(0,6),choice([-1,1]))
            if args[0]:
                self.update()
                args[1].draw()
            
    def render(self):
        #front(red) with b 0-8
        for j in range(3):
            for i in range(3):
                A = (1.5,-1.5+i,0.5-j)
                B = (1.5,-0.5+i,0.5-j)
                C = (1.5,-0.5+i,1.5-j)
                D = (1.5,-1.5+i,1.5-j)
                poly = Poly3DCollection([[A,B,C,D]], color=self.color_dic[str(int(self.sides[0][j][i]*6-0.06))])
                poly.set_edgecolor("white")
                self.side_dic.update({f"poly_{0}_{j}_{i}":poly})
                self.ax.add_collection3d(poly)
        
        #top(blue) with b 9-17        
        for j in range(3):
            for i in range(3):
                A = (-0.5+j,-1.5+i,1.5)
                B = (-0.5+j,-0.5+i,1.5)
                C = (-1.5+j,-0.5+i,1.5)
                D = (-1.5+j,-1.5+i,1.5)
                poly = Poly3DCollection([[A,B,C,D]], color=self.color_dic[str(int(self.sides[1][j][i]*6-0.06))])
                poly.set_edgecolor("white")
                self.side_dic.update({f"poly_{1}_{j}_{i}":poly})
                self.ax.add_collection3d(poly)
        
        #left(yellow) with 18-26
        for j in range(3):
            for i in range(3):
                A = (-1.5+i,-1.5,0.5-j)
                B = (-0.5+i,-1.5,0.5-j)
                C = (-0.5+i,-1.5,1.5-j)
                D = (-1.5+i,-1.5,1.5-j)
                poly = Poly3DCollection([[A,B,C,D]], color=self.color_dic[str(int(self.sides[2][j][i]*6-0.06))])
                poly.set_edgecolor("white")
                self.side_dic.update({f"poly_{2}_{j}_{i}":poly})
                self.ax.add_collection3d(poly)
        
        #back(orange) with 27-35
        for j in range(3):
            for i in range(3):
                A = (-1.5,1.5-i,0.5-j)
                B = (-1.5,0.5-i,0.5-j)
                C = (-1.5,0.5-i,1.5-j)
                D = (-1.5,1.5-i,1.5-j)
                poly = Poly3DCollection([[A,B,C,D]], color=self.color_dic[str(int(self.sides[3][j][i]*6-0.06))])
                poly.set_edgecolor("white")
                self.side_dic.update({f"poly_{3}_{j}_{i}":poly})
                self.ax.add_collection3d(poly)
        
        #right(white) with 36-44        
        for j in range(3):
            for i in range(3):
                A = (1.5-i,1.5,0.5-j)
                B = (0.5-i,1.5,0.5-j)
                C = (0.5-i,1.5,1.5-j)
                D = (1.5-i,1.5,1.5-j)
                poly = Poly3DCollection([[A,B,C,D]], color=self.color_dic[str(int(self.sides[4][j][i]*6-0.06))])
                poly.set_edgecolor("white")
                self.side_dic.update({f"poly_{4}_{j}_{i}":poly})
                self.ax.add_collection3d(poly)
            
        #bottom(green) with 45-53    
        for j in range(3):
            for i in range(3):
                A = (-0.5+j,1.5-i,-1.5)
                B = (-0.5+j,0.5-i,-1.5)
                C = (-1.5+j,0.5-i,-1.5)
                D = (-1.5+j,1.5-i,-1.5)
                poly = Poly3DCollection([[A,B,C,D]], color=self.color_dic[str(int(self.sides[5][j][i]*6-0.06))])
                poly.set_edgecolor("white")
                self.side_dic.update({f"poly_{5}_{j}_{i}":poly})
                self.ax.add_collection3d(poly)
        

    #updating the cubes sides color        
    def update(self):
        for l in range(6):
            for j in range(3):
                for i in range(3):
                    self.side_dic[f"poly_{l}_{j}_{i}"].set_color(self.color_dic[str(int(self.sides[l][j][i]*6-0.06))])
                    self.side_dic[f"poly_{l}_{j}_{i}"].set_edgecolor("white")
    
    def reset(self):
        self.sides = np.array([np.tile(i/6+0.01, (3, 3)) for i in range(6)])
        self.update()
    
if __name__ == "__main__":
    pass
