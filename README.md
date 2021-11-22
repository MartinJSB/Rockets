# Rockets: A Demonstration of a Genetic Algorithm

Installation:
pip install pygame

Run the simulation: 
python rockets.py

Each rocket is born with a random set of actions (two sequences of how to steer and thrust). For each time period, the ship is given a fitness for how close to the moon it got. At the end of the iteration, their proportional fitnesses was their chances of reporducing. A mother gives the ships starting position and initial action sequence, and both parents give action sequences. For some ships, the starting position and the action sequence is slightly mutated. 

The largest ship shows the last generations most fit ship. 

There's four colors, which is inherited by the mother. The proportion of each generations colored ships are showed in the left upper corner. In a sense this is a very slow 4-sided dice as one color, given enough time, will be the only surviving one. 

![alt text](https://github.com/MartinJSB/Rockets/blob/master/Capture.PNG)
