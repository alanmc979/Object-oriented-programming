import cTurtle
import math
import random

class World:
    def __init__(self, NX, NY):
        self.NX = NX
        self.NY = NY
        self.wturtle = cTurtle.Turtle()
        self.drawInit()  # draw world grid
        self.grid = []  # list of lists grid positions
        for j in range(NY):
            self.grid.append([])
            for i in range(NX):
                self.grid[j].append(None)
            
        self.thingList = []  # list of specific animals and plants

    def drawInit(self):
        # setup world grid
        self.wturtle.speed(0)
        self.wturtle.ht()
        self.wturtle.setWorldCoordinates(-0.1*self.NX, -0.1*self.NY, 1.1*self.NX, 1.1*self.NY)
        for i in range(self.NX + 1):
            self.wturtle.up()
            self.wturtle.goto(i, 0)
            self.wturtle.down()
            self.wturtle.goto(i, self.NY)
        for j in range(self.NY + 1):
            self.wturtle.up()
            self.wturtle.goto(0, j)
            self.wturtle.down()
            self.wturtle.goto(self.NX, j)
            
    def freezeScreen(self):
        self.wturtle.exitOnClick()

    def getThing(self, i, j):
        return self.grid[i][j]

    def getThingNumber(self):
        return len(self.thingList)
        
    def addThing(self, i, j, thing):
        # add object thing to world at location i, j
        #print('added: %s' % thing)
        self.grid[i][j] = thing
        self.thingList.append(thing)
        thing.setWorld(self)
        thing.setLocation(i, j)
        thing.show()
            
    def removeThing(self, thing):
        # remove object thing from world
        #print('removed: %s' % thing)
        i, j = thing.getLocation()
        self.grid[i][j] = None
        self.thingList.remove(thing)
        thing.hide()

    def live(self):
        # pick object at random from self.thingList to live
        idx = random.randrange(len(self.thingList))
        return self.thingList[idx].live()  # return the dying Thing (or None) 

class LivingThing:
    def __init__(self, x, y):
        self.t = 0  # current time
        self.lastBreed = 0  # time of last breed
        self.lastEat = 0  # time of last eat
        self.turtle = cTurtle.Turtle('blank')
        self.turtle.up()
        self.turtle.goto(x+0.5, y+0.5)
        self.turtle.speed(0)
        self.world = None
        self.i = None
        self.j = None

    def show(self):
        self.turtle.st()

    def hide(self):
        self.turtle.ht()

    def setWorld(self, world):
        self.world = world

    def getLocation(self):
        return (self.i, self.j)
    
    def setLocation(self, i, j):
        self.i = i
        self.j = j
        self.turtle.goto(i+0.5, j+0.5)

    def getSpeciesName(self):
        return self.speciesName

    def getNeighbors(self):
        # get a list of current neighbors and ii, jj relative positions
        # for example, ii = 1, jj = -1 is the position of lower-right neighbor 
        neighbors = []
        iN = []
        jN = []
        for ii in range(-1, 2):
            for jj in range(-1, 2):
                if (ii != 0 or jj != 0) and \
                   (0 <= (self.i + ii) < self.world.NX) and \
                   (0 <= (self.j + jj) < self.world.NY):
                    neighbors.append(self.world.getThing(self.i + ii, self.j + jj))
                    iN.append(ii)
                    jN.append(jj)

        return (neighbors, iN, jN)
    
    def live(self):
        self.t += 1
        self._live()  # call sub-class _live method
            
    def die(self):
        self.world.removeThing(self)
   
