import math

X = "X"
O = "O"
EMPTY = " "

def initial_state(size, win_length, first_player):
    return {
        'board': [EMPTY] * (size * size),
        'size': size,
        'win_length': win_length,
        'turn': first_player,
        'played_count': 0,
        'candidate_moves': set(),
        'neighbor_count': [0] * (size * size),
        'last_move': None,
        'move_history': []
    }

def print_board(state):
    size = state['size']
    board = state['board']
    if size > 20:
        print(f"\n[Bàn cờ quá lớn ({size}x{size}), ẩn in ấn chi tiết để tránh lag terminal]")
        return
    print("\n   " + "   ".join(str(i) for i in range(size)))
    print("  " + "-" * (size * 4 + 1))
    for r in range(size):
        row_str = " | ".join(board[r * size + c] for c in range(size))
        print(f"{r} | " + row_str + " |")
        print("  " + "-" * (size * 4 + 1))
    print()

def make_move(state, idx):
    size = state['size']
    r = idx // size
    c = idx % size
    
    state['board'][idx] = state['turn']
    state['played_count'] += 1
    state['move_history'].append(state['last_move'])
    state['last_move'] = idx
    state['turn'] = O if state['turn'] == X else X
    
    if idx in state['candidate_moves']:
        state['candidate_moves'].remove(idx)
        
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if dr == 0 and dc == 0: continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                n_idx = nr * size + nc
                state['neighbor_count'][n_idx] += 1
                if state['board'][n_idx] == EMPTY and state['neighbor_count'][n_idx] == 1:
                    state['candidate_moves'].add(n_idx)

def undo_move(state, idx):
    size = state['size']
    r = idx // size
    c = idx % size
    
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if dr == 0 and dc == 0: continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                n_idx = nr * size + nc
                state['neighbor_count'][n_idx] -= 1
                if state['neighbor_count'][n_idx] == 0 and n_idx in state['candidate_moves']:
                    state['candidate_moves'].remove(n_idx)
                    
    state['board'][idx] = EMPTY
    state['played_count'] -= 1
    state['last_move'] = state['move_history'].pop()
    state['turn'] = O if state['turn'] == X else X
    
    if state['neighbor_count'][idx] > 0:
        state['candidate_moves'].add(idx)

