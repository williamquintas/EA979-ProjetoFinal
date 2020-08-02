import math as mt
import random as rd
import sys
import pygame
<<<<<<< HEAD
import pygame_menu
=======
>>>>>>> 7dcab39c548b061da637fa316a64e3d6f937ff1d

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

def loadTexture(texture_url):
    tex_id = glGenTextures(1)
    tex = pygame.image.load(texture_url)
    tex_surface = pygame.image.tostring(tex, 'RGBA', 1)
    tex_width, tex_height = tex.get_size()
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_width, tex_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, tex_surface)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id   

class Field:
    def __init__(self):
        self.forestOrStreet = None
        self.isEmpty = None
        self.carPosition = None
        self.treeHeight = None

class CrossTheStreet:
    def __init__(self):
        # inicializa a matriz do campo
        fieldsSizeX = 20
        fieldsSizeY = 25
        self.fieldsMatrix = np.empty((fieldsSizeX, fieldsSizeY), dtype=Field)
        for i in range(fieldsSizeX):
            for j in range(fieldsSizeY):
                self.fieldsMatrix[i, j] = Field()

        # declaração e inicialização de variáveis
        self.alpha = 0  # ângulo de rotação do jogador
        self.beginAnimation = True  # true caso o modelo esteja em movimento (no meio do salto)
        self.carHitPlayer = False  # true caso o carro acerte o jogador
        self.crashedInSomething = False  # true caso o jogador esbarre em algo
        self.fieldsInitialized = False  # variable to control the fields are once initialized
        self.jump = 'w'  # armazena tecla pressionada para controlar a direção
        self.previousJump = 'w'  # armazena tecla pressionada para controlar a rotação do modelo
        self.isRunningTimer1 = False
        self.isRunningTimer2 = False
        self.time = 0  # variável de tempo para o movimento dos carros
        
        # posição do jogador
        self.xCurrent = 0
        self.yCurrent = 0.5
        self.zCurrent = 0

        self.zTime = 0
        self.zTrackBegin = -12  # terreno inicia em -12
        self.TIMER_1_ID = 0
        self.TIMER_1_INTERVAL = 10
        self.TIMER_2_ID = 0
        self.TIMER_2_INTERVAL = 1

        self.currentFront = 'w' # direção da frente do personagem  
        self.gameMode = 3 # inicializa o jogo em modo de terceira pessoa

        # posição da câmera em terceira pessoa 
        self.eyeX = 1
        self.eyeY = 7 - self.yCurrent
        self.eyeZ = 3
        self.centerX = 0
        self.centerY = 0 - self.yCurrent
        self.centerZ = 0              

        #posição da luz
        self.lightPosX = 0
        self.lightPosY = 4.5
        self.lightPosZ = 3
        self.lightPosJoker = 1

        # Numero de passos totais do jogador
        self.steps = 0

        # Numero de passos para frente do jogador
        self.stepsZ = 0

        # Indica para mudar de fase
        self.level = 0
        self.nextLevel = False

        # define qual personagem renderizar
        self.character = 1
        
    def selectCharacter(self, player, value):
        if (player == ('Chicken', 0)):
            self.character = 1
        elif (player == ('Bunny', 1)):
            self.character = 2 
            
    def run(self):
        # inicializa o GLUT
        glutInit()
        glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
        # cria a janela
        glutInitWindowSize(1000, 1000)
        glutInitWindowPosition(0,0)
        window = glutCreateWindow("Cross the street")
        # funções de callback do GLUT
        glutDisplayFunc(self.onDisplay)
        glutKeyboardFunc(self.onKeyboard)
        glutReshapeFunc(self.onReshape)
        # Inicia OpenGL
        glClearColor(1, 1, 1, 0)
        glEnable(GL_DEPTH_TEST)
        # Inicializa as texturas da skybox
        glEnable(GL_TEXTURE_2D)
        self.SKYFRONT = loadTexture('./data/texture/testee.png')
        self.SKYBACK = loadTexture('./data/texture/testee.png')
        self.SKYLEFT = loadTexture('./data/texture/testee.png')
        self.SKYRIGHT = loadTexture('./data/texture/testee.png')
        self.SKYUP = loadTexture('./data/texture/testee.png')
        self.SKYDOWN = loadTexture('./data/texture/down.jpg')
        # Setta o loop do programa
        glutMainLoop()
    
    def onDisplay(self):
        # deleta o conteudo da tela anterior
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # configura camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # semelhante ao glm.lookAt, só que usa valores soltos ao invés de três
        # matrizes. A ordem é a mesma: posição da câmera, frente da câmera e "cima"
        # da câmera
        gluLookAt(self.eyeX, self.eyeY,self.eyeZ, self.centerX, self.centerY, self.centerZ, 0, 1, 0)
        if (self.fieldsInitialized == False):
            self.zTrackBegin = -12 - 3
            self.fieldsInitialization(self.level)
            self.fieldsInitialized = True
            self.fieldsMatrix[10, -self.zTrackBegin].isEmpty = True
        self.configureIllumination()
        self.renderSkybox(0, 0, 0, 50, 50, 50)
        self.renderForest()
        self.renderTerrain()
        self.renderStreets()
        self.renderPlayer()

        stepsString = "Steps: " + str(self.steps)
        self.renderText(stepsString, 50, 200, 1, 0, 0)

        glutSwapBuffers()

    # posicionamento da câmera para cada modo de jogo
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
            # a direção em que a câmera aponta dependerá para onde o personagem estiver olhando (frente)
            self.changeCameraDirection()

            
    def changeFrontAnticlockwise(self):
        # muda câmera no sentido anti-horário
        if self.currentFront == 'w':
            self.currentFront = 'a'
        elif self.currentFront == 'a' :
            self.currentFront = 's'
        elif self.currentFront == 's':
            self.currentFront = 'd'
        elif self.currentFront == 'd':
            self.currentFront = 'w' 

    def changeFrontClockwise(self):            
        # muda câmera no sentido horário
        if self.currentFront == 'w':
            self.currentFront = 'd'
        elif self.currentFront == 'd':
            self.currentFront = 's'
        elif self.currentFront == 's':
            self.currentFront = 'a'
        elif self.currentFront == 'a':
            self.currentFront = 'w'

    def changeFrontThirdPerson(self):
        # mesmo no modo de terceira pessoa a frente do personagem precisa ser atualizada
        # para que a câmera seja posicionada corretamente ao ser mudado para primeira pessoa
        if (self.jump == 'w'):
            self.currentFront = 'w'
        if (self.jump == 'a'):
            self.currentFront = 'a'
        if (self.jump == 's'):
            self.currentFront = 's'
        if (self.jump == 'd'):
            self.currentFront = 'd'
            
    def changeCameraDirection(self):
        # setta a direção da câmera no modo em primeira pessoa
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
        # a direção "w" não precisa ser traduzida, já que é a padrão
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

    def sneakPeek(self, direction):
        # eixo para onde virará a olhadinha depende da frente do jogador
        if (self.currentFront == 'w'):
            if direction == 'right':
                self.centerX = self.centerX + 0.2
            elif direction == 'left':
                self.centerX = self.centerX - 0.2
        elif (self.currentFront == 'a'):
            if direction == 'right':
                self.centerZ = self.centerZ - 0.2
            elif direction == 'left':
                self.centerZ = self.centerZ + 0.2            
        elif (self.currentFront == 's'):
            if direction == 'right':
                self.centerX = self.centerX - 0.2
            elif direction == 'left':
                self.centerX = self.centerX + 0.2            
        elif (self.currentFront == 'd'):
            if direction == 'right':
                self.centerZ = self.centerZ + 0.2
            elif direction == 'left':
                self.centerZ = self.centerZ - 0.2            



    # timer usado para mover os carros
    def onTimer1(self, value: int):
        if value != 0:
            return
        self.time += 0.01
        glutPostRedisplay()
        if (self.isRunningTimer1 == True):
            glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)

    # timer usado para o salto do jogador
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

    def verifyStepsZ(self):    
        # atingiu total de passos para atravessar todas as ruas, inicializa novo field para nova fase
        if(self.stepsZ == 15):
            self.nextLevel = True
            self.beginAnimation = False
            glutPostRedisplay()

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
            
        elif key == 'w':  # para frente
            if (self.fieldsMatrix[int(self.xCurrent + 10), -self.zTrackBegin - 1].isEmpty == True) and self.beginAnimation == True and self.isRunningTimer2 == False and self.yCurrent == 0.5:
                self.alpha = 0
                self.jump = 'w'
                self.isRunningTimer2 = True
                self.zPrevious = self.zCurrent
                self.steps += 1
                self.stepsZ += 1
                glutTimerFunc(self.TIMER_2_INTERVAL, self.onTimer2, self.TIMER_2_ID)
                if self.isRunningTimer1 == False:
                    self.isRunningTimer1 = True
                    glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)
                
            elif (self.fieldsMatrix[int(self.xCurrent + 10), -self.zTrackBegin - 1].isEmpty == False and self.fieldsMatrix[int(self.xCurrent + 10), -self.zTrackBegin - 1].forestOrStreet != 'forest') and self.beginAnimation == True and self.isRunningTimer2 == False:
                self.crashedInSomething = True
                self.beginAnimation = False
                glutPostRedisplay()

            self.verifyStepsZ()    

        elif key == 'a':  # para esquerda           
            if self.fieldsMatrix[int(self.xCurrent + 9), -self.zTrackBegin].isEmpty == True and self.beginAnimation == True and self.isRunningTimer2 == False and self.yCurrent == 0.5:
                self.alpha = 0
                self.jump = 'a'
                self.isRunningTimer2 = True
                self.xPrevious = self.xCurrent
                self.steps += 1
                glutTimerFunc(self.TIMER_2_INTERVAL, self.onTimer2, self.TIMER_2_ID)
                if self.isRunningTimer1 == False:
                    self.isRunningTimer1 = True
                    glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)

        elif key == 'd':  # para direita              
            if self.fieldsMatrix[int(self.xCurrent + 11), -self.zTrackBegin].isEmpty == True and self.beginAnimation == True and self.isRunningTimer2 == False and self.yCurrent == 0.5:
                self.alpha = 0
                self.jump = 'd'
                self.isRunningTimer2 = True
                self.xPrevious = self.xCurrent
                self.steps += 1
                glutTimerFunc(self.TIMER_2_INTERVAL, self.onTimer2, self.TIMER_2_ID)
                if self.isRunningTimer1 == False:
                    self.isRunningTimer1 = True
                    glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)

        elif key == 's':  # para trás
            if self.fieldsMatrix[int(self.xCurrent + 10), -self.zTrackBegin + 1].isEmpty == True and self.beginAnimation == True and self.isRunningTimer2 == False and self.yCurrent == 0.5:
                self.alpha = 0
                self.jump = 's'
                self.isRunningTimer2 = True
                self.zPrevious = self.zCurrent
                self.steps += 1
                self.stepsZ -= 1
                glutTimerFunc(self.TIMER_2_INTERVAL, self.onTimer2, self.TIMER_2_ID)
                if self.isRunningTimer1 == False:
                    self.isRunningTimer1 = True
                    glutTimerFunc(self.TIMER_1_INTERVAL, self.onTimer1, self.TIMER_1_ID)

        elif key == '1': # muda o jogo para primeira pessoa
            self.gameMode = 1
            self.changeGameMode()
        elif key == '3': # muda o jogo para terceira pessoa
            self.gameMode = 3
            self.changeGameMode()

        elif key == 'o' and  self.gameMode == 1: # muda camera no sentido anti-horário
                self.changeFrontAnticlockwise()
                self.changeCameraDirection()
        elif key == 'p' and self.gameMode == 1: # muda camera no sentido horário
                self.changeFrontClockwise()
                self.changeCameraDirection()

        # olhadinha para os lados (para ver os carros ao atravessar a rua em primeira pessoa)
        elif key == '4' and self.gameMode == 1:
            self.sneakPeek('left')
        elif key == '5' and self.gameMode == 1:
           self.sneakPeek('right')

        # recomeça o jogo reiniciando todas as variáveis
        elif key == 'r':
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
            self.steps = 0
            self.stepsZ = 0
            self.level = 0 # comeca da primeira fase
            self.nextLevel = False
            glutPostRedisplay()
        # para comecar a proxima fase    
        elif key == 'n':
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
            self.steps = 0
            self.stepsZ = 0
            self.level += 1 # proxima fase
            self.nextLevel = False
            glutPostRedisplay()
    

    # o jogo funciona como uma esteira: as coordenadas do jogador e da câmera permanecem estáticas
    # enquanto o campo e os objetos presentes nele se mexem em relação ao jogador
    def moveObjects(self):
        rd.seed()

        # quando o jogador anda para frente (eixo z negativo), todos os objetos são movidos um 
        # campo para trás e um novo campo é criado após a última linha
        if self.jump == 'w':
            for j in range(23, -1, -1):
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
        # quando o jogador anda para trás (eixo z positivo), todos os objetos são movidos um 
        # campo para frente
        elif self.jump == 's':
            for j in range(1, 25):
                for i in range(0, 20):
                    self.fieldsMatrix[i, j - 1].isEmpty = self.fieldsMatrix[i, j].isEmpty
                    self.fieldsMatrix[i, j - 1].forestOrStreet = self.fieldsMatrix[i, j].forestOrStreet
                    self.fieldsMatrix[i, j - 1].carPosition = self.fieldsMatrix[i, j].carPosition
                    self.fieldsMatrix[i, j - 1].treeHeight = self.fieldsMatrix[i, j].treeHeight

    # posição das árvores aleatóras e posição dos carros
    def fieldsInitialization(self, fase):
        rd.seed()
        for i in range(0, 20):
            for j in range(0, 25):
                if (fase == 0):
                    if (j > 9):
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
                elif (fase == 1):
                    if (j > 8):
                        self.fieldsMatrix[i, j].forestOrStreet = 'forest'
                    elif (j % 4 == 0):
                        self.fieldsMatrix[i, j].forestOrStreet = 'forest'
                    else:
                        self.fieldsMatrix[i, j].forestOrStreet = 'street'

                    if (rd.random() > 0.9 and self.fieldsMatrix[i, j].forestOrStreet == 'forest'):
                        self.fieldsMatrix[i, j].isEmpty = False
                        self.fieldsMatrix[i, j].treeHeight = mt.ceil(rd.random() * 3)
                    else:
                        self.fieldsMatrix[i, j].isEmpty = True

                    self.fieldsMatrix[i, j].carPosition = rd.random() * 8 + 10 * i
                elif (fase == 2):
                    if (j > 9):
                        self.fieldsMatrix[i, j].forestOrStreet = 'forest'
                    elif (j % 6 == 0):
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
        glEnable(GL_LIGHT1)
        position = (GLfloat * 4)(0, self.lightPosY, self.lightPosZ, self.lightPosJoker)
        ambient = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
        diffuse = (GLfloat * 4)(0.7, 0.7, 0.7, 1)
        specular = (GLfloat * 4)(0.9, 0.9, 0.9, 1)
        glLightfv(GL_LIGHT0, GL_POSITION, position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, specular)

        position = (GLfloat * 4)(0, 4.5,-63, 1)
        glLightfv(GL_LIGHT1, GL_POSITION, position)
        glLightfv(GL_LIGHT1, GL_AMBIENT, ambient)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, diffuse)
        glLightfv(GL_LIGHT1, GL_SPECULAR, specular)

    def renderForest(self):
        glPushMatrix()
        glTranslatef(-self.xCurrent, -self.yCurrent, -self.zCurrent)
        for i in range(0, 20):
            for j in range(0, 25):
                if self.fieldsMatrix[i, j].isEmpty == False and self.fieldsMatrix[i, j].forestOrStreet == 'forest':
                    self.renderTree(i - 10, self.zTrackBegin + j)
        for j in range(0, 25):
            if self.fieldsMatrix[1, j].forestOrStreet == 'forest':
                self.renderTree(-11, self.zTrackBegin + j)
        for j in range(0, 25):
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

        # folhas da árvore
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

        # tronca da árvore
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
            for j in range(0, 25):
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
            for j in range(0, 25):
                if self.fieldsMatrix[i, j].forestOrStreet == 'street':
                    self.renderAsphalt(i, j)
        for i in range(-10, 0):
            for j in range(0, 25):
                if self.fieldsMatrix[i+15, j].forestOrStreet == 'street':
                    self.renderAsphalt(i, j)
        for i in range(20, 30):
            for j in range(0, 25):
                if self.fieldsMatrix[i-15, j].forestOrStreet == 'street':
                    self.renderAsphalt(i, j)
        for i in range(0, 20):
            for j in range(0, 25):
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
                self.fieldsMatrix[x - 1, z + 1].forestOrStreet == 'street' and
                x % 2 == 1
            ) or (
                x < 0 and
                self.fieldsMatrix[x + 14, z + 1].forestOrStreet == 'street' and
                np.abs(x) % 2 == 1
            ) or (
                x >= 20 and
                self.fieldsMatrix[x - 14, z + 1].forestOrStreet == 'street' and
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

    def renderSkybox (self, x, y, z, width, height, length):
        # desenha 6 quadrados, adiciona textura a eles e os posiciona ao redor da

        #Center the Skybox around the given x,y,z position
        x = x - width  / 2
        y = y - height / 2
        z = z - length / 2

        #Coloração branca para os quadrados
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))

        #Draw Front side
        glBindTexture(GL_TEXTURE_2D, self.SKYFRONT)
        glBegin(GL_QUADS);		
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x, y, z + length)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x, y + height, z+length)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x+width, y+height, z+length)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x+width, y,z+length)
        glEnd()    
        glBindTexture(GL_TEXTURE_2D, 0)

        #Draw Back side
        glColor3f(1, 1, 1)
        glBindTexture(GL_TEXTURE_2D, self.SKYBACK)
        glBegin(GL_QUADS)
        glColor3f(0.0, 0.0, 0.0)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x+width, y,z)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x+width, y+height, z); 
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x,y+height,z)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x,y,z)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

        #Draw Left side
        glColor3f(1, 1, 1)
        glBindTexture(GL_TEXTURE_2D, self.SKYLEFT)
        glBegin(GL_QUADS);		
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x, y+height,z)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x, y+height, z+length) 
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x, y, z+length)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x, y, z)		
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

        #Draw Right side
        glColor3f(1, 1, 1)
        glBindTexture(GL_TEXTURE_2D, self.SKYRIGHT)
        glBegin(GL_QUADS);		
        glTexCoord2f(0.0, 0.0) 
        glVertex3f(x+width, y, z)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x+width, y, z+length)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x+width, y+height,	z+length)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x+width, y+height,	z)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

        #Draw Up side
        glColor3f(1, 1, 1)
        glBindTexture(GL_TEXTURE_2D, self.SKYUP)
        glBegin(GL_QUADS)	
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x+width, y+height, z)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x+width, y+height, z+length)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x,		  y+height,	z+length)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x,y+height,	z)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)

        #Draw Down side
        glColor3f(1, 1, 1)
        glBindTexture(GL_TEXTURE_2D, self.SKYDOWN)
        glBegin(GL_QUADS);		
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x, y, z)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x, y, z+length)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x+width, y,	z+length)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x+width, y,	z)
        glEnd()    
        glBindTexture(GL_TEXTURE_2D, 0)

    def renderCar(self, x, z):

        #Aqui há a montagem e a desmontagem dos modelos
        # TSR, só que ao invés de colocar as matriz todas juntas, elas são aplicadas uma por vez.
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
            self.renderText("Game Over! Press R to restart.", 200, 400, 1, 0, 0)

            if (self.previousJump == 'a'):
                glRotatef(70, 0, 1, 0)

            if (self.previousJump == 'd'):
                glRotatef(-70, 0, 1, 0)
         
        if (self.nextLevel == True):
            self.isRunningTimer1 = False
            self.renderText("You pass! Press N to start next level.", 200, 400, 1, 0, 0)
    

        if (self.carHitPlayer == True):
            self.beginAnimation = False
            self.isRunningTimer1 = False
            glTranslatef(0, 0, 0)
            glScalef(1, 0.2, 1)
            self.renderText("Game Over! Press R to restart.", 200, 400, 1, 0, 0)
            
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

        #ambient = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
        specular = (GLfloat * 4)(0.1, 0.1, 0.1, 1)
        brightness = (GLfloat * 1)(0.0)
        #glMaterialfv(GL_FRONT, GL_AMBIENT, ambient)
        glMaterialfv(GL_FRONT, GL_SPECULAR, specular)
        glMaterialfv(GL_FRONT, GL_SHININESS, brightness)
        
        if (self.character == 1):
            self.renderChicken()
        elif (self.character == 2):    
            self.renderBunny()

    def renderChicken(self):
        # corpo
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.60, 0.40, 0.12))
        glTranslatef(0.0, 0.0, 0.0)
        glScaled(1.25, 1, 1.25)
        glutSolidCube(1.5)
        glPopMatrix()

        # pescoço
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.60, 0.40, 0.12))
        glTranslatef(0.0, 2.0, 0.0)
        glRotated(90, 0, 1, 0)
        glScaled(0.9, 3.0, 0.9)
        glutSolidCube(1.5)
        glPopMatrix()

        # asa direita
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.60, 0.40, 0.12))
        glTranslatef(-1.0, 0.0, 0.0)
        glRotated(90, 0, 1, 0)
        glScaled(0.5, 0.5, 0.5)
        glutSolidCube(1.5)
        glPopMatrix()

        # asa esquerda
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(0.60, 0.40, 0.12))
        glTranslatef(1.0, 0.0, 0.0)
        glRotated(90, 0, 1, 0)
        glScaled(0.5, 0.5, 0.5)
        glutSolidCube(1.5)
        glPopMatrix()

        # bico
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 0.6, 0.0))
        glTranslatef(0.0, 2.5, 0.8)
        glRotated(180, 0, 1, 0)
        glScaled(0.25, 0.5, 0.25)
        glutSolidCube(1.5)
        glPopMatrix()

        # crista
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 0.0, 0.0))
        glTranslatef(0.0, 4.5, 0.0)
        glRotated(180, 0, 1, 0)
        glScaled(0.25, 0.5, 0.5)
        glutSolidCube(1.5)
        glPopMatrix()

        glPopMatrix()

    def renderBunny(self):
        # rabo
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(0, 0.5, -1.5)
        glRotatef(-20, 1, 0, 0)
        glutSolidSphere(0.5, 50, 50)
        glPopMatrix()

        # orelha esquerda
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(0.35, 1.66, 1)
        glRotatef(-20, 1, 0, 0)
        glScalef(0.33, 1, 0.33)
        glutSolidCube(1)
        glPopMatrix()

        # orelha direita
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(-0.35, 1.66, 1)
        glRotatef(-20, 1, 0, 0)
        glScalef(0.33, 1, 0.33)
        glutSolidCube(1)
        glPopMatrix()

        # cabeca
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(0, 0.66, 1.5)
        glRotatef(15, 1, 0, 0)
        glutSolidCube(1)
        glPopMatrix()

        # perna frontal esquerda
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(0.5, -0.25, 1)
        glRotatef(-10, 1, 0, 0)
        glScalef(0.33, 0.85, 0.33)
        glutSolidCube(1)
        glPopMatrix()

        # perna frontal direita
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(-0.5, -0.25, 1)
        glRotatef(-10, 1, 0, 0)
        glScalef(0.33, 0.85, 0.33)
        glutSolidCube(1)
        glPopMatrix()

        # perna inferior esquerda
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(0.75, 0.2, -0.5)
        glRotatef(-10, 1, 0, 0)
        glScalef(0.25, 1, 1)
        glutSolidCube(1)
        glPopMatrix()

        # perna inferior direita
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(-0.75, 0.2, -0.5)
        glRotatef(-10, 1, 0, 0)
        glScalef(0.25, 1, 1)
        glutSolidCube(1)
        glPopMatrix()

        # corpo
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(0, 0.5, 0)
        glRotatef(-10, 1, 0, 0)
        glScalef(1.25, 1, 2.33)
        glutSolidCube(1)
        glPopMatrix()

        # pe esquerdo
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(0.8, -0.5, -0.25)
        glRotatef(20, 1, 0, 0)
        glScalef(0.33, 0.33, 1.33)
        glutSolidCube(1)
        glPopMatrix()

        # pe direito
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_DIFFUSE, (GLfloat * 4)(1.0, 1.0, 1.0))
        glTranslatef(-0.8, -0.5, -0.25)
        glRotatef(20, 1, 0, 0)
        glScalef(0.33, 0.33, 1.33)
        glutSolidCube(1)
        glPopMatrix()

        glPopMatrix()

    def onReshape(self, width: int, height: int):
        # função para caso haja variação no tamanho da janela
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, float(width/height), 1, 100)

    # funcao para renderizar texto
    def renderText(self, text, x, y, red, green, blue):

        glDisable(GL_TEXTURE_2D)
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0.0, 1000, 0.0, 1000)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glPushMatrix()
        glColor3f(red, green, blue)
        glTranslatef(x, y, 0.0)
        glScalef(0.2, 0.5, 0.5)
        
        for ch in text:
            glutStrokeCharacter(GLUT_STROKE_ROMAN, ord(ch))
            glTranslatef(20, 0.0, 0.0)
        glPopMatrix()
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()    
        
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

