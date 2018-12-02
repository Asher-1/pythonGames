# encoding: utf-8
import cocos.layer, cocos.draw, math
import data

PHYSICS_DT = 1. / 100 # en segundos

from util import Vector, to_tuple, intersection

class Shaped(): # Mixin
    def load(self, shape_file, scale=1.0):
        f = data.load (shape_file)
        points = []
        for line in f.readlines():
            if line.startswith('Center:'):
                self.image_anchor = tuple(float(f) for f in line[7:].strip().split())
            elif line.startswith('Mass:'):
                mass = float(line[5:].strip())
            elif line.startswith('MofI:'):
                moment_i = float(line[5:].strip())
            elif line.startswith('Point:'):
                x, y = (float(f) for f in line[6:].strip().split())
                points.append(Vector(x, y)*scale)
            elif line.startswith('VDrag:'):
                v_drag = float(line[6:].strip())
            elif line.startswith('WDrag:'):
                w_drag = float(line[6:].strip())
        self.shape = SimulatedBody (self, points, 0.0, mass, 0.0, moment_i, v_drag, w_drag)

    def set_forces(self):
        pass

#############################################################################
#############################################################################
class SimulatedBody:
    def __init__ (self, body, points, velocity, mass, angular_v, moment_i, v_drag=0.000, w_drag=0.5):
        """
           body: a cocosnode-like with .position & .rotation & .set_forces()
           points: polygon vertices (relative to center of mass)
             Must be convex and sorted counter-clockwise
        """
        self.body = body
        self.pos = Vector(*body.position)
        self.velocity = velocity
        self.mass = mass
        self.points = points
        self.radius = max(abs(p) for p in points)
        self.angle = -math.radians(body.rotation)  # CCW (as usual math) radians
        self.angular_v = angular_v
        self.moment_i  = moment_i
        self.v_drag = v_drag
        self.w_drag = w_drag
        self.ident = len(self.points) # Debug

        self.tr_points = [None] * (len(self.points)+1)
        self.transform_points()
        
        self.forces = 0
        self.momenta = 0


#############################################################################
    def transform_points (self):
        r = math.e**(1j*self.angle)
        for i, p in enumerate(self.points):
            self.tr_points[i] = self.pos + r*p
        self.tr_points[-1] = self.tr_points[0] ;

#############################################################################
    def set_forces (self, force, momentum):
        self.forces = force
        self.momenta = momentum

#############################################################################
    def add_forces (self, force, momentum):
        self.forces += force
        self.momenta += momentum


#############################################################################
    def dynamic_step (self, h):
        self.forces  -= self.velocity *self.v_drag
        self.momenta -= self.angular_v*self.w_drag

        self.velocity += self.forces/self.mass*h #Euler Cromer
        self.pos += self.velocity*h

        self.angular_v += self.momenta/self.moment_i*h #Euler Cromer
        self.angle += self.angular_v*h
        
        self.transform_points()
        # Copy position/rotation to cocos
        self.body.position = to_tuple (self.pos)
        self.body.rotation = -math.degrees(self.angle) # Cocos uses clockwise degrees

    def colission (self, p, v):
        best, d = None, None
        for i in xrange(0, len(self.tr_points)-1):
            x1, x2 = self.tr_points[i:i+2]
            q = intersection (p, v, x1, x2)
            if q is not None:
                newdist = abs(p-q)
                if (best is None or newdist < d):
                    best, d = q, newdist
        return best, d

