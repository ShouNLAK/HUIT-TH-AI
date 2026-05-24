import math
import time

class MinimaxNxN:
    def __init__(self, size=5, win_streak=4):
        self.N = size
        self.win_streak = win_streak
        self.board = self.initial()
        self.tt = {}
        self.tt_max = 50000
        self.search_start = 0.0
        self.time_limit = None
        self.verbose = True
        self.max_log_depth = 4
        self.log_board = False
    
    def initial(self):
        """Khởi tạo trạng thái bàn cờ NxN"""
        return [[' ' for _ in range(self.N)] for _ in range(self.N)]
    
    def log(self, message):
        """Ghi nhận log bàn cờ"""
        print(f"\n--- BÀI 3 LOG: {message} ({self.N}x{self.N}) ---")
        for row in self.board:
            print("| " + " | ".join(row) + " |")

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
        """Kiểm tra thắng/thua trên ma trận NxN với điều kiện win_streak"""
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for r in range(self.N):
            for c in range(self.N):
                if board[r][c] == ' ': continue
                player = board[r][c]
                for dr, dc in directions:
                    count = 0
                    for i in range(self.win_streak):
                        nr, nc = r + dr * i, c + dc * i
                        if 0 <= nr < self.N and 0 <= nc < self.N and board[nr][nc] == player:
                            count += 1
                        else: break
                    if count == self.win_streak: return player
        if all(cell != ' ' for row in board for cell in row): return 'Tie'
        return None

    def evaluate(self, board):
        """Hàm lượng giá heuristic khi đạt max_depth giới hạn"""
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

    def get_candidate_moves(self, board):
        candidates = set()
        has_stone = False
        for r in range(self.N):
            for c in range(self.N):
                if board[r][c] != ' ':
                    has_stone = True
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < self.N and 0 <= nc < self.N and board[nr][nc] == ' ':
                                candidates.add((nr, nc))
        if not has_stone:
            center = self.N // 2
            return [(center, center)]
        if not candidates:
            return self.get_empty_cells(board)
        return list(candidates)

    def ordered_moves(self, board):
        candidates = set(self.get_candidate_moves(board))
        if len(candidates) == self.N * self.N:
            return list(candidates)
        rest = [m for m in self.get_empty_cells(board) if m not in candidates]
        return list(candidates) + rest

    def minimax_limited(self, board, depth, is_maximizing, max_depth=3):
        """Minimax kết hợp giới hạn độ sâu (Depth-limited Minimax)"""
        if self.time_limit is not None and (time.time() - self.search_start) >= self.time_limit:
            return self.evaluate(board)

        result = self.finish(board)
        if result == 'X':
            self.log_step(depth, "Dung: X thang")
            return 1000 - depth
        if result == 'O':
            self.log_step(depth, "Dung: O thang")
            return -1000 + depth
        if result == 'Tie':
            self.log_step(depth, "Dung: Hoa")
            return 0
        if depth >= max_depth:
            val = self.evaluate(board)
            self.log_step(depth, f"Dung: Het do sau, danh gia = {val}")
            return val

        key = (tuple(tuple(row) for row in board), depth, is_maximizing, max_depth)
        cached = self.tt.get(key)
        if cached is not None:
            return cached

        actor = "MAX (X)" if is_maximizing else "MIN (O)"
        self.log_step(depth, f"{actor} dang xem (do sau {depth})")

        if is_maximizing:
            best_score = -math.inf
            for r, c in self.ordered_moves(board):
                self.log_step(depth, f"-> {actor} thu o ({r + 1},{c + 1})")
                board[r][c] = 'X'
                if self.log_board and self.should_log(depth):
                    self.print_board_fancy(board, indent=(depth + 1) * 4)
                score = self.minimax_limited(board, depth + 1, False, max_depth)
                board[r][c] = ' '
                self.log_step(depth, f"   <= Diem tra ve: {score}")
                best_score = max(score, best_score)
            if len(self.tt) >= self.tt_max:
                self.tt.clear()
            self.tt[key] = best_score
            self.log_step(depth, f"{actor} chon diem {best_score}")
            return best_score
        else:
            best_score = math.inf
            for r, c in self.ordered_moves(board):
                self.log_step(depth, f"-> {actor} thu o ({r + 1},{c + 1})")
                board[r][c] = 'O'
                if self.log_board and self.should_log(depth):
                    self.print_board_fancy(board, indent=(depth + 1) * 4)
                score = self.minimax_limited(board, depth + 1, True, max_depth)
                board[r][c] = ' '
                self.log_step(depth, f"   <= Diem tra ve: {score}")
                best_score = min(score, best_score)
            if len(self.tt) >= self.tt_max:
                self.tt.clear()
            self.tt[key] = best_score
            self.log_step(depth, f"{actor} chon diem {best_score}")
            return best_score

    def best_move(self, max_depth=3, time_limit=None):
        self.search_start = time.time()
        self.time_limit = time_limit
        best_score = -math.inf
        best_move = None
        for r, c in self.ordered_moves(self.board):
            self.log_step(0, f"[GOC] Xet nuoc ({r + 1},{c + 1})")
            self.board[r][c] = 'X'
            score = self.minimax_limited(self.board, 0, False, max_depth)
            self.board[r][c] = ' '
            self.log_step(0, f"   => Diem: {score}")
            if score > best_score:
                best_score, best_move = score, (r, c)
        if best_move is not None:
            self.log_step(0, f"[QUYET DINH] Chon ({best_move[0] + 1},{best_move[1] + 1}) voi diem {best_score}")
        return best_move

    def render_board(self):
        header = "   " + " ".join(f"{i + 1:2d}" for i in range(self.N))
        print(header)
        for r in range(self.N):
            row_cells = []
            for c in range(self.N):
                cell = self.board[r][c] if self.board[r][c] != ' ' else '.'
                row_cells.append(f"{cell:2s}")
            print(f"{r + 1:2d} " + " ".join(row_cells))

    def prompt_move(self):
        while True:
            text = input("Nước đi (hàng cột) hoặc q: ").strip().lower()
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

    def play_cli(self, max_depth=2, time_limit=None, player_first=None):
        print(f"Demo Minimax NxN ({self.N}x{self.N})")
        if max_depth < 1:
            max_depth = 1
        if player_first is None:
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
                move = self.best_move(max_depth=max_depth, time_limit=time_limit)
                if move is None:
                    print("Không còn nước đi hợp lệ.")
                    return
                r, c = move
                self.board[r][c] = 'X'
                print(f"AI đi: {r + 1} {c + 1}")

            turn = 'X' if turn == 'O' else 'O'

if __name__ == "__main__":
    SIZE = 5
    WIN_STREAK = 4
    MAX_DEPTH = 2
    TIME_LIMIT = None
    LOG_DEPTH = 4
    LOG_BOARD = False
    PLAYER_FIRST = None

    game = MinimaxNxN(size=SIZE, win_streak=WIN_STREAK)
    game.verbose = True
    game.max_log_depth = LOG_DEPTH
    game.log_board = LOG_BOARD
    game.play_cli(max_depth=MAX_DEPTH, time_limit=TIME_LIMIT, player_first=PLAYER_FIRST)