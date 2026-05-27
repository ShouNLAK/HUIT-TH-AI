import copy
import math

_XPST = {
    'R': [14,14,12,18,16,18,12,14,14,16,20,18,24,26,24,18,20,16,12,12,12,18,18,18,12,12,12,12,18,16,22,22,22,16,18,12,12,14,12,18,18,18,12,14,12,12,16,14,20,20,20,14,16,12,6,10,8,14,14,14,8,10,6,6,10,8,14,14,14,8,10,6,6,8,6,10,12,10,6,8,6,0,4,0,2,6,2,0,4,0],
    'H': [4,8,16,12,4,12,16,8,4,4,10,28,16,8,16,28,10,4,12,14,16,20,18,20,16,14,12,8,24,18,24,20,24,18,24,8,6,16,14,18,16,18,14,16,6,4,12,16,14,12,14,16,12,4,2,6,8,6,10,6,8,6,2,4,2,8,8,4,8,8,2,4,0,2,4,4,-2,4,4,2,0,0,-4,0,0,0,0,0,-4,0],
    'C': [6,4,0,-10,-12,-10,0,4,6,2,2,0,-4,-14,-4,0,2,2,2,6,4,0,-10,0,4,6,2,0,0,0,2,8,2,0,0,0,0,0,2,6,10,6,2,0,0,2,4,6,8,14,8,6,4,2,6,4,6,10,12,10,6,4,6,4,4,4,10,12,10,4,4,4,0,0,2,4,4,4,2,0,0,0,2,4,6,6,6,4,2,0],
    'E': [0,0,20,0,0,0,20,0,0,0,0,0,0,0,0,0,0,0,18,0,0,0,23,0,0,0,18,0,0,0,0,0,0,0,0,0,0,0,20,0,0,0,20,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    'A': [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,20,0,20,0,0,0,0,0,0,0,23,0,0,0,0,0,0,0,20,0,20,0,0],
    'P': [9,9,9,11,13,11,9,9,9,19,24,34,42,44,42,34,24,19,19,24,32,37,37,37,32,24,19,19,23,27,29,29,29,27,23,19,14,18,18,20,20,20,18,18,14,2,0,8,0,3,0,8,0,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    'K': [0,0,0,2,4,2,0,0,0,0,0,0,2,8,2,0,0,0,0,0,0,2,6,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
}

# Ký hiệu quân cờ (Viết hoa = ĐỎ, Viết thường = ĐEN)
# K, k: Tướng (King)
# A, a: Sĩ (Advisor)
# E, e: Tượng (Elephant)
# R, r: Xe (Rook)
# C, c: Pháo (Cannon)
# H, h: Mã (Horse)
# P, p: Tốt (Pawn)
EMPTY = "."
RED = "RED"
BLACK = "BLACK"

def get_initial_board():
    return [
        ['r', 'h', 'e', 'a', 'k', 'a', 'e', 'h', 'r'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', 'c', '.', '.', '.', '.', '.', 'c', '.'],
        ['p', '.', 'p', '.', 'p', '.', 'p', '.', 'p'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['P', '.', 'P', '.', 'P', '.', 'P', '.', 'P'],
        ['.', 'C', '.', '.', '.', '.', '.', 'C', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.', '.'],
        ['R', 'H', 'E', 'A', 'K', 'A', 'E', 'H', 'R']
    ]

def initial_state():
    return {
        'board': get_initial_board(),
        'turn': RED,
        'played_count': 0
    ,
        'history_counts': {tuple(tuple(r) for r in get_initial_board()): 1}
    }

def print_board(state):
    print("\n   " + " ".join(str(i) for i in range(9)))
    for r in range(10):
        print(f"{r}  " + " ".join(state['board'][r]))
    print()

def in_palace(r, c, is_red):
    if c < 3 or c > 5: return False
    if is_red: return 7 <= r <= 9
    else: return 0 <= r <= 2

def generate_pseudo_legal_moves(board, turn):
    moves = []
    is_red = (turn == RED)
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if p == EMPTY: continue
            if (p.isupper() and is_red) or (p.islower() and not is_red):
                # Generate moves for piece at (r, c)
                p_upper = p.upper()
                if p_upper == 'R':
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < 10 and 0 <= nc < 9:
                            if board[nr][nc] == EMPTY:
                                moves.append(((r, c), (nr, nc)))
                            else:
                                if (board[nr][nc].isupper() != is_red):
                                    moves.append(((r, c), (nr, nc)))
                                break
                            nr, nc = nr + dr, nc + dc
                elif p_upper == 'C':
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        jumped = False
                        while 0 <= nr < 10 and 0 <= nc < 9:
                            if board[nr][nc] == EMPTY:
                                if not jumped: moves.append(((r, c), (nr, nc)))
                            else:
                                if not jumped:
                                    jumped = True
                                else:
                                    if (board[nr][nc].isupper() != is_red):
                                        moves.append(((r, c), (nr, nc)))
                                    break
                            nr, nc = nr + dr, nc + dc
                elif p_upper == 'H':
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        br, bc = r + dr, c + dc # block point
                        if 0 <= br < 10 and 0 <= bc < 9 and board[br][bc] == EMPTY:
                            for ddr, ddc in ([(dr, -1), (dr, 1)] if dr != 0 else [(-1, dc), (1, dc)]):
                                nr, nc = r + dr + ddr, c + dc + ddc
                                if 0 <= nr < 10 and 0 <= nc < 9:
                                    if board[nr][nc] == EMPTY or (board[nr][nc].isupper() != is_red):
                                        moves.append(((r, c), (nr, nc)))
                elif p_upper == 'E':
                    for dr, dc in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                        nr, nc = r + dr, c + dc
                        br, bc = r + dr//2, c + dc//2
                        if 0 <= nr < 10 and 0 <= nc < 9:
                            if (is_red and nr < 5) or (not is_red and nr > 4): continue # qua sông
                            if board[br][bc] == EMPTY:
                                if board[nr][nc] == EMPTY or (board[nr][nc].isupper() != is_red):
                                    moves.append(((r, c), (nr, nc)))
                elif p_upper == 'A':
                    for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                        nr, nc = r + dr, c + dc
                        if in_palace(nr, nc, is_red):
                            if board[nr][nc] == EMPTY or (board[nr][nc].isupper() != is_red):
                                moves.append(((r, c), (nr, nc)))
                elif p_upper == 'K':
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = r + dr, c + dc
                        if in_palace(nr, nc, is_red):
                            if board[nr][nc] == EMPTY or (board[nr][nc].isupper() != is_red):
                                moves.append(((r, c), (nr, nc)))
                elif p_upper == 'P':
                    dirs = [(-1, 0)] if is_red else [(1, 0)]
                    if (is_red and r <= 4) or (not is_red and r >= 5):
                        dirs.extend([(0, -1), (0, 1)])
                    for dr, dc in dirs:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < 10 and 0 <= nc < 9:
                            if board[nr][nc] == EMPTY or (board[nr][nc].isupper() != is_red):
                                moves.append(((r, c), (nr, nc)))
    return moves

def check_flying_general(board):
    # Trả về True nếu 2 Tướng đối mặt không có quân cản
    kr, kc = -1, -1
    Kr, Kc = -1, -1
    for r in range(10):
        for c in range(9):
            if board[r][c] == 'k':
                kr, kc = r, c
            elif board[r][c] == 'K':
                Kr, Kc = r, c
    if kc != Kc or kc == -1: return False
    
    # Kiểm tra giữa 2 tướng có quân nào không
    min_r = min(kr, Kr)
    max_r = max(kr, Kr)
    for r in range(min_r + 1, max_r):
        if board[r][kc] != EMPTY:
            return False
    return True

def get_winner(state):
    if not state.get('has_legal_move', True):
        is_red = (state['turn'] == 'RED')
        return 'BLACK' if is_red else 'RED'
    return None

def terminal(state):
    """Kết thúc khi: một Tướng bị bắt, OR lặp 3 lần (hòa cưỡng bức)."""
    board = state['board']
    has_red_king   = any(board[r][c] == 'K' for r in range(10) for c in range(9))
    has_black_king = any(board[r][c] == 'k' for r in range(10) for c in range(9))
    if not has_red_king or not has_black_king:
        return True
    # Lặp 3 lần
    for count in state.get('history_counts', {}).values():
        if count >= 3:
            return True
    return False

def successors(state):
    """Sinh nước đi hợp lệ cho Cờ Tướng với move ordering (captures trước)."""
    board  = state['board']
    turn   = state['turn']
    is_red = (turn == 'RED')
    next_turn = 'BLACK' if is_red else 'RED'

    pseudo = generate_pseudo_legal_moves(board, turn)

    # Move ordering: tách captures & quiet moves
    captures, quiets = [], []
    for move in pseudo:
        (sr, sc), (er, ec) = move
        if board[er][ec] != EMPTY:
            captures.append(move)
        else:
            quiets.append(move)

    has_legal = False
    for move in captures + quiets:
        (sr, sc), (er, ec) = move
        nb = [row[:] for row in board]
        nb[er][ec] = nb[sr][sc]
        nb[sr][sc] = EMPTY

        if check_flying_general(nb):
            continue
        if is_in_check(nb, is_red):
            continue

        has_legal = True
        new_hist = state.get('history_counts', {}).copy()
        b_tup = tuple(tuple(r) for r in nb)
        new_hist[b_tup] = new_hist.get(b_tup, 0) + 1

        yield move, {
            'board':          nb,
            'turn':           next_turn,
            'played_count':   state['played_count'] + 1,
            'has_legal_move': True,
            'history_counts': new_hist,
        }
    state['has_legal_move'] = has_legal

def utility(state, current_depth=0):
    """Đánh giá thế cờ Cờ Tướng với Piece-Square Tables."""
    w = get_winner(state)
    if w == 'RED':   return  1000 - current_depth
    if w == 'BLACK': return -1000 + current_depth

    # Phạt lặp vòng
    for cnt in state.get('history_counts', {}).values():
        if cnt >= 3:
            return 0

    PIECE_VAL = {'K':10000,'R':900,'H':400,'C':450,'E':200,'A':200,'P':100}
    score = 0
    board = state['board']
    for r in range(10):
        for c in range(9):
            p = board[r][c]
            if p == EMPTY: continue
            pu = p.upper()
            pv = PIECE_VAL.get(pu, 0)
            idx = r * 9 + c
            if p.isupper():   # RED (bottom = row 9)
                pst_row = 9 - r   # flip for RED PST (PST indexed 0=top)
                pst_idx = pst_row * 9 + c
                pst_val = _XPST.get(pu, [0]*90)[pst_idx] if pst_idx < len(_XPST.get(pu, [])) else 0
                score += pv + pst_val
            else:             # BLACK (top = row 0)
                pst_idx = r * 9 + c
                pst_val = _XPST.get(pu, [0]*90)[pst_idx] if pst_idx < len(_XPST.get(pu, [])) else 0
                score -= pv + pst_val
    return score

def minimax(state, depth, is_maximizing, indent=0, current_depth=0):
    indent_str = "  " * indent
    if terminal(state):
        return utility(state, current_depth)
    if depth == 0:
        return utility(state, current_depth)

    if is_maximizing:
        max_eval = -math.inf
        has_moves = False
        for action, next_state in successors(state):
            has_moves = True
            eval_score = minimax(next_state, depth - 1, False, indent + 1, current_depth + 1)
            if eval_score > max_eval:
                max_eval = eval_score
        if not has_moves:
            return -1000 + current_depth
        return max_eval
    else:
        min_eval = math.inf
        has_moves = False
        for action, next_state in successors(state):
            has_moves = True
            eval_score = minimax(next_state, depth - 1, True, indent + 1, current_depth + 1)
            if eval_score < min_eval:
                min_eval = eval_score
        if not has_moves:
            return 1000 - current_depth
        return min_eval

def find_best_move(state, depth):
    turn = state['turn']
    is_max = (turn == RED)
    best_move = None
    
    print(f"\n[AI REPORT] AI ({turn}) suy nghĩ với Depth = {depth}")
    best_val = -math.inf if is_max else math.inf
        
    for action, next_state in successors(state):
        eval_score = minimax(next_state, depth - 1, not is_max, indent=1, current_depth=1)
        

        b_tup = tuple(tuple(row) for row in next_state['board'])
        if b_tup in state.get('history_counts', {}):
            eval_score += -500 if is_max else 500
        
        if is_max:
            if eval_score > best_val:
                best_val = eval_score
                best_move = action
        else:
            if eval_score < best_val:
                best_val = eval_score
                best_move = action
                
    print(f"[AI DECISION] AI chọn {best_move} với điểm: {best_val}")
    return best_move

def is_in_check(board, is_red):
    """Kiểm tra xem Tướng của phe is_red có đang bị chiếu không."""
    king_sym = 'K' if is_red else 'k'
    kr, kc = -1, -1
    for r in range(10):
        for c in range(9):
            if board[r][c] == king_sym:
                kr, kc = r, c; break
        if kr != -1: break
    if kr == -1: return True  # Tướng bị bắt = đang bị chiếu

    opp_red = not is_red

    # Xe (R/r) và Pháo (C/c) tấn công theo đường thẳng
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = kr+dr, kc+dc
        screen_count = 0
        while 0 <= nr < 10 and 0 <= nc < 9:
            p = board[nr][nc]
            if p != EMPTY:
                if screen_count == 0:
                    # Xe tấn công trực tiếp
                    if p.isupper() == opp_red and p.upper() == 'R':
                        return True
                elif screen_count == 1:
                    # Pháo bắn qua 1 quân
                    if p.isupper() == opp_red and p.upper() == 'C':
                        return True
                screen_count += 1
                if screen_count > 1:
                    break
            nr += dr; nc += dc

    # Mã (H/h) – kiểm tra chân Mã bị chặn không
    horse_attacks = [
        (-2,-1,(-1,0)), (-2,1,(-1,0)),
        (2,-1,(1,0)),   (2,1,(1,0)),
        (-1,-2,(0,-1)), (-1,2,(0,-1)),
        (1,-2,(0,1)),   (1,2,(0,1)),
    ]
    for dr, dc, (br_off, bc_off) in horse_attacks:
        nr, nc = kr+dr, kc+dc
        if 0 <= nr < 10 and 0 <= nc < 9:
            p = board[nr][nc]
            if p.isupper() == opp_red and p.upper() == 'H':
                # Kiểm tra chân chặn
                foot_r, foot_c = kr + br_off, kc + bc_off
                if board[foot_r][foot_c] == EMPTY:
                    return True

    # Tốt (P/p) tấn công Tướng
    if is_red:
        # Tốt đen (p) tấn công Tướng đỏ từ phía trên, hoặc hai bên nếu đã qua sông
        for dr, dc in [(-1,0),(0,-1),(0,1)]:
            nr, nc = kr+dr, kc+dc
            if 0 <= nr < 10 and 0 <= nc < 9:
                p = board[nr][nc]
                if p == 'p': return True
    else:
        # Tốt đỏ (P) tấn công Tướng đen từ phía dưới, hoặc hai bên nếu đã qua sông
        for dr, dc in [(1,0),(0,-1),(0,1)]:
            nr, nc = kr+dr, kc+dc
            if 0 <= nr < 10 and 0 <= nc < 9:
                p = board[nr][nc]
                if p == 'P': return True

    return False


def main():
    print("="*40)
    print("CỜ TƯỚNG - MINIMAX CƠ BẢN (DEPTH)")
    print("AI vs AI tự động đấu nếu cả 2 bên cùng chọn AI")
    print("="*40)
    
    depth = int(input("Nhập độ sâu tối đa (Depth): "))
    mode = input("Chọn chế độ (1: Bạn vs AI, 2: AI vs AI): ").strip()
    
    user_side = RED if mode == "1" else None
    
    state = initial_state()
    
    while True:
        print_board(state)
        if terminal(state):
            w = get_winner(state)
            print(f"🎉 KẾT THÚC: {w} THẮNG!" if w else "⚖️ HÒA!")
            break
            
        if state['turn'] == user_side:
            has_moves = any(True for _ in successors(state))
            if not has_moves:
                winner = 'BLACK' if user_side == 'RED' else 'RED'
                print(f"💥 BẠN ĐÃ HẾT NƯỚC ĐI! Tướng bị khóa chặt. Phe {winner} THẮNG!")
                break

            
            print(f"Lượt của BẠN ({state['turn']}):")
            sr = int(input("Hàng quân cờ: "))
            sc = int(input("Cột quân cờ: "))
            er = int(input("Hàng tới: "))
            ec = int(input("Cột tới: "))
            
            # Simple apply
            state['board'][er][ec] = state['board'][sr][sc]
            state['board'][sr][sc] = EMPTY
            state['turn'] = BLACK if state['turn'] == RED else RED
            state['played_count'] += 1

            b_tup = tuple(tuple(row) for row in state['board'])

            state['history_counts'][b_tup] = state.get('history_counts', {}).get(b_tup, 0) + 1
        else:
            move = find_best_move(state, depth)
            if move:
                for m, next_st in successors(state):
                    if m == move:
                        state = next_st
                        break
            else:
                winner = 'RED' if state['turn'] == 'BLACK' else 'BLACK'
                print(f"💥 AI ({state['turn']}) ĐÃ HẾT NƯỚC ĐI CỨU CHÚA! Phe {winner} THẮNG!")
                break

if __name__ == "__main__":
    main()
