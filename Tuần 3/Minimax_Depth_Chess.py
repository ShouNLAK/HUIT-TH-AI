import copy
import math

_PST = {
    'P': [0,0,0,0,0,0,0,0,50,50,50,50,50,50,50,50,10,10,20,30,30,20,10,10,5,5,10,25,25,10,5,5,0,0,0,20,20,0,0,0,5,-5,-10,0,0,-10,-5,5,5,10,10,-20,-20,10,10,5,0,0,0,0,0,0,0,0],
    'N': [-50,-40,-30,-30,-30,-30,-40,-50,-40,-20,0,0,0,0,-20,-40,-30,0,10,15,15,10,0,-30,-30,5,15,20,20,15,5,-30,-30,0,15,20,20,15,0,-30,-30,5,10,15,15,10,5,-30,-40,-20,0,5,5,0,-20,-40,-50,-40,-30,-30,-30,-30,-40,-50],
    'B': [-20,-10,-10,-10,-10,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,10,10,5,0,-10,-10,5,5,10,10,5,5,-10,-10,0,10,10,10,10,0,-10,-10,10,10,10,10,10,10,-10,-10,5,0,0,0,0,5,-10,-20,-10,-10,-10,-10,-10,-10,-20],
    'R': [0,0,0,0,0,0,0,0,5,10,10,10,10,10,10,5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,-5,0,0,0,0,0,0,-5,0,0,0,5,5,0,0,0],
    'Q': [-20,-10,-10,-5,-5,-10,-10,-20,-10,0,0,0,0,0,0,-10,-10,0,5,5,5,5,0,-10,-5,0,5,5,5,5,0,-5,0,0,5,5,5,5,0,-5,-10,5,5,5,5,5,0,-10,-10,0,5,0,0,0,0,-10,-20,-10,-10,-5,-5,-10,-10,-20],
    'K': [-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-30,-40,-40,-50,-50,-40,-40,-30,-20,-30,-30,-40,-40,-30,-30,-20,-10,-20,-20,-20,-20,-20,-20,-10,20,20,0,0,0,0,20,20,20,30,10,0,0,10,30,20],
}

# Ký hiệu quân cờ (Viết hoa = TRẮNG, Viết thường = ĐEN)
# K, k: Vua (King)
# Q, q: Hậu (Queen)
# R, r: Xe (Rook)
# B, b: Tượng (Bishop)
# N, n: Mã (Knight)
# P, p: Tốt (Pawn)
EMPTY = "."
WHITE = "WHITE"
BLACK = "BLACK"

def get_initial_board():
    return [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['.', '.', '.', '.', '.', '.', '.', '.'],
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]

def initial_state():
    b = get_initial_board()
    b_tup = tuple(tuple(r) for r in b)
    return {
        'board':   b,
        'turn':    WHITE,
        'played_count': 0,
        'castling': {'K': True, 'Q': True, 'k': True, 'q': True},
        'en_passant': None,
        'history_counts': {b_tup: 1},
        'has_legal_move': True,
    }

def print_board(state):
    print("\n   " + " ".join(str(i) for i in range(8)))
    for r in range(8):
        print(f"{r}  " + " ".join(state['board'][r]))
    print()

def is_attacked(board, r, c, attacker_is_white):
    # Check Knight
    for dr, dc in [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]:
        nr, nc = r+dr, c+dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            p = board[nr][nc]
            if p != EMPTY and p.isupper() == attacker_is_white and p.upper() == 'N':
                return True
    
    # Check Diagonals (Bishop, Queen)
    for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
        nr, nc = r+dr, c+dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            p = board[nr][nc]
            if p != EMPTY:
                if p.isupper() == attacker_is_white and p.upper() in ['B', 'Q']:
                    return True
                break
            nr, nc = nr+dr, nc+dc
            
    # Check Orthogonal (Rook, Queen)
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = r+dr, c+dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            p = board[nr][nc]
            if p != EMPTY:
                if p.isupper() == attacker_is_white and p.upper() in ['R', 'Q']:
                    return True
                break
            nr, nc = nr+dr, nc+dc
            
    # Check Pawn
    p_dir = 1 if attacker_is_white else -1
    for dc in [-1, 1]:
        nr, nc = r + p_dir, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8:
            p = board[nr][nc]
            if p != EMPTY and p.isupper() == attacker_is_white and p.upper() == 'P':
                return True
                
    # Check King
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0: continue
            nr, nc = r+dr, c+dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                p = board[nr][nc]
                if p != EMPTY and p.isupper() == attacker_is_white and p.upper() == 'K':
                    return True
                    
    return False