class Rope():
    def __init__ (self, line,
                        sbody1, point1, #point1 (de attachment) relativo a GC de sbody1.body sin rotar
                        sbody2, point2, #Ejercicio para el lector
                        rest_len0,
                        rest_lenf,     #Rest len final
                        k,             #Fuerza = k*(rest_len actual - distancia)
                                       #Fuerza es 0 si uno trata de comprimir la soga
                        strength,      #cuando se corta
                        max_length,
                        creation_time,
                        time_to_live):

        self.line = line
        self.sbody1 = sbody1
        self.point1 = point1
        self.sbody2 = sbody2
        self.point2 = point2
        self.rest_len0 = rest_len0
        self.rest_lenf = rest_lenf
        self.k = k
        self.strength = strength
        self.max_length = max_length
        self.creation_time = creation_time
        self.time_to_live = time_to_live
        self.tr_p1 = None
        self.tr_p2 = None
        self.broken = False
        self.transform_points()

    def transform_points(self):
        self.tr_p1 = self.sbody1.pos + self.point1*math.e**(1j*self.sbody1.angle)
        self.tr_p2 = self.sbody2.pos + self.point2*math.e**(1j*self.sbody2.angle)
        self.line.start = self.tr_p1
        self.line.end = self.tr_p2

    def add_forces(self, time):
    # Agrega fuerzas y momentos a los objetos unidos por la cuerda
    # Devuelve True si hay que borrar la soga porque es muy vieja, o muy larga,
    # o se corto por mucha fuerza. False en caso contrario
        life_time = min (time - self.creation_time, self.time_to_live)
        if self.broken:
            return True
        desired_length = (self.rest_len0*(self.time_to_live-life_time) +
                          self.rest_lenf*(life_time))/self.time_to_live
        actual_length = abs(self.tr_p2 - self.tr_p1)
        if actual_length > self.max_length:
            return True
        else:
            if actual_length < desired_length:
                return False
            else:
                force = self.k*(desired_length - actual_length) #Modulo
                if force > self.strength:
                    return True
                else:
                    force = force/(actual_length + 1e-16)*(self.tr_p2 - self.tr_p1) # vector
                    torque = -(force*(self.tr_p1-self.sbody1.pos).conjugate()).imag
                    self.sbody1.add_forces(-force,torque)
                    torque = (force*(self.tr_p2-self.sbody2.pos).conjugate()).imag
                    self.sbody2.add_forces(force,torque)
                    return False
#############################################################################
#############################################################################

#############################################################################
#############################################################################
class Physics():

    # Universe limits
    min_x = -1100
    max_x =  1100
    min_y = -1100
    max_y =  1100

    # Grid size
    nx = 16
    ny = 16

    # Useful to precalculate:
    xstep = float(max_x-min_x)/nx
    ystep = float(max_y-min_y)/ny

    def __init__ (self):
        self.space_grid = [[None]*self.nx for i in xrange(self.ny)]

        self.sb = [] # Moving bodies
        self.elapsed = 0
        self.sbw = [] # Walls (all with mass 0, non movable)
        self.ropes = []
        self.time = 0

    def add (self, sim_body):
        if sim_body.mass==0:
            self.sbw.append (sim_body)
        else:
            self.sb.append(sim_body)
    

#############################################################################
    def update_grid (self):
        for i in xrange(self.ny):
            for j in xrange(self.nx):
                self.space_grid[i][j] = ([], [])

        for layer, lst in ((0, self.sb), (1, self.sbw)):
            for b in lst:
                i = int(math.floor((b.pos.imag - self.min_y)/(self.max_y-self.min_y)*self.ny))
                if i == self.ny:
                   i -= 1 # Caso extremo

                j = int(math.floor((b.pos.real - self.min_x)/(self.max_x-self.min_x)*self.nx))
                if j == self.nx:
                   j -= 1 # Caso extremo

                self.space_grid[i][j][layer].append(b)

#############################################################################
    def find_and_handle_collisions (self):
        self.update_grid()

        for i in xrange(self.ny):
            for j in xrange(self.nx):
                cell_lists = self.space_grid[i][j]
                for l, some in enumerate(cell_lists[0]):
                    # Revisar dentro de la misma celda, contra otros obj
                    for k in xrange(l+1,len(cell_lists[0])): 
                        self.individual_collision_test(some, cell_lists[0][k])
                        self.individual_collision_test(cell_lists[0][k], some)

                for some in cell_lists[0]:
                    some = cell_lists[0][l]
                    # Revisar dentro de la misma celda, contra paredes
                    for other in cell_lists[1]:
                        self.individual_collision_test(some, other)
                        self.individual_collision_test(other, some)

                for some in cell_lists[0]:
                    if i < self.ny-1:
                        # Revisar con la celda de arriba
                        other_lists = self.space_grid[i+1][j]
                        for other in other_lists[0]: #Objetos
                            self.individual_collision_test(some, other)
                            self.individual_collision_test(other, some)
                        for other in other_lists[1]: #Paredes
                            self.individual_collision_test(some, other)
                            self.individual_collision_test(other, some)

                    if j < self.nx-1:
                        # Revisar con la celda de la derecha
                        other_lists = self.space_grid[i][j+1]
                        for other in other_lists[0]: #Objetos
                            self.individual_collision_test(some, other)
                            self.individual_collision_test(other, some)
                        for other in other_lists[1]: #Paredes
                            self.individual_collision_test(some, other)
                            self.individual_collision_test(other, some)

                    if i < self.ny-1 and j < self.nx-1:
                        # Revisar con la celda de arriba a la derecha
                        other_lists = self.space_grid[i+1][j+1]
                        for other in other_lists[0]: #Objetos
                            self.individual_collision_test(some, other)
                            self.individual_collision_test(other, some)
                        for other in other_lists[1]: #Paredes
                            self.individual_collision_test(some, other)
                            self.individual_collision_test(other, some)



