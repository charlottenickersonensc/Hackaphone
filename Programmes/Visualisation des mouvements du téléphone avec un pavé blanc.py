# ===== INSTALLATIONS =====
# pip install pyo wxpython PyOpenGL ahrs

# ===== IMPORTATIONS =====
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from pyo import *
import numpy as np
from ahrs.filters import Madgwick

# ===== FONCTIONS =====
def osc_donnees(adresse, *args):
    global osc_data
    if "/data/motion/gyroscope" in adresse:
        if adresse.endswith("x"): osc_data["gyro"][0] = float(args[0])
        elif adresse.endswith("y"): osc_data["gyro"][1] = float(args[0])
        elif adresse.endswith("z"): osc_data["gyro"][2] = float(args[0])
    elif "/data/motion/accelerometer" in adresse:
        if adresse.endswith("x"): osc_data["accel"][0] = float(args[0])
        elif adresse.endswith("y"): osc_data["accel"][1] = float(args[0])
        elif adresse.endswith("z"): osc_data["accel"][2] = float(args[0])

# Initialisation de Pygame et OpenGL
def init_display():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -5)

def draw_phone():
    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)
    vertices = [
        [-0.5, -1, -0.1], [0.5, -1, -0.1], [0.5, 1, -0.1], [-0.5, 1, -0.1],
        [-0.5, -1, 0.1], [0.5, -1, 0.1], [0.5, 1, 0.1], [-0.5, 1, 0.1]
    ]
    edges = [
        (0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (0,3,7,4), (1,2,6,5)
    ]
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def quaternion_to_euler(q):
    yaw = np.arctan2(2.0*(q[0]*q[3] + q[1]*q[2]), 1.0 - 2.0*(q[2]**2 + q[3]**2))
    pitch = np.arcsin(2.0*(q[0]*q[2] - q[3]*q[1]))
    roll = np.arctan2(2.0*(q[0]*q[1] + q[2]*q[3]), 1.0 - 2.0*(q[1]**2 + q[2]**2))
    return np.degrees(roll), np.degrees(pitch), np.degrees(yaw)

def main():
    global quaternion
    init_display()
    clock = pygame.time.Clock()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        
        # Fusion des capteurs avec Madgwick
        quaternion = madgwick.updateIMU(quaternion, osc_data["gyro"], osc_data["accel"])
        roll, pitch, yaw = quaternion_to_euler(quaternion)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(roll, 1, 0, 0)
        glRotatef(pitch, 0, 1, 0)
        glRotatef(yaw, 0, 0, 1)
        draw_phone()
        glPopMatrix()
        
        pygame.display.flip()
        clock.tick(60)

# ===== CODE =====
# Initialisation du serveur OSC
osc_data = {"gyro": np.zeros(3, dtype=np.float64), "accel": np.zeros(3, dtype=np.float64)}
madgwick = Madgwick()
quaternion = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float64)
serveur = Server().boot().start()
osc_receiver = OscDataReceive(port=8000, address="*", function=osc_donnees)

if __name__ == "__main__":
    main()