def generate_pseudo_legal_moves(state):
    board = state['board']
    turn = state['turn']
    is_white = (turn == WHITE)
    moves = []
    
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == EMPTY: continue
            if (p.isupper() and is_white) or (p.islower() and not is_white):
                p_upper = p.upper()
                
                if p_upper == 'P':
                    # Tiến
                    dr = -1 if is_white else 1
                    start_r = 6 if is_white else 1
                    
                    if 0 <= r + dr < 8 and board[r + dr][c] == EMPTY:
                        moves.append(((r, c), (r + dr, c), None)) # None = no promotion specified, handled in apply
                        # Tiến 2 bước
                        if r == start_r and board[r + 2*dr][c] == EMPTY:
                            moves.append(((r, c), (r + 2*dr, c), None))
                    # Ăn chéo
                    for dc in [-1, 1]:
                        if 0 <= r + dr < 8 and 0 <= c + dc < 8:
                            target = board[r + dr][c + dc]
                            if target != EMPTY and target.isupper() != is_white:
                                moves.append(((r, c), (r + dr, c + dc), None))
                            elif state['en_passant'] == (r + dr, c + dc):
                                moves.append(((r, c), (r + dr, c + dc), 'EP'))
                
                elif p_upper == 'N':
                    for dr, dc in [(-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)]:
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < 8 and 0 <= nc < 8:
                            if board[nr][nc] == EMPTY or board[nr][nc].isupper() != is_white:
                                moves.append(((r, c), (nr, nc), None))
                                
                elif p_upper in ['B', 'R', 'Q']:
                    dirs = []
                    if p_upper in ['B', 'Q']: dirs.extend([(-1,-1), (-1,1), (1,-1), (1,1)])
                    if p_upper in ['R', 'Q']: dirs.extend([(-1,0), (1,0), (0,-1), (0,1)])
                    
                    for dr, dc in dirs:
                        nr, nc = r+dr, c+dc
                        while 0 <= nr < 8 and 0 <= nc < 8:
                            if board[nr][nc] == EMPTY:
                                moves.append(((r, c), (nr, nc), None))
                            else:
                                if board[nr][nc].isupper() != is_white:
                                    moves.append(((r, c), (nr, nc), None))
                                break
                            nr, nc = nr+dr, nc+dc
                            
                elif p_upper == 'K':
                    for dr in [-1, 0, 1]:
                        for dc in [-1, 0, 1]:
                            if dr == 0 and dc == 0: continue
                            nr, nc = r+dr, c+dc
                            if 0 <= nr < 8 and 0 <= nc < 8:
                                if board[nr][nc] == EMPTY or board[nr][nc].isupper() != is_white:
                                    moves.append(((r, c), (nr, nc), None))
                    
                    # Castling
                    if is_white:
                        if state['castling']['K'] and board[7][5] == EMPTY and board[7][6] == EMPTY:
                            if not is_attacked(board, 7, 4, False) and not is_attacked(board, 7, 5, False) and not is_attacked(board, 7, 6, False):
                                moves.append(((7, 4), (7, 6), 'CASTLE_K'))
                        if state['castling']['Q'] and board[7][3] == EMPTY and board[7][2] == EMPTY and board[7][1] == EMPTY:
                            if not is_attacked(board, 7, 4, False) and not is_attacked(board, 7, 3, False) and not is_attacked(board, 7, 2, False):
                                moves.append(((7, 4), (7, 2), 'CASTLE_Q'))
                    else:
                        if state['castling']['k'] and board[0][5] == EMPTY and board[0][6] == EMPTY:
                            if not is_attacked(board, 0, 4, True) and not is_attacked(board, 0, 5, True) and not is_attacked(board, 0, 6, True):
                                moves.append(((0, 4), (0, 6), 'CASTLE_k'))
                        if state['castling']['q'] and board[0][3] == EMPTY and board[0][2] == EMPTY and board[0][1] == EMPTY:
                            if not is_attacked(board, 0, 4, True) and not is_attacked(board, 0, 3, True) and not is_attacked(board, 0, 2, True):
                                moves.append(((0, 4), (0, 2), 'CASTLE_q'))
    return moves

