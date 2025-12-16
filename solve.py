import math
import random

# --- CONSTANTS ---
EMPTY = 0
PLAYER_HUMAN = 1  # X
PLAYER_AI = 2     # O

# Điểm số cho hàm lượng giá
SCORE_WIN = 1_000_000_000
SCORE_PRE_WIN = 1_000_000
SCORE_BLOCK_WIN = 2_000_000 # Ưu tiên chặn hơn là tạo thế công
SCORE_ADVANTAGE = 1_000

class Board:
    """
    Quản lý trạng thái bàn cờ, logic di chuyển và kiểm tra thắng thua.
    """
    def __init__(self, state_1d, rows=15, cols=15, win_streak=5):
        self.rows = rows
        self.cols = cols
        self.win_streak = win_streak
        self.squares = self._convert_1d_to_2d(state_1d)

    def _convert_1d_to_2d(self, state_1d):
        """Chuyển đổi mảng 1 chiều (từ API) sang ma trận 2 chiều."""
        matrix = []
        for r in range(self.rows):
            start = r * self.cols
            end = start + self.cols
            matrix.append(state_1d[start:end])
        return matrix

    def is_valid_move(self, r, c):
        return 0 <= r < self.rows and 0 <= c < self.cols and self.squares[r][c] == EMPTY

    def get_possible_moves(self):
        """
        Tối ưu hóa không gian tìm kiếm:
        Chỉ trả về các ô trống nằm trong bán kính 1 ô so với các quân đã đánh.
        """
        moves = set()
        has_piece = False
        
        for r in range(self.rows):
            for c in range(self.cols):
                if self.squares[r][c] != EMPTY:
                    has_piece = True
                    # Quét các ô xung quanh (3x3)
                    for dr in range(-1, 2):
                        for dc in range(-1, 2):
                            if dr == 0 and dc == 0: continue
                            nr, nc = r + dr, c + dc
                            if self.is_valid_move(nr, nc):
                                moves.add((nr, nc))
        
        # Nếu bàn cờ trống, đánh vào giữa
        if not has_piece:
            return [(self.rows // 2, self.cols // 2)]
        
        return list(moves)

    def check_win(self, r, c, player):
        """
        Kiểm tra chiến thắng cục bộ tại vị trí (r, c) vừa đánh.
        Độ phức tạp O(1) nhờ chỉ duyệt xung quanh điểm mới.
        """
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)] # Ngang, Dọc, Chéo chính, Chéo phụ

        for dr, dc in directions:
            count = 1
            
            # 1. Duyệt hướng dương
            for i in range(1, self.win_streak):
                nr, nc = r + dr * i, c + dc * i
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.squares[nr][nc] == player:
                    count += 1
                else:
                    break
            
            # 2. Duyệt hướng âm
            for i in range(1, self.win_streak):
                nr, nc = r - dr * i, c - dc * i
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.squares[nr][nc] == player:
                    count += 1
                else:
                    break

            if count >= self.win_streak:
                return True
                
        return False

