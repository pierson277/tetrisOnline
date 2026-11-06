#Tetris Online
#imports
import pygame
import random
import sys
pygame.init()

#constant variables
width, height = 400, 520
fps = 60
cell = 20
rows = 20
cols = 10
boardWidth = cols * cell
boardHeight = rows * cell
panelHeight = height - boardHeight
gravityFrames = [
    60, 48, 37, 28, 21,
    16, 11, 8, 6, 4,
    3, 2, 1
]


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
        'L': [[1, 2, 5, 9], [4, 5, 6, 10], [1, 5, 9, 8], [0, 4, 5, 6]],
        'J': [[1, 2, 6, 10], [3, 5, 6, 7], [2, 6, 10, 11], [5, 6, 7, 9]],
        'T': [[1, 4, 5, 6], [1, 5, 6, 9], [4, 5, 6, 9], [1, 4, 5, 9]],
        'O': [[1, 2, 5, 6]]
    }
    shapes = ['I', 'Z', 'S', 'L', 'J', 'T', 'O']

    #constructor
    def __init__(self, x, y, rng, pieceType):
        self.x = x
        self.y = y
        self.type = pieceType
        self.shape = self.version[self.type]
        self.color = rng.randint(1,4)
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
    def __init__(self, rows, cols, seed=None):
        self.rows = rows
        self.cols = cols
        self.score = 0
        self.level = 1
        self.linesCleared = 0
        self.grid =[[0 for j in range(cols)] for i in range(rows)]
        self.next = None
        self.held = None
        self.canHold = True
        self.end = False

        if seed is None:
            seed = random.randrange(0, 2**32)
        self.seed = seed
        self.bagRng = random.Random(self.seed)
        self.colorRng = random.Random(self.seed ^ 0x5DEECE66D)
        self.bag = []

        self.newShape()

    #make grid
    def makeGrid(self):
        #Horizontal lines
        for i in range(self.rows + 1):
            pygame.draw.line(
                screen, grid,
                (0, i * cell),
                (boardWidth, i * cell)
            )
        #vertical lines
        for j in range(self.cols + 1):
            pygame.draw.line(
                screen, grid,
                (j * cell, 0),
                (j * cell, boardHeight)
            )
    #get next piece from 7 bag
    def getNextPiece(self):
        #refill bag when empty
        if not self.bag:
            self.bag = Shape.shapes.copy()
            #shuffle bag
            self.bagRng.shuffle(self.bag)
        #return and remove next piece
        return self.bag.pop()
            

    #make new shape
    def newShape(self):
        if not self.next:
            self.next = Shape(5, 0, self.colorRng, self.getNextPiece())
        self.figure = self.next
        self.next = Shape(5, 0, self.colorRng, self.getNextPiece())

    #hold pieces
    def holdPiece(self):
        if not self.canHold or self.end:
            return
        
        current = self.figure
        
        if self.held is None:
            self.held = current
            self.newShape()
        else:
            self.figure = self.held
            self.held = current
            self.figure.x = 5
            self.figure.y = 0
            self.figure.orientation = 0
        self.canHold = False
        if self.collision():
            self.end = True

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
        cleared = 0
        y = self.rows - 1 #19
        while y >= 0:
            if all(self.grid[y][x] > 0 for x in range(self.cols)):
                del self.grid[y]
                self.grid.insert(0, [0 for i in range(self.cols)])
                cleared += 1
            else:
                y -= 1
        if cleared > 0:
            points = {
                1: 100,
                2: 300,
                3: 500,
                4: 800
            }
            self.score += points[cleared] * self.level
            self.linesCleared += cleared
            self.level = self.linesCleared // 10 + 1


    #freeze
    def freeze(self):
        for i in range(4):
            for j in range(4):
                if (i*4 +j) in self.figure.image():
                    self.grid[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.removeRow()
        self.newShape()
        self.canHold = True
        if self.collision():
            self.end = True

    #move down
    def moveDown(self, softDrop = False):
        self.figure.y += 1
        if self.collision():
            self.figure.y -= 1
            self.freeze()
        elif softDrop:
            self.score += 1


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
        distance = 0
        while True:
            self.figure.y += 1
            if self.collision():
                self.figure.y -= 1
                break
            distance += 1
        self.score += distance * 2
        self.freeze()

    def shadowPosition(self):
        originalY = self.figure.y

        while not self.collision():
            self.figure.y += 1
        self.figure.y -= 1
        shadowY = self.figure.y
        self.figure.y = originalY
        return shadowY

    #rotate
    def rotate(self):
        oldOrientation = self.figure.orientation
        oldX = self.figure.x
        
        #rotate pieces
        self.figure.rotate()
        
        if not self.collision():
            return
        
        wallKicks = [-1, 1, -2, 2]
        for offset in wallKicks:
            self.figure.x = oldX + offset
            if not self.collision():
                return
        self.figure.x = oldX
        self.figure.orientation = oldOrientation

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
    gravityCounter = 0
    moveDelay = 100
    rotateDelay = 180
    downDelay = 50
    lastMove = 0
    lastRotate = 0
    lastDown = 0
    counter = 0
    move = True
    spacePressed = False
    run = True
    while run:
        screen.fill(bgColor)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not tetris.end:
                    tetris.freefall()
                if event.key == pygame.K_c and not tetris.end:
                    tetris.holdPiece()       
                if event.key == pygame.K_r:
                    tetris.__init__(rows, cols, tetris.seed)
                if event.key == pygame.K_ESCAPE:
                    run = False
            #event loop
        
        keys = pygame.key.get_pressed()
        currentTime = pygame.time.get_ticks()

        if not tetris.end:
            #left and right movement
            if currentTime - lastMove >= moveDelay:
                if keys[pygame.K_LEFT]:
                    tetris.left()
                    lastMove = currentTime
                elif keys[pygame.K_RIGHT]:
                    tetris.right()
                    lastMove = currentTime

            #rotation
            if keys[pygame.K_UP] and currentTime - lastRotate >= rotateDelay:
                tetris.rotate()
                lastRotate = currentTime

            #soft drop
            if keys[pygame.K_DOWN] and currentTime - lastDown >= downDelay:
                tetris.moveDown(softDrop=True)
                lastDown = currentTime
        if keys[pygame.K_r]:
            tetris.__init__(rows, cols, tetris.seed)

        if keys[pygame.K_ESCAPE]:
            run = False

            
                

        #gravity system
        gravityCounter += 1
        levelIndex = min(tetris.level - 1, len(gravityFrames) - 1)
        currentGravity = gravityFrames[levelIndex]
        if gravityCounter >= currentGravity:
            gravityCounter = 0
            if not tetris.end:
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

        #show shadow piece
        if tetris.figure:
            shadowY = tetris.shadowPosition()

            for i in range(4):
                for j in range(4):
                    if (i * 4 + j) in tetris.figure.image():
                        x = cell * (tetris.figure.x + j)
                        y = cell * (shadowY + i)
                        shadow = pygame.Surface((cell, cell), pygame.SRCALPHA)
                        shadow.fill((180, 180, 180, 100))
                        screen.blit(shadow, (x, y))
                        pygame.draw.rect(screen, (200, 200, 200), (x, y, cell, cell), 1)
        #show actual piece
        if tetris.figure:
            for i in range(4):
                for j in range(4):
                    if (i * 4 + j) in tetris.figure.image():
                        shape = assets[tetris.figure.color]
                        x = cell * (tetris.figure.x + j)
                        y = cell * (tetris.figure.y + i)
                        screen.blit(shape, (x, y))
                        pygame.draw.rect(screen, white, (x, y, cell, cell), 1)

        #control panel
        scoreText = font2.render("SCORE", True, white)
        scoreValue = font1.render(str(tetris.score), True, white)

        levelText = font2.render("LEVEL", True, white)
        levelValue = font1.render(str(tetris.level), True, white)

        linesText = font2.render("LINES", True, white)
        linesValue = font1.render(str(tetris.linesCleared), True, white)

        screen.blit(linesText, (220, 160))
        screen.blit(linesValue, (220, 175))

        heldText = font2.render("HELD", True, white)
        nextText = font2.render("NEXT", True, white)

        screen.blit(scoreText, (220, 10))
        screen.blit(scoreValue, (220, 25))

        screen.blit(levelText, (220, 80))
        screen.blit(levelValue, (220, 95))

        screen.blit(heldText, (220, 230))
        screen.blit(nextText, (220, 340))

        previewPieces = [
            (tetris.held, 220, 250),
            (tetris.next, 220, 360)
        ]

        for piece, previewX, previewY in previewPieces:
            if piece:
                for block in piece.image():
                    row = block // 4
                    col = block % 4

                    x = previewX + col * cell
                    y = previewY + row * cell

                    image = assets[piece.color]
                    screen.blit(image, (x, y))
                    pygame.draw.rect(screen, white, (x, y, cell, cell), 1)

        if tetris.end:
            tetris.endGame()

        pygame.display.update()
        clock.tick(fps)
if __name__ == "__main__":
    main()