def successors(state):
    sorted_moves = sorted(list(state['candidate_moves']), key=lambda idx: state['neighbor_count'][idx], reverse=True)
    if not sorted_moves and state['played_count'] == 0:
        size = state['size']
        yield (size // 2) * size + (size // 2)
    else:
        for move in sorted_moves:
            yield move

def get_winner(state):
    last_move = state['last_move']
    if last_move is None:
        return None
        
    board = state['board']
    size = state['size']
    win_length = state['win_length']
    
    r = last_move // size
    c = last_move % size
    p = board[last_move]
    
    def count_consecutive(dr, dc):
        count = 0
        for i in range(1, win_length):
            nr, nc = r + dr * i, c + dc * i
            if 0 <= nr < size and 0 <= nc < size:
                if board[nr * size + nc] == p:
                    count += 1
                else:
                    break
            else:
                break
        return count

    if 1 + count_consecutive(0, 1) + count_consecutive(0, -1) >= win_length: return p
    if 1 + count_consecutive(1, 0) + count_consecutive(-1, 0) >= win_length: return p
    if 1 + count_consecutive(1, 1) + count_consecutive(-1, -1) >= win_length: return p
    if 1 + count_consecutive(1, -1) + count_consecutive(-1, 1) >= win_length: return p
    return None

def terminal(state):
    if get_winner(state) is not None:
        return True
    if state['played_count'] == state['size'] * state['size']:
        return True
    return False

def utility(state, current_depth=0):
    """Hàm đánh giá Caro/TicTacToe với threat detection."""
    w = get_winner(state)
    if w == X:  return  1000 - current_depth
    if w == O:  return -1000 + current_depth
    if state['played_count'] == state['size'] * state['size']:
        return 0

    # Heuristic: đếm số chuỗi mở của mỗi bên
    board      = state['board']
    size       = state['size']
    win_length = state['win_length']
    DIRECTIONS = [(0,1),(1,0),(1,1),(1,-1)]

    def count_threats(player, length):
        opp = O if player == X else X
        count = 0
        for r in range(size):
            for c in range(size):
                for dr, dc in DIRECTIONS:
                    cells = []
                    for i in range(length):
                        nr, nc = r+dr*i, c+dc*i
                        if 0 <= nr < size and 0 <= nc < size:
                            cells.append(board[nr*size+nc])
                        else:
                            cells = None; break
                    if cells is None: continue
                    if opp not in cells and cells.count(player) == length - 1:
                        count += 1
        return count

    score = 0
    wl = win_length
    if wl >= 2:
        score += count_threats(X, wl - 0) * 100  # completed win (not captured yet by terminal)
        score -= count_threats(O, wl - 0) * 100
    if wl >= 3:
        score += count_threats(X, wl - 1) * 10
        score -= count_threats(O, wl - 1) * 10
    if wl >= 4:
        score += count_threats(X, wl - 2) * 3
        score -= count_threats(O, wl - 2) * 3
    return score

def minimax_alpha_beta(state, alpha, beta, is_maximizing, indent=0, current_depth=0):
    indent_str = "    " * indent
    if terminal(state):
        u = utility(state, current_depth)
        w = get_winner(state)
        res_str = f"{w} thắng" if w else "Hòa"
        return u
        
    if current_depth > 20: 
        return 0

    if is_maximizing:
        max_eval = -math.inf
        for action in successors(state):
            make_move(state, action)
            eval_score = minimax_alpha_beta(state, alpha, beta, False, indent + 1, current_depth + 1)
            undo_move(state, action)
            
            old_max = max_eval
            if eval_score > max_eval: max_eval = eval_score
            
            old_alpha = alpha
            alpha = max(alpha, eval_score)
            
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for action in successors(state):
            make_move(state, action)
            eval_score = minimax_alpha_beta(state, alpha, beta, True, indent + 1, current_depth + 1)
            undo_move(state, action)
            
            old_min = min_eval
            if eval_score < min_eval: min_eval = eval_score
            
            old_beta = beta
            beta = min(beta, eval_score)
            
            if beta <= alpha:
                break
        return min_eval

def find_best_move(state, initial_alpha, initial_beta):
    turn = state['turn']
    is_max = (turn == X)
    best_move = None
    
    alpha = initial_alpha
    beta = initial_beta
    
    if is_max:
        best_val = -math.inf
        print(f"\n[AI REPORT] AI (X - MAX) suy nghĩ KHÔNG GIỚI HẠN ĐỘ SÂU. Alpha={alpha}, Beta={beta}")
    else:
        best_val = math.inf
        print(f"\n[AI REPORT] AI (O - MIN) suy nghĩ KHÔNG GIỚI HẠN ĐỘ SÂU. Alpha={alpha}, Beta={beta}")
        
    for action in successors(state):
        print(f"\n-> Phân tích nhánh ngoài cùng: Thử {action}:")
        make_move(state, action)
        eval_score = minimax_alpha_beta(state, alpha, beta, not is_max, indent=1, current_depth=1)
        undo_move(state, action)
        
        # RE-SEARCH ASPIRATION WINDOW
        if eval_score <= initial_alpha or eval_score >= initial_beta:
            print(f"   [RE-SEARCH] Điểm {eval_score} văng khỏi khung [{initial_alpha}, {initial_beta}]. Re-search {action} với khung [-inf, +inf]")
            make_move(state, action)
            eval_score = minimax_alpha_beta(state, -math.inf, math.inf, not is_max, indent=1, current_depth=1)
            undo_move(state, action)
            print(f"   [RE-SEARCH] Hoàn tất. Điểm thực của {action} là: {eval_score}")
        
        print(f"<- Hoàn tất đánh giá {action}, điểm là: {eval_score}")
        
        if is_max:
            old_val = best_val
            if eval_score > best_val:
                best_val = eval_score
                best_move = action
            alpha = max(alpha, eval_score)
            print(f"   [Root MAX] So sánh Max hiện tại ({old_val}) và Điểm mới ({eval_score}) -> Cập nhật Max = {best_val}. Alpha = {alpha}")
        else:
            old_val = best_val
            if eval_score < best_val:
                best_val = eval_score
                best_move = action
            beta = min(beta, eval_score)
            print(f"   [Root MIN] So sánh Min hiện tại ({old_val}) và Điểm mới ({eval_score}) -> Cập nhật Min = {best_val}. Beta = {beta}")
            
    print(f"\n[AI DECISION] AI chọn nước đi {best_move} với điểm: {best_val}")
    return best_move

def main():
    print("="*50)
    print("TIC TAC TOE - ALPHA-BETA KHÔNG DEPTH (GLOBAL STATE 1D)")
    print("="*50)
    
    size = int(input("Nhập kích thước bàn cờ (N): "))
    win_length = int(input(f"Nhập số ô liên tiếp để thắng (M <= {size}): "))
    
    alpha_pct = float(input("Nhập phần trăm Alpha (vd: 100): "))
    beta_pct = float(input("Nhập phần trăm Beta (vd: 100): "))
    
    base_min = -1000
    base_max = 1000
    initial_alpha = (alpha_pct / 100.0) * base_min
    initial_beta = (beta_pct / 100.0) * base_max
    print(f"[*] Đã khởi tạo vùng tìm kiếm Alpha-Beta: Alpha = {initial_alpha}, Beta = {initial_beta}")

    user_side = input("Bạn chọn (X/O)? ").strip().upper()
    current_state = initial_state(size, win_length, X)
    
    while True:
        print_board(current_state)
        
        if terminal(current_state):
            w = get_winner(current_state)
            if w: print(f"🎉 TRÒ CHƠI KẾT THÚC: {w} THẮNG!")
            else: print("⚖️ TRÒ CHƠI KẾT THÚC: HÒA!")
            break
            
        if current_state['turn'] == user_side:
            print(f"Lượt của BẠN ({user_side}):")
            while True:
                try:
                    r = int(input(f"Nhập hàng (0-{size-1}): "))
                    c = int(input(f"Nhập cột (0-{size-1}): "))
                    idx = r * size + c
                    if 0 <= r < size and 0 <= c < size and current_state['board'][idx] == EMPTY:
                        make_move(current_state, idx)
                        break
                    else:
                        print("❌ Ô không hợp lệ hoặc đã có quân, chọn lại!")
                except ValueError:
                    print("❌ Vui lòng nhập số hợp lệ.")
        else:
            move_idx = find_best_move(current_state, initial_alpha, initial_beta)
            if move_idx is not None:
                make_move(current_state, move_idx)
                print(f"AI đánh tại: ({move_idx // size}, {move_idx % size})")
            else:
                print("Lỗi: AI không tìm được nước đi hợp lệ.")
                break

if __name__ == "__main__":
    main()