class Salmon(LivingThing):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.turtle.addshape('salmon8.gif')
        self.turtle.shape('salmon8.gif')
        self.speciesName = 'salmon'
    
    def _live(self):
        if self.t - self.lastEat > 5:
            self.die()
            return self

        # get neighbor object list (and iN, jN relative positions)
        neighbors, iN, jN = self.getNeighbors()

        # count no. of salmon neighbors
        sR = 0
        for n in neighbors:
            if n != None and n.getSpeciesName() == 'salmon':
                sR += 1
        if sR >= 2:  # check for overcrowding
            self.die()
            return self
        
        if (neighbors.count(None) != 0) and (self.lastEat > self.lastBreed):  # breed if possible
            idx = random.randrange(len(neighbors))
            if neighbors[idx] == None:
                i = self.i + iN[idx]
                j = self.j + jN[idx]
                s = Salmon(i, j)  # create a new salmon
                self.world.addThing(i, j, s)
                self.lastBreed = self.t
        else:
            # move and eat
            pN = []  # list of plant neighbors
            for n in neighbors:  
                if n != None and n.getSpeciesName() == 'plant':
                    pN.append(n)
            if len(pN) > 0:
                idxP = random.randrange(len(pN))
                p = pN[idxP]
                idx = neighbors.index(p)
            else:
                idx = random.randrange(len(neighbors))

            if neighbors[idx] == None:  # move to an empty neighbor position
                self.world.removeThing(self)
                self.world.addThing(self.i + iN[idx], \
                                    self.j + jN[idx], self) 
            elif neighbors[idx].getSpeciesName() == 'plant':
                self.lastEat = self.t  # eat plant
                #print('Before plant death')
                neighbors[idx].die()  # plant dies
                #print('After plant death')
                self.world.removeThing(self)
                self.world.addThing(self.i + iN[idx], \
                                    self.j + jN[idx], self) 
                
                return neighbors[idx]
        
class Rabbit(LivingThing):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.turtle.addshape('rabbit10.gif')
        self.turtle.shape('rabbit10.gif')
        self.speciesName = 'rabbit'
    
    def _live(self):
        if self.t - self.lastEat > 16:
            self.die()
            return self

        # get neighbor object list (and iN, jN relative positions)
        neighbors, iN, jN = self.getNeighbors()

        # count no. of wolf neighbors and try to avoid them
        nW =[]
        for n in neighbors:
            if n != None and n.getSpeciesName() == 'wolf':
                nW.append(n)
        if len(nW)>0:
            idx = random.randrange(len(neighbors))
            
        # count no. of rabbit neighbors
        nR = 0
        for n in neighbors:
            if n != None and n.getSpeciesName() == 'rabbit':
                nR += 1
        if nR >= 4:  # check for overcrowding
            self.die()
            return self
        
        if (self.t - self.lastBreed > 8) and (self.lastEat > self.lastBreed) and \
           (neighbors.count(None) != 0):  # breed if possible
            idx = random.randrange(len(neighbors))
            if neighbors[idx] == None:
                i = self.i + iN[idx]
                j = self.j + jN[idx]
                r = Rabbit(i, j)  # create a new rabbit
                self.world.addThing(i, j, r)
                self.lastBreed = self.t

        else:
            # move and eat
            pN = []  # list of plant neighbors
            for n in neighbors:  
                if n != None and n.getSpeciesName() == 'plant':
                    pN.append(n)
            if len(pN) > 0:
                idxP = random.randrange(len(pN))
                p = pN[idxP]
                idx = neighbors.index(p)
            else:
                idx = random.randrange(len(neighbors))

            if neighbors[idx] == None:  # move to an empty neighbor position
                self.world.removeThing(self)
                self.world.addThing(self.i + iN[idx], \
                                    self.j + jN[idx], self) 
            elif neighbors[idx].getSpeciesName() == 'plant':
                self.lastEat = self.t  # eat plant
                #print('Before plant death')
                neighbors[idx].die()  # plant dies
                #print('After plant death')
                self.world.removeThing(self)
                self.world.addThing(self.i + iN[idx], \
                                    self.j + jN[idx], self) 
                
                return neighbors[idx]
            
   
