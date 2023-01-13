To execute main.py you have to specify one parameter: the trainingsmode (onec/20/judge_5) <br/>
1st parameter is wether to turn on cmd only mode or GUI mode  
2nd parameter is which platform you are using with Pi just enabeling solve.py  
For example: "python main.py False Desktop" to start in GUI mode on Desktop   

main.py:  
contains the GUI and MainApplication to start training and getting the Network to solve the cube

neural_network.py:  
contains the class declaration of the Neural Network

cube.py:  
has the digital representation of the cube as a class

solve.py:  
code for the robot in class form; function gets called to move the robot
