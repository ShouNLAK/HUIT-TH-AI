import time
import random
from heapq import heappush, heappop

# ============================================================
# 1. TRẠNG THÁI BAN ĐẦU (INITIAL STATE)
#    Trạng thái = vị trí các ô trên lưới NxN.
#    Bài toán 1 tác nhân (AI giải), không có lượt người chơi.
# ============================================================
def initial_state(n):
    """
    Trả về (initial_1d, final_1d, target_pos):
      - initial_1d : tuple 1D – trạng thái ban đầu ngẫu nhiên hợp lệ.
      - final_1d   : tuple 1D – trạng thái đích (1,2,...,n²-1,0).
      - target_pos : dict {tile: (row, col)} – vị trí đích của từng ô.
    Người/tác nhân đi đầu tiên: thuật toán Weighted A*.
    """
    N = n * n
    final = tuple(range(1, N)) + (0,)
    target_pos = {val: (i // n, i % n) for i, val in enumerate(final)}
    while True:
        state = list(range(1, N)) + [0]
        random.shuffle(state)
        state_t = tuple(state)
        if _is_solvable(state_t, n):
            return state_t, final, target_pos


# ============================================================
# 2. TRẠNG THÁI KẾT THÚC (TERMINAL STATE)
#    Kiểm tra puzzle đã được giải xong chưa.
# ============================================================
def terminal(state_1d, final_1d):
    """
    Trả về True nếu state_1d == final_1d (đã đến đích).
    """
    return state_1d == final_1d


# ============================================================
# 3. HÀM CHUYỂN TRẠNG THÁI (SUCCESSORS)
#    Trả về iterator của (nước_đi, trạng_thái_mới).
#    Nước đi = ô được hoán đổi với ô trống.
# ============================================================
def successors(state_1d, blank_idx, n):
    """
    Sinh tất cả nước đi hợp lệ bằng cách hoán đổi ô trống
    với các ô kề (trái, phải, trên, dưới).
    Yield: (tile_from, new_state_1d)
      - tile_from    : vị trí cũ của ô vừa di chuyển (= vị trí blank mới).
      - new_state_1d : trạng thái mới sau khi hoán đổi.
    """
    r, c = blank_idx // n, blank_idx % n
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < n:
            tile_from = nr * n + nc
            lst = list(state_1d)
            lst[blank_idx], lst[tile_from] = lst[tile_from], lst[blank_idx]
            yield tile_from, tuple(lst)


# ============================================================
# 4. HÀM LỢI ÍCH (UTILITY / HEURISTIC)
#    Đánh giá trạng thái: khoảng cách Manhattan.
#    Dùng Weighted h → Weighted A* (giải bài toán lớn nhanh hơn).
# ============================================================
def utility(state_1d, target_pos, n):
    """
    Tính tổng khoảng cách Manhattan từ mỗi ô đến vị trí đích.
    Dùng một lần duy nhất khi khởi tạo; sau đó dùng incremental O(1).
    """
    dist = 0
    for i, val in enumerate(state_1d):
        if val != 0:
            tx, ty = target_pos[val]
            dist += abs(i // n - tx) + abs(i % n - ty)
    return dist


def incremental_update(h_prev, old_state, tile_from, tile_to, target_pos, n):
    """
    Cập nhật heuristic O(1):
    h_new = h_prev - old_dist(tile) + new_dist(tile)
    """
    tile = old_state[tile_from]
    if tile == 0:
        return h_prev
    tx, ty = target_pos[tile]
    old_r, old_c = tile_from // n, tile_from % n
    new_r, new_c = tile_to // n, tile_to % n
    return h_prev - abs(old_r - tx) - abs(old_c - ty) + abs(new_r - tx) + abs(new_c - ty)


# ============================================================
# CÁC HÀM HỖ TRỢ
# ============================================================
def _is_solvable(state_1d, n):
    arr = [x for x in state_1d if x != 0]
    inv = sum(1 for i in range(len(arr)) for j in range(i+1, len(arr)) if arr[i] > arr[j])
    blank_idx = state_1d.index(0)
    blank_row_from_bottom = n - (blank_idx // n)
    if n % 2 != 0:
        return inv % 2 == 0
    return (inv + blank_row_from_bottom) % 2 == 1

class Node:
    __slots__ = ['parent', 'state_1d', 'blank_idx', 'g', 'h', 'f', 'move_idx']
    def __init__(self, parent, state_1d, blank_idx, g, h, move_idx=-1):
        self.parent   = parent
        self.state_1d = state_1d
        self.blank_idx = blank_idx
        self.g = g
        self.h = h
        self.f = g + h
        self.move_idx = move_idx

    def __lt__(self, other):
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f

def print_path(node, n):
    path = []
    curr = node
    while curr:
        path.append(curr.state_1d)
        curr = curr.parent
    path.reverse()
    print(f"-> Tổng số bước (Path Length): {len(path) - 1}")
    print("\nChi tiết các bước giải:")
    for step, p_state in enumerate(path):
        print(f"\nBước {step}:")
        for r in range(n):
            row = p_state[r*n : (r+1)*n]
            print("\t".join(str(x) if x != 0 else " " for x in row))


# ============================================================
# THUẬT TOÁN WEIGHTED A* SỬ DỤNG 4 THÀNH PHẦN
# ============================================================
def solve_n_puzzle(n, weight=4.0):
    # --- 1. INITIAL STATE ---
    initial_1d, final_1d, target_pos = initial_state(n)

    print(f"\nMa trận ban đầu (Initial State) [{n}x{n}]:")
    for row_i in range(n):
        print("\t".join(str(initial_1d[row_i*n + c]) if initial_1d[row_i*n + c] != 0 else " " for c in range(n)))
    print("\nMa trận đích (Terminal/Goal State):")
    for row_i in range(n):
        print("\t".join(str(final_1d[row_i*n + c]) if final_1d[row_i*n + c] != 0 else " " for c in range(n)))

    # Kiểm tra khả năng giải
    if not _is_solvable(initial_1d, n):
        print("CẢNH BÁO: Trạng thái ban đầu KHÔNG THỂ GIẢI!")
        return

    start_time = time.time()
    blank_idx = initial_1d.index(0)

    # Tính heuristic ban đầu bằng utility() O(N²) – chỉ 1 lần
    h0 = utility(initial_1d, target_pos, n)

    root = Node(None, initial_1d, blank_idx, g=0, h=int(h0 * weight))
    pq = [root]
    visited = {initial_1d: 0}
    expanded = 0

    while pq:
        cur = heappop(pq)

        # --- 2. TERMINAL STATE ---
        if terminal(cur.state_1d, final_1d):
            print("\n--- ĐÃ TÌM THẤY ĐƯỜNG ĐI ---")
            print_path(cur, n)
            print(f"Số trạng thái đã mở rộng: {expanded}")
            print(f"Thời gian: {time.time() - start_time:.4f}s")
            return

        expanded += 1

        # --- 3. SUCCESSORS ---
        for tile_from, new_state in successors(cur.state_1d, cur.blank_idx, n):
            new_g = cur.g + 1
            if new_state not in visited or new_g < visited[new_state]:
                visited[new_state] = new_g

                # --- 4. UTILITY (incremental O(1)) ---
                raw_h = incremental_update(
                    cur.h // weight if weight != 0 else cur.h,
                    cur.state_1d, tile_from, cur.blank_idx, target_pos, n)
                weighted_h = int(raw_h * weight)
                
                new_blank = tile_from
                child = Node(cur, new_state, new_blank, new_g, weighted_h, tile_from)
                heappush(pq, child)

    print("Không tìm thấy đường đi!")


if __name__ == "__main__":
    while True:
        try:
            n = int(input("Nhập kích thước lưới n (khuyên 3-5): "))
            if n > 0:
                break
        except ValueError:
            pass
            
    print(f"Khởi tạo ma trận {n}x{n}...")
    print("Đang giải bằng Weighted A* (weight=4.0)...")
    solve_n_puzzle(n, weight=4.0)