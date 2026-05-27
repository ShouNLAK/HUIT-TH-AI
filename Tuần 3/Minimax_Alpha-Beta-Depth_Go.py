import copy
import math

# Ký hiệu quân cờ
# B: Quân Đen (Đi trước)
# W: Quân Trắng
EMPTY = "."
BLACK = "B"
WHITE = "W"

def get_initial_board(size):
    return [[EMPTY for _ in range(size)] for _ in range(size)]

def initial_state(size):
    b = get_initial_board(size)
    b_tup = tuple(tuple(r) for r in b)
    return {
        'board': b,
        'turn': BLACK,
        'played_count': 0,
        'pass_count': 0,
        'B_captured': 0, 
        'W_captured': 0, 
        'history': {b_tup},
        'size': size
    }

def print_board(state):
    print("\n   " + " ".join(str(i).rjust(2) for i in range(state["size"])))
    for r in range(state['size']):
        print(f"{r}  " + " ".join(state['board'][r]))
    print(f"Captured: B={state['B_captured']} | W={state['W_captured']}")
    print()

def get_group_and_liberties(board, r, c):
    color = board[r][c]
    if color == EMPTY: return set(), set()
    
    group = set()
    liberties = set()
    frontier = [(r, c)]
    
    while frontier:
        cr, cc = frontier.pop(0)
        if (cr, cc) in group: continue
        group.add((cr, cc))
        
        for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
            nr, nc = cr+dr, cc+dc
            if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                np = board[nr][nc]
                if np == EMPTY:
                    liberties.add((nr, nc))
                elif np == color and (nr, nc) not in group:
                    frontier.append((nr, nc))
                    
    return group, liberties

def apply_move(board, turn, r, c):
    new_board = copy.deepcopy(board)
    new_board[r][c] = turn
    
    opp_color = WHITE if turn == BLACK else BLACK
    captured_stones = set()
    
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < len(board) and 0 <= nc < len(board[0]) and new_board[nr][nc] == opp_color:
            if (nr, nc) not in captured_stones:
                grp, libs = get_group_and_liberties(new_board, nr, nc)
                if len(libs) == 0:
                    captured_stones.update(grp)
                    
    for cr, cc in captured_stones:
        new_board[cr][cc] = EMPTY
        
    if not captured_stones:
        grp, libs = get_group_and_liberties(new_board, r, c)
        if len(libs) == 0:
            return None, 0 
            
    return new_board, len(captured_stones)

def terminal(state):
    """Kết thúc khi cả hai phe đều PASS liên tiếp (pass_count >= 2).
    Cần ít nhất 2 quân đã đặt để tránh kết thúc ngay từ đầu."""
    if state['played_count'] < 2:
        return False
    return state.get('pass_count', 0) >= 2

def successors(state):
    """Sinh các nước đi hợp lệ. Ưu tiên đặt quân trung tâm, PASS cuối cùng."""
    board = state['board']
    turn  = state['turn']
    size  = state['size']
    next_turn = WHITE if turn == BLACK else BLACK
    center = (size - 1) / 2.0

    # 1. Liệt kê mọi ô trống, sắp xếp theo khoảng cách đến trung tâm (gần trước)
    candidates = []
    for r in range(size):
        for c in range(size):
            if board[r][c] == EMPTY:
                dist = (r - center)**2 + (c - center)**2
                candidates.append((dist, r, c))
    candidates.sort()

    # 2. Yield các nước đặt quân hợp lệ (không tự sát, không lặp KO)
    for _, r, c in candidates:
        new_board, cap_count = apply_move(board, turn, r, c)
        if new_board is not None:
            b_tup = tuple(tuple(row) for row in new_board)
            if b_tup not in state['history']:
                new_history = set(state['history'])
                new_history.add(b_tup)
                new_B = state['B_captured'] + (cap_count if turn == BLACK else 0)
                new_W = state['W_captured'] + (cap_count if turn == WHITE else 0)
                yield (r, c), {
                    'board':      new_board,
                    'turn':       next_turn,
                    'played_count': state['played_count'] + 1,
                    'pass_count': 0,
                    'history':    new_history,
                    'size':       size,
                    'B_captured': new_B,
                    'W_captured': new_W,
                }

    # 3. PASS luôn nằm CUỐI (AI chỉ chọn khi mọi nước đi khác đều tệ hơn)
    yield (-1, -1), {
        'board':      board,
        'turn':       next_turn,
        'played_count': state['played_count'] + 1,
        'pass_count': state['pass_count'] + 1,
        'history':    state['history'],
        'size':       size,
        'B_captured': state['B_captured'],
        'W_captured': state['W_captured'],
    }

