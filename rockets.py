import pygame as py 
from random import sample, getrandbits, randint, random
import math
#import pdb

# define constants  
WIDTH = 1100  
HEIGHT = 600  
FPS = 30
BORDER = 50
SHIPS = 1000
TARGET = (WIDTH//2, HEIGHT//8)
TARGET_SIZE = 100

# define colors  
BLACK = (0,0,0)  
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
BLUE = (0,0,255)
YELLOW = (255,255,0)
LIGHT_BLUE = (175,238,238) 
LIGHT_RED = (238,175,175)

# define forces
THRUSTERS = 1
GRAVITY = 0.80
STEER = 1.5
REBOUND = 0.3

# define time
ACTIONTIME = 7
ACTIONS = 40
EPOCH = ACTIONS * ACTIONTIME

# initialize pygame and create screen  
py.init()  
screen = py.display.set_mode((WIDTH , HEIGHT))
colors = ['red', 'green', 'yellow', 'blue']
col_img = {}
for color in colors:
    col_img[color] = (py.image.load('rocket_thrust_' + color +'.png'), py.image.load('rocket_idle_' + color +'.png'))
# rocket_thrust = py.image.load('rocket_thrust.png')
# rocket_idle = py.image.load('rocket_idle.png')
moon = py.image.load('moon.png')
moon = py.transform.scale(moon, (TARGET_SIZE*2, TARGET_SIZE*2))
stars = []
for _ in range(60):
    stars += [((randint(0,WIDTH), randint(0,HEIGHT)), randint(1,3))]
# for setting FPS  
clock = py.time.Clock()
def drawBackground():
    screen.fill(BLACK)
    for star in stars:
        py.draw.circle(screen, WHITE, star[0], star[1])
    moon_placement = [term[0]-term[1] for term in zip(TARGET,moon.get_rect().center)]
    screen.blit(moon, moon_placement)

class Ship():
    def __init__(self, color, starting_x = None,
        steer_actions = None,
        thrust_actions = None):
        self.starting_x = starting_x
        self.steer_actions = steer_actions
        self.thrust_actions = thrust_actions


        if self.starting_x is None:
            self.starting_x =  sample(range(WIDTH), 1)[0]
        if self.steer_actions is None:
            self.steer_actions = [item for sublist in [
                [randint(-3, 1)] * ACTIONTIME for _ in range(ACTIONS)]
                for item in sublist]
        if self.thrust_actions is None:
            self.thrust_actions = [item for sublist in [
                [getrandbits(1)] * ACTIONTIME for _ in range(ACTIONS)]
                for item in sublist]

        self.x = self.starting_x
        self.y = HEIGHT
        self.vx = 0
        self.vy = 0
        self.ax = 0
        self.ay = -0.01
        self.angle = 0
        self.fitness = 0
        self.color = color
        self.image_orig = col_img[self.color][0]
        self.image = self.image_orig.copy() 
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
    
    def rotate(self, rotation):
        self.angle = (self.angle + rotation) % 360
    
    def updatePos(self):
        self.x += self.vx
        self.y += self.vy
        # if self.x < 0 + BORDER:
        #     self.x = 0 + BORDER
        #     self.vx = - (REBOUND * self.vx)
        #     self.ax = 0
        # if self.x > WIDTH - BORDER:
        #     self.x = WIDTH - BORDER
        #     self.vx = - (REBOUND * self.vx)
        #     self.ax = 0
        # if self.y < 0 + BORDER:
        #     self.y = 0 + BORDER 
        #     self.vy = - (REBOUND * self.vy)
        #     self.ay = 0   
        # if self.y > HEIGHT - BORDER:
        #     self.y = HEIGHT - BORDER  
        #     self.vy = - (REBOUND * self.vy)
        #     self.ay = 0               

    def updateFitness(self):
        target_distance = math.sqrt((TARGET[0]-self.x)**2+(TARGET[1]-self.y)**2)
        target_distance = max(target_distance, TARGET_SIZE)
        #ground_distance = abs(HEIGHT-self.y)
        current_fitness = (1/(1+target_distance))#*(ground_distance/HEIGHT)
        self.fitness += current_fitness

    def updateVel(self):
        self.vx += self.ax
        self.vy += self.ay
    
    def targetAngle(self):
        target_angle = math.atan((TARGET[0]-self.x)/-abs(TARGET[1]-self.y))
        target_angle *= 180/math.pi
        target_angle = 180 - target_angle if (TARGET[1]-self.y) > 0 else target_angle
        return target_angle        
    
    def updateForces(self, time_delta):
        self.ax = 0
        self.ay = GRAVITY
        if self.steer_actions[time_delta] == -2:
            #Steer to the moon
            self.angle = self.targetAngle()
        if self.steer_actions[time_delta] == -3:
            #Steer up
            self.angle = 0
        if self.steer_actions[time_delta] == -4:
            #Hover
            #TODO
            return
        else:
            self.angle = (self.angle + STEER*self.steer_actions[time_delta]) % 360

        if self.thrust_actions[time_delta]:
            self.ax -= THRUSTERS*math.sin(self.angle*math.pi/180)
            self.ay -= THRUSTERS*math.cos(self.angle*math.pi/180)
            self.image_orig = col_img[self.color][0]
        else:
            self.image_orig = col_img[self.color][1]
    
    def drawSelf(self, fitest):
        old_center = (self.x, self.y)
        #py.draw.circle(self.image_orig, BLACK, center=(3,3), radius = 2)
        #TODO Fix the CHAMPION
        new_image = None
        new_image = py.transform.rotate(self.image_orig , self.angle)
        if self == fitest:
            fitest_scale = 3
            new_image = py.transform.scale(new_image , (new_image.get_width()*fitest_scale, new_image.get_height()*fitest_scale))
        self.rect = new_image.get_rect()
        self.rect.center = old_center
        new_image.convert_alpha()
        screen.blit(new_image, self.rect)

    def update(self, time_delta, fitest):
        self.updateFitness()
        self.updateForces(time_delta)
        self.updateVel()
        self.updatePos()
        self.drawSelf(fitest)
    
class Generation():
    def __init__(self, ships):
        #List of Ships
        self.ships = ships
        self.fitest = None
    
    def newGeneration(self):
        cum_sum = [0]
        fitest = None
        for ship in self.ships:
            #cum_sum is cumilative sum of fitnesses
            cum_sum += [cum_sum[-1] + ship.fitness]
            #find fitest ship
            if fitest is None:
                fitest = ship
            if fitest.fitness < ship.fitness:
                fitest = ship
        #Eggs keep their mother's starting position and initial action pattern.
        eggs = []
        for _ in range(len(self.ships)-1):
            #unif is uniformly distributed between the fittness total sum
            unif = random() * cum_sum[-1]
            for i, fit in enumerate(cum_sum):
                if unif < fit:
                    # i - 1 since first element in cum_sum = 0
                    mother_ship = self.ships[i-1]

                    new_starting_x = mother_ship.starting_x + randint(-2, 2)*3
                    egg = Ship(mother_ship.color,
                                starting_x=new_starting_x,
                                steer_actions=mother_ship.steer_actions,
                                thrust_actions=mother_ship.thrust_actions)
                    eggs += [egg]
                    break
        sperms = []
        for _ in range(len(self.ships)-1):
            #unif is uniformly distributed between the fittness total sum
            unif = random() * cum_sum[-1]
            for i, fit in enumerate(cum_sum):
                if unif < fit:
                    # i - 1 since first element in cum_sum = 0
                    father_ship = self.ships[i-1]
                    sperms += [(father_ship.steer_actions,father_ship.thrust_actions)]
                    break

        for i, (egg, sperm) in enumerate(zip(eggs, sperms)):
            #Half are asexually reproduced
            if i == len(sperms)//2 or egg == fitest:
                break

            #The action pattern will be inherited from both parents. 
            DNA_cut_locations = sorted(sample(range(len(egg.steer_actions)), randint(2,6)))
            DNA_cut_locations = [0] + DNA_cut_locations + [len(egg.steer_actions)]
            baby_steer_actions = []
            father_steer_actions = sperm[0]
            mother_steer_actions = egg.steer_actions
            baby_thrust_actions = []
            father_thrust_actions = sperm[1]
            mother_thrust_actions = egg.steer_actions
            for i in range(len(DNA_cut_locations)-1):
                start = DNA_cut_locations[i]
                end = DNA_cut_locations[i+1]
                if i % 2 == 0:
                    baby_steer_actions += mother_steer_actions[start:end]
                    baby_thrust_actions += mother_thrust_actions[start:end]
                else:
                    baby_steer_actions += father_steer_actions[start:end]
                    baby_thrust_actions += father_thrust_actions[start:end]                    
            
            #between 0% and 1% of the action pattern is mutated
            #for half of the sexually reproduced ships
            if randint(0,1):
                mutation_locations = sample(range(len(egg.steer_actions)), randint(0,len(egg.steer_actions)//100))
                for i in mutation_locations:
                    baby_steer_actions[i] = randint(-3, 1)
                mutation_locations = sample(range(len(egg.steer_actions)), randint(0,len(egg.steer_actions)//100))
                for i in mutation_locations:
                    baby_thrust_actions[i] = randint(0,1)
            egg.steer_actions = baby_steer_actions
            egg.thrust_actions = baby_thrust_actions

        self.fitest = Ship(fitest.color,
                            starting_x=fitest.starting_x,
                            steer_actions=fitest.steer_actions,
                            thrust_actions=fitest.thrust_actions)
        self.ships = eggs + [self.fitest]
    
    def drawColorPlot(self):
        color_counts = {}
        for color in colors:
            color_counts[color] = 0
        for ship in self.ships:
            color_counts[ship.color] += 1
        max_color_count = 0
        for color in color_counts:
            max_color_count = max(max_color_count, color_counts[color])
        start_y = 20
        staple_height = 30
        staple_width = 250
        increase_by_x = staple_height + 10
        current_x = start_y
        for color in colors:
            part = py.Surface((int(color_counts[color]/max_color_count*staple_width), staple_height))
            if color == "yellow":
                part.fill(YELLOW)
            if color == "red":
                part.fill(RED)  
            if color == "blue":
                part.fill(BLUE)  
            if color == "green":
                part.fill(GREEN)  
            screen.blit(part, (start_y,current_x))
            current_x += increase_by_x


        


    #TODO delete object that's not in the current iteration. 
ships = []
for i in range(SHIPS):
    ships += [Ship(colors[i%4])]

generation = Generation(ships)

# keep rotating the rectangle until running is set to False  
time = 0
running = True  
while running:  
    clock.tick(FPS)
    # clear the screen every time before drawing new objects 
    drawBackground() 
    generation.drawColorPlot()
    # check for the exit  
    for event in py.event.get():  
        if event.type == py.QUIT:  
            running = False  
    for ship in generation.ships:
        ship.update(time, generation.fitest)
    py.display.flip() 
    time += 1
    if time == EPOCH:
        time = 0
        generation.newGeneration()

py.quit()  