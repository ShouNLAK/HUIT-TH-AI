import tkinter as tk
from tkinter import messagebox
import math

class TicTacToeGUI:
    def __init__(self, root, verbose=True, max_log_depth=4, log_board=False):
        self.root = root
        self.root.title("TicTacToe - AI Đồ Họa")
        self.board = self.initial()
        self.buttons = [[None for _ in range(3)] for _ in range(3)]
        self.ai_algorithm = "minimax"
        self.verbose = verbose
        self.max_log_depth = max_log_depth
        self.log_board = log_board
        self.create_board_ui()
    
    def initial(self):
        """Khởi tạo trạng thái bàn cờ trong RAM"""
        return [[' ' for _ in range(3)] for _ in range(3)]

    def create_board_ui(self):
        """Khởi tạo UI nút bấm"""
        for r in range(3):
            for c in range(3):
                btn = tk.Button(self.root, text=' ', font=('Consolas', 40), width=5, height=2,
                                command=lambda row=r, col=c: self.player_click(row, col))
                btn.grid(row=r, column=c)
                self.buttons[r][c] = btn

    def log(self, actor, r, c):
        """Ghi nhận tiến trình chơi ra console"""
        print(f"[GUI LOG]: Lượt {actor} đánh vào ô ({r}, {c})")

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

    def finish(self, board=None):
        """Kiểm tra và hiển thị kết quả lên màn hình"""
        if board is None:
            board = self.board
        for i in range(3):
            if board[i][0] == board[i][1] == board[i][2] != ' ': return board[i][0]
            if board[0][i] == board[1][i] == board[2][i] != ' ': return board[0][i]
        if board[0][0] == board[1][1] == board[2][2] != ' ': return board[0][0]
        if board[0][2] == board[1][1] == board[2][0] != ' ': return board[0][2]
        if all(cell != ' ' for row in board for cell in row): return 'Tie'
        return None

    def check_game_over(self):
        result = self.finish()
        if result:
            if result == 'Tie': messagebox.showinfo("Kết thúc", "Trò chơi hòa!")
            else: messagebox.showinfo("Kết thúc", f"Bên {result} chiến thắng!")
            self.root.quit()
            return True
        return False

    def player_click(self, r, c):
        if self.board[r][c] == ' ' and not self.check_game_over():
            # Cập nhật mảng & UI cho Player
            self.board[r][c] = 'O'
            self.buttons[r][c].config(text='O', fg='blue')
            self.log("Player (O)", r, c)
            
            if self.check_game_over(): return
            
            # Kích hoạt AI đánh ngay sau đó
            self.root.after(200, self.ai_move)

    def get_empty_cells(self, board):
        return [(r, c) for r in range(3) for c in range(3) if board[r][c] == ' ']

    def minimax(self, board, depth, is_maximizing):
        result = self.finish(board)
        if result == 'X':
            self.log_step(depth, "Dung: X thang")
            return 10 - depth
        if result == 'O':
            self.log_step(depth, "Dung: O thang")
            return -10 + depth
        if result == 'Tie':
            self.log_step(depth, "Dung: Hoa")
            return 0

        actor = "MAX (X)" if is_maximizing else "MIN (O)"
        self.log_step(depth, f"{actor} dang xem (do sau {depth})")

        if is_maximizing:
            best_score = -math.inf
            for r, c in self.get_empty_cells(board):
                self.log_step(depth, f"-> {actor} thu o ({r + 1},{c + 1})")
                board[r][c] = 'X'
                if self.log_board and self.should_log(depth):
                    self.print_board_fancy(board, indent=(depth + 1) * 4)
                score = self.minimax(board, depth + 1, False)
                board[r][c] = ' '
                self.log_step(depth, f"   <= Diem tra ve: {score}")
                best_score = max(best_score, score)
            return best_score
        else:
            best_score = math.inf
            for r, c in self.get_empty_cells(board):
                self.log_step(depth, f"-> {actor} thu o ({r + 1},{c + 1})")
                board[r][c] = 'O'
                if self.log_board and self.should_log(depth):
                    self.print_board_fancy(board, indent=(depth + 1) * 4)
                score = self.minimax(board, depth + 1, True)
                board[r][c] = ' '
                self.log_step(depth, f"   <= Diem tra ve: {score}")
                best_score = min(best_score, score)
            return best_score

    def alphabeta(self, board, depth, alpha, beta, is_maximizing):
        result = self.finish(board)
        if result == 'X':
            self.log_step(depth, "Dung: X thang")
            return 10 - depth
        if result == 'O':
            self.log_step(depth, "Dung: O thang")
            return -10 + depth
        if result == 'Tie':
            self.log_step(depth, "Dung: Hoa")
            return 0

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
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    self.log_step(depth, f"   Cat tia: beta({beta}) <= alpha({alpha})")
                    break
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
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    self.log_step(depth, f"   Cat tia: beta({beta}) <= alpha({alpha})")
                    break
            return best_score

    def ai_move(self):
        """AI sử dụng Minimax/Alpha-Beta để phản hồi"""
        if self.check_game_over():
            return

        best_score = -math.inf
        best_move = None
        for r, c in self.get_empty_cells(self.board):
            self.log_step(0, f"[GOC] Xet nuoc ({r + 1},{c + 1})")
            self.board[r][c] = 'X'
            if self.ai_algorithm == "alphabeta":
                score = self.alphabeta(self.board, 0, -math.inf, math.inf, False)
            else:
                score = self.minimax(self.board, 0, False)
            self.board[r][c] = ' '
            self.log_step(0, f"   => Diem: {score}")
            if score > best_score:
                best_score, best_move = score, (r, c)

        if best_move:
            r, c = best_move
            self.board[r][c] = 'X'
            self.buttons[r][c].config(text='X', fg='red')
            self.log("AI (X)", r, c)
            self.log_step(0, f"[QUYET DINH] Chon ({r + 1},{c + 1}) voi diem {best_score}")
            self.check_game_over()

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()