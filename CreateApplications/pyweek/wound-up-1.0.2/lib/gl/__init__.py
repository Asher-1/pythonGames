from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from glstate import *
import globject, light, camera, particle, texture, overlay

def init(width, height, **options):
    if "noparticles" in options and options["noparticles"]:
        GLState.setParticles(False)
    else:
        GLState.setParticles(True)
    if GLState.inited:
        return
    glViewport(0, 0, width, height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 1.0* width/height, 0.1, 100.0)
    GLState.setResolution(width, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glShadeModel(GL_SMOOTH)
    glClearColor(0, 0, 0, 0)
    glClearDepth(1)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, (0.3,0.3,0.3))
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_POLYGON_SMOOTH)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_POINT_SMOOTH)
    glDepthFunc(GL_LEQUAL)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
    glLineWidth(2)
    glutInit([])
    GLState.inited = True

def clear():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glColor4f(1,1,1,1)

ParticleManager = particle.ParticleManager
ParticleSystem = particle.ParticleSystem
Particle = particle.Particle
Object = globject.Object
ModelObject = globject.ModelObject
Light = light.Light
Camera = camera.Camera
Texture = texture.Texture
Overlay = overlay.Overlay
