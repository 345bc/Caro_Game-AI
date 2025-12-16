from flask import Flask, render_template, request, jsonify
import traceback
from solve import Board, GomokuAI, PLAYER_AI

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    try:
        data = request.json
        board_state = data['board']
        rows = int(data.get('rows', 15))
        cols = int(data.get('cols', 15))
        depth = int(data.get('depth', 2))
        win_streak = int(data.get('win_streak', 5))

        # --- SỬA LỖI TẠI DÒNG NÀY ---
        # Đổi 'state=' thành 'state_1d=' để khớp với game_engine.py
        game_board = Board(state_1d=board_state, rows=rows, cols=cols, win_streak=win_streak)
        
        ai_player = GomokuAI(PLAYER_AI, win_streak=win_streak)

        # Chạy AI
        move_coords, _ = ai_player.minimax(game_board, depth, -float('inf'), float('inf'), True)

        if move_coords:
            r, c = move_coords
            game_board.squares[r][c] = PLAYER_AI
            is_win = game_board.check_win(r, c, PLAYER_AI)
            return jsonify({
                'move': r * cols + c,
                'winner': 'o' if is_win else None
            })
        else:
            return jsonify({'winner': 'draw'})

    except Exception as e:
        print("============== LỖI SERVER ==============")
        traceback.print_exc() # In chi tiết lỗi ra terminal
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)