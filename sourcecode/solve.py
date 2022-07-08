"""
Copyright 2022, Paul Kleineberg, Julian Schaeffer and Mattes Roetschke, All rights reserved. This code is for illustrative use only. 
"""

import time 
import RPi.GPIO as gpio

#clarify how to call channels and disable warnings
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

class App():
    def __init__(self):        
        #define direction pins for A4988
        self.direc = { 
                "0" : 0,
                "1" : 0,
                "2" : 0,
                "3" : 0,
                "4" : 0,
                "5" : 0,
            		} 
        
        #define step pins for A4988
        self.step = {
            	"0" : 0,
                "1" : 0,
                "2" : 0,
                "3" : 0,
                "4" : 0,
                "5" : 0,
                	} 
        #define disable pins for A4988
        self.disable = {
                "0" : 0,
                "1" : 0,
                "2" : 0,
                "3" : 0,
                "4" : 0,
                "5" : 0,
                    }
        
        #set the pins operation mode to output
        gpio.setup(list(self.direc.values()) + list(self.step.values()) + list(self.disable.values()), gpio.OUT)
        
        #define a delay in between steps
        self.delay = 0.0025
    
    #turning the cube right    
    def turn_right(self, side):
        #enable the driver board and define direction
        gpio.output(self.disable[str(side)], False)
        gpio.output(self.direc[str(side)], False)
        
        #do 100 steps, since 1 step equals 0.9°
        for i in range(100):
            gpio.output(self.step[str(side)], True)
            gpio.output(self.step[str(side)], False)
            time.sleep(self.delay)
        #disable the driver board again    
        gpio.output(self.disable[str(side)], True)
    
    #function for turning left    
    def turn_left(self, side):
        #enable the driver board and define direction
        gpio.output(self.disable[str(side)], False)        
        gpio.output(self.direc[str(side)], True)

        #do 100 steps, since 1 step equals 0.9°
        for i in range(100):
            gpio.output(self.step[str(side)], True)
            gpio.output(self.step[str(side)], False)
            time.sleep(self.delay)
        #disable the driver board again    
        gpio.output(self.disable[str(side)], True)
    
    #loops through the moves supplied by the NN and turns the cube accordingly    
    def solve_cube(self, moves):
        for i in moves:
            if i == 0:
                self.turn_left(0)
            elif i == 1:
                self.turn_right(0)
            elif i == 2:
                self.turn_left(1)
            elif i == 3:
                self.turn_right(1)
            elif i == 4:
                self.turn_left(2)
            elif i == 5:
                self.turn_right(2)
            elif i == 6:
                self.turn_left(3)
            elif i == 7:
                self.turn_right(3)
            elif i == 8:
                self.turn_left(4)
            elif i == 9:
                self.turn_right(4)
            elif i == 10:
                self.turn_left(5)
            elif i == 11:
                self.turn_right(5)

#execute main function                
if __name__ == "__main__":
    app = App()
    app.solve_cube()
            
