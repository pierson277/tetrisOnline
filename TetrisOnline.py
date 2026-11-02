#Tetris Online
#imports
import pygame
import random
import sys
pygame.init()

#constant variables
width, height = 300, 500
fps = 60
cell = 20
rows = (height - 120) // cell
cols = width // cell

#game settings
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
pygame.display.set_caption("Tetris Online")

#colors
black = (0, 0, 0)
white = (255, 255, 255)
bgColor = (30, 30, 76)
grid = (30, 30, 132)
win = (50, 230, 50)
lose = (250, 90, 120)

#load / store assets
assets = {
    1: pygame.image.load("C:\\Code\\Python\\assets\\1.png"),
    2: pygame.image.load("C:\\Code\\Python\\assets\\2.png"),
    3: pygame.image.load("C:\\Code\\Python\\assets\\3.png"),
    4: pygame.image.load("C:\\Code\\Python\\assets\\4.png")
}

#fonts
font1 = pygame.font.SysFont("verdana",50)
font2 = pygame.font.SysFont("verdana",15)

#shape class
class Shape:
    version = {
        'I': [[1, 5, 9, 13], [4, 5, 6, 7]],
        'Z': [[4, 5, 9, 10], [2, 6, 5, 9]],
        'S': [[6, 7, 9, 10], [1, 5, 6, 10]],
        'L': [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        'J': [[1, 2, 6, 10], [5, 6, 7, 3], [2, 6, 10, 11], [3, 5, 6, 7]],
        'T': [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        'O': [[1, 2, 5, 6]]
    }
    shapes = ['I', 'Z', 'S', 'L', 'J', 'T', 'O']


    #constructor
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.choice(self.shapes)
        self.shape = self.version[self.type]
        self.color = random.randint(1,4)
        self.orientation = 0

    #image ~ version of shape
    def image(self):
        return self.shape[self.orientation]

    #rotation
    def rotate(self):
        self.orientation = (self.orientation + 1) % len(self.shape)


#game class
class Tetris:
    #constructor
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.score = 0
        self.level = 0
        self.grid =[[0 for j in range(cols)] for i in range(rows)]
        self.next = None
        self.end = False
        self.newShape()

    #make grid
    def makeGrid(self):
        for i in range(self.rows+1):
            pygame.draw.line(screen, grid, (0, i*cell), (width, i*cell))
        for j in range(self.cols+1):
            pygame.draw.line(screen, grid, (j*cell, 0), (j*cell, height-120))

    #make new shape
    def newShape(self):
        if not self.next:
            self.next = Shape(5, 0)
        self.figure = self.next
        self.next = Shape(5, 0)


    #collison
    def collision(self):
        for i in range(4):
            for j in range(4):
                if (i*4 +j) in self.figure.image():
                    blockRow = i + self.figure.y
                    blockCol = j + self.figure.x
                    if(blockRow >= self.rows or blockCol >= self.cols or blockRow < 0 or self.grid[blockRow][blockCol] > 0): return True

    #remove row

    #move down

    #move left

    #move right






#main game loop
def main():
    tetris = Tetris(rows, cols)
    run = True
    while run:
        screen.fill(bgColor)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()


        tetris.makeGrid()

        #show shape on game screen
        for i in range(rows):
            for j in range(cols):
                if (i *4 + j) in tetris.figure.image():
                    shape = assets[tetris.figure.color]
                    x = cell * (tetris.figure.x + j)
                    y = cell * (tetris.figure.y + i)
                    screen.blit(shape, (x, y))
                    pygame.draw.rect(screen, white, (x,y,cell,cell), 1)


        pygame.display.update()
        clock.tick(fps)
if __name__ == "__main__":
    main()