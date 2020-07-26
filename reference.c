#include <GLUT/glut.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

// A estrutura de cada campo armazena informações se esse campo está void, se é
// uma floresta ou uma rua, caso a soma seja do tamanho de uma arvore e caso a
// rua seja a position de um carro

typedef struct field {
  char floresta_ou_rua;
  int empty;
  float car_position;
  int tree_height;
} field;
// O campo é composto por 400 campos e, a cada jump for frente, a primeira
// linha é excluída e uma nova é adicionada ao final do campo.
field all_fields[20][20];

#define TIMER_1_ID 0
#define TIMER_1_INTERVAL 10

#define TIMER_2_ID 0
#define TIMER_2_INTERVAL 1

#define TIMER_3_ID 0
#define TIMER_3_INTERVAL 10

#define pi 3.14159265358979323846

static void on_display();
static void on_keyboard(unsigned char key, int x, int y);
static void on_reshape(int w, int h);
/* Temporizador de partida do carro */
static void on_timer_1(int value);
/* Temporizador for pular animais */
static void on_timer_2(int value);
static void on_timer_3(int value);

void fields_initialization();
void arvore(int x, int z);
void soma();
void grama();
void rua();
void asfalto(int x, int z);
void animal();
void fita();
void carro(int x, int z);
void iluminacao();
void initialization();
void auxiliar_field();
void terreno();

/* O terreno começa em z = -12 */
int inicio_da_faixa_z;
/* Inicializamos os campos apenas uma vez, por isso coloquei essa variável */
int campos_estao_inicializados;
/* Ação de clique no teclado (pule for frente, for trás, esquerda, direita) */
char jump;
/* Também salvamos o jump anterior for saber como o animal gira */
char previous_jump;

/* Mantém informações sobre se um animal atingiu algo */
int animal_bateu_em_algo;
/* Mantém informações sobre se um carro atingiu um animal */
int carro_bateu_no_animal;
/* Variável for circulação de carros */
float t;

/* A animação for quando ocorre uma carro_bateu_no_animal ou impacto e é
 * interrompida no início */
int begin_animation;
int run_time_1;
int run_time_2;
int run_time_3;

/* Se voltarmos mais de três vezes seguidas à morte, devo acrescentar que o
 * animal é comido por uma águia se eu chegar */
int reverso;

float z_time;
/* Ângulo de rotação dos animais */
float alpha;

/* position atual do animal (terreno) */
float x_curr, y_curr, z_curr;
float x_previous, y_previous, z_previous;

int main(int argc, char **argv) {
  /* initialization GLUT */
  glutInit(&argc, argv);
  glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH);
  /* Criar janela */
  glutInitWindowSize(500, 500);
  glutInitWindowPosition(100, 100);
  glutCreateWindow("mi15054");
  /* Funções de retorno de chamada */
  glutDisplayFunc(on_display);
  glutKeyboardFunc(on_keyboard);
  glutReshapeFunc(on_reshape);
  initialization();
  /* Inicialize o OpenGl */
  glClearColor(1, 1, 1, 0);
  glEnable(GL_DEPTH_TEST);
  /* initialization do programa - loop infinito */
  glutMainLoop();
  return 0;
}

void initialization() {
  campos_estao_inicializados = 0;
  inicio_da_faixa_z = -12;
  alpha = 0;
  begin_animation = 1;
  run_time_1 = 0;
  run_time_2 = 0;
  run_time_3 = 0;
  jump = 'w';
  previous_jump = 'w';
  x_curr = 0;
  y_curr = 0.5;
  z_curr = 0;
  z_time = 0;
  animal_bateu_em_algo = 0;
  carro_bateu_no_animal = 0;
  reverso = 0;
  t = 0;
}

static void on_display() {
  /* Excluir conteúdo da janela anterior */
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
  /* Configuração da câmera */
  glMatrixMode(GL_MODELVIEW);
  glLoadIdentity();
  gluLookAt(1, 7 - y_curr, 3, 0, 0 - y_curr, -2, 0, 1, 0);
  if (campos_estao_inicializados == 0) {
    inicio_da_faixa_z = -12 - 3;
    fields_initialization();
    campos_estao_inicializados = 1;
    all_fields[10][-inicio_da_faixa_z].empty = 1;
  }
  iluminacao();
  // auxiliarry_field ();
  terreno();
  soma();
  rua();
  animal();
  if (run_time_3 == 0) {
    run_time_3 = 1;
    glutTimerFunc(TIMER_3_INTERVAL, on_timer_3, TIMER_3_ID);
  }
  glutSwapBuffers();
}

