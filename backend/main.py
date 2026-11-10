
import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from game import Tetris

app = FastAPI()

PROJECT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_DIR / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


@app.get("/")
async def home():
    return FileResponse(FRONTEND_DIR / "index.html")


def get_piece_data(piece):
    if piece is None:
        return None

    return {
        "type": piece.type,
        "x": piece.x,
        "y": piece.y,
        "color": piece.color,
        "orientation": piece.orientation,
        "shape": piece.image()
    }


def get_game_state(game):
    return {
        "grid": game.grid,
        "current": get_piece_data(game.figure),
        "next": get_piece_data(game.next),
        "held": get_piece_data(game.held),
        "score": game.score,
        "level": game.level,
        "lines": game.linesCleared,
        "canHold": game.canHold,
        "gameOver": game.end
    }


def handle_action(game, action):
    if game.end:
        if action == "restart":
            return Tetris()
        return game

    if action == "left":
        game.left()
    elif action == "right":
        game.right()
    elif action == "rotate":
        game.rotate()
    elif action == "down":
        game.moveDown(softDrop=True)
    elif action == "tick":
        game.moveDown()
    elif action == "drop":
        game.freefall()
    elif action == "hold":
        game.holdPiece()

    return game


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    game = Tetris()

    try:
        await websocket.send_json(get_game_state(game))

        while True:
            action = await websocket.receive_text()

            if action == "restart":
                game = Tetris()
            else:
                game = handle_action(game, action)

            await websocket.send_json(get_game_state(game))

    except WebSocketDisconnect:
        print("Player disconnected")
