import math as mt
import random as rd
import sys

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


# timer used to move the cars
def onTimer1(value: int):
    global t
    global runTime1
    if value != 0:
        return
    t += 0.01
    glutPostRedisplay()
    if (runTime1 == 1):
        glutTimerFunc(10, onTimer1, 0)


# player jump timer
def onTimer2(value: int):
    global alpha
    global jump
    global xCurrent
    global xPrevious
    global yCurrent
    global zCurrent

    if value != 0:
        return
    alpha += np.pi / 15
    aux1 = np.sin(alpha)
    aux2 = np.sin(alpha - np.pi / 15)
    if (jump == 'w'):
        zCurrent -= 1.0 / 15
        yCurrent += aux1 - aux2
    elif(jump == 'a'):
        xCurrent -= 1.0 / 15
        yCurrent += aux1 - aux2
    elif (jump == 'd'):
        xCurrent += 1.0 / 15
        yCurrent += aux1 - aux2
    elif (jump == 's'):
        zCurrent += 1.0 / 15
        yCurrent += aux1 - aux2

    glutPostRedisplay()
    if alpha < np.pi:
        glutTimerFunc(1, onTimer2, 0)
    else:
        yCurrent = 0.5
        if (jump == 'a'):
            xCurrent = xPrevious - 1
        elif (jump == 'd'):
            xCurrent = xPrevious + 1
        elif (jump == 'w'):
            moveObjects()
            zCurrent = 0
        elif (jump == 's'):
            moveObjects()
            zCurrent = 0

    runTime2 = 0


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

    configureIllumination()
    renderForest()
    renderTerrain()
    renderStreets()
    renderPlayer()

    glutSwapBuffers()


def onKeyboard(key: str, x: int, y: int):
    global alpha
    global beginAnimation
    global carHitPlayer
    global crashedInSomething
    global fieldsInitialized
    global fieldsMatrix
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
        sys.exit()
    elif key == 'w':  # moves forward
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


# the game works like a running machine
def moveObjects():
    global fieldsMatrix
    rd.seed()
    maxSize = 10000
    # while the player moves forward, all the objects (cars and streets) are placed back in one field
    # and another field is created in the end of the field
    if jump == 'w':
        for j in range(18, 0, -1):
            for i in range(0, 20):
                fieldsMatrix[i][j+1].setEmpty(fieldsMatrix[i][j].getEmpty())
                fieldsMatrix[i][j+1].setForestOrStreet(fieldsMatrix[i][j].getForestOrStreet())
                fieldsMatrix[i][j+1].setCarPosition(fieldsMatrix[i][j].getCarPosition())
                fieldsMatrix[i][j + 1].setTreeHeight(fieldsMatrix[i][j].getTreeHeight())
        for j in range(0, 20):
            fieldsMatrix[j][0].setEmpty(1)
            if fieldsMatrix[j][1].getForestOrStreet() == 'street' and fieldsMatrix[j][2].getForestOrStreet() == 'street':
                fieldsMatrix[j][0].getForestOrStreet() == 'forest'
            else:
                fieldsMatrix[j][0].getForestOrStreet() == 'street'
        for i in range(0, 20):
            if rd.randint(0, maxSize) / maxSize > 0.7 and fieldsMatrix[i][0].getForestOrStreet() == 'forest':
                fieldsMatrix[i][0].setTreeHeight(mt.ceil(rd.randint(0, maxSize) / maxSize * 3))
                fieldsMatrix[i][0].setEmpty(0)
            else:
                fieldsMatrix[i][0].setEmpty(1)
            fieldsMatrix[i][0].setCarPosition(rd.randint(0, maxSize) / maxSize * 8 + 10 * i + 10 * t)
    # if the player moves backward, all the objects are moved forward in one field
    elif jump == 's':
        for j in range(0, 20):
            for i in range(0, 20):
                fieldsMatrix[i][j - 1].setEmpty(fieldsMatrix[i][j].getEmpty())
                fieldsMatrix[i][j - 1].setForestOrStreet(fieldsMatrix[i][j].getForestOrStreet())
                fieldsMatrix[i][j - 1].setCarPosition(fieldsMatrix[i][j].getCarPosition())
                fieldsMatrix[i][j - 1].setTreeHeight(fieldsMatrix[i][j].getTreeHeight())


