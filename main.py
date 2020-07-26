import glm
import numpy as np
import OpenGL.GL as gl
from PyQt5 import QtOpenGL
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from renderers.ModelRenderer_v1 import ModelRenderer
from shader_programs.SimpleShaderProgram_v1 import SimpleShaderProgram


class CrossTheStreetGame(QtOpenGL.QGLWidget):
    def initializeGL(self):
        # posição de cada vértice dos triângulos
        vertex_position = np.array([
            -0.90, -0.90, 0.0, 1.0,  # Triângulo 1
            0.85, -0.90, 0.0, 1.0,
            -0.90,  0.85, 0.0, 1.0,
            0.90, -0.85, 0.0, 1.0,  # Triângulo 2
            0.90,  0.90, 0.0, 1.0,
            -0.85,  0.90, 0.0, 1.0],
            dtype=np.float32)
        # cor de cada vértice dos triângulos
        vertex_color = np.array([
            1.0, 0.0, 0.0, 1.0,  # Triângulo 1
            0.0, 1.0, 0.0, 1.0,
            0.0, 0.0, 1.0, 1.0,
            1.0, 0.0, 0.0, 1.0,  # Triângulo 2
            0.0, 1.0, 0.0, 1.0,
            0.0, 0.0, 1.0, 1.0],
            dtype=np.float32)
        # cria um objeto responsável por carregar os dados para a GPU e renderizá-los
        self.triangleRenderer = ModelRenderer(
            vertex_position, vertex_color=vertex_color)
        # cria um shader program simples
        self.shaderProgram = SimpleShaderProgram()
        # recupera os endereços das variáveis de entrada do shader program
        position_loc = self.shaderProgram.getVertexPositionLoc()
        color_loc = self.shaderProgram.getVertexColorLoc()
        # configura os dados do modelo para serem os dados de entrada do shader program
        self.triangleRenderer.setVertexPositionLoc(position_loc)
        self.triangleRenderer.setVertexColorLoc(color_loc)

    def paintGL(self):
        # configura a cor de background
        gl.glClearColor(0, 0, 0, 1)
        # limpa o background com a cor especificada
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # ativa o shader program que será executado pela GPU
        self.shaderProgram.bind()
        # inicia a renderização dos triângulos
        self.triangleRenderer.render()
        # desativa o shader program
        self.shaderProgram.release()
        # solicita que o método paintGL seja chamado novamente
        self.update()

    def resizeGL(self, width, height):
        gl.glViewport(0, 0, width, height)

    def keyPressEvent(self, event):
        super(Parte1, self).keyPressEvent(event)
        # step = 0.1
        # if event.key() == QtCore.Qt.Key_Left:
        #     self.lightPosition[0] -= step


def main():
    import sys
    # creates Qt app
    app = QCoreApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    # specifies OpenGL context
    glformat = QtOpenGL.QGLFormat()
    glformat.setVersion(3, 3)
    glformat.setDoubleBuffer(True)
    glformat.setProfile(QtOpenGL.QGLFormat.CoreProfile)
    # creates rendering window
    w = CrossTheStreetGame(glformat)
    w.resize(1000, 1000)
    w.setWindowTitle('Cross the street')
    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
