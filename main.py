import sys

import numpy as np
import random as rd
import math as mt

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
    global yCurrent
    global fieldsInitialized
    global zTrackBegin
    global fieldsMatrix
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
    
def fieldsInitialization():
    rd.seed()
    maxsize = 10000
    
    for x in range(0, 20):
        for y in range(0, 20):
            if (y > 5):
                fieldsMatrix[x][y].setForestOrStreet('s')
            elif (y % 3 == 0):
                fieldsMatrix[x][y].setForestOrStreet('s')
            else: 
                fieldsMatrix[x][y].setForestOrStreet('u')
      
            if (rd.randint(0, maxsize) / maxsize > 0.9 and fieldsMatrix[x][y].getForestOrStreet() == 's'):
                fieldsMatrix[x][y].setEmpty(0)
                fieldsMatrix[x][y].setTreeHeight(mt.ceil(rd.randint(0, maxsize) / maxsize * 3))
            else:
                fieldsMatrix[x][y].setEmpty(1)
      
            fieldsMatrix[x][y].setCarPosition(rd.randint(0, maxsize) / maxsize * 8 + 10 * x)
        
        
def onKeyboard(key: str, x: int, y: int):
    global alpha
    global beginAnimation
    global carHitPlayer
    global crashedInSomething
    global fieldsInitialized
    global jump
    global previousJump
    global runTime1
    global runTime2
    global t
    global xCurrent
    global xPrevious
    global yCurrent
    global yPrevious
    global zCurrent
    global zPrevious
    global zTime
    global zTrackBegin
    previousJump = jump
    keycode = ord(key)
    key = key.decode('utf-8')
    if keycode == 27:
        # glutDestroyWindow()
        sys.exit()
    elif key == 'w':  # moves forward
        print('in w')
        if (fieldsMatrix[xCurrent + 10][-zTrackBegin - 1].getEmpty() == 1) and beginAnimation == 1 and runTime2 == 0:
            alpha = 0
            jump = 'w'
            runTime2 = 1
            zPrevious = zCurrent
            glutTimerFunc(1, onTimer2, 0)
            if runTime1 == 0:
                runTime1 = 1
                glutTimerFunc(10, onTimer1, 0)

        elif beginAnimation == 1 and runTime2 == 0:
            crashedInSomething = 1
            beginAnimation = 0
            glutPostRedisplay()

    elif key == 'a':  # moves to left
        if fieldsMatrix[xCurrent + 9][-zTrackBegin].getEmpty() == 1 and beginAnimation == 1 and runTime2 == 0:
            alpha = 0
            jump = 'a'
            runTime2 = 1
            xPrevious = xCurrent
            glutTimerFunc(1, onTimer2, 0)
            if runTime1 == 0:
                runTime1 = 1
                glutTimerFunc(10, onTimer1, 0)

    elif key == 'd':  # moves to right
        if fieldsMatrix[xCurrent + 11][-zTrackBegin].getEmpty() == 1 and beginAnimation == 1 and runTime2 == 0:
            alpha = 0
            jump = 'd'
            runTime2 = 1
            xPrevious = xCurrent
            glutTimerFunc(1, onTimer2, 0)
            if runTime1 == 0:
                runTime1 = 1
                glutTimerFunc(10, onTimer1, 0)

    elif key == 's':  # moves back
        if fieldsMatrix[xCurrent + 10][-zTrackBegin + 1].getEmpty() == 1 and beginAnimation == 1 and runTime2 == 0:
            alpha = 0
            jump = 's'
            runTime2 = 1
            zPrevious = zCurrent
            glutTimerFunc(1, onTimer2, 0)
            if runTime1 == 0:
                runTime1 = 1
                glutTimerFunc(10, onTimer1, 0)

    elif key == 'r':  # reinitialize variables
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
        glutPostRedisplay()


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
    # Initializes OpenGL
    glClearColor(1, 1, 1, 0)
    glEnable(GL_DEPTH_TEST)
    # Program infinite loop
    glutMainLoop()


if __name__ == '__main__':
    main()