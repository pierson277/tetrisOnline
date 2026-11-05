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
        self.held = None
        self.canHold = True
        self.end = False
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
            

    #make new shape
    def newShape(self):
        if not self.next:
            self.next = Shape(5, 0)
        self.figure = self.next
        self.next = Shape(5, 0)

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
        rerun = False

        for y in range(self.rows-1, -1, -1):
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
        self.canHold = True
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
    moveDelay = 150
    lastMove = 0
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
            #event loop
        
        keys = pygame.key.get_pressed()
        currentTime = pygame.time.get_ticks()

        if not tetris.end and currentTime - lastMove >= moveDelay:
            if keys[pygame.K_LEFT]:
                    tetris.left()
                    lastMove = currentTime

            elif keys[pygame.K_RIGHT]:
                tetris.right()
                lastMove = currentTime
                    
            elif keys[pygame.K_UP]:
                    tetris.rotate()
                    lastMove = currentTime
                    
            elif keys[pygame.K_DOWN]:
                tetris.moveDown()
                lastMove = currentTime
                
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

        heldText = font2.render("HELD", True, white)
        nextText = font2.render("NEXT", True, white)

        screen.blit(scoreText, (220, 30))
        screen.blit(scoreValue, (220, 45))

        screen.blit(levelText, (220, 100))
        screen.blit(levelValue, (220, 115))

        screen.blit(heldText, (220, 170))
        screen.blit(nextText, (220, 320))

        previewPieces = [
            (tetris.held, 220, 210),
            (tetris.next, 220, 350)
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