class Wolf(LivingThing):
    def __init__(self, x, y):
        super().__init__(x, y)  # call LivingThing constructor
        self.turtle.addshape('wolf7.gif')
        self.turtle.shape('wolf7.gif')
        self.speciesName = 'wolf'

    
    def _live(self):
        if self.t - self.lastEat > 24:
            self.die()
            return self
        # get neighbor object list (and iN, jN relative positions)
        neighbors, iN, jN = self.getNeighbors()

        if (self.t - self.lastBreed > 8) and (self.lastEat > self.lastBreed) and \
           (neighbors.count(None) != 0):  # breed if possible
            idx = random.randrange(len(neighbors))
            if neighbors[idx] == None:
                i = self.i + iN[idx]
                j = self.j + jN[idx]
                w = Wolf(i,j)  # create a new wolf
                self.world.addThing(i, j, w)
                self.lastBreed = self.t
        else:
            # move and eat
            rN = []  # list of rabbit neighbors
            for n in neighbors:
                if n != None and n.getSpeciesName() == 'rabbit':
                    rN.append(n)
            # look for rabbits
            sN = []  # list of rabbit neighbors
            for n in neighbors:
                if n != None and n.getSpeciesName() == 'salmon':
                    sN.append(n)

                    
            if len(rN) > 0:  # if there are any rabbit neighbors, choose one
                idxR = random.randrange(len(rN))
                r = rN[idxR]
                idx = neighbors.index(r)
            if len(sN)>0:
                idxS= random.randrange(len(sN))
                s= sN[idxS]
                idx= neighbors.index(s)
            else:  # choose an empty neighboring spot to move to
                idx = random.randrange(len(neighbors))
                
                
            if neighbors[idx] == None:
                self.world.removeThing(self)  # wolf moves to empty neighbor spot
                self.world.addThing(self.i + iN[idx], \
                                    self.j + jN[idx], self) 
            elif neighbors[idx].getSpeciesName() == 'rabbit':
                self.lastEat = self.t  # eat rabbit
                neighbors[idx].die()  # rabbit dies
                self.world.removeThing(self)  # wolf moves to spot where rabbit was
                self.world.addThing(self.i + iN[idx], \
                                    self.j + jN[idx], self)
            elif neighbors[idx].getSpeciesName() == 'salmon':
                self.lastEat = self.t  # eat salmon
                neighbors[idx].die()  # salmon dies
                self.world.removeThing(self)  # wolf moves to spot where salmon was
                self.world.addThing(self.i + iN[idx], \
                                    self.j + jN[idx], self)
                
                return neighbors[idx]            
            

class Plant(LivingThing):
    def __init__(self, x, y):
        super().__init__(x, y)  # call LivingThing constructor
        self.turtle.addshape('plant16.gif')
        self.turtle.shape('plant16.gif')
        self.speciesName = 'plant'

    def _live(self):
        # get neighbor object list (and iN, jN relative positions)
        neighbors, iN, jN = self.getNeighbors()
        
        if self.t - self.lastBreed > 5:  # reproduce if possible
            idx = random.randrange(len(neighbors))  # pick a neighbor site 
            if neighbors[idx] == None:
                i = self.i + iN[idx]
                j = self.j + jN[idx]
                p = Plant(i,j)  # create a new plant
                self.world.addThing(i, j, p)
                self.lastBreed = self.t
                
        
def main(NX, NY, nWolf, nRabbit, nPlant, nSalmon):
    w = World(NX, NY)  # create world
    # add salmons
    k = 0
    while k < nSalmon:
        i = random.randrange(NX); j = random.randrange(NY)
        if w.getThing(i, j) == None:
            w.addThing(i, j, Salmon(i,j))
            k += 1
            
    # add rabbits
    k = 0
    while k < nRabbit:
        i = random.randrange(NX); j = random.randrange(NY)
        if w.getThing(i, j) == None:
            w.addThing(i, j, Rabbit(i,j))
            k += 1
            
    # add wolves
    k = 0
    while k < nWolf:
        i = random.randrange(NX); j = random.randrange(NY)
        if w.getThing(i, j) == None:
            w.addThing(i, j, Wolf(i,j))
            k += 1
            
    # add plants
    k = 0;
    while k < nPlant:
        i = random.randrange(NX); j = random.randrange(NY)
        if w.getThing(i, j) == None:
            p = Plant(i,j)
            w.addThing(i, j, p)
            #w.removeThing(p)
            k += 1
    
    # main loop where world lives until either world is full or empty
    while w.getThingNumber() not in [0, NX*NY]:
        obj = w.live()  # returns object that died during life cycle
                        # or None if no object died
        if obj != None: # delete from memory if obj died (i.e. != None)
            del obj
            
    w.freezeScreen()

main(24, 24, 6, 9, 9,9)
#Modifications:
#Problem 2 Rabbits can escape wolf
#Problem 4 Salmon



                
        