# random tree size and car position settings
def fieldsInitialization():
    global fieldsMatrix
    rd.seed()
    maxSize = 10000

    for x in range(0, 20):
        for y in range(0, 20):
            if (y > 5):
                fieldsMatrix[x][y].setForestOrStreet('forest')
            elif (y % 3 == 0):
                fieldsMatrix[x][y].setForestOrStreet('forest')
            else:
                fieldsMatrix[x][y].setForestOrStreet('street')

            if (rd.randint(0, maxSize) / maxSize > 0.9 and fieldsMatrix[x][y].getForestOrStreet() == 'forest'):
                fieldsMatrix[x][y].setEmpty(0)
                fieldsMatrix[x][y].setTreeHeight(mt.ceil(rd.randint(0, maxSize) / maxSize * 3))
            else:
                fieldsMatrix[x][y].setEmpty(1)

            fieldsMatrix[x][y].setCarPosition(rd.randint(0, maxSize) / maxSize * 8 + 10 * x)


def configureIllumination():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    position = (GLfloat * 4)(7, 7, 7, 0)
    ambient = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
    diffuse = (GLfloat * 4)(0.7, 0.7, 0.7, 1)
    specular = (GLfloat * 4)(0.9, 0.9, 0.9, 1)
    glLightfv(GL_LIGHT0, GL_POSITION, position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular)


def renderForest():
    global fieldsMatrix
    global xCurrent
    global yCurrent
    global zCurrent
    global zTrackBegin

    glPushMatrix()
    glTranslatef(-xCurrent, -yCurrent, -zCurrent)
    for i in range(0, 20):
        for j in range(0, 20):
            if fieldsMatrix[i][j].getEmpty() == 0 and fieldsMatrix[i][j].getForestOrStreet() == 'forest':
                renderTree(i - 10, zTrackBegin + j)
    for j in range(0, 20):
        if fieldsMatrix[0+1][j].getForestOrStreet() == 'forest':
            renderTree(0 - 10 - 1, zTrackBegin + j)
    for j in range(0, 20):
        if fieldsMatrix[20-1][j].getForestOrStreet() == 'forest':
            renderTree(20-10, zTrackBegin + j)
    glPopMatrix()


def renderTree(x: int, z: int):
    global fieldsMatrix
    ambient = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
    specular = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
    brightness = (GLfloat * 1)(0)
    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, brightness)

    # tree top
    glPushMatrix()
    glTranslatef(x, 0, z)
    glScalef(0.8, 0.8, 0.8)

    if (x > -11 and x < 10):
        aux = fieldsMatrix[x + 10][z - zTrackBegin].getTreeHeight()
    else:
        aux = 3

    for i in range(0, aux):
        glColor3f(51.0 / 256, 102.0 / 256, 0)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(51.0 / 256, 102.0 / 256, 0, 0))
        glPushMatrix()
        glTranslatef(0, 0.5 + 0.2 + 0.6 + i * 0.7, 0)
        glScalef(1, 0.2, 1)
        glutSolidCube(1)
        glPopMatrix()
        glColor3f(76.0 / 256, 153.0 / 256, 0)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(76.0 / 256, 153.0 / 256, 0, 0))
        glPushMatrix()
        glTranslatef(0, 0.5 + 0.2 + 0.25 + i * 0.7, 0)
        glScalef(1, 0.5, 1)
        glutSolidCube(1)
        glPopMatrix()

    glColor3f(51.0 / 256, 102.0 / 256, 0)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(51.0 / 256, 102.0 / 256, 0.0))
    glPushMatrix()
    glTranslatef(0, 0.5 + 0.1, 0)
    glScalef(1, 0.2, 1)
    glutSolidCube(1)
    glPopMatrix()

    # tree body
    glColor3f(51.0 / 256, 25.0 / 256, 0)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(51.0 / 256, 25.0 / 256, 0.0))
    glPushMatrix()
    glScalef(0.5, 1, 0.5)
    glutSolidCube(1)
    glPopMatrix()
    glPopMatrix()


