import math
import random
import time


class SearchTimeout(Exception):
    pass


class XiangqiAlphaBeta:
    MATE_SCORE = 100000

    def __init__(self, alpha_percent=100, beta_percent=100):
        self.board = self.initial()
        self.red_to_move = True
        self.alpha_percent = alpha_percent
        self.beta_percent = beta_percent
        self.init_zobrist()
        self.tt = {}
        self.tt_max = 200000
        self.search_start = 0.0
        self.time_limit = None
        self.verbose = True
        self.max_log_depth = 3
        self.log_board = False
        self.current_search_depth = 0

    def initial(self):
        """Khởi tạo bàn cờ Tướng (10x9)"""
        return [
            ['r', 'n', 'b', 'a', 'k', 'a', 'b', 'n', 'r'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', 'c', ' ', ' ', ' ', ' ', ' ', 'c', ' '],
            ['p', ' ', 'p', ' ', 'p', ' ', 'p', ' ', 'p'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            ['P', ' ', 'P', ' ', 'P', ' ', 'P', ' ', 'P'],
            [' ', 'C', ' ', ' ', ' ', ' ', ' ', 'C', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            ['R', 'N', 'B', 'A', 'K', 'A', 'B', 'N', 'R']
        ]

    def init_zobrist(self):
        rng = random.Random(2026)
        pieces = ['R', 'N', 'B', 'A', 'K', 'C', 'P', 'r', 'n', 'b', 'a', 'k', 'c', 'p']
        self.zobrist_piece = {p: [rng.getrandbits(64) for _ in range(90)] for p in pieces}
        self.zobrist_side = rng.getrandbits(64)

    def compute_hash(self, board, red_to_move):
        h = 0
        for r in range(10):
            for c in range(9):
                piece = board[r][c]
                if piece != ' ':
                    h ^= self.zobrist_piece[piece][r * 9 + c]
        if red_to_move:
            h ^= self.zobrist_side
        return h

    def render_board(self):
        header = "   " + " ".join(str(i + 1) for i in range(9))
        print(header)
        for r in range(10):
            row_cells = []
            for c in range(9):
                cell = self.board[r][c] if self.board[r][c] != ' ' else '.'
                row_cells.append(cell)
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
            row_str = "|".join([cell if cell != ' ' else '.' for cell in row])
            print(f"{prefix}{i + 1}|{row_str}|")

    def format_move(self, move):
        r, c, nr, nc = move
        return f"{r + 1},{c + 1}->{nr + 1},{nc + 1}"

    def in_bounds(self, r, c):
        return 0 <= r < 10 and 0 <= c < 9

    def piece_value(self, piece):
        values = {
            'k': 10000,
            'r': 900,
            'c': 450,
            'n': 400,
            'b': 200,
            'a': 200,
            'p': 100
        }
        return values.get(piece.lower(), 0)

    def score_bounds(self):
        return -self.MATE_SCORE, self.MATE_SCORE

    def evaluate(self, board):
        score = 0
        for r in range(10):
            for c in range(9):
                piece = board[r][c]
                if piece == ' ':
                    continue
                val = self.piece_value(piece)
                if piece.lower() == 'p':
                    if piece.isupper() and r <= 4:
                        val += 50
                    if piece.islower() and r >= 5:
                        val += 50
                if piece.isupper():
                    score += val
                else:
                    score -= val
        return score

    def kings_face(self, board):
        red_pos = None
        black_pos = None
        for r in range(10):
            for c in range(9):
                if board[r][c] == 'K':
                    red_pos = (r, c)
                elif board[r][c] == 'k':
                    black_pos = (r, c)
        if red_pos is None or black_pos is None:
            return False
        if red_pos[1] != black_pos[1]:
            return False
        col = red_pos[1]
        step = 1 if red_pos[0] < black_pos[0] else -1
        for r in range(red_pos[0] + step, black_pos[0], step):
            if board[r][col] != ' ':
                return False
        return True

    def is_square_attacked(self, board, r, c, by_red):
        enemy_rook = 'R' if by_red else 'r'
        enemy_cannon = 'C' if by_red else 'c'
        enemy_horse = 'N' if by_red else 'n'
        enemy_elephant = 'B' if by_red else 'b'
        enemy_advisor = 'A' if by_red else 'a'
        enemy_king = 'K' if by_red else 'k'
        enemy_pawn = 'P' if by_red else 'p'

        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr, nc):
                piece = board[nr][nc]
                if piece != ' ':
                    if piece == enemy_rook:
                        return True
                    break
                nr += dr
                nc += dc

        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            screen_found = False
            while self.in_bounds(nr, nc):
                piece = board[nr][nc]
                if piece != ' ':
                    if not screen_found:
                        screen_found = True
                    else:
                        if piece == enemy_cannon:
                            return True
                        break
                nr += dr
                nc += dc

        horse_steps = [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]
        for dr, dc in horse_steps:
            nr, nc = r + dr, c + dc
            if not self.in_bounds(nr, nc):
                continue
            leg_r, leg_c = (r + dr // 2, c) if abs(dr) == 2 else (r, c + dc // 2)
            if board[leg_r][leg_c] != ' ':
                continue
            if board[nr][nc] == enemy_horse:
                return True

        for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            nr, nc = r + dr, c + dc
            mid_r, mid_c = r + dr // 2, c + dc // 2
            if not self.in_bounds(nr, nc):
                continue
            if board[mid_r][mid_c] != ' ':
                continue
            if by_red and nr < 5:
                continue
            if (not by_red) and nr > 4:
                continue
            if board[nr][nc] == enemy_elephant:
                return True

        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = r + dr, c + dc
            if not self.in_bounds(nr, nc):
                continue
            if by_red and not (7 <= nr <= 9 and 3 <= nc <= 5):
                continue
            if (not by_red) and not (0 <= nr <= 2 and 3 <= nc <= 5):
                continue
            if board[nr][nc] == enemy_advisor:
                return True

        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            if not self.in_bounds(nr, nc):
                continue
            if by_red and not (7 <= nr <= 9 and 3 <= nc <= 5):
                continue
            if (not by_red) and not (0 <= nr <= 2 and 3 <= nc <= 5):
                continue
            if board[nr][nc] == enemy_king:
                return True

        if by_red:
            pr = r + 1
            if self.in_bounds(pr, c) and board[pr][c] == enemy_pawn:
                return True
            if r <= 4:
                for dc in (-1, 1):
                    pc = c + dc
                    if self.in_bounds(r, pc) and board[r][pc] == enemy_pawn:
                        return True
        else:
            pr = r - 1
            if self.in_bounds(pr, c) and board[pr][c] == enemy_pawn:
                return True
            if r >= 5:
                for dc in (-1, 1):
                    pc = c + dc
                    if self.in_bounds(r, pc) and board[r][pc] == enemy_pawn:
                        return True

        return False

    def is_in_check(self, board, red_to_move):
        king = 'K' if red_to_move else 'k'
        for r in range(10):
            for c in range(9):
                if board[r][c] == king:
                    if self.kings_face(board):
                        return True
                    return self.is_square_attacked(board, r, c, not red_to_move)
        return False

    def apply_move(self, board, r, c, nr, nc):
        new_board = [row[:] for row in board]
        new_board[nr][nc] = new_board[r][c]
        new_board[r][c] = ' '
        return new_board

    def generate_piece_moves(self, board, r, c, piece, red_to_move):
        moves = []
        p = piece.lower()

        if p == 'r':
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                while self.in_bounds(nr, nc):
                    target = board[nr][nc]
                    if target == ' ':
                        moves.append((r, c, nr, nc))
                    else:
                        if target.islower() if red_to_move else target.isupper():
                            moves.append((r, c, nr, nc))
                        break
                    nr += dr
                    nc += dc

        elif p == 'c':
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                screen_found = False
                while self.in_bounds(nr, nc):
                    target = board[nr][nc]
                    if not screen_found:
                        if target == ' ':
                            moves.append((r, c, nr, nc))
                        else:
                            screen_found = True
                    else:
                        if target != ' ':
                            if target.islower() if red_to_move else target.isupper():
                                moves.append((r, c, nr, nc))
                            break
                    nr += dr
                    nc += dc

        elif p == 'n':
            for dr, dc in [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]:
                nr, nc = r + dr, c + dc
                if not self.in_bounds(nr, nc):
                    continue
                leg_r, leg_c = (r + dr // 2, c) if abs(dr) == 2 else (r, c + dc // 2)
                if board[leg_r][leg_c] != ' ':
                    continue
                target = board[nr][nc]
                if target == ' ' or (target.islower() if red_to_move else target.isupper()):
                    moves.append((r, c, nr, nc))

        elif p == 'b':
            for dr, dc in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
                nr, nc = r + dr, c + dc
                mid_r, mid_c = r + dr // 2, c + dc // 2
                if not self.in_bounds(nr, nc):
                    continue
                if board[mid_r][mid_c] != ' ':
                    continue
                if red_to_move and nr < 5:
                    continue
                if (not red_to_move) and nr > 4:
                    continue
                target = board[nr][nc]
                if target == ' ' or (target.islower() if red_to_move else target.isupper()):
                    moves.append((r, c, nr, nc))

        elif p == 'a':
            for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                nr, nc = r + dr, c + dc
                if not self.in_bounds(nr, nc):
                    continue
                if red_to_move and not (7 <= nr <= 9 and 3 <= nc <= 5):
                    continue
                if (not red_to_move) and not (0 <= nr <= 2 and 3 <= nc <= 5):
                    continue
                target = board[nr][nc]
                if target == ' ' or (target.islower() if red_to_move else target.isupper()):
                    moves.append((r, c, nr, nc))

        elif p == 'k':
            for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nr, nc = r + dr, c + dc
                if not self.in_bounds(nr, nc):
                    continue
                if red_to_move and not (7 <= nr <= 9 and 3 <= nc <= 5):
                    continue
                if (not red_to_move) and not (0 <= nr <= 2 and 3 <= nc <= 5):
                    continue
                target = board[nr][nc]
                if target == ' ' or (target.islower() if red_to_move else target.isupper()):
                    moves.append((r, c, nr, nc))

        elif p == 'p':
            dr = -1 if red_to_move else 1
            nr, nc = r + dr, c
            if self.in_bounds(nr, nc):
                target = board[nr][nc]
                if target == ' ' or (target.islower() if red_to_move else target.isupper()):
                    moves.append((r, c, nr, nc))
            crossed = r <= 4 if red_to_move else r >= 5
            if crossed:
                for dc in (-1, 1):
                    nr, nc = r, c + dc
                    if self.in_bounds(nr, nc):
                        target = board[nr][nc]
                        if target == ' ' or (target.islower() if red_to_move else target.isupper()):
                            moves.append((r, c, nr, nc))

        return moves

    def generate_legal_moves(self, board, red_to_move):
        moves = []
        for r in range(10):
            for c in range(9):
                piece = board[r][c]
                if piece == ' ':
                    continue
                if red_to_move and not piece.isupper():
                    continue
                if (not red_to_move) and not piece.islower():
                    continue
                for move in self.generate_piece_moves(board, r, c, piece, red_to_move):
                    new_board = self.apply_move(board, move[0], move[1], move[2], move[3])
                    if not self.is_in_check(new_board, red_to_move):
                        moves.append(move)
        return moves

    def score_move(self, board, move):
        r, c, nr, nc = move
        target = board[nr][nc]
        if target == ' ':
            return 0
        return 10 * self.piece_value(target)

    def order_moves(self, board, moves):
        return sorted(moves, key=lambda m: self.score_move(board, m), reverse=True)

    def negamax(self, board, depth, alpha, beta, red_to_move):
        if self.time_limit is not None and (time.time() - self.search_start) >= self.time_limit:
            raise SearchTimeout()

        depth_from_root = max(self.current_search_depth - depth, 0)
        side = "Do" if red_to_move else "Den"
        self.log_step(depth_from_root, f"{side} dang xem (con {depth})")
        if self.log_board and self.should_log(depth_from_root):
            self.print_board_fancy(board, indent=(depth_from_root + 1) * 4)

        hash_key = self.compute_hash(board, red_to_move)
        tt_entry = self.tt.get(hash_key)
        if tt_entry is not None:
            entry_depth, entry_score, entry_flag = tt_entry
            if entry_depth >= depth:
                if entry_flag == "EXACT":
                    return entry_score
                if entry_flag == "LOWER" and entry_score > alpha:
                    alpha = entry_score
                elif entry_flag == "UPPER" and entry_score < beta:
                    beta = entry_score
                if alpha >= beta:
                    return entry_score

        if depth == 0:
            score = self.evaluate(board)
            self.log_step(depth_from_root, f"Dung: Luong gia = {score}")
            return score if red_to_move else -score

        moves = self.generate_legal_moves(board, red_to_move)
        if not moves:
            if self.is_in_check(board, red_to_move):
                self.log_step(depth_from_root, "Dung: Chieu bi")
                return -self.MATE_SCORE + depth
            self.log_step(depth_from_root, "Dung: Hoa (stalemate)")
            return 0

        moves = self.order_moves(board, moves)
        best_score = -math.inf
        best_flag = "UPPER"

        for move in moves:
            self.log_step(depth_from_root, f"-> Thu {self.format_move(move)}")
            new_board = self.apply_move(board, move[0], move[1], move[2], move[3])
            score = -self.negamax(new_board, depth - 1, -beta, -alpha, not red_to_move)
            self.log_step(depth_from_root, f"   <= Diem: {score}")
            if score > best_score:
                best_score = score
            if score > alpha:
                alpha = score
                best_flag = "EXACT"
            if alpha >= beta:
                self.log_step(depth_from_root, f"   Cat tia: alpha({alpha}) >= beta({beta})")
                best_flag = "LOWER"
                break

        if len(self.tt) >= self.tt_max:
            self.tt.clear()
        self.tt[hash_key] = (depth, best_score, best_flag)
        return best_score

    def search_best_move(self, max_depth=3, time_limit=2.0):
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
                moves = self.generate_legal_moves(self.board, self.red_to_move)
                moves = self.order_moves(self.board, moves)
                current_best = None
                current_score = -math.inf

                for move in moves:
                    self.log_step(0, f"-> Xet {self.format_move(move)}")
                    new_board = self.apply_move(self.board, move[0], move[1], move[2], move[3])
                    score = -self.negamax(new_board, depth - 1, -beta_init, -alpha_init, not self.red_to_move)
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
            text = input("Nhập nước đi (hàng cột hàng2 cột2) hoặc q: ").strip().lower()
            if text in ("q", "quit", "exit"):
                return None
            parts = text.split()
            if len(parts) != 4:
                print("Nhập sai. Ví dụ: 10 1 9 1")
                continue
            try:
                r, c, nr, nc = [int(p) - 1 for p in parts]
            except ValueError:
                print("Số không hợp lệ.")
                continue
            if self.in_bounds(r, c) and self.in_bounds(nr, nc):
                return (r, c, nr, nc)
            print("Nước đi không hợp lệ.")

    def play_cli(self, max_depth=3, time_limit=2.0, human_is_red=None):
        print("Demo Cờ Tướng Alpha-Beta (luật đầy đủ)")
        if human_is_red is None:
            human_is_red = input("Bạn chơi Đỏ? (y/n): ").strip().lower().startswith("y")

        while True:
            self.render_board()
            legal_moves = self.generate_legal_moves(self.board, self.red_to_move)
            if not legal_moves:
                if self.is_in_check(self.board, self.red_to_move):
                    winner = "Đen" if self.red_to_move else "Đỏ"
                    print(f"Chiếu bí. {winner} thắng.")
                else:
                    print("Hòa (Stalemate).")
                return

            if self.red_to_move == human_is_red:
                move = self.prompt_move()
                if move is None:
                    print("Thoát.")
                    return
                if move not in legal_moves:
                    print("Nước đi không hợp lệ.")
                    continue
                self.board = self.apply_move(self.board, move[0], move[1], move[2], move[3])
            else:
                best_move, _ = self.search_best_move(max_depth=max_depth, time_limit=time_limit)
                if best_move is None:
                    print("Không còn nước đi hợp lệ.")
                    return
                self.board = self.apply_move(self.board, best_move[0], best_move[1], best_move[2], best_move[3])
                print(f"AI đi: {best_move[0] + 1} {best_move[1] + 1} -> {best_move[2] + 1} {best_move[3] + 1}")

            self.red_to_move = not self.red_to_move


if __name__ == "__main__":
    MAX_DEPTH = 3
    TIME_LIMIT = 2.0
    ALPHA_PERCENT = 100
    BETA_PERCENT = 100
    LOG_DEPTH = 3
    LOG_BOARD = False
    HUMAN_IS_RED = None

    game = XiangqiAlphaBeta(alpha_percent=ALPHA_PERCENT, beta_percent=BETA_PERCENT)
    game.verbose = True
    game.max_log_depth = LOG_DEPTH
    game.log_board = LOG_BOARD
    game.play_cli(max_depth=MAX_DEPTH, time_limit=TIME_LIMIT, human_is_red=HUMAN_IS_RED)