

import time

import sys
import select
import termios
import os

from random import randrange

FRAME_DELAY = 0.5

FIELD_X = 10
FIELD_Y = 5
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




def draw(field, snake, bait, failed = False, last_chance = True):

    canvas = [[' '] * len(field[0]) for i in range(len(field))]

    # draw head
    if not failed:
        x,y = snake[0]
        canvas[x][y] = 'S'
    
    # draw tail
    for x,y in snake[1:]:
        canvas[x][y] = 'O'

    # draw bait
    x,y = bait
    canvas[x][y] = 'X'

    # add boundaries
    canvas.append(['='] * len(field[0]))
    canvas.insert(0, ['='] * len(field[0]))
    for line in canvas:
        line.append('|')
        line.insert(0, '|')


    # draw a snake head smashed into a wall or itself :)
    if failed:
        x,y = snake[0]
        canvas[x+1][y+1] = '?' if last_chance else 'Ж'
        

    print("Snake head: {}, bait: {}". format(snake[0], bait))
    for line in canvas:
        print(''.join(line))
    print("SCORE: {}".format((len(snake) - 2) * 10))



        
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

    snake_moved = snake[:]
    snake_moved.insert(0, new_head)
    if new_head != bait:
        snake_moved.pop()

    return snake_moved
    

def place_bait(field, snake, bait):

    while bait in snake:
        # generate new random bait
        bait = (randrange(len(field)), randrange(len(field[0])))
    return bait
        

def check_win_condition(field, snake):

    # WTF??? Who is capable of that?
    return len(snake) >= len(field) * len(field[0])


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

bait = (0,0)
bait = place_bait(field, snake, bait)

counter = 0
with KeyPoller() as keyPoller:
    while True:
        counter += 1

        for i in range(int(FRAME_DELAY / 0.01)):
            time.sleep(0.01)
            keyPoller.buffer()

        
        c = keyPoller.poll()
        while not c is None:
            if handle_key_press(c):
                print (c)
                break
            c = keyPoller.poll()

        snake_moved = move(snake, direction, bait)
        if not check_boundaries(field, snake_moved):

            if last_chance:
                draw(field, snake, bait, failed = True, last_chance = last_chance)
                last_chance = False
                continue

            draw(field, snake_moved, bait, failed = True, last_chance = last_chance)

            print("===== GAME OVER! =====")
            exit(0)

        snake = snake_moved
        last_chance = True

        if check_win_condition(field, snake):
            print("======= YOU WIN! ======= ")
            print("======= I admire your resolve, sir! ======")
            exit(0)

        bait = place_bait(field, snake, bait)
        

        draw(field, snake, bait)


