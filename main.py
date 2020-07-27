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

    def getForestOrStreet(self):
        return self.forestOrStreet

    def getEmpty(self):
        return self.empty

    def getCarPosition(self):
        return self.carPosition

    def getTreeHeight(self):
        return self.treeHeight

    def setForestOrStreet(self, value):
        self.forestOrStreet = value

    def setEmpty(self, value):
        self.empty = value

    def setCarPosition(self, value):
        self.carPosition = value

    def setTreeHeight(self, value):
        self.treeHeight = value


# initializes fields matrix
fieldsSize = 20
fieldsMatrix = np.full((fieldsSize, fieldsSize), Field())


def initialization():
    # declare variables
    global alpha  # player rotation angle
    global beginAnimation  # animation when player jumps control
    global carHitPlayer  # 1 if any car hit the player
    global crashedInSomething  # 1 if the player crashed in something
    global fieldsInitialized  # variable to control the fields are once initialized
    global jump  # stores pressed key to control player direction
    global previousJump  # stores previous pressed key to control player rotation
    global runTime1
    global runTime2
    global t  # time variable for cars movement
    global xCurrent  # player position
    global xPrevious
    global yCurrent
    global yPrevious
    global zCurrent
    global zPrevious
    global zTime
    global zTrackBegin  # terrain starts in z=-12

    # initialize variables
    alpha = 0
    beginAnimation = 1
    carHitPlayer = 0
    crashedInSomething = 0
    fieldsInitialized = 0
    jump = 'w'
    previousJump = 'w'
    runTime1 = 0
    runTime2 = 0
    t = 0
    xCurrent = 0
    yCurrent = 0.5
    zCurrent = 0
    zTime = 0
    zTrackBegin = -12


# car start timer
def onTimer1(value: int):
    return None
# player jump timer


def onTimer2(value: int):
    return None


def onDisplay():
    # delete previous screen content
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    # configure camera
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(1, 7 - yCurrent, 3, 0, 0 - yCurrent, -2, 0, 1, 0)
    if (fieldsInitialized == 0):
        zTrackBegin = -12 - 3
        fieldsInitialization()
        fieldsInitialized = 1
        fieldsMatrix[10][-zTrackBegin].setEmpty(1)

    # configureIllumination()
    # renderTerrain()
    # defineTreesPosition()
    # renderStreets()
    # renderPlayer()

    glutSwapBuffers()


def onKeyboard(key: str, x: int, y: int):
    return null


def onReshape(width: int, height: int):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, float(width/height), 1, 100)


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
    initialization()
    # Initializes OpenGL
    glClearColor(1, 1, 1, 0)
    glEnable(GL_DEPTH_TEST)
    # Program infinite loop
    glutMainLoop()


if __name__ == '__main__':
    main()