def utility(state, current_depth=0):
    """Đánh giá bàn cờ Cờ Vây bằng territory flood-fill + stones + liberties."""
    board = state['board']
    size  = state['size']

    # Stones trên bàn cờ: mỗi quân = 10 điểm
    b_stones = sum(1 for r in range(size) for c in range(size) if board[r][c] == BLACK)
    w_stones = sum(1 for r in range(size) for c in range(size) if board[r][c] == WHITE)

    # Quân bị bắt
    b_score = b_stones * 10 + state['B_captured'] * 10
    w_score = w_stones * 10 + state['W_captured'] * 10

    # Liberties
    seen = set()
    for r in range(size):
        for c in range(size):
            p = board[r][c]
            if p != EMPTY and (r, c) not in seen:
                grp, libs = get_group_and_liberties(board, r, c)
                seen.update(grp)
                lib_bonus = len(libs) * 3
                if p == BLACK: b_score += lib_bonus
                else:          w_score += lib_bonus

    # Territory: flood-fill từ các ô trống
    visited = set()
    for sr in range(size):
        for sc in range(size):
            if board[sr][sc] == EMPTY and (sr, sc) not in visited:
                # BFS flood-fill
                region = []
                frontier = [(sr, sc)]
                border_colors = set()
                while frontier:
                    cr, cc = frontier.pop()
                    if (cr, cc) in visited: continue
                    visited.add((cr, cc))
                    region.append((cr, cc))
                    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nr, nc = cr+dr, cc+dc
                        if 0 <= nr < size and 0 <= nc < size:
                            if board[nr][nc] == EMPTY:
                                frontier.append((nr, nc))
                            else:
                                border_colors.add(board[nr][nc])
                # Nếu chỉ 1 màu bao quanh → territory của màu đó
                if len(border_colors) == 1:
                    color = list(border_colors)[0]
                    territory = len(region) * 5
                    if color == BLACK: b_score += territory
                    else:              w_score += territory

    return b_score - w_score

def minimax_alpha_beta(state, depth, alpha, beta, is_maximizing, indent=0, current_depth=0):
    if terminal(state):
        return utility(state, current_depth)
    if depth == 0:
        return utility(state, current_depth)

    if is_maximizing:
        max_eval = -math.inf
        for action, next_state in successors(state):
            eval_score = minimax_alpha_beta(next_state, depth - 1, alpha, beta, False, indent + 1, current_depth + 1)
            if eval_score > max_eval:
                max_eval = eval_score
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for action, next_state in successors(state):
            eval_score = minimax_alpha_beta(next_state, depth - 1, alpha, beta, True, indent + 1, current_depth + 1)
            if eval_score < min_eval:
                min_eval = eval_score
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(state, depth, initial_alpha, initial_beta):
    turn = state['turn']
    is_max = (turn == BLACK)
    best_move = None
    
    alpha = initial_alpha
    beta = initial_beta
    
    print(f"\n[AI REPORT] AI ({turn}) suy nghĩ với Depth = {depth}, Khung Alpha/Beta: [{initial_alpha}, {initial_beta}]")
    best_val = -math.inf if is_max else math.inf
        
    for action, next_state in successors(state):
        eval_score = minimax_alpha_beta(next_state, depth - 1, alpha, beta, not is_max, indent=1, current_depth=1)
        
        # RE-SEARCH ASPIRATION WINDOW
        if eval_score <= initial_alpha or eval_score >= initial_beta:
            print(f"   [RE-SEARCH] Điểm {eval_score} văng khỏi khung [{initial_alpha}, {initial_beta}]. Re-search nhánh với [-inf, +inf]")
            eval_score = minimax_alpha_beta(next_state, depth - 1, -math.inf, math.inf, not is_max, indent=1, current_depth=1)
        
        if is_max:
            if eval_score > best_val:
                best_val = eval_score
                best_move = action
            alpha = max(alpha, eval_score)
        else:
            if eval_score < best_val:
                best_val = eval_score
                best_move = action
            beta = min(beta, eval_score)
                
    print(f"[AI DECISION] AI chọn {best_move} với điểm: {best_val}")
    return best_move