#############################################################################
    def individual_collision_test (self, some, other):
        distance = abs(some.pos - other.pos)
        if distance < some.radius + other.radius:
            last_i = len(some.tr_points) - 2 # Not -1, last point is repeated
            collided = False
            i = 0
            while i <= last_i and not collided:
                p_some = some.tr_points[i]
                j = 0
                last_j = len(other.tr_points) - 2
                collided = True
                while j <= last_j and collided:
                    v = p_some - other.tr_points[j]
                    u = other.tr_points[j+1] - other.tr_points[j] 
                    if abs(v) > 1e-8: # paranoia
                        collided = collided and (v/u).imag > 0
                    j += 1

                if collided: #Hay penetracion pero solo importa si es "entrante"
                    j = 0
                    found = False
                    visitor = p_some - other.pos
                    while j <= last_j and not found: #Detectar la porcion de pizza donde esta el vertice interior
                        u = other.tr_points[j] - other.pos
                        v = other.tr_points[j+1] - other.pos
                        found = (visitor/u).imag >= 0 and \
                                (visitor/v).imag < 0
                        j += 1

                    assert found, "Collision point lost!!!"
                    j -= 1  # Deshacer incremento innecesario
                    # Ahora comienza test de vel relativa perpendicular del punto penetrante
                    # wrt la arista exterior de la porcion de pizza
                    x_side = other.tr_points[j+1]-other.tr_points[j]
                    w_rel = some.angular_v - other.angular_v
                    v_rel = some.velocity - other.velocity
                    p_rel = some.pos - other.pos
                    r     = some.tr_points[i] - other.pos
                    v_side = v_rel - p_rel*1j*some.angular_v + r*1j*w_rel
                    
                    assert abs(x_side) > 1e-8, "Side of length 0"
                    if (v_side/x_side).imag > 0:
                        assert some.tr_points[i]==p_some, "Paranoia"
                        if some.mass==0:
                            self.obj2wall(other, some, x_side, p_some)
                        elif other.mass==0:
                            self.obj2wall(some, other, x_side, p_some)
                        else:
                            self.obj2obj(some, other, x_side, p_some)
                i += 1

#############################################################################
    def obj2obj(self, obj1, obj2, contact_side, contact_point):
        #base del espacio vectorial que contiene solucion. Se contruye
        #basandose en conservacion de momentos lineales y rotacionales
        dp1 = contact_side*1j
        dp2 = -dp1
        dL1 = -(dp1*(obj1.pos-contact_point).conjugate()).imag
        dL2 = -(dp2*(obj2.pos-contact_point).conjugate()).imag
        #Transformar momentos a velocidades lineales y angulares
        #Ahora son VELOCIDADES a pesar de los nombres
        dp1 /= obj1.mass
        dp2 /= obj2.mass
        dL1 /= obj1.moment_i
        dL2 /= obj2.moment_i
        #Usar conservacion de energia como ultima condicion
        t = obj1.mass*(dp1.real*obj1.velocity.real+dp1.imag*obj1.velocity.imag) +\
            obj2.mass*(dp2.real*obj2.velocity.real+dp2.imag*obj2.velocity.imag) +\
            obj1.moment_i*dL1*obj1.angular_v +\
            obj2.moment_i*dL2*obj2.angular_v
        t /= -.5 * ( obj1.mass * (dp1*(dp1.conjugate())).real +
                     obj2.mass * (dp2*(dp2.conjugate())).real +
                     obj1.moment_i * dL1*dL1 +
                     obj2.moment_i * dL2*dL2 )
        #t*base es el delta de velocidades. Agregar a las velocidades iniciales
        obj1.velocity  += dp1*t
        obj2.velocity  += dp2*t
        obj1.angular_v += dL1*t
        obj2.angular_v += dL2*t
        #Y que la fuerza nos acompañe a todos

    def obj2wall(self, obj, wall_obj, contact_side, contact_point):
        #base del espacio vectorial que contiene solucion. Se contruye
        #basandose en conservacion de momentos lineales y rotacionales
        dp = contact_side*1j
        dL = -(dp*(obj.pos-contact_point).conjugate()).imag
        #Transformar momentos a velocidades lineales y angulares
        #Ahora son VELOCIDADES a pesar de los nombres
        dp /= obj.mass
        dL /= obj.moment_i
        #Usar conservacion de energia como ultima condicion
        t = obj.mass*(dp.real*obj.velocity.real+dp.imag*obj.velocity.imag) +\
            obj.moment_i*dL*obj.angular_v
        t /= -.5 * ( obj.mass * (dp*(dp.conjugate())).real +
                     obj.moment_i * dL*dL )
        #t*base es el delta de velocidades. Agregar a las velocidades iniciales
        obj.velocity  += dp*t
        obj.angular_v += dL*t
        #Y que la fuerza nos siga acompañando a todos