static void on_keyboard(unsigned char key, int x, int y) {
  previous_jump = jump;
  switch (key) {
  case 27:
    exit(0);
    break;
  case 'w':
    /* Ação pressionando a tecla 'w' */
    /* Se o campo na frente do animal estiver void, se a animação for iniciada e
     * se o timer for iniciado, o animal pula um campo for a frente */
    if (all_fields[(int)x_curr + 10][-inicio_da_faixa_z - 1].empty == 1 &&
        begin_animation == 1 && run_time_2 == 0) {
      alpha = 0;
      jump = 'w';
      run_time_2 = 1;
      z_previous = z_curr;
      glutTimerFunc(TIMER_2_INTERVAL, on_timer_2, TIMER_2_ID);
      reverso = 0;
      if (run_time_1 == 0) {
        run_time_1 = 1;
        glutTimerFunc(TIMER_1_INTERVAL, on_timer_1, TIMER_1_ID);
      }
    }
    /* Se o campo não estiver void, o animal atingirá um carro ou uma arvore
     * nesse campo */
    else if (begin_animation == 1 && run_time_2 == 0) {
      animal_bateu_em_algo = 1;
      begin_animation = 0;
      glutPostRedisplay();
    }
    break;
  case 'a':
    /* Ação pressionando a tecla 'a' */
    /* Se o campo na frente do animal estiver void, se a animação for iniciada
     * e se o cronômetro for iniciado, o animal pula um campo for a esquerda
     * e, se estiver ocupado, não haverá movimento */
    if (all_fields[(int)x_curr + 9][-inicio_da_faixa_z].empty == 1 &&
        begin_animation == 1 && run_time_2 == 0) {
      alpha = 0;
      jump = 'a';
      run_time_2 = 1;
      x_previous = x_curr;
      glutTimerFunc(TIMER_2_INTERVAL, on_timer_2, TIMER_2_ID);
      if (run_time_1 == 0) {
        run_time_1 = 1;
        glutTimerFunc(TIMER_1_INTERVAL, on_timer_1, TIMER_1_ID);
      }
    }
    break;
  case 'd':
    /* Ação pressionando a tecla 'd' */
    /* Se o campo na frente do animal estiver void, se a animação for iniciada
     * e se o cronômetro do animal for iniciado, um campo salta for a direita
     * e, se estiver ocupado, não haverá movimento */
    if (all_fields[(int)x_curr + 11][-inicio_da_faixa_z].empty == 1 &&
        begin_animation == 1 && run_time_2 == 0) {
      alpha = 0;
      jump = 'd';
      run_time_2 = 1;
      x_previous = x_curr;
      glutTimerFunc(TIMER_2_INTERVAL, on_timer_2, TIMER_2_ID);
      if (run_time_1 == 0) {
        run_time_1 = 1;
        glutTimerFunc(TIMER_1_INTERVAL, on_timer_1, TIMER_1_ID);
      }
    }
    break;
  case 's':
    /* Ação pressionando a tecla 's' /
    /* Se o campo na frente do animal estiver void, se a animação for iniciada e
    se o cronômetro do animal for iniciado, um campo pula for trás e, se
    estiver ocupado, não haverá movimento */
    if (all_fields[(int)x_curr + 10][-inicio_da_faixa_z + 1].empty == 1 &&
        begin_animation == 1 && run_time_2 == 0) {
      alpha = 0;
      jump = 's';
      run_time_2 = 1;
      z_previous = z_curr;
      glutTimerFunc(TIMER_2_INTERVAL, on_timer_2, TIMER_2_ID);
      reverso++;
      if (run_time_1 == 0) {
        run_time_1 = 1;
        glutTimerFunc(TIMER_1_INTERVAL, on_timer_1, TIMER_1_ID);
      }
    }
    break;
  case 'r':
    /* Ação pressionando a tecla 'r' */
    /* Defina variáveis ​​for os valuees iniciais */
    x_curr = 0;
    reverso = 0;
    y_curr = 0.5;
    z_curr = 0;
    z_time = 0;
    t = 0;
    jump = 'w';
    previous_jump = 'w';
    campos_estao_inicializados = 0;
    run_time_1 = 0;
    run_time_2 = 0;
    run_time_3 = 0;
    begin_animation = 1;
    animal_bateu_em_algo = 0;
    carro_bateu_no_animal = 0;
    alpha = 0;
    glutPostRedisplay();
    break;
  }
}