def renderTerrain():
    global fieldsMatrix
    global xCurrent
    global yCurrent
    global zCurrent
    glPushMatrix()
    glTranslatef(-xCurrent, -yCurrent, -zCurrent)
    for i in range(0, 20):
        for j in range(0, 20):
            if fieldsMatrix[i][j].getForestOrStreet() != 'street':
                renderGrass(i, j)

    for i in range(-10, 0):
        for j in range(0, 20):
            if fieldsMatrix[i + 15][j].getForestOrStreet() != 'street':
                renderGrass(i, j)

    for i in range(20, 30):
        for j in range(0, 20):
            if fieldsMatrix[i - 15][j].getForestOrStreet() != 'street':
                renderGrass(i, j)
    glPopMatrix()


def renderGrass(x, z):
    glPushMatrix()
    glTranslatef(0, 0, -3)
    glDisable(GL_LIGHTING)
    if (x % 2 == 1):
        glColor3f(178.0 / 256, 255.0 / 256, 102.0 / 256)
    else:
        glColor3f(166.0 / 256, 245.0 / 256, 92.0 / 256)
    glBegin(GL_QUADS)
    glVertex3f(x - 10 - 0.5, 0, z - 12 + 0.5)
    glVertex3f(x - 10 - 0.5, 0, z - 12 - 0.5)
    glVertex3f(x - 10 + 0.5, 0, z - 12 - 0.5)
    glVertex3f(x - 10 + 0.5, 0, z - 12 + 0.5)
    glEnd()
    glEnable(GL_LIGHTING)
    glPopMatrix()


def renderStreets():
    global fieldsMatrix
    global xCurrent
    global yCurrent
    global zCurrent
    glPushMatrix()
    glTranslatef(-xCurrent, -yCurrent, -zCurrent)
    for i in range(0, 20):
        for j in range(0, 20):
            if fieldsMatrix[i][j].getForestOrStreet() == 'street':
                renderAsphalt(i, j)
    for i in range(-10, 0):
        for j in range(0, 20):
            if fieldsMatrix[i+15][j].getForestOrStreet() == 'street':
                renderAsphalt(i, j)
    for i in range(20, 30):
        for j in range(0, 20):
            if fieldsMatrix[i-15][j].getForestOrStreet() == 'street':
                renderAsphalt(i, j)
    for i in range(0, 20):
        for j in range(0, 20):
            if fieldsMatrix[i][j].getForestOrStreet() == 'street':
                renderCar(fieldsMatrix[i][j].getCarPosition(), j)
    glPopMatrix()


def renderAsphalt(x, z):
    global fieldsMatrix
    glDisable(GL_LIGHTING)
    glPushMatrix()
    glTranslatef(0, 0, -3)
    if (
        (
            x >= 0 and
            x < 20 and
            fieldsMatrix[x][z + 1].getForestOrStreet() == 'street' and
            x % 2 == 1
        ) or (
            x < 0 and
            fieldsMatrix[x + 15][z + 1].getForestOrStreet() == 'street' and
            np.abs(x) % 2 == 1
        ) or (
            x >= 20 and
            fieldsMatrix[x - 15][z + 1].getForestOrStreet() == 'street' and
            x % 2 == 1
        )
    ):
        glColor3f(1, 1, 1)
        ambient = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
        specular = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
        brightness = (GLfloat * 1)(0)
        glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, brightness)

        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1, 1, 1, 0))

        glBegin(GL_QUADS)
        glVertex3f(x - 10 - 0.5, 0.0001, z - 12 + 0.55)
        glVertex3f(x - 10 - 0.5, 0.0001, z - 12 + 0.45)
        glVertex3f(x - 10 + 0.5, 0.0001, z - 12 + 0.45)
        glVertex3f(x - 10 + 0.5, 0.0001, z - 12 + 0.55)
        glEnd()

    glPopMatrix()

    glPushMatrix()
    glTranslatef(0, 0, -3)
    glColor3f(64.0 / 256, 64.0 / 256, 64.0 / 256)

    glBegin(GL_QUADS)
    glVertex3f(x - 10 - 0.5, 0, z - 12 + 0.5)
    glVertex3f(x - 10 - 0.5, 0, z - 12 - 0.5)
    glVertex3f(x - 10 + 0.5, 0, z - 12 - 0.5)
    glVertex3f(x - 10 + 0.5, 0, z - 12 + 0.5)
    glEnd()
    glPopMatrix()

    glEnable(GL_LIGHTING)


