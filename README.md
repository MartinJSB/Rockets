# Rockets demonstrates a genetic algorithm. 

Installation:
pip install pygame

Run the simulation: 
python rockets.py

Each rocket is born with a random set of actions (two sequences of how to steer and thrust). For each time period, the ship is given a fitness for how close to the moon it got. At the end of the iteration, their proportional fitnesses was their chances of reporducing. A mother gives the ships starting position and initial action sequence, and both parents give action sequences. For some ships, the starting position and the action sequence is slightly mutated. 