/* O terreno funciona como uma esteira transportadora */
void barra() {
  int i, j;
  /* Quando avançamos, todo o campo e todos os objetos (carros, soma)) são
   * convertidos for trás em um campo e um novo campo é criado no final do
   * campo e, primeiro, no início da estrada, ele é excluído */
  if (jump == 'w') {
    for (j = 18; j >= 0; j--) {
      for (i = 0; i < 20; i++) {
        all_fields[i][j + 1].empty = all_fields[i][j].empty;
        all_fields[i][j + 1].floresta_ou_rua = all_fields[i][j].floresta_ou_rua;
        all_fields[i][j + 1].car_position = all_fields[i][j].car_position;
        all_fields[i][j + 1].tree_height = all_fields[i][j].tree_height;
      }
    }

    for (j = 0; j < 20; j++) {
      all_fields[j][0].empty = 1;
      if (all_fields[j][1].floresta_ou_rua == 'u' &&
          all_fields[j][2].floresta_ou_rua == 'u') {
        all_fields[j][0].floresta_ou_rua = 's';
      } else {
        all_fields[j][0].floresta_ou_rua = 'u';
      }
    }
    for (i = 0; i < 20; i++) {
      if (rand() / (float)RAND_MAX > 0.7 &&
          all_fields[i][0].floresta_ou_rua == 's') {
        all_fields[i][0].tree_height = (int)ceil(rand() / (float)RAND_MAX * 3);
        all_fields[i][0].empty = 0;
      } else
        all_fields[i][0].empty = 1;

      all_fields[i][0].car_position =
          rand() / (float)RAND_MAX * 8 + 10 * i + 10 * t;
    }
  }
  /* Quando saltamos for trás, todo o campo e todos os objetos (carros,
   * soma)) são convertidos for frente em um campo */
  else if (jump == 's') {
    if (reverso > 3) {
      begin_animation = 0;
    }
    for (j = 1; j < 20; j++) {
      for (i = 0; i < 20; i++) {
        all_fields[i][j - 1].empty = all_fields[i][j].empty;
        all_fields[i][j - 1].floresta_ou_rua = all_fields[i][j].floresta_ou_rua;
        all_fields[i][j - 1].car_position = all_fields[i][j].car_position;
        all_fields[i][j - 1].tree_height = all_fields[i][j].tree_height;
      }
    }
  }
}

/* Configuração aleatória do tamanho da arvore e position do carro */
void fields_initialization() {
  int i, j;
  srand(time(NULL));
  for (i = 0; i < 20; i++) {
    for (j = 0; j < 20; j++) {
      if (j > 5) {
        all_fields[i][j].floresta_ou_rua = 's';
      } else if (j % 3 == 0) {
        all_fields[i][j].floresta_ou_rua = 's';
      } else {
        all_fields[i][j].floresta_ou_rua = 'u';
      }

      if (rand() / (float)RAND_MAX > 0.9 &&
          all_fields[i][j].floresta_ou_rua == 's') {
        all_fields[i][j].empty = 0;
        all_fields[i][j].tree_height = (int)ceil(rand() / (float)RAND_MAX * 3);
      } else {
        all_fields[i][j].empty = 1;
      }

      all_fields[i][j].car_position = rand() / (float)RAND_MAX * 8 + 10 * i;
    }
  }
}

/* Temporizador usado for mover o carro */
static void on_timer_1(int value) {
  if (TIMER_1_ID != value)
    return;
  t += 0.01;
  glutPostRedisplay();
  if (run_time_1 == 1) {
    glutTimerFunc(TIMER_1_INTERVAL, on_timer_1, TIMER_1_ID);
  }
}

/* Temporizador usado for jumps, cada jump é aproximado pela função sin de 0 a
 * pi */
static void on_timer_2(int value) {
  if (TIMER_2_ID != value)
    return;
  alpha += pi / 15;
  float aux1 = sin(alpha);
  float aux2 = sin(alpha - pi / 15);
  ;
  if (jump == 'w') {
    z_curr -= 1.0 / 15;
    y_curr += aux1 - aux2;
  } else if (jump == 'a') {
    x_curr -= 1.0 / 15;
    y_curr += aux1 - aux2;
  } else if (jump == 'd') {
    x_curr += 1.0 / 15;
    y_curr += aux1 - aux2;
  } else if (jump == 's') {
    z_curr += 1.0 / 15;
    y_curr += aux1 - aux2;
  }
  glutPostRedisplay();
  if (alpha < pi) {
    glutTimerFunc(TIMER_2_INTERVAL, on_timer_2, TIMER_2_ID);
  } else {
    y_curr = 0.5;
    if (jump == 'a')
      x_curr = x_previous - 1;
    else if (jump == 'd')
      x_curr = x_previous + 1;
    else if (jump == 'w') {
      fita();
      z_curr = 0;
    } else if (jump == 's') {
      fita();
      z_curr = 0;
    }
    run_time_2 = 0;
  }
}

