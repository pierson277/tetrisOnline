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
screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
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
    1: pygame.image.load("C:\\Code\\Python\\TetrisProject\\assets\\1.png"),
    2: pygame.image.load("C:\\Code\\Python\\TetrisProject\\assets\\2.png"),
    3: pygame.image.load("C:\\Code\\Python\\TetrisProject\\assets\\3.png"),
    4: pygame.image.load("C:\\Code\\Python\\TetrisProject\\assets\\4.png")
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
        self.level = 1
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
                    if(blockRow >= self.rows or blockCol >= self.cols or blockCol < 0 or self.grid[blockRow]
                    [blockCol] > 0): 
                        return True
        return False


    #remove row
    def removeRow(self):
        rerun = False

        for y in range(self.rows-1, 0, -1):
            completed = True
            for x in range(0, self.cols):
                if self.grid[y][x] == 0:
                    completed = False

            if completed:
                del self.grid[y]
                self.grid.insert(0, [0 for i in range(self.cols)])
                self.score += 100
                if self.score % 10 == 0:
                    self.level += 1
                rerun = True
        if rerun:
            self.removeRow()


    #freeze
    def freeze(self):
        for i in range(4):
            for j in range(4):
                if (i*4 +j) in self.figure.image():
                    self.grid[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.removeRow()
        self.newShape()
        if self.collision():
            self.end = True

    #move down
    def moveDown(self):
        self.figure.y += 1
        if self.collision():
            self.figure.y -= 1
            self.freeze()


    #move left
    def left(self):
        self.figure.x -= 1
        if self.collision():
            self.figure.x += 1
            
    #move right
    def right(self):
        self.figure.x += 1
        if self.collision():
            self.figure.x -= 1

    #freefall
    def freefall(self):
        while not self.collision():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()



    #rotate
    def rotate(self):
        orientation = self.figure.orientation
        self.figure.rotate()
        if self.collision():
            self.figure.orientation = orientation

    def endGame(self):
        popUp = pygame.Rect(50, 140, width-100, height-350)
        pygame.draw.rect(screen, black, popUp)
        pygame.draw.rect(screen, lose, popUp, 2)

        gameOver = font2.render("Game Over", True, white)
        option1 = font2.render("Press R to restart", True, lose)
        option2 = font2.render("Press Q to quit", True, lose)

        screen.blit(gameOver, (popUp.centerx-gameOver.get_width()//2, popUp.y + 20))
        screen.blit(option1, (popUp.centerx-option1.get_width()//2, popUp.y + 80))
        screen.blit(option2, (popUp.centerx-option2.get_width()//2, popUp.y + 110))





#main game loop
def main():
    pygame.font.init()
    font = pygame.font.SysFont("Arial", 30)

    tetris = Tetris(rows, cols)
    counter = 0
    move = True
    spacePressed = False
    run = True
    while run:
        screen.fill(bgColor)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()
            #event loop
        
            keys = pygame.key.get_pressed()
            if not tetris.end:
                if keys[pygame.K_LEFT]:
                    tetris.left()
                elif keys[pygame.K_RIGHT]:
                    tetris.right()
                elif keys[pygame.K_UP]:
                    tetris.rotate()
                elif keys[pygame.K_DOWN]:
                    tetris.moveDown()
                elif keys[pygame.K_SPACE]:
                    spacePressed = True
            if keys[pygame.K_r]:
                tetris.__init__(rows,cols)
            if keys[pygame.K_ESCAPE]:
                run = False

        #allows block to fall at constant rate
        counter += 1
        if counter >= 10000:
            counter = 0


        if move:
            if counter % (fps//(tetris.level*2)) == 0:
                if not tetris.end:
                    if spacePressed:
                        tetris.freefall()
                        spacePressed = False
                    else:
                        tetris.moveDown()

        tetris.makeGrid()

        #keep fallen shapes on screen
        for x in range(rows):
            for y in range(cols):
                if tetris.grid[x][y] > 0:
                    value = tetris.grid[x][y]
                    image = assets[value]
                    screen.blit(image, (cell * y, cell * x))
                    pygame.draw.rect(screen, white, (cell * y, cell * x, cell, cell), 1)

        #show shape on game screen
        if tetris.figure:
            for i in range(4):
                for j in range(4):
                    if (i *4 + j) in tetris.figure.image():
                        shape = assets[tetris.figure.color]
                        x = cell * (tetris.figure.x + j)
                        y = cell * (tetris.figure.y + i)
                        screen.blit(shape, (x, y))
                        pygame.draw.rect(screen, white, (x,y,cell,cell), 1)

        #control panel
        if tetris.next:
            for i in range(4):
                for j in range(4):
                    if (i *4 + j) in tetris.next.image():
                        image = assets[tetris.next.color]
                        x = cell * (tetris.next.x + j -4)
                        y = height -100 + cell * (tetris.next.y + i)
                        screen.blit(image, (x, y))

        if tetris.end:
            tetris.endGame()



        scoreText = font.render(f"Score: {tetris.score}", True, white)
        levelText = font2.render(f"Level: {tetris.level}", True, white)
        screen.blit(scoreText, (200-scoreText.get_width()//2, height-110))
        screen.blit(levelText, (250-levelText.get_width()//2, height-30))





        pygame.display.update()
        clock.tick(fps)
if __name__ == "__main__":
    main()