class GomokuAI:
    """
    Trí tuệ nhân tạo sử dụng Minimax + Alpha-Beta Pruning.
    """
    def __init__(self, player_id, win_streak=5):
        self.player_id = player_id
        self.opponent_id = 1 if player_id == 2 else 2
        self.win_streak = win_streak

    def evaluate_window(self, window):
        """
        Hàm Heuristic: Đánh giá điểm số của một cửa sổ (window).
        Logic động dựa trên self.win_streak.
        """
        score = 0
        my_count = window.count(self.player_id)
        opp_count = window.count(self.opponent_id)
        empty_count = window.count(EMPTY)

        target = self.win_streak

        # --- TẤN CÔNG (AI) ---
        if my_count == target:
            score += SCORE_WIN
        elif my_count == target - 1 and empty_count == 1:
            score += SCORE_PRE_WIN
        elif my_count == target - 2 and empty_count == 2:
            score += SCORE_ADVANTAGE

        # --- PHÒNG THỦ (Chặn đối thủ) ---
        if opp_count == target - 1 and empty_count == 1:
            # Điểm chặn phải lớn hơn điểm tấn công tương đương để ưu tiên phòng thủ
            score -= SCORE_BLOCK_WIN 
        elif opp_count == target - 2 and empty_count == 2:
            score -= (SCORE_ADVANTAGE * 2)

        return score

    def evaluate_board(self, board):
        """Tính tổng điểm heuristic của toàn bộ bàn cờ."""
        score = 0
        window_len = self.win_streak
        
        # Đánh giá Hàng ngang
        for r in range(board.rows):
            for c in range(board.cols - window_len + 1):
                window = board.squares[r][c : c + window_len]
                score += self.evaluate_window(window)

        # Đánh giá Hàng dọc
        for c in range(board.cols):
            col_arr = [board.squares[r][c] for r in range(board.rows)]
            for r in range(board.rows - window_len + 1):
                window = col_arr[r : r + window_len]
                score += self.evaluate_window(window)

        # Đánh giá Chéo chính
        for r in range(board.rows - window_len + 1):
            for c in range(board.cols - window_len + 1):
                window = [board.squares[r+i][c+i] for i in range(window_len)]
                score += self.evaluate_window(window)

        # Đánh giá Chéo phụ
        for r in range(window_len - 1, board.rows):
            for c in range(board.cols - window_len + 1):
                window = [board.squares[r-i][c+i] for i in range(window_len)]
                score += self.evaluate_window(window)

        return score

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        """
        Thuật toán Minimax đệ quy có cắt tỉa Alpha-Beta.
        """
        # 1. Lấy danh sách nước đi khả thi
        valid_moves = board.get_possible_moves()

        # 2. Điều kiện dừng (Hết độ sâu hoặc hết nước đi)
        if depth == 0 or not valid_moves:
            return None, self.evaluate_board(board)

        # 3. Tối ưu: Sắp xếp nước đi từ trung tâm ra ngoài
        # Giúp Alpha-Beta cắt tỉa sớm hơn, tăng tốc độ tính toán.
        center_r, center_c = board.rows // 2, board.cols // 2
        valid_moves.sort(key=lambda m: abs(m[0] - center_r) + abs(m[1] - center_c))

        if is_maximizing: # Lượt AI
            max_eval = -math.inf
            best_move = random.choice(valid_moves) # Fallback ngẫu nhiên

            for (r, c) in valid_moves:
                board.squares[r][c] = self.player_id
                
                # TỐI ƯU CỰC ĐẠI: Kiểm tra thắng ngay lập tức
                if board.check_win(r, c, self.player_id):
                    board.squares[r][c] = EMPTY
                    return (r, c), SCORE_WIN # Trả về điểm thắng tuyệt đối
                
                eval_score = self.minimax(board, depth - 1, alpha, beta, False)[1]
                board.squares[r][c] = EMPTY # Backtrack (Hoàn tác)

                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (r, c)
                
                alpha = max(alpha, eval_score)
                if beta <= alpha: break # Cắt tỉa
            
            return best_move, max_eval

        else: # Lượt Người chơi (Giả lập đối thủ chơi tối ưu)
            min_eval = math.inf
            best_move = random.choice(valid_moves)

            for (r, c) in valid_moves:
                board.squares[r][c] = self.opponent_id
                
                # TỐI ƯU CỰC ĐẠI: Kiểm tra thua ngay lập tức
                if board.check_win(r, c, self.opponent_id):
                    board.squares[r][c] = EMPTY
                    return (r, c), -SCORE_WIN
                
                eval_score = self.minimax(board, depth - 1, alpha, beta, True)[1]
                board.squares[r][c] = EMPTY # Backtrack

                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (r, c)
                
                beta = min(beta, eval_score)
                if beta <= alpha: break # Cắt tỉa
            
            return best_move, min_eval