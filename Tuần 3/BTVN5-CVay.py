import math
import random
import time


class SearchTimeout(Exception):
    pass


class GoAlphaBeta:
    def __init__(self, size=9, alpha_percent=100, beta_percent=100):
        self.size = size
        self.board = self.initial()
        self.black_to_move = True
        self.passes = 0
        self.komi = 6.5
        self.alpha_percent = alpha_percent
        self.beta_percent = beta_percent
        self.init_zobrist()
        self.tt = {}
        self.tt_max = 200000
        self.search_start = 0.0
        self.time_limit = None
        self.history = set()
        self.position_hash = self.compute_hash(self.board, self.black_to_move)
        self.history.add(self.position_hash)
        self.verbose = True
        self.max_log_depth = 3
        self.log_board = False
        self.current_search_depth = 0
        self.verbose = True
        self.max_log_depth = 3
        self.log_board = False
        self.current_search_depth = 0

    def initial(self):
        return [['.' for _ in range(self.size)] for _ in range(self.size)]

    def init_zobrist(self):
        rng = random.Random(2026)
        self.zobrist_piece = {
            'B': [rng.getrandbits(64) for _ in range(self.size * self.size)],
            'W': [rng.getrandbits(64) for _ in range(self.size * self.size)]
        }
        self.zobrist_side = rng.getrandbits(64)

    def compute_hash(self, board, black_to_move):
        h = 0
        for r in range(self.size):
            for c in range(self.size):
                piece = board[r][c]
                if piece == 'B':
                    h ^= self.zobrist_piece['B'][r * self.size + c]
                elif piece == 'W':
                    h ^= self.zobrist_piece['W'][r * self.size + c]
        if black_to_move:
            h ^= self.zobrist_side
        return h

    def render_board(self):
        header = "   " + " ".join(str(i + 1) for i in range(self.size))
        print(header)
        for r in range(self.size):
            row_cells = []
            for c in range(self.size):
                row_cells.append(self.board[r][c])
            print(f"{r + 1:2d} " + " ".join(row_cells))

    def should_log(self, depth_from_root):
        return self.verbose and depth_from_root <= self.max_log_depth

    def log_step(self, depth_from_root, message):
        if not self.should_log(depth_from_root):
            return
        indent = "    " * depth_from_root
        print(f"{indent}{message}")

    def print_board_fancy(self, board, indent=0):
        if not self.verbose or not self.log_board:
            return
        prefix = " " * indent
        for i, row in enumerate(board):
            row_str = "|".join(row)
            print(f"{prefix}{i + 1}|{row_str}|")

    def format_move(self, move):
        if move == 'PASS':
            return "PASS"
        return f"{move[0] + 1},{move[1] + 1}"

    def in_bounds(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size

    def neighbors(self, r, c):
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc):
                yield nr, nc

    def get_group_and_liberties(self, board, r, c):
        color = board[r][c]
        stack = [(r, c)]
        visited = set()
        group = set()
        liberties = set()
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in visited:
                continue
            visited.add((cr, cc))
            group.add((cr, cc))
            for nr, nc in self.neighbors(cr, cc):
                if board[nr][nc] == '.':
                    liberties.add((nr, nc))
                elif board[nr][nc] == color and (nr, nc) not in visited:
                    stack.append((nr, nc))
        return group, liberties

    def remove_group(self, board, group):
        for r, c in group:
            board[r][c] = '.'

    def apply_move(self, board, move, black_to_move, passes, history):
        if move == 'PASS':
            new_passes = passes + 1
            next_black = not black_to_move
            new_hash = self.compute_hash(board, next_black)
            if new_hash in history:
                return board, passes, history, False, black_to_move
            new_history = set(history)
            new_history.add(new_hash)
            return board, new_passes, new_history, True, next_black

        r, c = move
        if board[r][c] != '.':
            return board, passes, history, False, black_to_move

        color = 'B' if black_to_move else 'W'
        opponent = 'W' if color == 'B' else 'B'
        new_board = [row[:] for row in board]
        new_board[r][c] = color

        for nr, nc in self.neighbors(r, c):
            if new_board[nr][nc] == opponent:
                group, libs = self.get_group_and_liberties(new_board, nr, nc)
                if not libs:
                    self.remove_group(new_board, group)

        group, libs = self.get_group_and_liberties(new_board, r, c)
        if not libs:
            return board, passes, history, False, black_to_move

        new_passes = 0
        next_black = not black_to_move
        new_hash = self.compute_hash(new_board, next_black)
        if new_hash in history:
            return board, passes, history, False, black_to_move

        new_history = set(history)
        new_history.add(new_hash)
        return new_board, new_passes, new_history, True, next_black

    def get_candidate_moves(self, board):
        candidates = set()
        has_stone = False
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] != '.':
                    has_stone = True
                    for nr, nc in self.neighbors(r, c):
                        if board[nr][nc] == '.':
                            candidates.add((nr, nc))
        if not has_stone:
            center = self.size // 2
            return [(center, center)]
        if not candidates:
            for r in range(self.size):
                for c in range(self.size):
                    if board[r][c] == '.':
                        candidates.add((r, c))
        return list(candidates)

    def evaluate_fast(self, board):
        black = 0
        white = 0
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] == 'B':
                    black += 1
                elif board[r][c] == 'W':
                    white += 1
        return black - white - self.komi

    def score_bounds(self):
        max_score = self.size * self.size
        return -max_score - self.komi, max_score

    def score_area(self, board):
        black = 0
        white = 0
        visited = set()
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] == 'B':
                    black += 1
                elif board[r][c] == 'W':
                    white += 1
                elif board[r][c] == '.' and (r, c) not in visited:
                    region = []
                    queue = [(r, c)]
                    visited.add((r, c))
                    owners = set()
                    while queue:
                        cr, cc = queue.pop()
                        region.append((cr, cc))
                        for nr, nc in self.neighbors(cr, cc):
                            if board[nr][nc] == '.' and (nr, nc) not in visited:
                                visited.add((nr, nc))
                                queue.append((nr, nc))
                            elif board[nr][nc] in ('B', 'W'):
                                owners.add(board[nr][nc])
                    if len(owners) == 1:
                        owner = owners.pop()
                        if owner == 'B':
                            black += len(region)
                        else:
                            white += len(region)
        return black - white - self.komi

    def negamax(self, board, depth, alpha, beta, black_to_move, passes, history):
        if self.time_limit is not None and (time.time() - self.search_start) >= self.time_limit:
            raise SearchTimeout()

        depth_from_root = max(self.current_search_depth - depth, 0)
        side = "Den" if black_to_move else "Trang"
        self.log_step(depth_from_root, f"{side} dang xem (con {depth})")
        if self.log_board and self.should_log(depth_from_root):
            self.print_board_fancy(board, indent=(depth_from_root + 1) * 4)

        hash_key = self.compute_hash(board, black_to_move)
        tt_entry = self.tt.get((hash_key, depth, passes))
        if tt_entry is not None:
            return tt_entry

        if passes >= 2:
            self.log_step(depth_from_root, "Dung: Ket thuc, tinh diem")
            return self.score_area(board)
        if depth == 0:
            val = self.evaluate_fast(board)
            self.log_step(depth_from_root, f"Dung: Luong gia nhanh = {val}")
            return val

        moves = ['PASS'] + self.get_candidate_moves(board)
        best_score = -math.inf

        for move in moves:
            self.log_step(depth_from_root, f"-> Thu {self.format_move(move)}")
            next_board, next_passes, next_history, valid, next_black = self.apply_move(
                board, move, black_to_move, passes, history
            )
            if not valid:
                continue
            score = -self.negamax(next_board, depth - 1, -beta, -alpha, next_black, next_passes, next_history)
            self.log_step(depth_from_root, f"   <= Diem: {score}")
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score
            if alpha >= beta:
                self.log_step(depth_from_root, f"   Cat tia: alpha({alpha}) >= beta({beta})")
                break

        if len(self.tt) >= self.tt_max:
            self.tt.clear()
        self.tt[(hash_key, depth, passes)] = best_score
        return best_score

    def search_best_move(self, max_depth=2, time_limit=2.0):
        self.search_start = time.time()
        self.time_limit = time_limit
        min_score, max_score = self.score_bounds()
        alpha_init = min_score * (self.alpha_percent / 100.0)
        beta_init = max_score * (self.beta_percent / 100.0)
        if alpha_init >= beta_init:
            alpha_init, beta_init = min_score, max_score
        best_move = None
        best_score = -math.inf

        for depth in range(1, max_depth + 1):
            self.current_search_depth = depth
            self.log_step(0, f"[GOC] Duyet do sau {depth}")
            try:
                moves = ['PASS'] + self.get_candidate_moves(self.board)
                current_best = None
                current_score = -math.inf
                for move in moves:
                    self.log_step(0, f"-> Xet {self.format_move(move)}")
                    next_board, next_passes, next_history, valid, next_black = self.apply_move(
                        self.board, move, self.black_to_move, self.passes, self.history
                    )
                    if not valid:
                        continue
                    score = -self.negamax(next_board, depth - 1, -beta_init, -alpha_init, next_black, next_passes, next_history)
                    self.log_step(0, f"   => Diem: {score}")
                    if score > current_score:
                        current_score = score
                        current_best = move
                if current_best is not None:
                    best_move = current_best
                    best_score = current_score
                    self.log_step(0, f"[GOC] Tam chon: {self.format_move(current_best)} (diem {current_score})")
            except SearchTimeout:
                break

        return best_move, best_score

    def prompt_move(self):
        while True:
            text = input("Nước đi (hàng cột), pass hoặc q: ").strip().lower()
            if text in ("q", "quit", "exit"):
                return None
            if text == "pass":
                return 'PASS'
            parts = text.split()
            if len(parts) != 2:
                print("Nhập sai. Ví dụ: 4 4")
                continue
            try:
                r = int(parts[0]) - 1
                c = int(parts[1]) - 1
            except ValueError:
                print("Số không hợp lệ.")
                continue
            if self.in_bounds(r, c):
                return (r, c)
            print("Nước đi không hợp lệ.")

    def play_cli(self, max_depth=2, time_limit=2.0):
        print("Demo Cờ Vây Alpha-Beta (luật đầy đủ)")
        size_text = input(f"Kích thước bàn (mặc định {self.size}): ").strip()
        if size_text:
            try:
                self.size = int(size_text)
                self.board = self.initial()
                self.history = set()
                self.position_hash = self.compute_hash(self.board, self.black_to_move)
                self.history.add(self.position_hash)
            except ValueError:
                pass
        depth_text = input(f"Độ sâu tối đa (mặc định {max_depth}): ").strip()
        if depth_text:
            try:
                max_depth = int(depth_text)
            except ValueError:
                max_depth = max_depth
        time_text = input(f"Giới hạn thời gian mỗi nước (giây, mặc định {time_limit}): ").strip()
        if time_text:
            try:
                time_limit = float(time_text)
            except ValueError:
                time_limit = time_limit

        log_choice = input("Bat log chi tiet? (y/n, mac dinh y): ").strip().lower()
        if log_choice:
            self.verbose = log_choice.startswith("y")
        if self.verbose:
            depth_text = input(f"Gioi han do sau log (mac dinh {self.max_log_depth}): ").strip()
            if depth_text:
                try:
                    self.max_log_depth = int(depth_text)
                except ValueError:
                    pass
            board_text = input("In ban co khi duyet? (y/n, mac dinh n): ").strip().lower()
            if board_text:
                self.log_board = board_text.startswith("y")

        human_is_black = input("Bạn chơi Đen? (y/n): ").strip().lower().startswith("y")

        while True:
            self.render_board()
            if self.passes >= 2:
                score = self.score_area(self.board)
                if score > 0:
                    print("Kết thúc: Đen thắng.")
                elif score < 0:
                    print("Kết thúc: Trắng thắng.")
                else:
                    print("Kết thúc: Hòa.")
                return

            if self.black_to_move == human_is_black:
                move = self.prompt_move()
                if move is None:
                    print("Thoát.")
                    return
                new_board, new_passes, new_history, valid, next_black = self.apply_move(
                    self.board, move, self.black_to_move, self.passes, self.history
                )
                if not valid:
                    print("Nước đi không hợp lệ.")
                    continue
                self.board = new_board
                self.passes = new_passes
                self.history = new_history
                self.black_to_move = next_black
            else:
                best_move, _ = self.search_best_move(max_depth=max_depth, time_limit=time_limit)
                if best_move is None:
                    print("Không còn nước đi hợp lệ.")
                    return
                new_board, new_passes, new_history, _, next_black = self.apply_move(
                    self.board, best_move, self.black_to_move, self.passes, self.history
                )
                self.board = new_board
                self.passes = new_passes
                self.history = new_history
                self.black_to_move = next_black
                if best_move == 'PASS':
                    print("AI đi: PASS")
                else:
                    print(f"AI đi: {best_move[0] + 1} {best_move[1] + 1}")


if __name__ == "__main__":
    game = GoAlphaBeta(size=9)
    game.play_cli(max_depth=2, time_limit=2.0)