def get_winner(state):
    # 3-fold repetition
    for cnt in state.get('history_counts', {}).values():
        if cnt >= 3:
            return 'DRAW'
    if not state.get('has_legal_move', True):
        is_white = (state['turn'] == WHITE)
        kr, kc = -1, -1
        for r in range(8):
            for c in range(8):
                if state['board'][r][c] == ('K' if is_white else 'k'):
                    kr, kc = r, c; break
            if kr != -1: break
        if kr != -1 and is_attacked(state['board'], kr, kc, not is_white):
            return BLACK if is_white else WHITE
        return 'DRAW'
    return None

def utility(state, current_depth=0):
    w = get_winner(state)
    if w == WHITE:  return  1000 - current_depth
    if w == BLACK:  return -1000 + current_depth
    if w == 'DRAW': return 0

    # Repetition penalty inside search
    for cnt in state.get('history_counts', {}).values():
        if cnt >= 3:
            return 0

    PIECE_VAL = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
    score = 0
    board = state['board']
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == EMPTY: continue
            pu = p.upper()
            pv = PIECE_VAL.get(pu, 0)
            if p.isupper():          # White
                pst_idx = r * 8 + c
                pst = _PST.get(pu, [0]*64)[pst_idx]
                score += pv + pst
            else:                    # Black (mirror row)
                pst_idx = (7 - r) * 8 + c
                pst = _PST.get(pu, [0]*64)[pst_idx]
                score -= pv + pst
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
            kr, kc = -1, -1
            for r in range(8):
                for c in range(8):
                    if state['board'][r][c] == 'K': kr, kc = r, c; break
                if kr != -1: break
            if kr != -1 and is_attacked(state['board'], kr, kc, False):
                return -1000 + current_depth
            else:
                return 0
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
            kr, kc = -1, -1
            for r in range(8):
                for c in range(8):
                    if state['board'][r][c] == 'k': kr, kc = r, c; break
                if kr != -1: break
            if kr != -1 and is_attacked(state['board'], kr, kc, True):
                return 1000 - current_depth
            else:
                return 0
        return min_eval

def find_best_move(state, depth):
    turn = state['turn']
    is_max = (turn == WHITE)
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

def terminal(state):
    # 3-fold repetition → draw
    for cnt in state.get('history_counts', {}).values():
        if cnt >= 3:
            return True
    # No legal moves → checkmate or stalemate (handled by get_winner)
    if not state.get('has_legal_move', True):
        return True
    return False


