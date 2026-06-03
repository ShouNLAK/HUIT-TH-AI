import time
import random
from heapq import heappush, heappop

# ============================================================
# 1. TRẠNG THÁI BAN ĐẦU (INITIAL STATE)
#    Trạng thái của trò chơi (N-Puzzle) + Người "đi" đầu tiên.
#    Vì N-Puzzle là bài toán 1 người chơi, không có khái niệm
#    lượt, nhưng "người di chuyển" luôn là AI (thuật toán).
# ============================================================
def initial_state(n):
    """
    Trả về (initial_1d, final_1d, n):
      - initial_1d : tuple 1D – trạng thái khởi đầu ngẫu nhiên hợp lệ.
      - final_1d   : tuple 1D – trạng thái đích (1,2,...,n²-1,0).
      - n          : kích thước lưới.
    Người đi đầu tiên: thuật toán A* (bài toán 1 người).
    """
    final = tuple(range(1, n * n)) + (0,)
    initial = _make_solvable(list(final), n)
    return tuple(initial), final, n


# ============================================================
# 2. TRẠNG THÁI KẾT THÚC (TERMINAL STATE)
#    Kiểm tra kết thúc trò chơi: đã đến đích chưa?
# ============================================================
def terminal(state_1d, final_1d):
    """
    Trả về True nếu state_1d == final_1d (đã giải xong).
    """
    return state_1d == final_1d


# ============================================================
# 3. HÀM CHUYỂN TRẠNG THÁI (SUCCESSORS)
#    Trả về iterator của (tile_from, new_state).
#    tile_from = vị trí cũ của ô được hoán đổi với blank
#               = vị trí mới của blank.
# ============================================================
def successors(state_1d, blank_idx, n):
    """
    Sinh tất cả nước đi hợp lệ từ state_1d.
    Yield: (tile_from, new_state_1d)
      - tile_from    : vị trí cũ của ô vừa được di chuyển vào chỗ blank
                       (= vị trí mới của blank sau nước đi).
      - new_state_1d : trạng thái mới sau khi hoán đổi.
    Blank sau nước đi sẽ ở tile_from.
    Ô di chuyển sẽ ở blank_idx (vị trí cũ của blank).
    """
    r, c = blank_idx // n, blank_idx % n
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < n:
            tile_from = nr * n + nc        # vị trí của ô sẽ di chuyển
            lst = list(state_1d)
            lst[blank_idx], lst[tile_from] = lst[tile_from], lst[blank_idx]
            # Sau swap: ô di chuyển đến blank_idx, blank đến tile_from
            yield tile_from, tuple(lst)


