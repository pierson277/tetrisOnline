import random

# Game settings
ROWS = 20
COLS = 10

class Shape:
    version = {
        'I': [[1, 5, 9, 13], [4, 5, 6, 7]],
        'Z': [[4, 5, 9, 10], [2, 6, 5, 9]],
        'S': [[6, 7, 9, 10], [1, 5, 6, 10]],
        'L': [[1, 2, 5, 9], [4, 5, 6, 10],
              [1, 5, 9, 8], [0, 4, 5, 6]],
        'J': [[1, 2, 6, 10], [3, 5, 6, 7],
              [2, 6, 10, 11], [5, 6, 7, 9]],
        'T': [[1, 4, 5, 6], [1, 5, 6, 9],
              [4, 5, 6, 9], [1, 4, 5, 9]],
        'O': [[1, 2, 5, 6]]
    }

    shapes = ['I', 'Z', 'S', 'L', 'J', 'T', 'O']

    def __init__(self, x, y, rng, pieceType):
        self.x = x
        self.y = y
        self.type = pieceType
        self.shape = self.version[self.type]
        self.color = rng.randint(1, 4)
        self.orientation = 0

    def image(self):
        return self.shape[self.orientation]

    def rotate(self):
        self.orientation = (self.orientation + 1) % len(self.shape)


class Tetris:

    def __init__(self, rows=ROWS, cols=COLS, seed=None):
        self.rows = rows
        self.cols = cols
        self.score = 0
        self.level = 1
        self.linesCleared = 0

        self.grid = [[0 for j in range(cols)] for i in range(rows)]

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

    def getNextPiece(self):
        if not self.bag:
            self.bag = Shape.shapes.copy()
            self.bagRng.shuffle(self.bag)

        return self.bag.pop()

    def newShape(self):
        if not self.next:
            self.next = Shape(5, 0, self.colorRng, self.getNextPiece())

        self.figure = self.next
        self.next = Shape(5, 0, self.colorRng, self.getNextPiece())

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

    def collision(self):
        for i in range(4):
            for j in range(4):
                if (i * 4 + j) in self.figure.image():
                    blockRow = i + self.figure.y
                    blockCol = j + self.figure.x

                    if (blockRow >= self.rows or
                        blockCol >= self.cols or
                        blockCol < 0 or
                        self.grid[blockRow][blockCol] > 0):
                        return True

        return False

    def removeRow(self):
        cleared = 0
        y = self.rows - 1

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

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if (i * 4 + j) in self.figure.image():
                    self.grid[i + self.figure.y][j + self.figure.x] = self.figure.color

        self.removeRow()
        self.newShape()
        self.canHold = True

        if self.collision():
            self.end = True

    def moveDown(self, softDrop=False):
        self.figure.y += 1

        if self.collision():
            self.figure.y -= 1
            self.freeze()
        elif softDrop:
            self.score += 1

    def left(self):
        self.figure.x -= 1

        if self.collision():
            self.figure.x += 1

    def right(self):
        self.figure.x += 1

        if self.collision():
            self.figure.x -= 1

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

    def rotate(self):
        oldOrientation = self.figure.orientation
        oldX = self.figure.x

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
