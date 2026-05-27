import tkinter as tk
from tkinter import messagebox
import importlib
import threading
import sys
import os

# Đảm bảo import được các module Minimax trong cùng thư mục
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class GoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Vây AI (Go)")
        self.root.configure(bg="#2E3440")
        
        # Styles
        self.font = ("Segoe UI", 10)
        self.font_bold = ("Segoe UI", 10, "bold")
        self.bg_color = "#2E3440"
        self.fg_color = "#D8DEE9"
        self.btn_color = "#4C566A"
        self.accent_color = "#88C0D0"
        
        self.setup_ui()
        
        self.engine = None
        self.state = None
        self.ai_is_thinking = False
        self.game_over = False
        self.selected_piece = None

    def setup_ui(self):
        control_frame = tk.Frame(self.root, bg=self.bg_color)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        
        # Cài đặt thuật toán
        tk.Label(control_frame, text="Chế độ:", bg=self.bg_color, fg=self.fg_color, font=self.font_bold).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.mode_var = tk.StringVar(value="Người vs AI (Người đi trước)")
        mode_dropdown = tk.OptionMenu(control_frame, self.mode_var, "Người vs AI (Người đi trước)", "AI vs Người (AI đi trước)", "AI vs AI")
        mode_dropdown.config(bg=self.btn_color, fg=self.fg_color, font=self.font)
        mode_dropdown.grid(row=0, column=1, columnspan=2, padx=5, pady=5, sticky="w")
        
        tk.Label(control_frame, text="Thuật toán:", bg=self.bg_color, fg=self.fg_color, font=self.font_bold).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.engine_var = tk.StringVar(value="Alpha-Beta-Depth")
        engine_dropdown = tk.OptionMenu(control_frame, self.engine_var, "Depth", "Alpha-Beta", "Alpha-Beta-Depth")
        engine_dropdown.config(bg=self.btn_color, fg=self.fg_color, font=self.font)
        engine_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(control_frame, text="Độ sâu:", bg=self.bg_color, fg=self.fg_color, font=self.font).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.depth_var = tk.IntVar(value=4)
        tk.Entry(control_frame, textvariable=self.depth_var, width=5, font=self.font).grid(row=1, column=3, padx=5, pady=5, sticky="w")
        tk.Label(control_frame, text="% Alpha:", bg=self.bg_color, fg=self.fg_color, font=self.font).grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.alpha_var = tk.DoubleVar(value=100)
        tk.Entry(control_frame, textvariable=self.alpha_var, width=5, font=self.font).grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        tk.Label(control_frame, text="% Beta:", bg=self.bg_color, fg=self.fg_color, font=self.font).grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.beta_var = tk.DoubleVar(value=100)
        tk.Entry(control_frame, textvariable=self.beta_var, width=5, font=self.font).grid(row=2, column=3, padx=5, pady=5, sticky="w")

        
        tk.Label(control_frame, text="Kích thước (N):", bg=self.bg_color, fg=self.fg_color, font=self.font).grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.size_var = tk.IntVar(value=9)
        tk.Entry(control_frame, textvariable=self.size_var, width=5, font=self.font).grid(row=1, column=5, padx=5, pady=5, sticky="w")
        
        # Controls
        start_btn = tk.Button(control_frame, text="BẮT ĐẦU VÁN MỚI", command=self.start_game, bg=self.accent_color, fg=self.bg_color, font=self.font_bold)
        start_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=10)
        
        self.pass_btn = tk.Button(control_frame, text="PASS (Bỏ Lượt)", command=self.user_pass, bg="#EBCB8B", fg=self.bg_color, font=self.font_bold)
        self.pass_btn.grid(row=3, column=2, columnspan=2, padx=5, pady=10)
        
        # Canvas
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="#ECEFF4", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        self.status_label = tk.Label(self.root, text="Vui lòng thiết lập thông số và bấm Bắt Đầu", bg=self.bg_color, fg=self.accent_color, font=("Segoe UI", 12, "bold"))
        self.status_label.pack(pady=5)

    def load_engine(self):
        engine_type = self.engine_var.get()
        module_name = f"Minimax_{engine_type}_Go"
        try:
            self.engine = importlib.import_module(module_name)
            importlib.reload(self.engine)
            return True
        except Exception as e:
            messagebox.showerror("Lỗi Tải Engine", f"Không thể tải {module_name}.py\nLỗi: {e}")
            return False

    def start_game(self):
        if not self.load_engine(): return
        
        self.selected_piece = None
        self.game_over = False
        
        mode = self.mode_var.get()
        self.state = self.engine.initial_state(self.size_var.get())
            
        if "AI vs AI" in mode:
            self.user_side = None
            self.status_label.config(text="AI vs AI đang đấu...")
            self.root.after(100, self.ai_turn)
        elif "Người đi trước" in mode:
            self.user_side = 'BLACK'
            self.status_label.config(text=f"Lượt của bạn ({self.user_side})")
        else:
            self.user_side = 'WHITE'
            self.status_label.config(text="AI đang suy nghĩ...")
            self.root.after(100, self.ai_turn)
            
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        if not self.state: return
        w, h = 600, 600
        board = self.state['board']
        
        n = self.size_var.get()
        pad = 40
        space = (w - 2*pad) / (n - 1)
        self.canvas.create_rectangle(0, 0, w, h, fill="#EBCB8B")
        for i in range(n):
            self.canvas.create_line(pad, pad + i*space, w - pad, pad + i*space, fill="black")
            self.canvas.create_line(pad + i*space, pad, pad + i*space, h - pad, fill="black")
        
        radius = space * 0.45
        for r in range(n):
            for c in range(n):
                if board[r][c] == 'BLACK':
                    self.canvas.create_oval(pad + c*space - radius, pad + r*space - radius, pad + c*space + radius, pad + r*space + radius, fill="black")
                elif board[r][c] == 'WHITE':
                    self.canvas.create_oval(pad + c*space - radius, pad + r*space - radius, pad + c*space + radius, pad + r*space + radius, fill="white", outline="black")

    def on_canvas_click(self, event):
        if self.game_over or self.ai_is_thinking: return
        if self.state['turn'] != self.user_side and self.user_side is not None: return
        
        w, h = 600, 600
        n = self.size_var.get()
        pad = 40
        space = (w - 2*pad) / (n - 1)
        c = round((event.x - pad) / space)
        r = round((event.y - pad) / space)
        if 0 <= r < n and 0 <= c < n and self.state['board'][r][c] == '.':
            new_board, caps = self.engine.apply_move(self.state['board'], self.state['turn'], r, c)
            if new_board:
                b_tup = tuple(tuple(row) for row in new_board)
                if b_tup not in self.state['history']:
                    self.state['board'] = new_board
                    if self.state['turn'] == 'BLACK': self.state['B_captured'] += caps
                    else: self.state['W_captured'] += caps
                    self.state['pass_count'] = 0
                    self.state['history'].add(b_tup)
                    self.state['turn'] = 'WHITE' if self.state['turn'] == 'BLACK' else 'BLACK'
                    self.finish_user_turn()
                else:
                    messagebox.showwarning("Lỗi", "Vi phạm luật Superko!")
            else:
                messagebox.showwarning("Lỗi", "Nước đi tự sát không hợp lệ!")

    def user_pass(self):
        if not self.ai_is_thinking and not self.game_over:
            if self.state['turn'] == self.user_side or self.user_side is None:
                self.state['turn'] = 'WHITE' if self.state['turn'] == 'BLACK' else 'BLACK'
                self.state['pass_count'] += 1
                self.finish_user_turn()

    def finish_user_turn(self):
        self.draw_board()
        self.check_game_over()
        if not self.game_over and self.user_side is not None:
            self.status_label.config(text="AI đang suy nghĩ...")
            self.root.after(100, self.ai_turn)
            
    def ai_turn(self):
        if self.game_over: return
        self.ai_is_thinking = True
        
        def worker():
            engine_type = self.engine_var.get()
            depth = self.depth_var.get()
            if "Alpha-Beta" in engine_type:
                alpha_val = -1000 * (self.alpha_var.get() / 100) if hasattr(self, 'alpha_var') else -1000
                beta_val = 1000 * (self.beta_var.get() / 100) if hasattr(self, 'beta_var') else 1000
                if "Depth" in engine_type:
                    move = self.engine.find_best_move(self.state, depth, alpha_val, beta_val)
                else:
                    move = self.engine.find_best_move(self.state, alpha_val, beta_val)
            else:
                move = self.engine.find_best_move(self.state, depth)
                
            self.root.after(0, self.apply_ai_move, move)
            
        threading.Thread(target=worker, daemon=True).start()
        
    def apply_ai_move(self, move):
        self.ai_is_thinking = False
        if move:
            r, c = move
            if r == -1 and c == -1:
                self.state['turn'] = 'WHITE' if self.state['turn'] == 'BLACK' else 'BLACK'
                self.state['pass_count'] += 1
            else:
                new_board, caps = self.engine.apply_move(self.state['board'], self.state['turn'], r, c)
                self.state['board'] = new_board
                if self.state['turn'] == 'BLACK': self.state['B_captured'] += caps
                else: self.state['W_captured'] += caps
                self.state['pass_count'] = 0
                self.state['history'].add(tuple(tuple(row) for row in new_board))
                self.state['turn'] = 'WHITE' if self.state['turn'] == 'BLACK' else 'BLACK'
        self.draw_board()
        self.check_game_over()
        
        if not self.game_over and self.user_side is None:
            self.status_label.config(text=f"AI {self.state['turn']} đang suy nghĩ...")
            self.root.after(500, self.ai_turn)
        elif not self.game_over:
            self.status_label.config(text=f"Lượt của bạn ({self.state['turn']})")

    def check_game_over(self):
        if self.engine.terminal(self.state):
            self.game_over = True
            b_score = self.state['B_captured'] * 10
            w_score = self.state['W_captured'] * 10
            for r in range(self.size_var.get()):
                for c in range(self.size_var.get()):
                    if self.state['board'][r][c] != '.':
                        grp, libs = self.engine.get_group_and_liberties(self.state['board'], r, c)
                        if self.state['board'][r][c] == 'BLACK': b_score += len(libs)
                        else: w_score += len(libs)
            msg = f"KẾT THÚC!\nĐen: {b_score}\nTrắng: {w_score}\n\n{'Đen Thắng' if b_score > w_score else 'Trắng Thắng' if w_score > b_score else 'Hòa'}"
            self.status_label.config(text=msg.replace('\n', ' '))
            messagebox.showinfo("Kết thúc", msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = GoGUI(root)
    root.mainloop()
