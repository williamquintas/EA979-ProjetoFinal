import math as mt
import random as rd
import sys

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class Field:
    def __init__(self):
        self.forestOrStreet = None
        self.isEmpty = None
        self.carPosition = None
        self.treeHeight = None


class CrossTheStreet:
    def __init__(self):
        # initializes fields matrix
        fieldsSize = 20
        self.fieldsMatrix = np.empty((fieldsSize, fieldsSize), dtype=Field)
        for i in range(fieldsSize):
            for j in range(fieldsSize):
                self.fieldsMatrix[i, j] = Field()

        # declare and initialize variables
        self.alpha = 0  # player rotation angle
        self.beginAnimation = True  # animation when player jumps control
        self.carHitPlayer = False  # true if car hits player
        self.crashedInSomething = False  # true if the player crashed in something
        self.fieldsInitialized = False  # variable to control the fields are once initialized
        self.jump = 'w'  # stores pressed key to control player direction
        self.previousJump = 'w'  # stores previous pressed key to control player rotation
        self.isRunningTimer1 = False
        self.isRunningTimer2 = False
        self.time = 0  # time variable for cars movement
        self.xCurrent = 0  # player position
        self.yCurrent = 0.5
        self.zCurrent = 0
        self.zTime = 0
        self.zTrackBegin = -12  # terrain starts in z=-12
        self.TIMER_1_ID = 0
        self.TIMER_1_INTERVAL = 10
        self.TIMER_2_ID = 0
        self.TIMER_2_INTERVAL = 1

        # variável que guarda a direção da frente do personagem
        self.currentFront = 'w'

        # camera position
        self.eyeX = 1
        self.eyeY = 7 - self.yCurrent
        self.eyeZ = 3
        self.centerX = 0
        self.centerY = 0 - self.yCurrent
        self.centerZ = 0    

        self.gameMode = 3 #3 for third person and 1 for first person

    def run(self):
        # initializes GLUT
        glutInit()
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        # creates the window
        glutInitWindowSize(1000, 1000)
        glutInitWindowPosition(0, 0)
        window = glutCreateWindow("Cross the street")
        # GLUT callback functions
        glutDisplayFunc(self.onDisplay)
        glutKeyboardFunc(self.onKeyboard)
        glutReshapeFunc(self.onReshape)
        # Initializes OpenGL
        glClearColor(1, 1, 1, 0)
        glEnable(GL_DEPTH_TEST)
        # Program infinite loop
        glutMainLoop()

    def onDisplay(self):
        # delete previous screen content
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # configure camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(self.eyeX, self.eyeY,self.eyeZ, self.centerX, self.centerY, self.centerZ, 0, 1, 0)
        if (self.fieldsInitialized == False):
            self.zTrackBegin = -12 - 3
            self.fieldsInitialization()
            self.fieldsInitialized = True
            self.fieldsMatrix[10, -self.zTrackBegin].isEmpty = True
        self.configureIllumination()
        self.renderForest()
        self.renderTerrain()
        self.renderStreets()
        self.renderPlayer()
        glutSwapBuffers()

    # camera position for each mode
    def changeGameMode(self):
        if self.gameMode == 3:
            self.eyeX = 1
            self.eyeY = 7 - self.yCurrent
            self.eyeZ = 3
            self.centerX = 0
            self.centerY = 0 - self.yCurrent
            self.centerZ = 0 
        if self.gameMode == 1:
            self.eyeX = 0.5
            self.eyeY = 1
            self.eyeZ = 0.5
            # A direção em que a câmera aponta dependerá da frente do personagem
            self.changeCameraDirection()

            
    def changeFrontAnticlockwise(self):
        # Muda câmera no sentido anti-horário
        if self.currentFront == 'w':
            self.currentFront = 'a'
        elif self.currentFront == 'a' :
            self.currentFront = 's'
        elif self.currentFront == 's':
            self.currentFront = 'd'
        elif self.currentFront == 'd':
            self.currentFront = 'w' 

    def changeFrontClockwise(self):            
        # Muda câmera no sentido horário
        if self.currentFront == 'w':
            self.currentFront = 'd'
        elif self.currentFront == 'd':
            self.currentFront = 's'
        elif self.currentFront == 's':
            self.currentFront = 'a'
        elif self.currentFront == 'a':
            self.currentFront = 'w'

    def changeFrontThirdPerson(self):
        if (self.jump == 'w'):
            self.currentFront = 'w'
        if (self.jump == 'a'):
            self.currentFront = 'a'
        if (self.jump == 's'):
            self.currentFront = 's'
        if (self.jump == 'd'):
            self.currentFront = 'd'
            
    def changeCameraDirection(self):
        # Agora que a direção (frente) atual já está settada, mudamos
        # a câmera para essa direção
        self.centerY = 1
        if self.currentFront == 'w':
            self.centerX = 0
            self.centerZ = -7
        elif self.currentFront == 's':
            self.centerX = 0
            self.centerZ = 7
        elif self.currentFront == 'd':
            self.centerX = 7
            self.centerZ = 0
        elif self.currentFront == 'a':
            self.centerX = -7
            self.centerZ = 0              

    def translateDirection(self, key: str):
        #if when front is 'w', direction is already correct
        if (self.currentFront == 'a'):
            if (key == 'w'):
                key = 'a'
            elif (key == 'a'):
                key = 's'
            elif (key == 's'):
                key = 'd'
            elif (key == 'd'):
                key = 'w'
        elif (self.currentFront == 's'):
            if (key == 'w'):
                key = 's'
            elif (key == 'a'):
                key = 'd'
            elif (key == 's'):
                key = 'w'
            elif (key == 'd'):
                key = 'a'
        elif (self.currentFront == 'd'):
            if (key == 'w'):
                key = 'd'
            elif (key == 'a'):
                key = 'w'
            elif (key == 's'):
                key = 'a'
            elif (key == 'd'):
                key = 's'

        return key

    # timer used to move the cars
    def onTimer1(self, value: int):
        if value != 0:
            return
        self.time += 0.01
        glutPostRedisplay()
        if (self.isRunningTimer1 == True):
            glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)

    # player jump timer
    def onTimer2(self, value: int):
        if value != 0:
            return
        
        self.alpha += np.pi / 15
        aux1 = np.sin(self.alpha)
        aux2 = np.sin(self.alpha - np.pi / 15)
        if (self.jump == 'w'):
            self.zCurrent -= 1.0 / 15
            self.yCurrent += aux1 - aux2
        elif(self.jump == 'a'):
            self.xCurrent -= 1.0 / 15
            self.yCurrent += aux1 - aux2
        elif (self.jump == 'd'):
            self.xCurrent += 1.0 / 15
            self.yCurrent += aux1 - aux2
        elif (self.jump == 's'):
            self.zCurrent += 1.0 / 15
            self.yCurrent += aux1 - aux2
         
        glutPostRedisplay()
        if self.alpha < np.pi:
            glutTimerFunc(self.TIMER_2_INTERVAL, self.onTimer2, self.TIMER_2_ID)
        else:
            self.yCurrent = 0.5
            if (self.jump == 'a'):
                self.xCurrent = self.xPrevious - 1
            elif (self.jump == 'd'):
                self.xCurrent = self.xPrevious + 1
            elif (self.jump == 'w'):
                self.moveObjects()
                self.zCurrent = 0
            elif (self.jump == 's'):
                self.moveObjects()
                self.zCurrent = 0

        self.isRunningTimer2 = False

    def onKeyboard(self, key: str, x: int, y: int):
        self.previousJump = self.jump
        keycode = ord(key)
        key = key.decode('utf-8')

        # Primeira pessoa: as teclas mudam de direção dependendo de
        # onde é a frente do personagem
        if(self.gameMode == 1):
            key = self.translateDirection(key)
        # Terceira pessoa: a frente sempre será a tecla que foi pressionada
        elif(self.gameMode == 3):
            self.changeFrontThirdPerson()

        if keycode == 27:
            sys.exit()

        elif key == 'w':  # moves forward
            if (self.fieldsMatrix[int(self.xCurrent + 10), -self.zTrackBegin - 1].isEmpty == True) and self.beginAnimation == True and self.isRunningTimer2 == False and self.yCurrent == 0.5:
                self.alpha = 0
                self.jump = 'w'
                self.isRunningTimer2 = True
                self.zPrevious = self.zCurrent
                glutTimerFunc(self.TIMER_2_INTERVAL, self.onTimer2, self.TIMER_2_ID)
                if self.isRunningTimer1 == False:
                    self.isRunningTimer1 = True
                    glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)

            elif (self.fieldsMatrix[int(self.xCurrent + 10), -self.zTrackBegin - 1].isEmpty == False and self.fieldsMatrix[int(self.xCurrent + 10), -self.zTrackBegin - 1].forestOrStreet != 'forest') and self.beginAnimation == True and self.isRunningTimer2 == False:
                self.crashedInSomething = True
                self.beginAnimation = False
                glutPostRedisplay()

        elif key == 'a':  # moves to left           
            if self.fieldsMatrix[int(self.xCurrent + 9), -self.zTrackBegin].isEmpty == True and self.beginAnimation == True and self.isRunningTimer2 == False and self.yCurrent == 0.5:
                self.alpha = 0
                self.jump = 'a'
                self.isRunningTimer2 = True
                self.xPrevious = self.xCurrent
                glutTimerFunc(self.TIMER_2_INTERVAL, self.onTimer2, self.TIMER_2_ID)
                if self.isRunningTimer1 == False:
                    self.isRunningTimer1 = True
                    glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)

        elif key == 'd':  # moves to right                
            if self.fieldsMatrix[int(self.xCurrent + 11), -self.zTrackBegin].isEmpty == True and self.beginAnimation == True and self.isRunningTimer2 == False and self.yCurrent == 0.5:
                self.alpha = 0
                self.jump = 'd'
                self.isRunningTimer2 = True
                self.xPrevious = self.xCurrent
                glutTimerFunc(self.TIMER_2_INTERVAL, self.onTimer2, self.TIMER_2_ID)
                if self.isRunningTimer1 == False:
                    self.isRunningTimer1 = True
                    glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)

        elif key == 's':  # moves back
            if self.fieldsMatrix[int(self.xCurrent + 10), -self.zTrackBegin + 1].isEmpty == True and self.beginAnimation == True and self.isRunningTimer2 == False and self.yCurrent == 0.5:
                self.alpha = 0
                self.jump = 's'
                self.isRunningTimer2 = True
                self.zPrevious = self.zCurrent
                glutTimerFunc(self.TIMER_2_INTERVAL, self.onTimer2, self.TIMER_2_ID)
                if self.isRunningTimer1 == False:
                    self.isRunningTimer1 = True
                    glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)

        elif key == '1': # first person mode
            self.gameMode = 1
            self.changeGameMode()
        elif key == '3': # third person mode
            self.gameMode = 3
            self.changeGameMode()

        elif key == 'o': # muda camera no sentido anti-horário
            if self.gameMode == 1:
                self.changeFrontAnticlockwise()
                self.changeCameraDirection()
        elif key == 'p': # muda camera no sentido horário
            if self.gameMode == 1:
                self.changeFrontClockwise()
                self.changeCameraDirection()

        elif key == 'r':  # reinitialize variables
            self.alpha = 0
            self.beginAnimation = True
            self.carHitPlayer = False
            self.crashedInSomething = False
            self.fieldsInitialized = False
            self.jump = 'w'
            self.previousJump = 'w'
            self.isRunningTimer1 = False
            self.isRunningTimer2 = False
            self.time = 0
            self.xCurrent = 0
            self.yCurrent = 0.5
            self.zCurrent = 0
            self.zTime = 0
            glutPostRedisplay()

    # the game works like a running machine

    def moveObjects(self):
        rd.seed()

        # while the player moves forward, all the objects (cars and streets) are placed back in one field
        # and another field is created in the end of the field
        if self.jump == 'w':
            for j in range(18, -1, -1):
                for i in range(0, 20):
                    self.fieldsMatrix[i, j + 1].isEmpty = self.fieldsMatrix[i, j].isEmpty
                    self.fieldsMatrix[i, j + 1].forestOrStreet = self.fieldsMatrix[i, j].forestOrStreet
                    self.fieldsMatrix[i, j + 1].carPosition = self.fieldsMatrix[i, j].carPosition
                    self.fieldsMatrix[i, j + 1].treeHeight = self.fieldsMatrix[i, j].treeHeight
            for j in range(0, 20):
                self.fieldsMatrix[j, 0].isEmpty = True
                if self.fieldsMatrix[j, 1].forestOrStreet == 'street' and self.fieldsMatrix[j, 2].forestOrStreet == 'street':
                    self.fieldsMatrix[j, 0].forestOrStreet == 'forest'
                else:
                    self.fieldsMatrix[j, 0].forestOrStreet == 'street'
            for i in range(0, 20):
                if rd.random() > 0.7 and self.fieldsMatrix[i, 0].forestOrStreet == 'forest':
                    self.fieldsMatrix[i, 0].treeHeight = mt.ceil(rd.random() * 3)
                    self.fieldsMatrix[i, 0].isEmpty = False
                else:
                    self.fieldsMatrix[i, 0].isEmpty = True
                self.fieldsMatrix[i, 0].carPosition = rd.random() * 8 + 10 * i + 10 * self.time
        # if the player moves backward, all the objects are moved forward in one field
        elif self.jump == 's':
            for j in range(0, 20):
                for i in range(0, 20):
                    self.fieldsMatrix[i, j - 1].isEmpty = self.fieldsMatrix[i, j].isEmpty
                    self.fieldsMatrix[i, j - 1].forestOrStreet = self.fieldsMatrix[i, j].forestOrStreet
                    self.fieldsMatrix[i, j - 1].carPosition = self.fieldsMatrix[i, j].carPosition
                    self.fieldsMatrix[i, j - 1].treeHeight = self.fieldsMatrix[i, j].treeHeight

    # random tree size and car position settings

    def fieldsInitialization(self):
        rd.seed()
        for i in range(0, 20):
            for j in range(0, 20):
                if (j > 5):
                    self.fieldsMatrix[i, j].forestOrStreet = 'forest'
                elif (j % 3 == 0):
                    self.fieldsMatrix[i, j].forestOrStreet = 'forest'
                else:
                    self.fieldsMatrix[i, j].forestOrStreet = 'street'

                if (rd.random() > 0.9 and self.fieldsMatrix[i, j].forestOrStreet == 'forest'):
                    self.fieldsMatrix[i, j].isEmpty = False
                    self.fieldsMatrix[i, j].treeHeight = mt.ceil(rd.random() * 3)
                else:
                    self.fieldsMatrix[i, j].isEmpty = True

                self.fieldsMatrix[i, j].carPosition = rd.random() * 8 + 10 * i

    def configureIllumination(self):
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

    def renderForest(self):
        glPushMatrix()
        glTranslatef(-self.xCurrent, -self.yCurrent, -self.zCurrent)
        for i in range(0, 20):
            for j in range(0, 20):
                if self.fieldsMatrix[i, j].isEmpty == False and self.fieldsMatrix[i, j].forestOrStreet == 'forest':
                    self.renderTree(i - 10, self.zTrackBegin + j)
        for j in range(0, 20):
            if self.fieldsMatrix[1, j].forestOrStreet == 'forest':
                self.renderTree(-11, self.zTrackBegin + j)
        for j in range(0, 20):
            if self.fieldsMatrix[19, j].forestOrStreet == 'forest':
                self.renderTree(10, self.zTrackBegin + j)
        glPopMatrix()

    def renderTree(self, x: int, z: int):
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
            aux = self.fieldsMatrix[x + 10, z - self.zTrackBegin].treeHeight
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

    def renderTerrain(self):
        glPushMatrix()
        glTranslatef(-self.xCurrent, -self.yCurrent, -self.zCurrent)
        for i in range(0, 20):
            for j in range(0, 20):
                if self.fieldsMatrix[i, j].forestOrStreet != 'street':
                    self.renderGrass(i, j)

        for i in range(-10, 0):
            for j in range(0, 20):
                if self.fieldsMatrix[i + 15, j].forestOrStreet != 'street':
                    self.renderGrass(i, j)

        for i in range(20, 30):
            for j in range(0, 20):
                if self.fieldsMatrix[i - 15, j].forestOrStreet != 'street':
                    self.renderGrass(i, j)
        glPopMatrix()

    def renderGrass(self, x, z):
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

    def renderStreets(self):
        glPushMatrix()
        glTranslatef(-self.xCurrent, -self.yCurrent, -self.zCurrent)
        for i in range(0, 20):
            for j in range(0, 20):
                if self.fieldsMatrix[i, j].forestOrStreet == 'street':
                    self.renderAsphalt(i, j)
        for i in range(-10, 0):
            for j in range(0, 20):
                if self.fieldsMatrix[i+15, j].forestOrStreet == 'street':
                    self.renderAsphalt(i, j)
        for i in range(20, 30):
            for j in range(0, 20):
                if self.fieldsMatrix[i-15, j].forestOrStreet == 'street':
                    self.renderAsphalt(i, j)
        for i in range(0, 20):
            for j in range(0, 20):
                if self.fieldsMatrix[i, j].forestOrStreet == 'street':
                    self.renderCar(self.fieldsMatrix[i, j].carPosition, j)
        glPopMatrix()

    def renderAsphalt(self, x, z):
        glDisable(GL_LIGHTING)
        glPushMatrix()
        glTranslatef(0, 0, -3)
        if (
            (
                x >= 0 and
                x < 20 and
                self.fieldsMatrix[x, z].forestOrStreet == 'street' and
                x % 2 == 1
            ) or (
                x < 0 and
                self.fieldsMatrix[x + 15, z].forestOrStreet == 'street' and
                np.abs(x) % 2 == 1
            ) or (
                x >= 20 and
                self.fieldsMatrix[x - 15, z].forestOrStreet == 'street' and
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

    def renderCar(self, x, z):

        glPushMatrix()
        glColor3f(1, 1, 0)
        glTranslatef(-10 + self.time * 10 - x, 0.3, z + self.zTrackBegin)

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

        position = int(np.ceil(self.time * 10 - x))
        if (position == 0 or position == 1):
            self.fieldsMatrix[position, z].isEmpty = False

        if (position > 1 and position < 19):
            self.fieldsMatrix[position, z].isEmpty = False
            self.fieldsMatrix[position - 1, z].isEmpty = False
            self.fieldsMatrix[position - 2, z].isEmpty = True
            self.fieldsMatrix[position + 1, z].isEmpty = True

        if (position == 19):
            self.fieldsMatrix[position, z].isEmpty = False
            self.fieldsMatrix[position - 2, z].isEmpty = True

        if (position == 20):
            self.fieldsMatrix[position - 2, z].isEmpty = True

        if (position == 21):
            self.fieldsMatrix[position - 2, z].isEmpty = True

        if (position - 10 == self.xCurrent and z + self.zTrackBegin == 0):
            self.carHitPlayer = True

    def renderPlayer(self):
        pi = 3.1415

        glPushMatrix()

        if (self.crashedInSomething == True):
            self.isRunningTimer1 = False
            glTranslatef(0, 0, -0.5)
            glScalef(1, 1, 0.2)

            if (self.previousJump == 'a'):
                glRotatef(70, 0, 1, 0)

            if (self.previousJump == 'd'):
                glRotatef(-70, 0, 1, 0)

        if (self.carHitPlayer == True):
            self.beginAnimation = False
            self.isRunningTimer1 = False
            glTranslatef(0, 0, 0)
            glScalef(1, 0.2, 1)

        if (self.jump == 'a' and self.previousJump == 'a'):
            glRotatef(-90, 0, 1, 0)

        elif (self.jump == 'a' and self.previousJump == 'd'):
            glRotatef(90 + self.alpha * 180 / pi, 0, 1, 0)

        elif (self.jump == 'a' and self.previousJump == 'w'):
            glRotatef(180 + self.alpha * 90 / pi, 0, 1, 0)

        elif (self.jump == 'a' and self.previousJump == 's'):
            glRotatef(0 - self.alpha * 90 / pi, 0, 1, 0)

        elif (self.jump == 'd' and self.previousJump == 'd'):
            glRotatef(90, 0, 1, 0)

        elif (self.jump == 'd' and self.previousJump == 'w'):
            glRotatef(180 - self.alpha * 90 / pi, 0, 1, 0)

        elif (self.jump == 'd' and self.previousJump == 'a'):
            glRotatef(-90 - self.alpha * 180 / pi, 0, 1, 0)

        elif (self.jump == 'd' and self.previousJump == 's'):
            glRotatef(0 + self.alpha * 90 / pi, 0, 1, 0)

        elif (self.jump == 'w' and self.previousJump == 'd'):
            glRotatef(90 + self.alpha * 90 / pi, 0, 1, 0)

        elif (self.jump == 'w' and self.previousJump == 'w'):
            glRotatef(180, 0, 1, 0)

        elif (self.jump == 'w' and self.previousJump == 's'):
            glRotatef(0 - self.alpha * 180 / pi, 0, 1, 0)

        elif (self.jump == 'w' and self.previousJump == 'a'):
            glRotatef(-90 - self.alpha * 90 / pi, 0, 1, 0)

        elif (self.jump == 's' and self.previousJump == 'a'):
            glRotatef(-90 + self.alpha * 90 / pi, 0, 1, 0)

        elif (self.jump == 's' and self.previousJump == 'd'):
            glRotatef(90 - self.alpha * 90 / pi, 0, 1, 0)

        elif (self.jump == 's' and self.previousJump == 's'):
            glRotatef(0, 0, 1, 0)

        elif (self.jump == 's' and self.previousJump == 'w'):
            glRotatef(180 + self.alpha * 180 / pi, 0, 1, 0)

        glScalef(0.25, 0.25, 0.25)

        ambient = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
        specular = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
        brightness = (GLfloat * 1)(0.0)
        glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, brightness)
        
        # body
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.60, 0.40, 0.12))
        glTranslatef(0.0, 0.0, 0.0)
        glScaled(1.25, 1, 1.25)
        glutSolidCube(1.5)
        glPopMatrix()

        # neck
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.60, 0.40, 0.12))
        glTranslatef(0.0, 2.0, 0.0)
        glRotated(90, 0, 1, 0)
        glScaled(0.9, 3.0, 0.9)
        glutSolidCube(1.5)
        glPopMatrix()

        # right wing
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.60, 0.40, 0.12))
        glTranslatef(-1.0, 0.0, 0.0)
        glRotated(90, 0, 1, 0)
        glScaled(0.5, 0.5, 0.5)
        glutSolidCube(1.5)
        glPopMatrix()

        # left wing
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.60, 0.40, 0.12))
        glTranslatef(1.0, 0.0, 0.0)
        glRotated(90, 0, 1, 0)
        glScaled(0.5, 0.5, 0.5)
        glutSolidCube(1.5)
        glPopMatrix()

        # beak
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 0.6, 0.0))
        glTranslatef(0.0, 2.5, 0.8)
        glRotated(180, 0, 1, 0)
        glScaled(0.25, 0.5, 0.25)
        glutSolidCube(1.5)
        glPopMatrix()

        # crest
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 0.0, 0.0))
        glTranslatef(0.0, 4.5, 0.0)
        glRotated(180, 0, 1, 0)
        glScaled(0.25, 0.5, 0.5)
        glutSolidCube(1.5)
        glPopMatrix()

        glPopMatrix()

    def onReshape(self, width: int, height: int):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, float(width/height), 1, 100)


def main():
    game = CrossTheStreet()
    game.run()


if __name__ == '__main__':
    main()
