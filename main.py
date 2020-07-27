import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Field():
    def __init__(self):
        self.forestOrStreet = None
        self.empty = None
        self.carPosition = None
        self.treeHeight = None


# initializes fields matrix
fieldsSize = 20
fieldsMatrix = np.full((fieldsSize, fieldsSize), Field())


def fieldsInitialization():
    global fieldsInitialized
    fieldsInitialized = 0
    global zTrackBegin
    zTrackBegin = -12
    global alpha
    alpha = 0
    global beginAnimation
    beginAnimation = 1
    global runTime1
    runTime1 = 0
    global runTime2
    runTime2 = 0
    global runTime3
    runTime3 = 0
    global jump
    jump = 'w'
    global previousJump
    previousJump = 'w'
    global xCurr
    xCurr = 0
    global yCurr
    yCurr = 0.5
    global zCurr
    zCurr = 0
    global zTime
    zTime = 0
    global crashedInSomething
    crashedInSomething = 0
    global carHitPlayer
    carHitPlayer = 0
    global reverse
    reverse = 0
    global t
    t = 0


def onDisplay():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glutSwapBuffers()


def onKeyboard(key: str, x: int, y: int):
    return null


def onReshape():
    return null


def main():
    # initializes GLUT
    glutInit()
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    # creates the window
    glutInitWindowSize(1000, 1000)
    glutInitWindowPosition(100, 100)
    window = glutCreateWindow("Cross the street")
    # GLUT callback functions
    glutDisplayFunc(onDisplay)
    glutKeyboardFunc(onKeyboard)
    glutReshapeFunc(onReshape)
    # initializes game controls
    fieldsInitialization()
    # Initializes OpenGL
    glClearColor(1, 1, 1, 0)
    glEnable(GL_DEPTH_TEST)
    # Program infinite loop
    glutMainLoop()


if __name__ == '__main__':
    main()
