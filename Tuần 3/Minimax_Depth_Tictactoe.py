import math

X = "X"
O = "O"
EMPTY = " "

def initial_state(size, win_length, first_player):
    """
    1. Trạng thái ban đầu: Dùng chung 1 Global State (Mảng 1 chiều)
    """
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
    """ Cập nhật trạng thái (Make Move) O(1) """
    size = state['size']
    r = idx // size
    c = idx % size
    
    state['board'][idx] = state['turn']
    state['played_count'] += 1
    state['move_history'].append(state['last_move'])
    state['last_move'] = idx
    state['turn'] = O if state['turn'] == X else X
    
    # Gỡ bỏ ô vừa đánh khỏi danh sách ứng viên
    if idx in state['candidate_moves']:
        state['candidate_moves'].remove(idx)
        
    # Thêm các ô lân cận vào danh sách ứng viên
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < size and 0 <= nc < size:
                n_idx = nr * size + nc
                state['neighbor_count'][n_idx] += 1
                if state['board'][n_idx] == EMPTY and state['neighbor_count'][n_idx] == 1:
                    state['candidate_moves'].add(n_idx)

def undo_move(state, idx):
    """ Hoàn tác trạng thái (Undo Move) O(1) """
    size = state['size']
    r = idx // size
    c = idx % size
    
    # Rút lại lân cận
    for dr in range(-2, 3):
        for dc in range(-2, 3):
            if dr == 0 and dc == 0:
                continue
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
    
    # Nếu bản thân ô vừa rút vẫn nằm kề quân cờ khác, ném lại vào ứng viên
    if state['neighbor_count'][idx] > 0:
        state['candidate_moves'].add(idx)

def successors(state):
    """ 
    2. Hàm chuyển trạng thái: Generator (yield) để tiết kiệm RAM. 
       Kết hợp Move Ordering sắp xếp theo neighbor_count.
    """
    sorted_moves = sorted(list(state['candidate_moves']), key=lambda idx: state['neighbor_count'][idx], reverse=True)
    if not sorted_moves and state['played_count'] == 0:
        size = state['size']
        yield (size // 2) * size + (size // 2)
    else:
        for move in sorted_moves:
            yield move

def get_winner(state):
    """ 3. Trạng thái kết thúc: Kiểm tra thắng thua $O(M)$ """
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
    """ Hòa kiểm tra trong O(1) """
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

def minimax(state, depth, is_maximizing, indent=0, current_depth=0):
    indent_str = "    " * indent
    
    if terminal(state):
        u = utility(state, current_depth)
        w = get_winner(state)
        res_str = f"{w} thắng" if w else "Hòa"
        print(f"{indent_str}-> Trạng thái kết thúc ({res_str}), Điểm: {u}")
        return u
        
    if depth == 0:
        print(f"{indent_str}-> Chạm giới hạn độ sâu (Depth=0). Trả về điểm: 0")
        return 0

    if is_maximizing:
        print(f"{indent_str}[MAX-X] Xét nước đi (Depth còn {depth})...")
        max_eval = -math.inf
        for action in successors(state):
            print(f"{indent_str}  > X thử nước đi (1D index): {action}")
            make_move(state, action)
            eval_score = minimax(state, depth - 1, False, indent + 1, current_depth + 1)
            undo_move(state, action)
            
            print(f"{indent_str}  < Điểm {action} = {eval_score}. So sánh Max hiện tại ({max_eval})")
            if eval_score > max_eval:
                max_eval = eval_score
        print(f"{indent_str}[MAX-X] Chốt max = {max_eval}")
        return max_eval
    else:
        print(f"{indent_str}[MIN-O] Xét nước đi (Depth còn {depth})...")
        min_eval = math.inf
        for action in successors(state):
            print(f"{indent_str}  > O thử nước đi (1D index): {action}")
            make_move(state, action)
            eval_score = minimax(state, depth - 1, True, indent + 1, current_depth + 1)
            undo_move(state, action)
            
            print(f"{indent_str}  < Điểm {action} = {eval_score}. So sánh Min hiện tại ({min_eval})")
            if eval_score < min_eval:
                min_eval = eval_score
        print(f"{indent_str}[MIN-O] Chốt min = {min_eval}")
        return min_eval

def find_best_move(state, depth):
    turn = state['turn']
    is_max = (turn == X)
    best_move = None
    
    if is_max:
        best_val = -math.inf
        print(f"\n[AI REPORT] AI (X - MAX) suy nghĩ với Depth = {depth}")
    else:
        best_val = math.inf
        print(f"\n[AI REPORT] AI (O - MIN) suy nghĩ với Depth = {depth}")
        
    for action in successors(state):
        print(f"\n-> Phân tích nhánh ngoài cùng: Thử {action}:")
        make_move(state, action)
        eval_score = minimax(state, depth - 1, not is_max, indent=1, current_depth=1)
        undo_move(state, action)
        
        print(f"<- Hoàn tất đánh giá {action}, điểm là: {eval_score}")
        
        if is_max:
            old_val = best_val
            if eval_score > best_val:
                best_val = eval_score
                best_move = action
            print(f"   [Root MAX] So sánh Max hiện tại ({old_val}) và Điểm mới ({eval_score}) -> Cập nhật Max = {best_val}")
        else:
            old_val = best_val
            if eval_score < best_val:
                best_val = eval_score
                best_move = action
            print(f"   [Root MIN] So sánh Min hiện tại ({old_val}) và Điểm mới ({eval_score}) -> Cập nhật Min = {best_val}")
                
    print(f"\n[AI DECISION] AI chọn nước đi {best_move} với điểm: {best_val}")
    return best_move

def main():
    print("="*50)
    print("TIC TAC TOE KHỔNG LỒ - GLOBAL STATE 1D (MAKE/UNDO)")
    print("="*50)
    
    size = int(input("Nhập kích thước bàn cờ (N): "))
    win_length = int(input(f"Nhập số ô liên tiếp để thắng (M <= {size}): "))
    depth = int(input("Nhập độ sâu tối đa (Depth): "))
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
            move_idx = find_best_move(current_state, depth)
            if move_idx is not None:
                make_move(current_state, move_idx)
                # In ra để user biết tọa độ 2D tương ứng
                print(f"AI đánh tại: ({move_idx // size}, {move_idx % size})")
            else:
                print("Lỗi: AI không tìm được nước đi hợp lệ.")
                break

if __name__ == "__main__":
    main()
