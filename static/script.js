// --- CẤU HÌNH ---
const PLAYER_HUMAN = 1;
const PLAYER_AI = 2;

let rows = 15;
let cols = 15;
let difficulty = 2;
let winStreak = 5;
let boardState = [];
let isGameActive = false;
let isHumanTurn = true;

const boardElement = document.getElementById('board');
const statusElement = document.getElementById('status');
const loadingElement = document.getElementById('loading');

// --- HÀM KHỞI TẠO GAME ---
function initGame() {
    // 1. Lấy dữ liệu từ giao diện
    rows = parseInt(document.getElementById('rows').value);
    cols = parseInt(document.getElementById('cols').value);
    difficulty = parseInt(document.getElementById('difficulty').value);
    winStreak = parseInt(document.getElementById('win-streak').value);
    
    // Lấy thông tin ai đi trước
    const firstMove = document.getElementById('first-move').value;

    // Validate
    if (rows < 5) rows = 5; if (rows > 25) rows = 25;
    if (cols < 5) cols = 5; if (cols > 25) cols = 25;

    // Reset trạng thái
    boardState = Array(rows * cols).fill(0);
    isGameActive = true;
    
    renderBoard();

    // 2. Xử lý lượt đi đầu tiên
    if (firstMove === 'ai') {
        isHumanTurn = false;
        updateStatus("AI đang đi nước đầu...", false);
        
        // Nếu AI đi trước, đánh luôn vào giữa bàn cờ cho nhanh (đỡ gọi API)
        const centerIndex = Math.floor((rows * cols) / 2);
        
        // Tạo hiệu ứng chờ giả (500ms) cho tự nhiên
        loadingElement.classList.remove('hidden');
        setTimeout(() => {
            makeMove(centerIndex, PLAYER_AI);
            loadingElement.classList.add('hidden');
            isHumanTurn = true;
            updateStatus("Lượt của bạn (X)", false);
        }, 500);
        
    } else {
        isHumanTurn = true;
        updateStatus("Lượt của bạn (X)", false);
    }
}

// --- VẼ BÀN CỜ (Tailwind Style) ---
function renderBoard() {
    boardElement.innerHTML = '';
    boardElement.style.gridTemplateColumns = `repeat(${cols}, 35px)`;
    boardElement.style.gridTemplateRows = `repeat(${rows}, 35px)`;

    for (let i = 0; i < rows * cols; i++) {
        const cell = document.createElement('div');
        // Class Tailwind cho ô cờ
        cell.className = 'cell w-[35px] h-[35px] flex justify-center items-center text-xl font-bold cursor-pointer hover:bg-blue-50 transition-colors select-none';
        cell.dataset.index = i;
        cell.addEventListener('click', onCellClick);
        boardElement.appendChild(cell);
    }
}

// --- XỬ LÝ CLICK ---
function onCellClick(e) {
    if (!isGameActive || !isHumanTurn) return;

    const index = parseInt(e.target.dataset.index);
    if (boardState[index] !== 0) return;

    // Người chơi đi
    makeMove(index, PLAYER_HUMAN);

    // AI đi
    requestAIMove();
}

// --- HIỂN THỊ NƯỚC ĐI ---
function makeMove(index, player) {
    boardState[index] = player;
    const cell = boardElement.children[index];
    
    if (player === PLAYER_HUMAN) {
        cell.textContent = 'X';
        cell.classList.add('text-blue-600');
    } else {
        cell.textContent = 'O';
        cell.classList.add('text-red-500');
    }
}

// --- GỌI API BACKEND ---
async function requestAIMove() {
    isHumanTurn = false;
    updateStatus(`AI (Cấp ${difficulty}) đang nghĩ...`, false);
    loadingElement.classList.remove('hidden');

    try {
        const response = await fetch('/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                board: boardState,
                rows: rows,
                cols: cols,
                depth: difficulty,
                win_streak: winStreak // Gửi luật thắng
            })
        });

        const data = await response.json();
        loadingElement.classList.add('hidden');

        if (data.move !== undefined && data.move !== null) {
            makeMove(data.move, PLAYER_AI);
        }

        if (data.winner) {
            setTimeout(() => handleGameOver(data.winner), 100);
        } else {
            isHumanTurn = true;
            updateStatus("Lượt của bạn (X)", false);
        }
    } catch (error) {
        console.error(error);
        loadingElement.classList.add('hidden');
        updateStatus("Lỗi kết nối!", true);
    }
}

// --- XỬ LÝ KẾT THÚC GAME ---
function handleGameOver(winner) {
    isGameActive = false;
    let message = "";
    let colorClass = "";

    if (winner == PLAYER_HUMAN || winner === 'x') {
        message = "🏆 BẠN THẮNG RỒI!";
        colorClass = "text-green-600";
    } else if (winner == PLAYER_AI || winner === 'o') {
        message = "🤖 AI ĐÃ CHIẾN THẮNG!";
        colorClass = "text-red-600";
    } else {
        message = "🤝 HÒA CỜ!";
        colorClass = "text-gray-600";
    }

    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    statusEl.className = `text-lg font-bold block ${colorClass} animate-bounce`;
    
    // Popup thông báo
    setTimeout(() => alert(message), 50);
}

// --- CẬP NHẬT TRẠNG THÁI ---
function updateStatus(msg, isError) {
    const statusEl = document.getElementById('status');
    statusEl.textContent = msg;
    statusEl.className = isError ? "text-lg font-bold text-red-500" : "text-lg font-bold text-blue-600";
}

// Chạy lần đầu
document.addEventListener('DOMContentLoaded', initGame);