from pyglet.window import key as key
import os.path

from cocos.layer import Layer, ColorLayer
from cocos.text import Label
from cocos.director import director

class TablaPuntuacion(object):

    def __init__ (self):
        try:
            f = file (os.path.join('data','levels.txt'), 'r')
            names = []
            for l in f:
                row = l.strip().split(',')
                names.append(row[1])
            self.names = names
        except:
            # Lola
            self.names = ['North Atlantic', 'Mediterranean', 'Caribbean', 'Red Sea', 'Hudson Bay', 'Black Sea', 'Arabian Sea', 'Arctic', 'Sea of Okhotsk', 'Bering', 'Sea of Japan', 'Indian', 'Andaman', 'South Pacific', 'South Atlantic']
        self.mejores = [('', 'Nobody')]* len(self.names)
        try:
            f = file ('kas.hiscore', 'r')
            newbest = []
            for l in f:
                valor, nombre = l.strip().split(',',1)
                newbest.append((valor, nombre))
            if len(newbest) == len(self.mejores):
                self.mejores = newbest
        except:
            self.guardar()

    def es_mejor (self, tiempo, levelName):
        idx = self.idx(levelName)
        if len(self.mejores[idx][0]) == 0:
            return True
        newmin, newseg, newmil = [int(x) for x in tiempo.split(':')]
        min, seg, mil = [int(x) for x in self.mejores[idx][0].split(':')]
        return newmin < min or (newmin == min and newseg < seg) or (newmin == min and newseg == seg and newmil < mil)

    def idx(self, levelName):
        return self.names.index(levelName)

    def agregar (self, nombre, levelName, tiempo):
        self.mejores[self.idx(levelName)] = (tiempo, nombre)
        self.guardar()

    def guardar(self):
        #try:
            f = file ('kas.hiscore', 'w')
            for p, n in self.mejores:
                f.write('%s,%s\n' % (p, n))
            f.close()
        #except:
        #    pass # Mala suerte

tabla = TablaPuntuacion()

class CapaTabla(Layer):

    is_event_handler = True

    def __init__ (self, tiempo=None, nombre=None, levelName=None, color0=(210,210,210,255)):
        super(CapaTabla, self).__init__()
        self.add (ColorLayer(0,0,0,200, width=640, height=480),z=-10)
        self.color0 = color0
        self.levelName = levelName
        if levelName is None:
            title = 'Fastest racers'
        else:
            title = 'You set a new mark!'
        self.add (Label(title,
                        position=(320, 420), anchor_x='center',
                        font_name='Yellowjacket', font_size=40,
                        color=color0))
        mejores = tabla.mejores[:]
        if tiempo is not None and tabla.es_mejor (tiempo, levelName):
            self.editable = True
            self.nombre = ''
            self.nuevo_tiempo = tiempo
            posicion = tabla.idx(levelName)
            mejores[posicion] = (tiempo, '<nombre>')
        else:
            self.editable = False
        formato = dict(font_name='Yellowjacket', font_size=18, color=color0)
        for i, (puntos, nombre) in enumerate (mejores):
            y = 20 + 26*i
            level = Label(tabla.names[i]+':', position=(220, y), anchor_x='right', **formato)
            self.add (level)
            nombre = Label(nombre, position=(290, y), anchor_x='left', **formato)
            self.add (nombre)
            if self.editable and i==posicion:
                self.entrada = nombre
                self.entrada.element.color = (255,0,0,255)
            if mejores[i][0]:
                self.add (Label(mejores[i][0], position=(420, y), anchor_x='left', **formato))

    def on_text (self, text):
        if self.editable:
            self.nombre += text
            self.entrada.element.text = self.nombre
            return True
        return False
    
    def on_key_press (self, symbol, modifiers):
        if symbol in (key.ESCAPE, key.SPACE, key.ENTER) and not self.editable:
            self.onFinished()
            self.onFinished = lambda:None
            return True
        if not self.editable: return False
        if symbol == key.BACKSPACE:
            self.nombre = self.nombre[:-1]
            self.entrada.element.text = self.nombre
            return True
        elif symbol == key.ENTER and self.editable and self.nombre != '':
            tabla.agregar (self.nombre, self.levelName, self.nuevo_tiempo)
            self.entrada.element.color = self.color0
            self.editable = False
            return True

        return False