class GameMenu:
    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.gameDisplay = pygame.display.set_mode((800, 800))
        pygame.display.set_caption('Projeto EA979')
        self.game = CrossTheStreet()
      
    def startMenu(self):
        mytheme = pygame_menu.themes.THEME_ORANGE.copy()

        # Estilizando o menu
        mytheme.title_background_color=(0, 0, 0, 0)
        mytheme.widget_font=pygame_menu.font.FONT_8BIT
        mytheme.title_bar_style=pygame_menu.widgets.MENUBAR_STYLE_TITLE_ONLY
        mytheme.title_font=pygame_menu.font.FONT_8BIT
        mytheme.title_font_color=(37, 207, 240)
        mytheme.widget_selection_effect=pygame_menu.widgets.LeftArrowSelection(arrow_size=(10, 15), arrow_right_margin=5, arrow_vertical_offset=0, blink_ms=0)
        mytheme.selection_color=(0, 0, 0)
        mytheme.widget_font_color=(37, 207, 240)
        mytheme.widget_font_size=40
        
        # criando o menu
        menu = pygame_menu.Menu(800, 800, 'Cross the Street', theme=mytheme)

        # adicionando botao 
        menu.add_button('Play', self.startGame)
        menu.add_selector('Character :', [('Chicken', 1), ('Bunny', 2)], onchange=self.game.selectCharacter)
        menu.add_vertical_margin(50)
        menu.add_button('Quit', pygame_menu.events.EXIT)

        menu.mainloop(self.gameDisplay) 
        
    def startGame(self):
        # fecha a janela do pygame para comecar o jogo
        pygame.quit()
        self.game.run()      

def main():
    menu = GameMenu()
    menu.startMenu()
    
if __name__ == '__main__':
    main()