def renderCar(x, z):
    global carHitPlayer
    global fieldsMatrix
    global t
    global zTrackBegin

    glPushMatrix()
    glColor3f(1, 1, 0)
    glTranslatef(-10 + t * 10 - x, 0.3, z + zTrackBegin)

    # Pneus e rodas
    # Frente direita
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.1, 0.1, 0.1, 0))
    glPushMatrix()
    glTranslatef(0.45, -0.1, 0.4)
    glScalef(1, 1, 0.5)
    glutSolidCube(0.35)
    glPopMatrix()

    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.2, 0.2, 0.2, 0))
    glPushMatrix()
    glTranslatef(0.45, -0.1, 0.45)
    glScalef(0.5, 0.5, 0.25)
    glutSolidCube(0.35)
    glPopMatrix()
    # Traseira direita
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.1, 0.1, 0.1, 0))
    glPushMatrix()
    glTranslatef(-0.45, -0.1, 0.4)
    glScalef(1, 1, 0.5)
    glutSolidCube(0.35)
    glPopMatrix()

    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.2, 0.2, 0.2, 0))
    glPushMatrix()
    glTranslatef(-0.45, -0.1, 0.45)
    glScalef(0.5, 0.5, 0.25)
    glutSolidCube(0.35)
    glPopMatrix()
    # Traseira esquerda
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.1, 0.1, 0.1, 0))
    glPushMatrix()
    glTranslatef(-0.45, -0.1, -0.4)
    glScalef(1, 1, 0.5)
    glutSolidCube(0.35)
    glPopMatrix()

    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.2, 0.2, 0.2, 0))
    glPushMatrix()
    glTranslatef(-0.45, -0.1, -0.45)
    glScalef(0.5, 0.5, 0.25)
    glutSolidCube(0.35)
    glPopMatrix()
    # Frente esquerda
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.1, 0.1, 0.1, 0))
    glPushMatrix()
    glTranslatef(0.45, -0.1, -0.4)
    glScalef(1, 1, 0.5)
    glutSolidCube(0.35)
    glPopMatrix()

    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.2, 0.2, 0.2, 0))
    glPushMatrix()
    glTranslatef(0.45, -0.1, -0.45)
    glScalef(0.5, 0.5, 0.25)
    glutSolidCube(0.35)
    glPopMatrix()
    # Parte superior
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.9, 0.9, 0.9, 0))
    glPushMatrix()
    glTranslatef(-0.1, 0.4, 0)
    glScalef(1.1, 0.5, 0.9)
    glutSolidCube(0.8)
    glPopMatrix()
    # Párabrisa
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0, 0, 0, 0))
    glPushMatrix()
    glTranslatef(-0.09, 0.4, 0)
    glScalef(1.1, 0.3, 0.89)
    glutSolidCube(0.8)
    glPopMatrix()
    # Janelas frontais
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0, 0, 0, 0))
    glPushMatrix()
    glTranslatef(0.1, 0.4, 0)
    glScalef(0.5, 0.3, 0.91)
    glutSolidCube(0.8)
    glPopMatrix()
    # Janelas traseiras
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0, 0, 0, 0))
    glPushMatrix()
    glTranslatef(-0.35, 0.4, 0)
    glScalef(0.3, 0.3, 0.91)
    glutSolidCube(0.8)
    glPopMatrix()
    # Parte de baixo
    # Faróis
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.1, 0.1, 0.1, 0))
    # Farol esquerdo
    glPushMatrix()
    glTranslatef(0.75, 0.05, -0.2)
    glScalef(0.2, 0.15, 0.2)
    glutSolidCube(0.8)
    glPopMatrix()
    # Farol direito
    glPushMatrix()
    glTranslatef(0.75, 0.05, 0.2)
    glScalef(0.2, 0.15, 0.2)
    glutSolidCube(0.8)
    glPopMatrix()

    if (x % 7 == 0):
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(204.0 / 256, 0, 0, 0))
    elif (x % 7 == 1):
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1, 1, 0, 0))
    elif (x % 7 == 2):
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0, 76.0 / 256, 153.0 / 256, 0))
    elif (x % 7 == 3):
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(204.0 / 256, 0, 102.0 / 256, 0))
    elif (x % 7 == 4):
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0, 153.0 / 256, 153.0 / 256, 0))
    elif (x % 7 == 5):
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.2, 0.2, 0.2, 0))
    elif (x % 7 == 6):
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1, 1, 1, 0))

    # Retrovisores
    glPushMatrix()
    glTranslatef(0.2, 0.13, 0)
    glScalef(0.2, 0.15, 1.2)
    glutSolidCube(0.8)
    glPopMatrix()

    glPushMatrix()
    glScalef(2, 0.5, 1)
    glutSolidCube(0.8)
    glPopMatrix()
    glPopMatrix()

    position = np.ceil(t * 10 - x)
    if (position == 0 or position == 1):
        fieldsMatrix[position][z].setEmpty(0)

    if (position > 1 and position < 19):
        fieldsMatrix[position][z].setEmpty(0)
        fieldsMatrix[position - 1][z].setEmpty(0)
        fieldsMatrix[position - 2][z].setEmpty(1)
        fieldsMatrix[position + 1][z].setEmpty(1)

    if (position == 19):
        fieldsMatrix[position][z].setEmpty(0)
        fieldsMatrix[position - 2][z].setEmpty(1)

    if (position == 20):
        fieldsMatrix[position - 2][z].setEmpty(1)

    if (position == 21):
        fieldsMatrix[position - 2][z].setEmpty(1)

    if (position - 10 == x_curr and z + zTrackBegin == 0):
        carHitPlayer = 1


