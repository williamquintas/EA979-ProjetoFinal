PROGRAM = crossy_road
CC      = gcc
CFLAGS  = -g -std=c99 -Wall -I/usr/X11R6/include -I/usr/pkg/include 
LDFLAGS = -framework GLUT -framework OpenGL -framework Cocoa
# LDLIBS  = -lglut -lGLU -lGL -lm

$(PROGRAM): reference.o
	$(CC) $(LDFLAGS) -o $(PROGRAM) reference.o $(LDLIBS)
	
reference.o: reference.c
	gcc -c reference.c

.PHONY: clean dist

clean:
	-rm *.o $(PROGRAM) *core

dist: clean
	-tar -chvj -C .. -f ../$(PROGRAM).tar.bz2 $(PROGRAM)
