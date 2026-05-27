import tkinter as tk
from tkinter import messagebox
import importlib

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe AI Engine GUI")
        
        self.settings_frame = tk.Frame(self.root)
        self.settings_frame.pack(pady=10, padx=10)
        
        tk.Label(self.settings_frame, text="N (Kích thước):").grid(row=0, column=0, sticky="e")
        self.n_var = tk.IntVar(value=3)
        tk.Entry(self.settings_frame, textvariable=self.n_var, width=5).grid(row=0, column=1)
        
        tk.Label(self.settings_frame, text="M (Số ô thắng):").grid(row=0, column=2, sticky="e")
        self.m_var = tk.IntVar(value=3)
        tk.Entry(self.settings_frame, textvariable=self.m_var, width=5).grid(row=0, column=3)
        
        tk.Label(self.settings_frame, text="Depth:").grid(row=0, column=4, sticky="e")
        self.depth_var = tk.IntVar(value=5)
        tk.Entry(self.settings_frame, textvariable=self.depth_var, width=5).grid(row=0, column=5)
        
        tk.Label(self.settings_frame, text="Engine:").grid(row=1, column=0, sticky="e")
        self.engine_var = tk.StringVar(value="Depth")
        tk.OptionMenu(self.settings_frame, self.engine_var, "Depth", "Alpha-Beta-Depth", "Alpha-Beta").grid(row=1, column=1, columnspan=2, sticky="w")
        
        tk.Label(self.settings_frame, text="% Alpha:").grid(row=1, column=3, sticky="e")
        self.alpha_var = tk.DoubleVar(value=100)
        tk.Entry(self.settings_frame, textvariable=self.alpha_var, width=5).grid(row=1, column=4)
        
        tk.Label(self.settings_frame, text="% Beta:").grid(row=1, column=5, sticky="e")
        self.beta_var = tk.DoubleVar(value=100)
        tk.Entry(self.settings_frame, textvariable=self.beta_var, width=5).grid(row=1, column=6)
        
        self.start_btn = tk.Button(self.settings_frame, text="Khởi Tạo Bàn Cờ Mới", command=self.start_game, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
        self.start_btn.grid(row=2, column=0, columnspan=7, pady=10)
        
        self.board_frame = tk.Frame(self.root)
        self.board_frame.pack(pady=10)
        
        self.buttons = []
        self.state = None
        self.engine = None
        
    def start_game(self):
        n = self.n_var.get()
        m = self.m_var.get()
        engine_name = self.engine_var.get()
        
        try:
            if engine_name == "Depth":
                self.engine = importlib.import_module("Minimax_Depth_Tictactoe")
            elif engine_name == "Alpha-Beta-Depth":
                self.engine = importlib.import_module("Minimax_Alpha-Beta-Depth_Tictactoe")
            else:
                self.engine = importlib.import_module("Minimax_Alpha-Beta_Tictactoe")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải Engine: {e}")
            return
            
        self.state = self.engine.initial_state(n, m, "X")
        
        for widget in self.board_frame.winfo_children():
            widget.destroy()
            
        self.buttons = []
        for r in range(n):
            row_btns = []
            for c in range(n):
                btn = tk.Button(self.board_frame, text="", font=("Helvetica", 20, "bold"), width=3, height=1,
                                command=lambda r=r, c=c: self.user_move(r, c))
                btn.grid(row=r, column=c, padx=2, pady=2)
                row_btns.append(btn)
            self.buttons.append(row_btns)
            
    def update_board(self):
        n = self.state['size']
        board = self.state['board']
        for r in range(n):
            for c in range(n):
                idx = r * n + c
                val = board[idx]
                color = "blue" if val == "X" else "red"
                self.buttons[r][c].config(text=val if val != " " else "", fg=color)
                
    def check_terminal(self):
        if self.engine.terminal(self.state):
            w = self.engine.get_winner(self.state)
            if w:
                messagebox.showinfo("Game Over", f"Người chơi {w} thắng!")
            else:
                messagebox.showinfo("Game Over", "Trò chơi hòa!")
            return True
        return False
        
    def user_move(self, r, c):
        if self.check_terminal(): return
        if self.state['turn'] != "X": return # Chỉ cho phép user đi lượt X
        
        n = self.state['size']
        idx = r * n + c
        if self.state['board'][idx] == " ":
            self.engine.make_move(self.state, idx)
            self.update_board()
            if not self.check_terminal():
                self.root.after(100, self.ai_move)
                
    def ai_move(self):
        self.root.config(cursor="watch")
        self.root.update()
        import threading
        threading.Thread(target=self._ai_worker, daemon=True).start()
        
    def _ai_worker(self):
        engine_name = self.engine_var.get()
        depth = self.depth_var.get()
        
        try:
            if engine_name == "Depth":
                move_idx = self.engine.find_best_move(self.state, depth)
            else:
                alpha_pct = self.alpha_var.get()
                beta_pct = self.beta_var.get()
                base_min = -1000
                base_max = 1000
                initial_alpha = (alpha_pct / 100.0) * base_min
                initial_beta = (beta_pct / 100.0) * base_max
                
                if engine_name == "Alpha-Beta-Depth":
                    move_idx = self.engine.find_best_move(self.state, depth, initial_alpha, initial_beta)
                else:
                    move_idx = self.engine.find_best_move(self.state, initial_alpha, initial_beta)
        except Exception as e:
            print(f"Error in AI computation: {e}")
            move_idx = None
            
        self.root.after(0, self._apply_ai_move, move_idx)
        
    def _apply_ai_move(self, move_idx):
        if move_idx is not None:
            self.engine.make_move(self.state, move_idx)
            self.update_board()
            self.check_terminal()
            
        self.root.config(cursor="")

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()