#############################################################################
    def dynamic_step (self,dt):
        new_ropes = []
        for rope in self.ropes:
            stale = rope.add_forces(self.time)
            if not stale:
                new_ropes.append(rope)
            else:
                rope.line.remove()
        self.ropes = new_ropes

        for sb_i in self.sb:
            sb_i.body.set_forces()
            self.edge_wall (sb_i)
            sb_i.dynamic_step(dt)
            sb_i.forces = sb_i.momenta = 0

        for rope in self.ropes: # Se mueven los objetos, se mueven las sogas
            rope.transform_points()

    def edge_wall (self,body):
        FORCE = 0.33
        x, y = body.pos.real, body.pos.imag
        dx = dy = 0.0
        if abs(x) > 1000.0:
            if x < -1000:
                dx = (-1000-x)**3 * FORCE
            else:
                dx = -(x-1000)**3 * FORCE
        if abs(y) > 1000.0:
            if y < -1000:
                dy = (-1000-y)**3 * FORCE
            else:
                dy = -(y-1000)**3 * FORCE
        body.add_forces (Vector (dx, dy), 20*(abs(dx)+abs(dy)))

#############################################################################
    def step (self, dt):
        self.elapsed += dt
        while self.elapsed >= PHYSICS_DT:
            self.elapsed -= PHYSICS_DT
            self.simulate()
            
#############################################################################
    def simulate (self):
        self.time += PHYSICS_DT
        # Acá se actualiza un paso de simulación
        self.find_and_handle_collisions()
        self.dynamic_step (PHYSICS_DT)

#############################################################################

    def find_in (self, l, p, v, distance):
        """Find closest body starting at p, going in direction v, at no more
        than given distance. Look for bodies in l"""
        object, endpoint, dist = None, None, distance
        for o in l:
            r = o.radius
            disp = o.pos-p
            dist_o = abs (disp)
            if dist_o == 0: # its me!
                ep, d = o.colission (p, v)
                if ep is not None and d < dist:
                    object, endpoint, dist = o, ep, d
            elif dist_o - r <= distance: # at the right distance
                v0 = v/disp
                r0 = r/dist_o
                edge1 = Vector (1-r0, r0)
                edge2 = Vector (1-r0, -r0)
                if v0.real > 0 and (edge1*v0).imag >= 0 and (edge2*v0).imag <= 0: 
                    ep, d = o.colission (p, v)
                    if ep is not None and d < dist:
                        object, endpoint, dist = o, ep, d
        return object, endpoint, dist

    def to_grid (self, x, min, max, n):
        i = int(math.floor((x - min)/(max-min)*n))
        return i
    
    def find (self, p, v, distance):
        """Find closest body starting at p, going in direction v, at no more
        than given distance"""
        px, py = p.real, p.imag
        i=self.to_grid (py, self.min_y, self.max_y, self.ny)
        j=self.to_grid (px, self.min_x, self.max_x, self.nx)

        if v.real >= 0:
            dx = +1
        else:
            dx = -1
        if v.imag >= 0:
            dy = +1
        else:
            dy = -1            

        mx = self.xstep*(dx+1)/2 - ((px-self.min_x) % self.xstep)
        my = self.ystep*(dy+1)/2 - ((py-self.min_y) % self.ystep)
        #print "Starting lookup", dx, dy, p, v
        #print mx, my
        while 0 <= j < self.nx and 0 <= i < self.ny and abs(p-Vector(px,py))<=distance+max(self.xstep,self.ystep):
            #print "checking grid: ",j , i             
            objs, walls = self.space_grid[i][j]
            obj1, p1, d1 = self.find_in (objs, p, v, distance)
            obj2, p2, d2 = self.find_in (walls, p, v, distance)
            if obj1 is None and obj2 is None:
                pass # Not found here, keep looking
            elif d1 < d2:
                return obj1, p1, d1
            else:
                return obj2, p2, d2

            if (abs(v.real) > 1e-8) and ((abs(v.imag) < 1e-8) or mx/v.real <= my/v.imag):
                j += dx
                px += mx
                py += v.imag*(mx/v.real)
                my -= v.imag*(mx/v.real)
                mx = self.xstep* dx
            else:
                i += dy
                py += my
                px += v.real*(my/v.imag)
                mx -= v.real*(my/v.imag)
                my = self.ystep* dy
                
        return None, None, distance