/* Temporizador que move a câmera for a frente for solicitar ao player que
 * pule por um certo período de tempo */
/* Não tive tempo de configurar */
static void on_timer_3(int value) {
  if (TIMER_3_ID != value)
    return;
  z_time += 0.01;
  glutPostRedisplay();
  if (run_time_3 == 1) {
    glutTimerFunc(TIMER_3_INTERVAL, on_timer_3, TIMER_3_ID);
  } else {
    run_time_3 = 0;
  }
}

void auxiliar_field() {
  glPushMatrix();
  int i, j;
  glTranslatef(-x_curr, -y_curr, -z_curr);
  glTranslatef(0, 0, -3);
  glColor3f(1, 0, 0);
  for (i = 0; i < 20; i++) {
    for (j = 0; j < 20; j++) {
      glBegin(GL_LINE_LOOP);
      glVertex3f(i - 10 - 0.5, 0, j - 12 + 0.5);
      glVertex3f(i - 10 - 0.5, 0, j - 12 - 0.5);
      glVertex3f(i - 10 + 0.5, 0, j - 12 - 0.5);
      glVertex3f(i - 10 + 0.5, 0, j - 12 + 0.5);
      glEnd();
    }
  }
  glPopMatrix();
}

/* Definir a iluminacao */
void iluminacao() {
  glEnable(GL_LIGHTING);
  glEnable(GL_LIGHT0);
  GLfloat position[] = {7, 7, 7, 0};
  GLfloat ambiente[] = {0.1, 0.1, 0.1, 1};
  GLfloat diffuse[] = {0.7, 0.7, 0.7, 1};
  GLfloat specular[] = {0.9, 0.9, 0.9, 1};
  glLightfv(GL_LIGHT0, GL_POSITION, position);
  glLightfv(GL_LIGHT0, GL_AMBIENT, ambiente);
  glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse);
  glLightfv(GL_LIGHT0, GL_SPECULAR, specular);
}

/* Desenhando a soma, se o campo i, j estiver ocupado na estrutura e se for a
 * soma em i, j, a arvore for desenhada */
void soma() {
  glPushMatrix();
  glTranslatef(-x_curr, -y_curr, -z_curr);
  int i, j;
  for (i = 0; i < 20; i++) {
    for (j = 0; j < 20; j++) {
      if (all_fields[i][j].empty == 0 &&
          all_fields[i][j].floresta_ou_rua == 's')
        arvore(i - 10, inicio_da_faixa_z + j);
    }
  }

  for (j = 0; j < 20; j++) {
    if (all_fields[0 + 1][j].floresta_ou_rua == 's')
      arvore(0 - 10 - 1, inicio_da_faixa_z + j);
  }

  for (j = 0; j < 20; j++) {
    if (all_fields[20 - 1][j].floresta_ou_rua == 's')
      arvore(20 - 10, inicio_da_faixa_z + j);
  }
  glPopMatrix();
}
/* Desenho de arvore */
void arvore(int x, int z) {
  GLfloat ambiente[] = {0.1, 0.1, 0.1, 1};
  GLfloat specular[] = {0.1, 0.1, 0.1, 1};
  GLfloat brilho[] = {0};
  glMaterialfv(GL_FRONT, GL_AMBIENT, ambiente);
  glMaterialfv(GL_FRONT, GL_SPECULAR, specular);
  glMaterialfv(GL_FRONT, GL_SHININESS, brilho);
  // Krosnja
  glPushMatrix();
  glTranslatef(x, 0, z);
  glScalef(0.8, 0.8, 0.8);
  int i;
  int aux = (x > -11 && x < 10)
                ? all_fields[x + 10][z - inicio_da_faixa_z].tree_height
                : 3;

  for (i = 0; i < aux; i++) {
    glColor3f(51.0 / 256, 102.0 / 256, 0);
    glMaterialfv(GL_FRONT, GL_DIFFUSE,
                 (float[4]){51.0 / 256, 102.0 / 256, 0, 0});
    glPushMatrix();
    glTranslatef(0, 0.5 + 0.2 + 0.6 + i * 0.7, 0);
    glScalef(1, 0.2, 1);
    glutSolidCube(1);
    glPopMatrix();

    glColor3f(76.0 / 256, 153.0 / 256, 0);
    glMaterialfv(GL_FRONT, GL_DIFFUSE,
                 (float[4]){76.0 / 256, 153.0 / 256, 0, 0});
    glPushMatrix();
    glTranslatef(0, 0.5 + 0.2 + 0.25 + i * 0.7, 0);
    glScalef(1, 0.5, 1);
    glutSolidCube(1);
    glPopMatrix();
  }

  glColor3f(51.0 / 256, 102.0 / 256, 0);
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){51.0 / 256, 102.0 / 256, 0.0});
  glPushMatrix();
  glTranslatef(0, 0.5 + 0.1, 0);
  glScalef(1, 0.2, 1);
  glutSolidCube(1);
  glPopMatrix();

  // arvore
  glColor3f(51.0 / 256, 25.0 / 256, 0);
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){51.0 / 256, 25.0 / 256, 0.0});
  glPushMatrix();
  glScalef(0.5, 1, 0.5);
  glutSolidCube(1);
  glPopMatrix();
  glPopMatrix();
}

