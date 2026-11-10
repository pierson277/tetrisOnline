from game import Tetris

game = Tetris()

print("Starting score:", game.score)
print("Current piece:", game.figure.type)

game.left()
game.rotate()
game.moveDown()

print("New position:", game.figure.x, game.figure.y)
print("Game over:", game.end)