import tkinter as tk
from tkinter import messagebox
import importlib
import threading
import sys
import os

# Đảm bảo import được các module Minimax trong cùng thư mục
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class XiangqiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Cờ Tướng AI (Xiangqi)")
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

        

        
        # Controls
        start_btn = tk.Button(control_frame, text="BẮT ĐẦU VÁN MỚI", command=self.start_game, bg=self.accent_color, fg=self.bg_color, font=self.font_bold)
        start_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=10)
        

        
        # Canvas
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="#ECEFF4", highlightthickness=0)
        self.canvas.pack(padx=20, pady=20)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        self.status_label = tk.Label(self.root, text="Vui lòng thiết lập thông số và bấm Bắt Đầu", bg=self.bg_color, fg=self.accent_color, font=("Segoe UI", 12, "bold"))
        self.status_label.pack(pady=5)

    def load_engine(self):
        engine_type = self.engine_var.get()
        module_name = f"Minimax_{engine_type}_Xiangqi"
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
        self.state = self.engine.initial_state()
            
        if "AI vs AI" in mode:
            self.user_side = None
            self.status_label.config(text="AI vs AI đang đấu...")
            self.root.after(100, self.ai_turn)
        elif "Người đi trước" in mode:
            self.user_side = 'RED'
            self.status_label.config(text=f"Lượt của bạn ({self.user_side})")
        else:
            self.user_side = 'BLACK'
            self.status_label.config(text="AI đang suy nghĩ...")
            self.root.after(100, self.ai_turn)
            
        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        if not self.state: return
        w, h = 600, 600
        board = self.state['board']
        self.canvas.create_rectangle(0, 0, w, h, fill="#EBCB8B")
        pad_x, pad_y = 40, 40
        cw = (w - 2*pad_x) / 8
        ch = (h - 2*pad_y) / 9
        
        for i in range(10):
            if i == 4 or i == 5: continue
            self.canvas.create_line(pad_x, pad_y + i*ch, w - pad_x, pad_y + i*ch, fill="black")
        self.canvas.create_line(pad_x, pad_y + 4*ch, w - pad_x, pad_y + 4*ch, fill="black")
        self.canvas.create_line(pad_x, pad_y + 5*ch, w - pad_x, pad_y + 5*ch, fill="black")
        
        for i in range(9):
            self.canvas.create_line(pad_x + i*cw, pad_y, pad_x + i*cw, pad_y + 4*ch, fill="black")
            self.canvas.create_line(pad_x + i*cw, pad_y + 5*ch, pad_x + i*cw, pad_y + 9*ch, fill="black")
        
        self.canvas.create_line(pad_x, pad_y, pad_x, pad_y + 9*ch, fill="black")
        self.canvas.create_line(w - pad_x, pad_y, w - pad_x, pad_y + 9*ch, fill="black")
        
        self.canvas.create_line(pad_x + 3*cw, pad_y, pad_x + 5*cw, pad_y + 2*ch, fill="black")
        self.canvas.create_line(pad_x + 5*cw, pad_y, pad_x + 3*cw, pad_y + 2*ch, fill="black")
        self.canvas.create_line(pad_x + 3*cw, pad_y + 7*ch, pad_x + 5*cw, pad_y + 9*ch, fill="black")
        self.canvas.create_line(pad_x + 5*cw, pad_y + 7*ch, pad_x + 3*cw, pad_y + 9*ch, fill="black")
        
        self.canvas.create_text(w/2, pad_y + 4.5*ch, text="SÔNG CHU - HÁN GIỚI", font=("Arial", 16, "bold"), fill="#BF616A")
        
        radius = min(cw, ch) * 0.4
        chars = {'K': '帥', 'A': '仕', 'E': '相', 'H': '傌', 'R': '車', 'C': '炮', 'P': '兵',
                 'k': '將', 'a': '士', 'e': '象', 'h': '馬', 'r': '車', 'c': '砲', 'p': '卒'}
                 
        for r in range(10):
            for c in range(9):
                p = board[r][c]
                if p != '.':
                    x, y = pad_x + c*cw, pad_y + r*ch
                    color = "#BF616A" if p.isupper() else "#2E3440"
                    bg_color = "#EBCB8B" if not (self.selected_piece == (r,c)) else "#A3BE8C"
                    self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=bg_color, outline=color, width=2)
                    self.canvas.create_text(x, y, text=chars.get(p, p), font=("Arial", int(radius*1.2), "bold"), fill=color)

    def on_canvas_click(self, event):
        if self.game_over or self.ai_is_thinking: return
        if self.state['turn'] != self.user_side and self.user_side is not None: return
        
        w, h = 600, 600
        pad_x, pad_y = 40, 40
        cw = (w - 2*pad_x) / 8
        ch = (h - 2*pad_y) / 9
        c = round((event.x - pad_x) / cw)
        r = round((event.y - pad_y) / ch)
            
        if 0 <= r < 10 and 0 <= c < 9:
            p = self.state['board'][r][c]
            is_red = self.state['turn'] == 'RED'
            if self.selected_piece:
                sr, sc = self.selected_piece
                for move, next_st in self.engine.successors(self.state):
                    if move[0] == (sr, sc) and move[1] == (r, c):
                        self.state = next_st
                        self.selected_piece = None
                        self.finish_user_turn()
                        return
                if p != '.' and (p.isupper() == is_red):
                    self.selected_piece = (r, c)
                    self.draw_board()
                else:
                    self.selected_piece = None
                    self.draw_board()
            else:
                if p != '.' and (p.isupper() == is_red):
                    self.selected_piece = (r, c)
                    self.draw_board()



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
            for m, next_st in self.engine.successors(self.state):
                if m == move:
                    self.state = next_st
                    break
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
            w = self.engine.get_winner(self.state)
            if w: msg = f"🎉 KẾT THÚC: Phe {w} THẮNG!"
            else: msg = "⚖️ HÒA! (Lặp vòng)"
            self.status_label.config(text=msg)
            messagebox.showinfo("Kết thúc", msg)
        else:
            has_moves = any(True for _ in self.engine.successors(self.state))
            if not has_moves:
                self.game_over = True
                msg = "💥 ĐÃ HẾT NƯỚC ĐI!"
                messagebox.showinfo("Kết thúc", msg)
                self.status_label.config(text=msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = XiangqiGUI(root)
    root.mainloop()