/* Desenho de grama (não sei por que chamei a função terreno), se i, j campo
 * não é uma rua, grama é desenhada */
void terreno() {
  glPushMatrix();
  glTranslatef(-x_curr, -y_curr, -z_curr);
  int i, j;
  for (i = 0; i < 20; i++) {
    for (j = 0; j < 20; j++) {
      if (all_fields[i][j].floresta_ou_rua != 'u')
        grama(i, j);
    }
  }
  for (i = -10; i < 0; i++) {
    for (j = 0; j < 20; j++) {
      if (all_fields[i + 15][j].floresta_ou_rua != 'u')
        grama(i, j);
    }
  }
  for (i = 20; i < 30; i++) {
    for (j = 0; j < 20; j++) {
      if (all_fields[i - 15][j].floresta_ou_rua != 'u')
        grama(i, j);
    }
  }
  glPopMatrix();
}

/* Desenho de grama */
void grama(int x, int z) {

  glPushMatrix();
  glTranslatef(0, 0, -3);
  glDisable(GL_LIGHTING);
  if (x % 2 == 1)
    glColor3f(178.0 / 256, 255.0 / 256, 102.0 / 256);
  else
    glColor3f(166.0 / 256, 245.0 / 256, 92.0 / 256);

  glBegin(GL_QUADS);
  glVertex3f(x - 10 - 0.5, 0, z - 12 + 0.5);
  glVertex3f(x - 10 - 0.5, 0, z - 12 - 0.5);
  glVertex3f(x - 10 + 0.5, 0, z - 12 - 0.5);
  glVertex3f(x - 10 + 0.5, 0, z - 12 + 0.5);
  glEnd();
  glEnable(GL_LIGHTING);
  glPopMatrix();
}

/* Se i, j é um campo de rua, o asfalto é desenhado */
void rua() {
  glPushMatrix();
  glTranslatef(-x_curr, -y_curr, -z_curr);
  int i, j;
  for (i = 0; i < 20; i++) {
    for (j = 0; j < 20; j++) {
      if (all_fields[i][j].floresta_ou_rua == 'u')
        asfalto(i, j);
    }
  }
  for (i = -10; i < 0; i++) {
    for (j = 0; j < 20; j++) {
      if (all_fields[i + 15][j].floresta_ou_rua == 'u')
        asfalto(i, j);
    }
  }
  for (i = 20; i < 30; i++) {
    for (j = 0; j < 20; j++) {
      if (all_fields[i - 15][j].floresta_ou_rua == 'u')
        asfalto(i, j);
    }
  }
  for (i = 0; i < 20; i++) {
    for (j = 0; j < 20; j++) {
      if (all_fields[i][j].floresta_ou_rua == 'u')
        carro(all_fields[i][j].car_position, j);
    }
  }
  glPopMatrix();
}

