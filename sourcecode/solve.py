"""
MIT License

Copyright (c) 2022 Paul Kleineberg and Mattes Rötschke

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

import time 
import RPi.GPIO as gpio

#clarify how to call channels and disable warnings
gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

class App():
    def __init__(self):        
        #place direction pins here
        self.direc = { 
                "0" : 0,
                "1" : 0,
                "2" : 0,
                "3" : 0,
                "4" : 0,
                "5" : 0,
            		} 
        
        #place step pins here
        self.step = {
            	"0" : 0,
                "1" : 0,
                "2" : 0,
                "3" : 0,
                "4" : 0,
                "5" : 0,
                	} 
        #tf is this?
        self.disable = {
                "0" : 0,
                "1" : 0,
                "2" : 0,
                "3" : 0,
                "4" : 0,
                "5" : 0,
                    }
        
        #setting up the pins
        gpio.setup(list(self.direc.values()) + list(self.step.values()) + list(self.disable.values()), gpio.OUT)
        
        #delay so the cube doesnt break
        self.delay = 0.0025
    
    #turning the cube right    
    def turn_right(self, side):
        gpio.output(self.disable[str(side)], False)
        gpio.output(self.direc[str(side)], False)
        
        for i in range(100):
            gpio.output(self.step[str(side)], True)
            gpio.output(self.step[str(side)], False)
            time.sleep(self.delay) #doesnt this have to be between the things above?
            
        gpio.output(self.disable[str(side)], True)
    
    #function for turning left    
    def turn_left(self, side):
        gpio.output(self.disable[str(side)], False)
        
        gpio.output(self.direc[str(side)], True)
        
        for i in range(100):
            gpio.output(self.step[str(side)], True)
            gpio.output(self.step[str(side)], False)
            time.sleep(self.delay)
            
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
                
if __name__ == "__main__":
    app = App()
    app.solve_cube()
            