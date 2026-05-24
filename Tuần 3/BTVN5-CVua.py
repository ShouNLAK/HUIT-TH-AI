import math
import random
import time


class SearchTimeout(Exception):
    pass


class ChessAlphaBeta:
    MATE_SCORE = 100000

    def __init__(self, alpha_percent=100, beta_percent=100):
        self.board = self.initial()
        self.white_to_move = True
        self.castling_rights = 0b1111
        self.en_passant = None
        self.halfmove_clock = 0
        self.fullmove_number = 1
        self.alpha_percent = alpha_percent
        self.beta_percent = beta_percent
        self.init_zobrist()
        self.tt = {}
        self.tt_max = 200000
        self.search_start = 0.0
        self.time_limit = None
        self.history = {}
        self.position_hash = self.compute_hash(self.board, self.white_to_move, self.castling_rights, self.en_passant)
        self.history[self.position_hash] = 1
        self.verbose = True
        self.max_log_depth = 3
        self.log_board = False
        self.current_search_depth = 0

    def initial(self):
        """Khởi tạo bàn cờ Vua (mảng 8x8)"""
        return [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]

    def init_zobrist(self):
        rng = random.Random(2026)
        pieces = ['P', 'N', 'B', 'R', 'Q', 'K', 'p', 'n', 'b', 'r', 'q', 'k']
        self.zobrist_piece = {p: [rng.getrandbits(64) for _ in range(64)] for p in pieces}
        self.zobrist_castling = [rng.getrandbits(64) for _ in range(16)]
        self.zobrist_ep = [rng.getrandbits(64) for _ in range(8)]
        self.zobrist_side = rng.getrandbits(64)

    def compute_hash(self, board, white_to_move, castling_rights, en_passant):
        h = 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece != ' ':
                    h ^= self.zobrist_piece[piece][r * 8 + c]
        h ^= self.zobrist_castling[castling_rights]
        if en_passant is not None:
            h ^= self.zobrist_ep[en_passant[1]]
        if white_to_move:
            h ^= self.zobrist_side
        return h

    def render_board(self):
        header = "   " + " ".join(str(i + 1) for i in range(8))
        print(header)
        for r in range(8):
            row_cells = []
            for c in range(8):
                cell = self.board[r][c] if self.board[r][c] != ' ' else '.'
                row_cells.append(cell)
            print(f"{r + 1}  " + " ".join(row_cells))

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
        r, c, nr, nc, promo, is_castle, is_ep = move
        move_str = f"{r + 1},{c + 1}->{nr + 1},{nc + 1}"
        if promo:
            move_str += f"={promo}"
        if is_castle:
            move_str += " (nhap thanh)"
        if is_ep:
            move_str += " (bat qua duong)"
        return move_str

    def piece_value(self, piece):
        values = {
            'p': 100,
            'n': 320,
            'b': 330,
            'r': 500,
            'q': 900,
            'k': 0
        }
        return values.get(piece.lower(), 0)

    def score_bounds(self):
        return -self.MATE_SCORE, self.MATE_SCORE

    def evaluate(self, board):
        score = 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == ' ':
                    continue
                val = self.piece_value(piece)
                if piece == 'P':
                    val += (6 - r) * 2
                elif piece == 'p':
                    val += (r - 1) * 2
                if piece.isupper():
                    score += val
                else:
                    score -= val
        return score

    def in_bounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def is_square_attacked(self, board, r, c, by_white):
        pawn = 'P' if by_white else 'p'
        pawn_dir = -1 if by_white else 1
        for dc in (-1, 1):
            pr, pc = r - pawn_dir, c + dc
            if self.in_bounds(pr, pc) and board[pr][pc] == pawn:
                return True

        knight = 'N' if by_white else 'n'
        for dr, dc in [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]:
            nr, nc = r + dr, c + dc
            if self.in_bounds(nr, nc) and board[nr][nc] == knight:
                return True

        bishop = 'B' if by_white else 'b'
        rook = 'R' if by_white else 'r'
        queen = 'Q' if by_white else 'q'
        king = 'K' if by_white else 'k'

        for dr, dc in [(1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr, nc):
                piece = board[nr][nc]
                if piece != ' ':
                    if piece == bishop or piece == queen:
                        return True
                    break
                nr += dr
                nc += dc

        for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nr, nc = r + dr, c + dc
            while self.in_bounds(nr, nc):
                piece = board[nr][nc]
                if piece != ' ':
                    if piece == rook or piece == queen:
                        return True
                    break
                nr += dr
                nc += dc

        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.in_bounds(nr, nc) and board[nr][nc] == king:
                    return True

        return False

    def is_in_check(self, board, white_to_move):
        king = 'K' if white_to_move else 'k'
        for r in range(8):
            for c in range(8):
                if board[r][c] == king:
                    return self.is_square_attacked(board, r, c, not white_to_move)
        return False

    def update_castling_rights(self, rights, piece, r, c, captured, nr, nc):
        if piece == 'K':
            rights &= ~0b0011
        elif piece == 'k':
            rights &= ~0b1100
        elif piece == 'R':
            if r == 7 and c == 0:
                rights &= ~0b0010
            elif r == 7 and c == 7:
                rights &= ~0b0001
        elif piece == 'r':
            if r == 0 and c == 0:
                rights &= ~0b1000
            elif r == 0 and c == 7:
                rights &= ~0b0100

        if captured == 'R':
            if nr == 7 and nc == 0:
                rights &= ~0b0010
            elif nr == 7 and nc == 7:
                rights &= ~0b0001
        elif captured == 'r':
            if nr == 0 and nc == 0:
                rights &= ~0b1000
            elif nr == 0 and nc == 7:
                rights &= ~0b0100

        return rights

    def make_move(self, board, move, white_to_move, castling_rights, en_passant, halfmove, fullmove):
        r, c, nr, nc, promo, is_castle, is_ep = move
        new_board = [row[:] for row in board]
        piece = new_board[r][c]
        captured = new_board[nr][nc]

        if is_ep:
            captured_r = r
            new_board[captured_r][nc] = ' '
            captured = 'p' if white_to_move else 'P'

        new_board[r][c] = ' '
        new_board[nr][nc] = piece

        if promo:
            new_board[nr][nc] = promo

        if is_castle:
            if nc == 6:
                rook_from, rook_to = (r, 7), (r, 5)
            else:
                rook_from, rook_to = (r, 0), (r, 3)
            rook_piece = new_board[rook_from[0]][rook_from[1]]
            new_board[rook_from[0]][rook_from[1]] = ' '
            new_board[rook_to[0]][rook_to[1]] = rook_piece

        new_castling = self.update_castling_rights(castling_rights, piece, r, c, captured, nr, nc)

        new_en_passant = None
        if piece.lower() == 'p' and abs(nr - r) == 2:
            new_en_passant = ((r + nr) // 2, c)

        if piece.lower() == 'p' or captured != ' ':
            new_halfmove = 0
        else:
            new_halfmove = halfmove + 1

        new_fullmove = fullmove + (0 if white_to_move else 1)

        return new_board, new_castling, new_en_passant, new_halfmove, new_fullmove

    def generate_pseudo_moves(self, board, white_to_move, castling_rights, en_passant):
        moves = []
        in_check = self.is_in_check(board, white_to_move)

        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == ' ':
                    continue
                if white_to_move and not piece.isupper():
                    continue
                if (not white_to_move) and not piece.islower():
                    continue

                p = piece.lower()
                if p == 'p':
                    direction = -1 if white_to_move else 1
                    start_row = 6 if white_to_move else 1
                    promo_row = 0 if white_to_move else 7

                    nr, nc = r + direction, c
                    if self.in_bounds(nr, nc) and board[nr][nc] == ' ':
                        if nr == promo_row:
                            for promo in ('Q', 'R', 'B', 'N') if white_to_move else ('q', 'r', 'b', 'n'):
                                moves.append((r, c, nr, nc, promo, False, False))
                        else:
                            moves.append((r, c, nr, nc, None, False, False))
                            nr2 = r + 2 * direction
                            if r == start_row and board[nr2][nc] == ' ':
                                moves.append((r, c, nr2, nc, None, False, False))

                    for dc in (-1, 1):
                        nr, nc = r + direction, c + dc
                        if not self.in_bounds(nr, nc):
                            continue
                        target = board[nr][nc]
                        if target != ' ' and (target.islower() if white_to_move else target.isupper()):
                            if nr == promo_row:
                                for promo in ('Q', 'R', 'B', 'N') if white_to_move else ('q', 'r', 'b', 'n'):
                                    moves.append((r, c, nr, nc, promo, False, False))
                            else:
                                moves.append((r, c, nr, nc, None, False, False))

                    if en_passant is not None:
                        if en_passant == (r + direction, c - 1) or en_passant == (r + direction, c + 1):
                            moves.append((r, c, en_passant[0], en_passant[1], None, False, True))

                elif p == 'n':
                    for dr, dc in [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)]:
                        nr, nc = r + dr, c + dc
                        if not self.in_bounds(nr, nc):
                            continue
                        target = board[nr][nc]
                        if target == ' ' or (target.islower() if white_to_move else target.isupper()):
                            moves.append((r, c, nr, nc, None, False, False))

                elif p in ('b', 'r', 'q'):
                    directions = []
                    if p in ('b', 'q'):
                        directions += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
                    if p in ('r', 'q'):
                        directions += [(1, 0), (-1, 0), (0, 1), (0, -1)]
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        while self.in_bounds(nr, nc):
                            target = board[nr][nc]
                            if target == ' ':
                                moves.append((r, c, nr, nc, None, False, False))
                            else:
                                if target.islower() if white_to_move else target.isupper():
                                    moves.append((r, c, nr, nc, None, False, False))
                                break
                            nr += dr
                            nc += dc

                elif p == 'k':
                    for dr in (-1, 0, 1):
                        for dc in (-1, 0, 1):
                            if dr == 0 and dc == 0:
                                continue
                            nr, nc = r + dr, c + dc
                            if not self.in_bounds(nr, nc):
                                continue
                            target = board[nr][nc]
                            if target == ' ' or (target.islower() if white_to_move else target.isupper()):
                                moves.append((r, c, nr, nc, None, False, False))

                    if not in_check:
                        if white_to_move:
                            if castling_rights & 0b0001:
                                if board[7][5] == ' ' and board[7][6] == ' ':
                                    if not self.is_square_attacked(board, 7, 5, False) and not self.is_square_attacked(board, 7, 6, False):
                                        moves.append((7, 4, 7, 6, None, True, False))
                            if castling_rights & 0b0010:
                                if board[7][1] == ' ' and board[7][2] == ' ' and board[7][3] == ' ':
                                    if not self.is_square_attacked(board, 7, 3, False) and not self.is_square_attacked(board, 7, 2, False):
                                        moves.append((7, 4, 7, 2, None, True, False))
                        else:
                            if castling_rights & 0b0100:
                                if board[0][5] == ' ' and board[0][6] == ' ':
                                    if not self.is_square_attacked(board, 0, 5, True) and not self.is_square_attacked(board, 0, 6, True):
                                        moves.append((0, 4, 0, 6, None, True, False))
                            if castling_rights & 0b1000:
                                if board[0][1] == ' ' and board[0][2] == ' ' and board[0][3] == ' ':
                                    if not self.is_square_attacked(board, 0, 3, True) and not self.is_square_attacked(board, 0, 2, True):
                                        moves.append((0, 4, 0, 2, None, True, False))

        return moves

    def generate_legal_moves(self, board, white_to_move, castling_rights, en_passant, halfmove, fullmove):
        moves = self.generate_pseudo_moves(board, white_to_move, castling_rights, en_passant)
        legal = []
        for move in moves:
            new_board, new_castling, new_ep, new_half, new_full = self.make_move(
                board, move, white_to_move, castling_rights, en_passant, halfmove, fullmove
            )
            if not self.is_in_check(new_board, white_to_move):
                legal.append(move)
        return legal

    def score_move(self, board, move):
        r, c, nr, nc, promo, is_castle, is_ep = move
        score = 0
        target = board[nr][nc]
        if is_ep:
            target = 'p' if board[r][c].isupper() else 'P'
        if target != ' ':
            score += 10 * self.piece_value(target)
        if promo:
            score += 900
        if is_castle:
            score += 50
        return score

    def order_moves(self, board, moves):
        return sorted(moves, key=lambda m: self.score_move(board, m), reverse=True)

    def negamax(self, board, depth, alpha, beta, white_to_move, castling_rights, en_passant, halfmove, fullmove):
        if self.time_limit is not None and (time.time() - self.search_start) >= self.time_limit:
            raise SearchTimeout()

        depth_from_root = max(self.current_search_depth - depth, 0)
        side = "Trang" if white_to_move else "Den"
        self.log_step(depth_from_root, f"{side} dang xem (con {depth})")
        if self.log_board and self.should_log(depth_from_root):
            self.print_board_fancy(board, indent=(depth_from_root + 1) * 4)

        hash_key = self.compute_hash(board, white_to_move, castling_rights, en_passant)
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

        if halfmove >= 100:
            self.log_step(depth_from_root, "Dung: Hoa (50 nuoc)")
            return 0

        if depth == 0:
            val = self.evaluate(board)
            self.log_step(depth_from_root, f"Dung: Luong gia = {val}")
            return val

        moves = self.generate_legal_moves(board, white_to_move, castling_rights, en_passant, halfmove, fullmove)
        if not moves:
            if self.is_in_check(board, white_to_move):
                self.log_step(depth_from_root, "Dung: Chieu bi")
                return -self.MATE_SCORE + depth
            self.log_step(depth_from_root, "Dung: Hoa (stalemate)")
            return 0

        moves = self.order_moves(board, moves)
        best_score = -math.inf
        best_flag = "UPPER"

        for move in moves:
            self.log_step(depth_from_root, f"-> Thu {self.format_move(move)}")
            new_board, new_castling, new_ep, new_half, new_full = self.make_move(
                board, move, white_to_move, castling_rights, en_passant, halfmove, fullmove
            )
            score = -self.negamax(new_board, depth - 1, -beta, -alpha, not white_to_move, new_castling, new_ep, new_half, new_full)
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
                moves = self.generate_legal_moves(
                    self.board, self.white_to_move, self.castling_rights, self.en_passant, self.halfmove_clock, self.fullmove_number
                )
                moves = self.order_moves(self.board, moves)
                current_best = None
                current_score = -math.inf

                for move in moves:
                    self.log_step(0, f"-> Xet {self.format_move(move)}")
                    new_board, new_castling, new_ep, new_half, new_full = self.make_move(
                        self.board, move, self.white_to_move, self.castling_rights, self.en_passant, self.halfmove_clock, self.fullmove_number
                    )
                    score = -self.negamax(new_board, depth - 1, -beta_init, -alpha_init, not self.white_to_move, new_castling, new_ep, new_half, new_full)
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

    def update_history(self):
        self.position_hash = self.compute_hash(self.board, self.white_to_move, self.castling_rights, self.en_passant)
        self.history[self.position_hash] = self.history.get(self.position_hash, 0) + 1

    def is_draw_by_repetition(self):
        return self.history.get(self.position_hash, 0) >= 3

    def prompt_move(self):
        while True:
            text = input("Nhập nước đi (hàng cột hàng2 cột2) hoặc q: ").strip().lower()
            if text in ("q", "quit", "exit"):
                return None
            parts = text.split()
            if len(parts) != 4:
                print("Nhập sai. Ví dụ: 2 1 3 1")
                continue
            try:
                r, c, nr, nc = [int(p) - 1 for p in parts]
            except ValueError:
                print("Số không hợp lệ.")
                continue
            if self.in_bounds(r, c) and self.in_bounds(nr, nc):
                return (r, c, nr, nc)
            print("Nước đi không hợp lệ.")

    def pick_promotion(self, is_white):
        while True:
            text = input("Chọn phong cấp (q/r/b/n): ").strip().lower()
            if text in ("q", "r", "b", "n"):
                return text.upper() if is_white else text
            print("Lựa chọn không hợp lệ.")

    def play_cli(self, max_depth=3, time_limit=2.0, human_is_white=None):
        print("Demo Cờ Vua Alpha-Beta (luật đầy đủ)")
        if human_is_white is None:
            human_is_white = input("Bạn chơi Trắng? (y/n): ").strip().lower().startswith("y")

        while True:
            self.render_board()
            legal_moves = self.generate_legal_moves(
                self.board, self.white_to_move, self.castling_rights, self.en_passant, self.halfmove_clock, self.fullmove_number
            )
            if not legal_moves:
                if self.is_in_check(self.board, self.white_to_move):
                    winner = "Đen" if self.white_to_move else "Trắng"
                    print(f"Chiếu bí. {winner} thắng.")
                else:
                    print("Hòa (Stalemate).")
                return

            if self.is_draw_by_repetition() or self.halfmove_clock >= 100:
                print("Hòa (lặp lại hoặc 50 nước).")
                return

            if self.white_to_move == human_is_white:
                move = self.prompt_move()
                if move is None:
                    print("Thoát.")
                    return
                r, c, nr, nc = move

                legal_by_coords = [m for m in legal_moves if m[0] == r and m[1] == c and m[2] == nr and m[3] == nc]
                if not legal_by_coords:
                    print("Nước đi không hợp lệ.")
                    continue

                chosen = legal_by_coords[0]
                if len(legal_by_coords) > 1:
                    promo = self.pick_promotion(self.white_to_move)
                    for m in legal_by_coords:
                        if m[4] == promo:
                            chosen = m
                            break

                self.board, self.castling_rights, self.en_passant, self.halfmove_clock, self.fullmove_number = self.make_move(
                    self.board, chosen, self.white_to_move, self.castling_rights, self.en_passant, self.halfmove_clock, self.fullmove_number
                )
            else:
                best_move, _ = self.search_best_move(max_depth=max_depth, time_limit=time_limit)
                if best_move is None:
                    print("Không còn nước đi hợp lệ.")
                    return
                self.board, self.castling_rights, self.en_passant, self.halfmove_clock, self.fullmove_number = self.make_move(
                    self.board, best_move, self.white_to_move, self.castling_rights, self.en_passant, self.halfmove_clock, self.fullmove_number
                )
                print(f"AI đi: {best_move[0] + 1} {best_move[1] + 1} -> {best_move[2] + 1} {best_move[3] + 1}")

            self.white_to_move = not self.white_to_move
            self.update_history()


if __name__ == "__main__":
    MAX_DEPTH = 3
    TIME_LIMIT = 2.0
    ALPHA_PERCENT = 100
    BETA_PERCENT = 100
    LOG_DEPTH = 3
    LOG_BOARD = False
    HUMAN_IS_WHITE = None

    game = ChessAlphaBeta(alpha_percent=ALPHA_PERCENT, beta_percent=BETA_PERCENT)
    game.verbose = True
    game.max_log_depth = LOG_DEPTH
    game.log_board = LOG_BOARD
    game.play_cli(max_depth=MAX_DEPTH, time_limit=TIME_LIMIT, human_is_white=HUMAN_IS_WHITE)