/* Desenhando um carro */
void carro(int x, int z) {
  glPushMatrix();
  glColor3f(1, 1, 0);
  glTranslatef(-10 + t * 10 - x, 0.3, z + inicio_da_faixa_z);
  // Gume i ratkapne
  // Prednja desna
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.1, 0.1, 0.1, 0});
  glPushMatrix();
  glTranslatef(0.45, -0.1, 0.4);
  glScalef(1, 1, 0.5);
  glutSolidCube(0.35);
  glPopMatrix();

  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.2, 0.2, 0.2, 0});
  glPushMatrix();
  glTranslatef(0.45, -0.1, 0.45);
  glScalef(0.5, 0.5, 0.25);
  glutSolidCube(0.35);
  glPopMatrix();
  // Zadnja desna
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.1, 0.1, 0.1, 0});
  glPushMatrix();
  glTranslatef(-0.45, -0.1, 0.4);
  glScalef(1, 1, 0.5);
  glutSolidCube(0.35);
  glPopMatrix();

  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.2, 0.2, 0.2, 0});
  glPushMatrix();
  glTranslatef(-0.45, -0.1, 0.45);
  glScalef(0.5, 0.5, 0.25);
  glutSolidCube(0.35);
  glPopMatrix();
  // Zadnja leva
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.1, 0.1, 0.1, 0});
  glPushMatrix();
  glTranslatef(-0.45, -0.1, -0.4);
  glScalef(1, 1, 0.5);
  glutSolidCube(0.35);
  glPopMatrix();

  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.2, 0.2, 0.2, 0});
  glPushMatrix();
  glTranslatef(-0.45, -0.1, -0.45);
  glScalef(0.5, 0.5, 0.25);
  glutSolidCube(0.35);
  glPopMatrix();
  // Prednja leva
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.1, 0.1, 0.1, 0});
  glPushMatrix();
  glTranslatef(0.45, -0.1, -0.4);
  glScalef(1, 1, 0.5);
  glutSolidCube(0.35);
  glPopMatrix();

  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.2, 0.2, 0.2, 0});
  glPushMatrix();
  glTranslatef(0.45, -0.1, -0.45);
  glScalef(0.5, 0.5, 0.25);
  glutSolidCube(0.35);
  glPopMatrix();

  // Gornji deo
  // Konstrukcija
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.9, 0.9, 0.9, 0});
  glPushMatrix();
  glTranslatef(-0.1, 0.4, 0);
  glScalef(1.1, 0.5, 0.9);
  glutSolidCube(0.8);
  glPopMatrix();
  // Prednje staklo
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0, 0, 0, 0});
  glPushMatrix();
  glTranslatef(-0.09, 0.4, 0);
  glScalef(1.1, 0.3, 0.89);
  glutSolidCube(0.8);
  glPopMatrix();
  // Prozori prednji
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0, 0, 0, 0});
  glPushMatrix();
  glTranslatef(0.1, 0.4, 0);
  glScalef(0.5, 0.3, 0.91);
  glutSolidCube(0.8);
  glPopMatrix();
  // Prozori zadnji
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0, 0, 0, 0});
  glPushMatrix();
  glTranslatef(-0.35, 0.4, 0);
  glScalef(0.3, 0.3, 0.91);
  glutSolidCube(0.8);
  glPopMatrix();

  // Donji deo

  // Farovi
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.1, 0.1, 0.1, 0});

  // Levi far
  glPushMatrix();
  glTranslatef(0.75, 0.05, -0.2);
  glScalef(0.2, 0.15, 0.2);
  glutSolidCube(0.8);
  glPopMatrix();

  // Desni far
  glPushMatrix();
  glTranslatef(0.75, 0.05, 0.2);
  glScalef(0.2, 0.15, 0.2);
  glutSolidCube(0.8);
  glPopMatrix();

  if (x % 7 == 0)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){204.0 / 256, 0, 0, 0});
  else if (x % 7 == 1)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){1, 1, 0, 0});
  else if (x % 7 == 2)
    glMaterialfv(GL_FRONT, GL_DIFFUSE,
                 (float[4]){0, 76.0 / 256, 153.0 / 256, 0});
  else if (x % 7 == 3)
    glMaterialfv(GL_FRONT, GL_DIFFUSE,
                 (float[4]){204.0 / 256, 0, 102.0 / 256, 0});
  else if (x % 7 == 4)
    glMaterialfv(GL_FRONT, GL_DIFFUSE,
                 (float[4]){0, 153.0 / 256, 153.0 / 256, 0});
  else if (x % 7 == 5)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){0.2, 0.2, 0.2, 0});
  else if (x % 7 == 6)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){1, 1, 1, 0});

  // Retrovizori
  glPushMatrix();
  glTranslatef(0.2, 0.13, 0);
  glScalef(0.2, 0.15, 1.2);
  glutSolidCube(0.8);
  glPopMatrix();

  // Donja konstrukcija
  glPushMatrix();
  glScalef(2, 0.5, 1);
  glutSolidCube(0.8);
  glPopMatrix();
  glPopMatrix();

  int position = (int)ceil(t * 10 - x);
  if (position == 0 || position == 1) {
    all_fields[position][z].empty = 0;
  }
  if (position > 1 && position < 19) {
    all_fields[position][z].empty = 0;
    all_fields[position - 1][z].empty = 0;
    all_fields[position - 2][z].empty = 1;
    all_fields[position + 1][z].empty = 1;
  }
  if (position == 19) {
    all_fields[position][z].empty = 0;
    all_fields[position - 2][z].empty = 1;
  }
  if (position == 20) {
    all_fields[position - 2][z].empty = 1;
  }
  if (position == 21) {
    all_fields[position - 2][z].empty = 1;
  }
  if (position - 10 == x_curr && z + inicio_da_faixa_z == 0) {
    carro_bateu_no_animal = 1;
  }
}

