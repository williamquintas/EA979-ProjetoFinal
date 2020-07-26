from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def onDisplay():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glutSwapBuffers()


def onKeyboard():
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
    # gameInitialization()
    # Initializes OpenGL
    glClearColor(1, 1, 1, 0)
    glEnable(GL_DEPTH_TEST)
    # Program infinite loop
    glutMainLoop()


if __name__ == '__main__':
    main()