def main():
    print("="*40)
    print("CỜ VÂY (9x9) - MINIMAX ALPHA-BETA (DEPTH)")
    print("AI vs AI tự động đấu nếu cả 2 bên cùng chọn AI")
    print("="*40)
    
    depth = int(input("Nhập độ sâu tối đa (Khuyên dùng 2-3 do hệ số phân nhánh cao): "))
    
    alpha_pct = float(input("Nhập phần trăm Alpha (vd: 100): "))
    beta_pct = float(input("Nhập phần trăm Beta (vd: 100): "))
    initial_alpha = (alpha_pct / 100.0) * -1000
    initial_beta = (beta_pct / 100.0) * 1000
    mode = input("Chọn chế độ (1: Bạn vs AI, 2: AI vs AI): ").strip()
    
    user_side = BLACK if mode == "1" else None
    size = int(input("Nhập kích thước bàn cờ Cờ Vây (VD: 9): "))
    state = initial_state(size)
    
    while True:
        print_board(state)
        if terminal(state):
            score = utility(state, 0)
            if score > 0: w = BLACK
            elif score < 0: w = WHITE
            else: w = None
            print(f"🎉 KẾT THÚC: {w} THẮNG! (Điểm ưu thế Đen: {score})" if w else "⚖️ HÒA!")
            break
            
        if state['turn'] == user_side:
            print(f"Lượt của BẠN ({state['turn']}):")
            user_input = input("Nhập Hàng Cột (vd: 3 4), hoặc -1 -1 để Pass: ").strip()
            parts = user_input.split()
            if len(parts) == 2:
                r, c = int(parts[0]), int(parts[1])
                if r == -1 and c == -1:
                    state['turn'] = WHITE if state['turn'] == BLACK else BLACK
                    state['pass_count'] += 1
                else:
                    new_board, cap_count = apply_move(state['board'], state['turn'], r, c)
                    if new_board:
                        state['board'] = new_board
                        if state['turn'] == BLACK: state['B_captured'] += cap_count
                        else: state['W_captured'] += cap_count
                        state['turn'] = WHITE if state['turn'] == BLACK else BLACK
                        state['pass_count'] = 0
                        state['history'].add(tuple(tuple(row) for row in new_board))
                    else:
                        print("Nước đi không hợp lệ (Tự sát hoặc KO)!")
        else:
            move = find_best_move(state, depth, initial_alpha, initial_beta)
            if move:
                r, c = move
                if r == -1 and c == -1:
                    print(f"AI ({state['turn']}) PASS.")
                    state['turn'] = WHITE if state['turn'] == BLACK else BLACK
                    state['pass_count'] += 1
                else:
                    new_board, cap_count = apply_move(state['board'], state['turn'], r, c)
                    state['board'] = new_board
                    if state['turn'] == BLACK: state['B_captured'] += cap_count
                    else: state['W_captured'] += cap_count
                    state['turn'] = WHITE if state['turn'] == BLACK else BLACK
                    state['pass_count'] = 0
                    state['history'].add(tuple(tuple(row) for row in new_board))
            else:
                break

if __name__ == "__main__":
    main()