/* Desenho de estrada, asfalto */
void asfalto(int x, int z) {
  glDisable(GL_LIGHTING);
  glPushMatrix();
  glTranslatef(0, 0, -3);
  if ((x >= 0 && x < 20 && all_fields[x][z + 1].floresta_ou_rua == 'u' &&
       x % 2 == 1) ||
      (x < 0 && all_fields[x + 15][z + 1].floresta_ou_rua == 'u' &&
       abs(x) % 2 == 1) ||
      (x >= 20 && all_fields[x - 15][z + 1].floresta_ou_rua == 'u' &&
       x % 2 == 1)) {
    glColor3f(1, 1, 1);
    GLfloat ambiente[] = {0.1, 0.1, 0.1, 1};
    GLfloat specular[] = {0.1, 0.1, 0.1, 1};
    GLfloat brilho[] = {0};

    glMaterialfv(GL_FRONT, GL_AMBIENT, ambiente);
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular);
    glMaterialfv(GL_FRONT, GL_SHININESS, brilho);

    glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){1, 1, 1, 0});

    glBegin(GL_QUADS);
    glVertex3f(x - 10 - 0.5, 0.0001, z - 12 + 0.55);
    glVertex3f(x - 10 - 0.5, 0.0001, z - 12 + 0.45);
    glVertex3f(x - 10 + 0.5, 0.0001, z - 12 + 0.45);
    glVertex3f(x - 10 + 0.5, 0.0001, z - 12 + 0.55);
    glEnd();
  }

  glPopMatrix();

  glPushMatrix();
  glTranslatef(0, 0, -3);
  glColor3f(64.0 / 256, 64.0 / 256, 64.0 / 256);

  glBegin(GL_QUADS);
  glVertex3f(x - 10 - 0.5, 0, z - 12 + 0.5);
  glVertex3f(x - 10 - 0.5, 0, z - 12 - 0.5);
  glVertex3f(x - 10 + 0.5, 0, z - 12 - 0.5);
  glVertex3f(x - 10 + 0.5, 0, z - 12 + 0.5);
  glEnd();
  glPopMatrix();

  glEnable(GL_LIGHTING);
}

/* Ação for alterar o tamanho da janela */
static void on_reshape(int w, int h) {
  glViewport(0, 0, w, h);
  glMatrixMode(GL_PROJECTION);
  glLoadIdentity();
  gluPerspective(60, (float)w / h, 1, 100);
}

/* Desenhando um animal */