def successors(state):
    board      = state['board']
    turn       = state['turn']
    is_white   = (turn == WHITE)
    next_turn  = BLACK if is_white else WHITE
    castling   = state.get('castling', {'K':False,'Q':False,'k':False,'q':False})

    # Move ordering buffers: captures first, then quiet moves
    captures, quiets = [], []
    for move in generate_pseudo_legal_moves(state):
        (sr, sc), (er, ec), special = move
        target = board[er][ec]
        if target != EMPTY or special == 'EP':
            captures.append(move)
        else:
            quiets.append(move)

    has_legal = False
    for move in captures + quiets:
        (sr, sc), (er, ec), special = move
        nb = [row[:] for row in board]
        nc = dict(castling)
        nep = None

        p = nb[sr][sc]
        nb[er][ec] = p
        nb[sr][sc] = EMPTY

        if special == 'EP':
            nb[sr][ec] = EMPTY
        elif special == 'CASTLE_K':
            nb[7][5] = nb[7][7]; nb[7][7] = EMPTY
        elif special == 'CASTLE_Q':
            nb[7][3] = nb[7][0]; nb[7][0] = EMPTY
        elif special == 'CASTLE_k':
            nb[0][5] = nb[0][7]; nb[0][7] = EMPTY
        elif special == 'CASTLE_q':
            nb[0][3] = nb[0][0]; nb[0][0] = EMPTY

        # Promotion → always Queen
        if p.upper() == 'P':
            if abs(er - sr) == 2:
                nep = ((sr + er) // 2, sc)
            if er == 0:
                nb[er][ec] = 'q'
            elif er == 7:
                nb[er][ec] = 'Q'

        # Castling rights update
        if p == 'K': nc['K'] = nc['Q'] = False
        if p == 'k': nc['k'] = nc['q'] = False
        if p == 'R':
            if sr == 7 and sc == 7: nc['K'] = False
            if sr == 7 and sc == 0: nc['Q'] = False
        if p == 'r':
            if sr == 0 and sc == 7: nc['k'] = False
            if sr == 0 and sc == 0: nc['q'] = False

        # King safety check
        kr, kc = -1, -1
        king_sym = 'K' if is_white else 'k'
        for r in range(8):
            for c in range(8):
                if nb[r][c] == king_sym:
                    kr, kc = r, c; break
            if kr != -1: break
        if kr == -1 or is_attacked(nb, kr, kc, not is_white):
            continue

        has_legal = True
        new_hist = state.get('history_counts', {}).copy()
        b_tup = tuple(tuple(row) for row in nb)
        new_hist[b_tup] = new_hist.get(b_tup, 0) + 1

        yield move, {
            'board': nb,
            'turn':  next_turn,
            'played_count': state['played_count'] + 1,
            'castling':     nc,
            'en_passant':   nep,
            'has_legal_move': True,
            'history_counts': new_hist,
        }
    state['has_legal_move'] = has_legal


def main():
    print("="*40)
    print("CỜ VUA - MINIMAX CƠ BẢN (DEPTH)")
    print("AI vs AI tự động đấu nếu cả 2 bên cùng chọn AI")
    print("="*40)
    
    depth = int(input("Nhập độ sâu tối đa (Depth): "))
    mode = input("Chọn chế độ (1: Bạn vs AI, 2: AI vs AI): ").strip()
    
    user_side = WHITE if mode == "1" else None
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
                is_white = (state['turn'] == 'WHITE')
                kr, kc = -1, -1
                for r in range(8):
                    for c in range(8):
                        if state['board'][r][c] == ('K' if is_white else 'k'):
                            kr, kc = r, c; break
                    if kr != -1: break
                
                if kr != -1 and is_attacked(state['board'], kr, kc, not is_white):
                    winner = 'BLACK' if is_white else 'WHITE'
                    print(f"💥 BẠN ĐÃ BỊ CHIẾU BÍ (CHECKMATE)! Phe {winner} THẮNG!")
                else:
                    print("⚖️ HÒA! (STALEMATE - Bạn hết nước đi nhưng Vua không bị chiếu)")
                break

            
            print(f"Lượt của BẠN ({state['turn']}):")
            sr = int(input("Hàng quân cờ: "))
            sc = int(input("Cột quân cờ: "))
            er = int(input("Hàng tới: "))
            ec = int(input("Cột tới: "))
            
            # Simple apply without full validation for user input (Assuming user inputs legal moves)
            # Validate through successors (handles all special moves)
            found = False
            for move, next_st in successors(state):
                (msr, msc), (mer, mec), msp = move
                if msr == sr and msc == sc and mer == er and mec == ec:
                    state = next_st
                    found = True
                    break
            if not found:
                print("❌ Nước đi không hợp lệ! Thử lại.")
                continue
        else:
            move = find_best_move(state, depth)
            if move:
                (sr, sc), (er, ec), special = move
                for m, next_st in successors(state):
                    if m == move:
                        state = next_st
                        break
            else:
                is_white = (state['turn'] == 'WHITE')
                kr, kc = -1, -1
                for r in range(8):
                    for c in range(8):
                        if state['board'][r][c] == ('K' if is_white else 'k'):
                            kr, kc = r, c; break
                    if kr != -1: break
                
                if kr != -1 and is_attacked(state['board'], kr, kc, not is_white):
                    winner = 'BLACK' if is_white else 'WHITE'
                    print(f"💥 AI ({state['turn']}) BỊ CHIẾU BÍ (CHECKMATE)! Phe {winner} THẮNG!")
                else:
                    print("⚖️ HÒA! (STALEMATE - AI hết nước đi nhưng Vua không bị chiếu)")
                break

if __name__ == "__main__":
    main()
