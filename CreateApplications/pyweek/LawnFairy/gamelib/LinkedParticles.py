import math
import random
 
class LinkedParticles:
    def __init__(self, world_width, world_height):
        self.world_width = world_width
        self.world_height = world_height
        
        self.n_particles = 0
        self.n_constraints = 0
        
        self.pos = [] #tuple (x,y)
        self.old_pos = [] #tuple (x,y)
        self.accel = [] #tuple (x,y)
        self.mass = [] #float x
        self.constraints = [] #{constraint a, b, restlength}


    def MakeConstraint(self, pA, pB, rest_length):
        return {'pA': pA, 'pB': pB, 'Length': rest_length}
        
    def AddConstraint(self, pA, pB, rest_length):
        self.n_constraints += 1
        self.constraints.append(self.MakeConstraint(pA, pB, rest_length))
        
    def AddParticle(self, x, y):
        self.n_particles += 1        
        self.pos.append([x,y])
        self.old_pos.append([x,y])
        self.accel.append([0,0])
        self.mass.append(0.5)
        
    def AccumulateForces(self):        
        for p in range(0, self.n_particles):
            self.accel[p][0] = 0
            self.accel[p][1] = 0
        
    def Verlet(self):
        self.total_correction = 0
        for p in range(0,self.n_particles):
            if (self.mass[p] == 0):
                continue
                
            pos = self.pos[p][:]
            tmp_pos = pos[:]
            old_pos = self.old_pos[p][:]
            accel = self.accel[p][:]
            
            pos = map(lambda p, old_p, a: (p + (p - old_p)*0.95 + a), pos, old_pos, accel)            
            
            self.pos[p] = pos[:]
            self.old_pos[p] = tmp_pos[:]
            
            self.total_correction = self.total_correction + abs(pos[0] - tmp_pos[0]) + abs(pos[1] - tmp_pos[1])
        
    def SatisfyConstraints(self):        
        #World limits
        #for p in range(0, self.n_particles):        
        #    world_limits = [self.world_width, self.world_height]            
        #    self.pos[p] = map(lambda p, limit: min( max( p, 0 ), limit), self.pos[p], world_limits)
        #    
        #Links
        for c in range(0, self.n_constraints):        
            pA = self.constraints[c]["pA"]
            pB = self.constraints[c]["pB"]
            
            delta = map(lambda a, b: (b - a), self.pos[pA], self.pos[pB])
                       
            #delta_length = math.sqrt(delta[0]*delta[0] + delta[1]*delta[1])                       
            delta_length = (abs(delta[0]) + abs(delta[1])) 
        
            diff = (delta_length - self.constraints[c]["Length"]) / (1.0 + delta_length)
                                    
            self.pos[self.constraints[c]["pA"]] = map(lambda p, d: p + self.mass[pA]*d*diff, self.pos[pA], delta)
            self.pos[self.constraints[c]["pB"]] = map(lambda p, d: p - self.mass[pB]*d*diff, self.pos[pB], delta)
                       
					   
    def GetParticleAt(self, x, y):
        for p in range(0, self.n_particles):
            dist = math.sqrt((self.pos[p][0] - x)*(self.pos[p][0] - x) + (self.pos[p][1] - y)*(self.pos[p][1] - y))
            if (dist < 25):
                return p
        return -1
        
		
    def TimeStep(self):
        self.AccumulateForces()
        self.Verlet()
        self.SatisfyConstraints()
        
        
   