# ============================================================
# 4. HÀM LỢI ÍCH / HEURISTIC (UTILITY / EVALUATION)
#    Đánh giá trạng thái: khoảng cách Manhattan đến đích.
# ============================================================
def utility(state_1d, target_pos, n):
    """
    Tính tổng khoảng cách Manhattan từ mỗi ô đến vị trí đích.
    Dùng một lần ở khởi tạo (O(N²)); sau đó dùng incremental
    O(1) trong vòng lặp chính.
    """
    dist = 0
    for i, val in enumerate(state_1d):
        if val != 0:
            tx, ty = target_pos[val]
            dist += abs(i // n - tx) + abs(i % n - ty)
    return dist


def incremental_h(h_prev, old_state, tile_from, tile_to, target_pos, n):
    """
    Cập nhật heuristic O(1) sau mỗi nước đi:
      - tile_from : vị trí cũ của ô (đọc từ old_state để lấy giá trị).
      - tile_to   : vị trí mới của ô (= vị trí cũ của blank).
    h_new = h_prev - old_manhattan(tile) + new_manhattan(tile)
    """
    tile = old_state[tile_from]
    if tile == 0:
        return h_prev
    tx, ty = target_pos[tile]
    old_d = abs(tile_from // n - tx) + abs(tile_from % n - ty)
    new_d = abs(tile_to   // n - tx) + abs(tile_to   % n - ty)
    return h_prev - old_d + new_d


# ============================================================
# CÁC HÀM HỖ TRỢ
# ============================================================
def _get_target_pos(final_1d, n):
    return {val: (i // n, i % n) for i, val in enumerate(final_1d)}

def _is_solvable(state, n):
    lst = list(state)
    inv = sum(
        1 for i in range(len(lst))
          for j in range(i + 1, len(lst))
          if lst[i] != 0 and lst[j] != 0 and lst[i] > lst[j]
    )
    if n % 2 != 0:
        return inv % 2 == 0
    blank_row_from_bottom = n - (lst.index(0) // n)
    return (inv % 2 != 0) if (blank_row_from_bottom % 2 == 0) else (inv % 2 == 0)

def _make_solvable(state, n):
    random.shuffle(state)
    if not _is_solvable(state, n):
        # Hoán đổi 2 ô đầu tiên ≠ 0 để đổi parity
        i1, i2 = [i for i, v in enumerate(state) if v != 0][:2]
        state[i1], state[i2] = state[i2], state[i1]
    return state

def print_grid(state, n):
    for i in range(0, n * n, n):
        row = state[i:i+n]
        print(" | ".join(f"{x:2}" if x != 0 else "  " for x in row))
    print("-" * (n * 5))


# ============================================================
# THUẬT TOÁN A* SỬ DỤNG 4 THÀNH PHẦN
# ============================================================
def solve_npuzzle(n):
    # --- 1. INITIAL STATE ---
    init_1d, final_1d, n = initial_state(n)
    target_pos = _get_target_pos(final_1d, n)

    print("\n--- Trạng thái ban đầu (Initial State) ---")
    print_grid(init_1d, n)
    print("Đang giải...\n")

    start_time = time.time()
    blank_idx = init_1d.index(0)

    # Tính heuristic ban đầu bằng utility() O(N²) – chỉ 1 lần
    h0 = utility(init_1d, target_pos, n)

    # Priority Queue: (f, g, blank_idx, state_1d, h)
    pq = [(h0, 0, blank_idx, init_1d, h0)]
    g_scores = {init_1d: 0}
    came_from = {init_1d: None}

    while pq:
        f, g, cur_blank, cur_state, cur_h = heappop(pq)

        # --- 2. TERMINAL STATE ---
        if terminal(cur_state, final_1d):
            path = []
            s = cur_state
            while s is not None:
                path.append(s)
                s = came_from[s]
            path.reverse()

            elapsed = time.time() - start_time
            print(f"Giải xong trong {elapsed:.4f}s")
            print(f"Số bước: {g} | Số trạng thái đã xét: {len(g_scores)}\n")

            print("\nChi tiết các bước giải:")
            for step, p_state in enumerate(path):
                print(f"Bước {step}:")
                print_grid(p_state, n)
            return

        if g > g_scores.get(cur_state, float('inf')):
            continue

        # --- 3. SUCCESSORS (hàm chuyển trạng thái) ---
        for tile_from, new_state in successors(cur_state, cur_blank, n):
            new_g = g + 1
            if new_g < g_scores.get(new_state, float('inf')):
                g_scores[new_state] = new_g
                came_from[new_state] = cur_state

                # --- 4. UTILITY (incremental O(1)) ---
                # Ô ở tile_from đã di chuyển đến cur_blank (vị trí blank cũ)
                # Blank mới ở tile_from
                new_h = incremental_h(cur_h, cur_state, tile_from, cur_blank, target_pos, n)
                new_blank = tile_from   # blank đã di chuyển đến đây
                heappush(pq, (new_g + new_h, new_g, new_blank, new_state, new_h))

    print("Không tìm thấy đường đi!")


if __name__ == "__main__":
    while True:
        try:
            n = int(input("Nhập kích thước lưới n (khuyên 2-5, có thể tới 7+): "))
            if n > 0:
                break
        except ValueError:
            pass
    solve_npuzzle(n)