def renderPlayer():
    global alpha
    global beginAnimation
    global carHitPlayer
    global crashedInSomething
    global jump
    global previousJump
    global runTime1
    pi = 3.1415
    
    glPushMatrix()

    if (crashedInSomething == 1):
        runTime1 = 0
        glTranslatef(0, 0, -0.5)
        glScalef(1, 1, 0.2)
    if (previousJump == 'a'):
        glRotatef(70, 0, 1, 0)
    
    if (previousJump == 'd'):
        glRotatef(-70, 0, 1, 0)

    if (carHitPlayer == 1):
        beginAnimation = 0
        runTime1 = 0
        glTranslatef(0, 0, 0)
        glScalef(1, 0.2, 1)

    if (jump == 'a' and previousJump == 'a'):
        glRotatef(-90, 0, 1, 0)
        
    elif (jump == 'a' and previousJump == 'd'):
        glRotatef(90 + alpha * 180 / pi, 0, 1, 0)
        
    elif (jump == 'a' and previousJump == 'w'):
        glRotatef(180 + alpha * 90 / pi, 0, 1, 0)
        
    elif (jump == 'a' and previousJump == 's'):
        glRotatef(0 - alpha * 90 / pi, 0, 1, 0)
        
    elif (jump == 'd' and previousJump == 'd'):
        glRotatef(90, 0, 1, 0)
        
    elif (jump == 'd' and previousJump == 'w'):
        glRotatef(180 - alpha * 90 / pi, 0, 1, 0)
        
    elif (jump == 'd' and previousJump == 'a'):
        glRotatef(-90 - alpha * 180 / pi, 0, 1, 0)
        
    elif (jump == 'd' and previousJump == 's'):
        glRotatef(0 + alpha * 90 / pi, 0, 1, 0)
        
    elif (jump == 'w' and previousJump == 'd'):
        glRotatef(90 + alpha * 90 / pi, 0, 1, 0)
        
    elif (jump == 'w' and previousJump == 'w'):
        glRotatef(180, 0, 1, 0)
        
    elif (jump == 'w' and previousJump == 's'):
        glRotatef(0 - alpha * 180 / pi, 0, 1, 0)
        
    elif (jump == 'w' and previousJump == 'a'):
        glRotatef(-90 - alpha * 90 / pi, 0, 1, 0)
        
    elif (jump == 's' and previousJump == 'a'):
        glRotatef(-90 + alpha * 90 / pi, 0, 1, 0)
        
    elif (jump == 's' and previousJump == 'd'):
        glRotatef(90 - alpha * 90 / pi, 0, 1, 0)
        
    elif (jump == 's' and previousJump == 's'):
        glRotatef(0, 0, 1, 0)
        
    elif (jump == 's' and previousJump == 'w'):
        glRotatef(180 + alpha * 180 / pi, 0, 1, 0)

    glScalef(0.3, 0.3, 0.3)

    ambient = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
    specular = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
    brightness = (GLfloat * 1)(0)
    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, brightness)
    glColor3f(0, 0, 0)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1, 1, 1, 0))

    # tail
    glPushMatrix()
    glTranslatef(0, 0.5, -1.5)
    glRotatef(-20, 1, 0, 0)
    glutSolidSphere(0.5, 50, 50)
    glPopMatrix()

    # left ear
    glPushMatrix()
    glTranslatef(0.35, 1.66, 1)
    glRotatef(-20, 1, 0, 0)
    glScalef(0.33, 1, 0.33)
    glutSolidCube(1)
    glPopMatrix()

    # right ear
    glPushMatrix()
    glTranslatef(-0.35, 1.66, 1)
    glRotatef(-20, 1, 0, 0)
    glScalef(0.33, 1, 0.33)
    glutSolidCube(1)
    glPopMatrix()

    # head
    glPushMatrix()
    glTranslatef(0, 0.66, 1.5)
    glRotatef(15, 1, 0, 0)
    glutSolidCube(1)
    glPopMatrix()

    # left front leg
    glPushMatrix()
    glTranslatef(0.5, -0.25, 1)
    glRotatef(-10, 1, 0, 0)
    glScalef(0.33, 0.85, 0.33)
    glutSolidCube(1)
    glPopMatrix()

    # right front leg
    glPushMatrix()
    glTranslatef(-0.5, -0.25, 1)
    glRotatef(-10, 1, 0, 0)
    glScalef(0.33, 0.85, 0.33)
    glutSolidCube(1)
    glPopMatrix()

    # left back leg
    glPushMatrix()
    glTranslatef(0.75, 0.2, -0.5)
    glRotatef(-10, 1, 0, 0)
    glScalef(0.25, 1, 1)
    glutSolidCube(1)
    glPopMatrix()

    # right back leg
    glPushMatrix()
    glTranslatef(-0.75, 0.2, -0.5)
    glRotatef(-10, 1, 0, 0)
    glScalef(0.25, 1, 1)
    glutSolidCube(1)
    glPopMatrix()

    # body
    glPushMatrix()
    glTranslatef(0, 0.5, 0)
    glRotatef(-10, 1, 0, 0)
    glScalef(1.25, 1, 2.33)
    glutSolidCube(1)
    glPopMatrix()

    # left foot
    glPushMatrix()
    glTranslatef(0.8, -0.5, -0.25)
    glRotatef(20, 1, 0, 0)
    glScalef(0.33, 0.33, 1.33)
    glutSolidCube(1)
    glPopMatrix()

    # right foot
    glPushMatrix()
    glTranslatef(-0.8, -0.5, -0.25)
    glRotatef(20, 1, 0, 0)
    glScalef(0.33, 0.33, 1.33)
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()


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
