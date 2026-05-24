import math

class TicTacToeAlphaBeta:
    def __init__(self, size=3, win_streak=3, max_depth=None, alpha_percent=100, beta_percent=100, verbose=True, max_log_depth=6, log_board=False):
        self.N = size
        self.win_streak = win_streak
        self.max_depth = max_depth
        self.alpha_percent = alpha_percent
        self.beta_percent = beta_percent
        self.win_score = 1000
        self.board = self.initial()
        self.memo = {}
        self.verbose = verbose
        self.max_log_depth = max_log_depth
        self.log_board = log_board
    
    def initial(self):
        """Khởi tạo trạng thái bàn cờ 3x3"""
        return [[' ' for _ in range(self.N)] for _ in range(self.N)]
    
    def log(self, message):
        """Ghi nhận trạng thái bàn cờ hiện tại"""
        print(f"\n--- BÀI 2 LOG: {message} ---")
        for row in self.board:
            print("| " + " | ".join(row) + " |")
        print("-" * 25)

    def should_log(self, depth):
        return self.verbose and depth <= self.max_log_depth

    def log_step(self, depth, message):
        if not self.should_log(depth):
            return
        indent = "    " * depth
        print(f"{indent}{message}")

    def print_board_fancy(self, board, indent=0):
        if not self.verbose or not self.log_board:
            return
        prefix = " " * indent
        symbols = {'X': 'X', 'O': 'O', ' ': '.'}
        for i, row in enumerate(board):
            row_str = "|".join([symbols[cell] for cell in row])
            print(f"{prefix}{i + 1}|{row_str}|")

    def finish(self, board):
        """Kiểm tra kết thúc trò chơi"""
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(self.N):
            for c in range(self.N):
                if board[r][c] == ' ':
                    continue
                player = board[r][c]
                for dr, dc in directions:
                    count = 0
                    for i in range(self.win_streak):
                        nr, nc = r + dr * i, c + dc * i
                        if 0 <= nr < self.N and 0 <= nc < self.N and board[nr][nc] == player:
                            count += 1
                        else:
                            break
                    if count == self.win_streak:
                        return player
        if all(cell != ' ' for row in board for cell in row): return 'Tie'
        return None

    def evaluate(self, board):
        score = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for r in range(self.N):
            for c in range(self.N):
                for dr, dc in directions:
                    end_r = r + (self.win_streak - 1) * dr
                    end_c = c + (self.win_streak - 1) * dc
                    if not (0 <= end_r < self.N and 0 <= end_c < self.N):
                        continue
                    x_count = 0
                    o_count = 0
                    for i in range(self.win_streak):
                        cell = board[r + dr * i][c + dc * i]
                        if cell == 'X':
                            x_count += 1
                        elif cell == 'O':
                            o_count += 1
                    if x_count and o_count:
                        continue
                    if x_count:
                        score += self.line_weight(x_count)
                    elif o_count:
                        score -= self.line_weight(o_count)
        return score

    def line_weight(self, count):
        if count <= 0:
            return 0
        return 10 ** (count - 1)

    def get_empty_cells(self, board):
        return [(r, c) for r in range(self.N) for c in range(self.N) if board[r][c] == ' ']

    def score_bounds(self):
        return -self.win_score, self.win_score

    def alphabeta(self, board, depth, alpha, beta, is_maximizing):
        """Thuật toán cắt tỉa Alpha-Beta tối ưu nhánh duyệt"""
        result = self.finish(board)
        if result == 'X':
            self.log_step(depth, "Dung: X thang")
            return self.win_score - depth
        if result == 'O':
            self.log_step(depth, "Dung: O thang")
            return -self.win_score + depth
        if result == 'Tie':
            self.log_step(depth, "Dung: Hoa")
            return 0
        if self.max_depth is not None and depth >= self.max_depth:
            val = self.evaluate(board)
            self.log_step(depth, f"Dung: Het do sau, danh gia = {val}")
            return val

        key = (tuple(tuple(row) for row in board), depth, is_maximizing)
        cached = self.memo.get(key)
        if cached is not None:
            return cached

        actor = "MAX (X)" if is_maximizing else "MIN (O)"
        self.log_step(depth, f"{actor} dang xem (do sau {depth})")

        if is_maximizing:
            best_score = -math.inf
            for r, c in self.get_empty_cells(board):
                self.log_step(depth, f"-> {actor} thu o ({r + 1},{c + 1})")
                board[r][c] = 'X'
                if self.log_board and self.should_log(depth):
                    self.print_board_fancy(board, indent=(depth + 1) * 4)
                score = self.alphabeta(board, depth + 1, alpha, beta, False)
                board[r][c] = ' '
                self.log_step(depth, f"   <= Diem tra ve: {score}")
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    self.log_step(depth, f"   Cat tia: beta({beta}) <= alpha({alpha})")
                    break
            self.memo[key] = best_score
            self.log_step(depth, f"{actor} chon diem {best_score}")
            return best_score
        else:
            best_score = math.inf
            for r, c in self.get_empty_cells(board):
                self.log_step(depth, f"-> {actor} thu o ({r + 1},{c + 1})")
                board[r][c] = 'O'
                if self.log_board and self.should_log(depth):
                    self.print_board_fancy(board, indent=(depth + 1) * 4)
                score = self.alphabeta(board, depth + 1, alpha, beta, True)
                board[r][c] = ' '
                self.log_step(depth, f"   <= Diem tra ve: {score}")
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    self.log_step(depth, f"   Cat tia: beta({beta}) <= alpha({alpha})")
                    break
            self.memo[key] = best_score
            self.log_step(depth, f"{actor} chon diem {best_score}")
            return best_score

    def best_move(self):
        min_score, max_score = self.score_bounds()
        alpha = min_score * (self.alpha_percent / 100.0)
        beta = max_score * (self.beta_percent / 100.0)
        if alpha >= beta:
            alpha, beta = min_score, max_score
        best_score = -math.inf
        best_move = None
        for r, c in self.get_empty_cells(self.board):
            self.log_step(0, f"[GOC] Xet nuoc ({r + 1},{c + 1})")
            self.board[r][c] = 'X'
            score = self.alphabeta(self.board, 0, alpha, beta, False)
            self.board[r][c] = ' '
            self.log_step(0, f"   => Diem: {score}")
            if score > best_score:
                best_score, best_move = score, (r, c)
        if best_move is not None:
            self.log_step(0, f"[QUYET DINH] Chon ({best_move[0] + 1},{best_move[1] + 1}) voi diem {best_score}")
        return best_move

    def render_board(self):
        header = "   " + " ".join(str(i + 1) for i in range(self.N))
        print(header)
        for r in range(self.N):
            row = []
            for c in range(self.N):
                cell = self.board[r][c] if self.board[r][c] != ' ' else '.'
                row.append(cell)
            print(f"{r + 1:2d} " + " ".join(row))

    def prompt_move(self):
        while True:
            text = input(f"Nước đi (hàng cột 1-{self.N}) hoặc q: ").strip().lower()
            if text in ("q", "quit", "exit"):
                return None
            parts = text.split()
            if len(parts) != 2:
                print("Nhập sai. Ví dụ: 2 3")
                continue
            try:
                r = int(parts[0]) - 1
                c = int(parts[1]) - 1
            except ValueError:
                print("Số không hợp lệ.")
                continue
            if 0 <= r < self.N and 0 <= c < self.N and self.board[r][c] == ' ':
                return (r, c)
            print("Nước đi không hợp lệ.")

    def play_cli(self):
        print("Demo TicTacToe Alpha-Beta")
        player_first = input("Bạn đi trước? (y/n): ").strip().lower().startswith("y")
        turn = 'O' if player_first else 'X'

        while True:
            self.render_board()
            result = self.finish(self.board)
            if result:
                if result == 'Tie':
                    print("Kết thúc: Hòa.")
                else:
                    print(f"Kết thúc: {result} thắng.")
                return

            if turn == 'O':
                move = self.prompt_move()
                if move is None:
                    print("Thoát.")
                    return
                r, c = move
                self.board[r][c] = 'O'
            else:
                move = self.best_move()
                if move is None:
                    print("Không còn nước đi hợp lệ.")
                    return
                r, c = move
                self.board[r][c] = 'X'
                print(f"AI đi: {r + 1} {c + 1}")

            turn = 'X' if turn == 'O' else 'O'

if __name__ == "__main__":
    SIZE = 3
    WIN_STREAK = 3
    MAX_DEPTH = None
    ALPHA_PERCENT = 100
    BETA_PERCENT = 100
    LOG_DEPTH = 6
    LOG_BOARD = False

    game = TicTacToeAlphaBeta(
        size=SIZE,
        win_streak=WIN_STREAK,
        max_depth=MAX_DEPTH,
        alpha_percent=ALPHA_PERCENT,
        beta_percent=BETA_PERCENT,
        verbose=True,
        max_log_depth=LOG_DEPTH,
        log_board=LOG_BOARD,
    )
    game.play_cli()