void animal() {
  glPushMatrix();
  /* Quando o impacto é 1, o animal bate em uma arvore ou carro e deve ser
   * achatado (por z) */
  if (animal_bateu_em_algo == 1) {
    run_time_1 = 0;
    glTranslatef(0, 0, -0.5);
    glScalef(1, 1, 0.2);
    if (previous_jump == 'a') {
      glRotatef(70, 0, 1, 0);
    }
    if (previous_jump == 'd') {
      glRotatef(-70, 0, 1, 0);
    }
  }

  /* Na carro_bateu_no_animal 1, o animal foi atropelado por um carro e deve
   * ser achatado (por ano) */
  if (carro_bateu_no_animal == 1) {
    begin_animation = 0;
    run_time_1 = 0;
    glTranslatef(0, 0, 0);
    glScalef(1, 0.2, 1);
  }

  /* Rotações de animais ao pular */
  if (jump == 'a' && previous_jump == 'a')
    glRotatef(-90, 0, 1, 0);
  else if (jump == 'a' && previous_jump == 'd')
    glRotatef(90 + alpha * 180 / pi, 0, 1, 0);
  else if (jump == 'a' && previous_jump == 'w')
    glRotatef(180 + alpha * 90 / pi, 0, 1, 0);
  else if (jump == 'a' && previous_jump == 's')
    glRotatef(0 - alpha * 90 / pi, 0, 1, 0);
  else if (jump == 'd' && previous_jump == 'd')
    glRotatef(90, 0, 1, 0);
  else if (jump == 'd' && previous_jump == 'w')
    glRotatef(180 - alpha * 90 / pi, 0, 1, 0);
  else if (jump == 'd' && previous_jump == 'a')
    glRotatef(-90 - alpha * 180 / pi, 0, 1, 0);
  else if (jump == 'd' && previous_jump == 's')
    glRotatef(0 + alpha * 90 / pi, 0, 1, 0);
  else if (jump == 'w' && previous_jump == 'd')
    glRotatef(90 + alpha * 90 / pi, 0, 1, 0);
  else if (jump == 'w' && previous_jump == 'w')
    glRotatef(180, 0, 1, 0);
  else if (jump == 'w' && previous_jump == 's')
    glRotatef(0 - alpha * 180 / pi, 0, 1, 0);
  else if (jump == 'w' && previous_jump == 'a')
    glRotatef(-90 - alpha * 90 / pi, 0, 1, 0);
  else if (jump == 's' && previous_jump == 'a')
    glRotatef(-90 + alpha * 90 / pi, 0, 1, 0);
  else if (jump == 's' && previous_jump == 'd')
    glRotatef(90 - alpha * 90 / pi, 0, 1, 0);
  else if (jump == 's' && previous_jump == 's')
    glRotatef(0, 0, 1, 0);
  else if (jump == 's' && previous_jump == 'w')
    glRotatef(180 + alpha * 180 / pi, 0, 1, 0);

  glScalef(0.3, 0.3, 0.3);

  /* Ajuste de material animal */
  GLfloat ambiente[] = {0.1, 0.1, 0.1, 1};
  GLfloat specular[] = {0.1, 0.1, 0.1, 1};
  GLfloat brilho[] = {0};
  glMaterialfv(GL_FRONT, GL_AMBIENT, ambiente);
  glMaterialfv(GL_FRONT, GL_SPECULAR, specular);
  glMaterialfv(GL_FRONT, GL_SHININESS, brilho);
  glColor3f(0, 0, 0);
  glMaterialfv(GL_FRONT, GL_DIFFUSE, (float[4]){1, 1, 1, 0});

  /* Desenhando um animal */

  /* rabo */
  glPushMatrix();
  glTranslatef(0, 0.5, -1.5);
  glRotatef(-20, 1, 0, 0);
  glutSolidSphere(0.5, 50, 50);
  glPopMatrix();

  /* orelha esquerda */
  glPushMatrix();
  glTranslatef(0.35, 1.66, 1);
  glRotatef(-20, 1, 0, 0);
  glScalef(0.33, 1, 0.33);
  glutSolidCube(1);
  glPopMatrix();

  /* orelha direita */
  glPushMatrix();
  glTranslatef(-0.35, 1.66, 1);
  glRotatef(-20, 1, 0, 0);
  glScalef(0.33, 1, 0.33);
  glutSolidCube(1);
  glPopMatrix();

  /* cabeça */
  glPushMatrix();
  glTranslatef(0, 0.66, 1.5);
  glRotatef(15, 1, 0, 0);
  glutSolidCube(1);
  glPopMatrix();

  /* perna esquerda dianteira */
  glPushMatrix();
  glTranslatef(0.5, -0.25, 1);
  glRotatef(-10, 1, 0, 0);
  glScalef(0.33, 0.85, 0.33);
  glutSolidCube(1);
  glPopMatrix();

  /* perna dianteira direita */
  glPushMatrix();
  glTranslatef(-0.5, -0.25, 1);
  glRotatef(-10, 1, 0, 0);
  glScalef(0.33, 0.85, 0.33);
  glutSolidCube(1);
  glPopMatrix();

  /* perna esquerda traseira */
  glPushMatrix();
  glTranslatef(0.75, 0.2, -0.5);
  glRotatef(-10, 1, 0, 0);
  glScalef(0.25, 1, 1);
  glutSolidCube(1);
  glPopMatrix();

  /* perna direita traseira */
  glPushMatrix();
  glTranslatef(-0.75, 0.2, -0.5);
  glRotatef(-10, 1, 0, 0);
  glScalef(0.25, 1, 1);
  glutSolidCube(1);
  glPopMatrix();

  /* corpo */
  glPushMatrix();
  glTranslatef(0, 0.5, 0);
  glRotatef(-10, 1, 0, 0);
  glScalef(1.25, 1, 2.33);
  glutSolidCube(1);
  glPopMatrix();

  /* pé esquerdo traseiro */
  glPushMatrix();
  glTranslatef(0.8, -0.5, -0.25);
  glRotatef(20, 1, 0, 0);
  glScalef(0.33, 0.33, 1.33);
  glutSolidCube(1);
  glPopMatrix();

  /* pé direito traseiro */
  glPushMatrix();
  glTranslatef(-0.8, -0.5, -0.25);
  glRotatef(20, 1, 0, 0);
  glScalef(0.33, 0.33, 1.33);
  glutSolidCube(1);
  glPopMatrix();

  glPopMatrix();
}