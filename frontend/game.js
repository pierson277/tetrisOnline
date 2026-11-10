
const board = document.getElementById("board");
const ctx = board.getContext("2d");

const holdCanvas = document.getElementById("holdCanvas");
const holdCtx = holdCanvas.getContext("2d");

const nextCanvas = document.getElementById("nextCanvas");
const nextCtx = nextCanvas.getContext("2d");

const connection = document.getElementById("connection");

const COLORS = {
    0: "#101018",
    1: "#00e5ff",
    2: "#ff4455",
    3: "#55dd66",
    4: "#ffcc33"
};

const BLOCK_SIZE = 30;

let gameState = null;
let socket = null;

function connect() {
    const protocol = location.protocol === "https:" ? "wss:" : "ws:";
    socket = new WebSocket(`${protocol}//${location.host}/ws`);

    socket.onopen = () => {
        connection.textContent = "Connected";
        connection.style.color = "#55dd66";
    };

    socket.onmessage = (event) => {
        gameState = JSON.parse(event.data);
        drawGame();
    };

    socket.onclose = () => {
        connection.textContent = "Disconnected";
        connection.style.color = "#ff4455";

        setTimeout(connect, 2000);
    };

    socket.onerror = () => {
        connection.textContent = "Connection error";
    };
}

function sendAction(action) {
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(action);
    }
}

function drawBlock(context, x, y, color, size) {
    context.fillStyle = COLORS[color] || "#ffffff";
    context.fillRect(x * size, y * size, size - 1, size - 1);

    context.strokeStyle = "#08080e";
    context.lineWidth = 1;
    context.strokeRect(x * size, y * size, size - 1, size - 1);
}

function drawBoard() {
    if (!gameState) return;

    ctx.clearRect(0, 0, board.width, board.height);

    // Grid
    ctx.strokeStyle = "#252535";

    for (let x = 0; x <= 10; x++) {
        ctx.beginPath();
        ctx.moveTo(x * BLOCK_SIZE, 0);
        ctx.lineTo(x * BLOCK_SIZE, 600);
        ctx.stroke();
    }

    for (let y = 0; y <= 20; y++) {
        ctx.beginPath();
        ctx.moveTo(0, y * BLOCK_SIZE);
        ctx.lineTo(300, y * BLOCK_SIZE);
        ctx.stroke();
    }

    // Locked blocks
    for (let y = 0; y < 20; y++) {
        for (let x = 0; x < 10; x++) {
            if (gameState.grid[y][x] > 0) {
                drawBlock(ctx, x, y, gameState.grid[y][x], BLOCK_SIZE);
            }
        }
    }

    const piece = gameState.current;

    if (!piece) return;

    // Ghost piece
    let ghostY = piece.y;

    while (canPlace(piece, piece.x, ghostY + 1)) {
        ghostY++;
    }

    for (const block of piece.shape) {
        const x = piece.x + block % 4;
        const y = ghostY + Math.floor(block / 4);

        if (y >= 0 && y < 20) {
            ctx.globalAlpha = 0.25;
            drawBlock(ctx, x, y, piece.color, BLOCK_SIZE);
            ctx.globalAlpha = 1;
        }
    }

    // Current piece
    for (const block of piece.shape) {
        const x = piece.x + block % 4;
        const y = piece.y + Math.floor(block / 4);

        if (y >= 0 && y < 20) {
            drawBlock(ctx, x, y, piece.color, BLOCK_SIZE);
        }
    }
}

function canPlace(piece, x, y) {
    for (const block of piece.shape) {
        const blockX = x + block % 4;
        const blockY = y + Math.floor(block / 4);

        if (
            blockX < 0 ||
            blockX >= 10 ||
            blockY >= 20 ||
            (blockY >= 0 && gameState.grid[blockY][blockX] > 0)
        ) {
            return false;
        }
    }

    return true;
}

function drawPreview(context, canvas, piece) {
    context.clearRect(0, 0, canvas.width, canvas.height);

    if (!piece) return;

    const size = 20;

    const positions = piece.shape.map(block => ({
        x: block % 4,
        y: Math.floor(block / 4)
    }));

    const minX = Math.min(...positions.map(p => p.x));
    const maxX = Math.max(...positions.map(p => p.x));
    const minY = Math.min(...positions.map(p => p.y));
    const maxY = Math.max(...positions.map(p => p.y));

    const width = (maxX - minX + 1) * size;
    const height = (maxY - minY + 1) * size;

    const offsetX = (canvas.width - width) / 2;
    const offsetY = (canvas.height - height) / 2;

    context.fillStyle = COLORS[piece.color] || "#ffffff";

    for (const position of positions) {
        context.fillRect(
            offsetX + (position.x - minX) * size,
            offsetY + (position.y - minY) * size,
            size - 1,
            size - 1
        );
    }
}

function drawGame() {
    drawBoard();

    document.getElementById("score").textContent = gameState.score;
    document.getElementById("level").textContent = gameState.level;
    document.getElementById("lines").textContent = gameState.lines;

    drawPreview(holdCtx, holdCanvas, gameState.held);
    drawPreview(nextCtx, nextCanvas, gameState.next);

    document.getElementById("gameOver").classList.toggle(
        "hidden",
        !gameState.gameOver
    );
}

// Keyboard controls
document.addEventListener("keydown", (event) => {
    const keys = {
        ArrowLeft: "left",
        ArrowRight: "right",
        ArrowUp: "rotate",
        ArrowDown: "down",
        Space: "drop",
        KeyC: "hold"
    };

    const action = keys[event.code];

    if (action) {
        event.preventDefault();
        sendAction(action);
    }
});

// Restart
document.getElementById("restart").addEventListener("click", () => {
    sendAction("restart");
});

// Automatic falling
setInterval(() => {
    if (gameState && !gameState.gameOver) {
        sendAction("tick");
    }
}, 800);

// Connect to server
connect();
