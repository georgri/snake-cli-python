

import time

import sys
import select
import termios
import os

from random import randrange

FIELD_X = 50
FIELD_Y = 20
field = [[' '] * FIELD_X for i in range(FIELD_Y)]

class KeyPoller():
    def __enter__(self):
        # Save the terminal settings
        self.fd = sys.stdin.fileno()
        self.new_term = termios.tcgetattr(self.fd)
        self.old_term = termios.tcgetattr(self.fd)

        # New terminal setting unbuffered
        self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

        self.queue = []

        return self

    def __exit__(self, type, value, traceback):
        termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def buffer(self):
        dr,dw,de = select.select([sys.stdin], [], [], 0)
        if not dr == []:
            self.queue.append(sys.stdin.read(1))


    def poll(self):
        if self.queue:
            return self.queue.pop(0)
        return None




def draw(field, snake, bait):

    field = [[' '] * FIELD_X for i in range(FIELD_Y)]
    x,y = snake[0]
    field[x][y] = 'S'
    for x,y in snake[1:]:
        field[x][y] = 'O'

    x,y = bait
    field[x][y] = 'X'

    # add boundaries
    field.insert(0, ['='] * len(field[0]))
    field.append(['='] * len(field[0]))
    for line in field:
        line.insert(0, '|')
        line.append('|')

    for line in field:
        print(''.join(line))


        
def check_boundaries(field, snake):
    head = snake[0]
    if head[0] < 0 or head[0] >= len(field):
        return False
    if head[1] < 0 or head[1] >= len(field[0]):
        return False
    if head in snake[1:]:
        return False
    return True
    

def move(snake, direction, bait):
    vectors = [(0,1), (1, 0), (0, -1), (-1, 0)]
    vector = vectors[direction]
    new_head = (snake[0][0] + vector[0], snake[0][1] + vector[1])
    snake.insert(0, new_head)
    if new_head != bait:
        snake.pop()
    

def check_bait(field, snake, bait):

    # WTF???
    if len(snake) >= len(field) * len(field[0]):
        return (-1,-1)

    while bait in snake:
        # generate new random bait
        bait = (randrange(len(field)), randrange(len(field[0])))
    return bait
        



def handle_key_press(c):
    global direction
    c = c.lower()
    if c == 'd': # right
        if direction in (0,2):
            return False
        direction = 0
        return True
    elif c == 's': # down
        if direction in (1,3):
            return False
        direction = 1
        return True
    elif c == 'a': # left
        if direction in (0,2):
            return False
        direction = 2
        return True
    elif c == 'w': # up
        if direction in (1,3):
            return False
        direction = 3
        return True

    return False

    


# head first!
snake = [(1,0), (0,0)]

# 0 - right, 1 - down, 2 - left, 3 - up
direction = 0

bait = (8,8)

counter = 0
with KeyPoller() as keyPoller:
    while True:
        counter += 1

        for i in range(20):
            keyPoller.buffer()
            time.sleep(0.01)

        
        c = keyPoller.poll()
        while not c is None:
            if handle_key_press(c):
                print (c)
                break
            c = keyPoller.poll()

        move(snake, direction, bait)
        bait = check_bait(field, snake, bait)
        print("Snake head: {}, bait: {}". format(snake[0], bait))
        
        if not check_boundaries(field, snake):
            print("===== GAME OVER! =====")
            exit(0)

        draw(field, snake, bait)


        print("SCORE: {}".format((len(snake) - 2) * 10))
