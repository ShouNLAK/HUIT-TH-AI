import time
import random
from heapq import heappush, heappop

# 1. KIỂM TRA TÍNH KHẢ GIẢI (Ngăn chặn vòng lặp vô hạn nếu ma trận ngẫu nhiên bị lỗi)
def is_solvable(state_1d, n):
    inversions = 0
    arr = [x for x in state_1d if x != 0]
    for i in range(len(arr)):
        for j in range(i + 1, len(arr)):
            if arr[i] > arr[j]:
                inversions += 1
    
    blank_idx = state_1d.index(0)
    blank_row_from_bottom = n - (blank_idx // n)
    
    if n % 2 != 0:
        return inversions % 2 == 0
    else:
        return (inversions + blank_row_from_bottom) % 2 == 1

# 2. TẠO TRẠNG THÁI NGẪU NHIÊN HỢP LỆ (Luôn luôn giải được)
def generate_solvable_state(n):
    N = n * n
    while True:
        # Trạng thái đích mặc định: Thứ tự tăng dần từ 1 đến (n^2 - 1), ô trống ở cuối (0)
        state = list(range(1, N)) + [0]
        random.shuffle(state)
        state_tuple = tuple(state)
        if is_solvable(state_tuple, n):
            return [list(state_tuple[i*n:(i+1)*n]) for i in range(n)]

# 3. CẤU TRÚC NODE TỐI ƯU CỰC NHẸ
class Node:
    def __init__(self, parent, state_1d, blank_idx, g, h):
        self.parent = parent
        self.state_1d = state_1d
        self.blank_idx = blank_idx
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        if self.f == other.f:
            return self.g > other.g  # Ưu tiên các node có chiều sâu g lớn hơn để đến đích nhanh hơn
        return self.f < other.f

# 4. HÀM TÍNH MANHATTAN TỐI ƯU TRÊN MẢNG 1D
def calculate_manhattan(state_1d, target_pos, n):
    dist = 0
    for idx, val in enumerate(state_1d):
        if val == 0:
            continue
        target_r, target_c = target_pos[val]
        current_r, current_c = idx // n, idx % n
        dist += abs(target_r - current_r) + abs(target_c - current_c)
    return dist

# 5. IN ĐƯỜNG ĐI CHI TIẾT
def print_path(node, n):
    path = []
    curr = node
    while curr:
        mat_2d = [list(curr.state_1d[i*n:(i+1)*n]) for i in range(n)]
        path.append(mat_2d)
        curr = curr.parent
    
    print(f"-> Tổng số bước di chuyển (Path Length): {len(path) - 1}")
    # Bạn có thể bỏ comment đoạn dưới nếu muốn in ra từng bước dịch chuyển cụ thể
    """
    for i, step in enumerate(reversed(path)):
        print(f"\n[Bước {i}]")
        for row in step:
            print("\t".join(map(str, row)))
    """

# 6. THUẬT TOÁN WEIGHTED A* CHÍNH
def solve_n_puzzle(initial_mat, final_mat, n, weight=4.0):
    start_time = time.time()
    
    # Flatten dữ liệu sang 1D tuple để tối ưu bộ nhớ và tốc độ băm
    initial_1d = tuple(item for row in initial_mat for item in row)
    final_1d = tuple(item for row in final_mat for item in row)
    
    if not is_solvable(initial_1d, n):
        print("CẢNH BÁO: Trạng thái khởi tạo KHÔNG THỂ GIẢI ĐƯỢC!")
        return
        
    # Tính toán trước sơ đồ đích O(1)
    target_pos = {val: (i // n, i % n) for i, val in enumerate(final_1d)}
    
    blank_idx = initial_1d.index(0)
    initial_h = calculate_manhattan(initial_1d, target_pos, n)
    
    # Khởi tạo Node gốc với Heuristic có trọng số (Weighted)
    root = Node(None, initial_1d, blank_idx, 0, int(initial_h * weight))
    
    pq = [root]
    visited = {initial_1d: 0} # Lưu trạng thái kèm chi phí g nhỏ nhất
    expanded_nodes = 0
    
    while pq:
        current = heappop(pq)
        
        if current.state_1d == final_1d:
            print("--- ĐÃ TÌM THẤY ĐƯỜNG ĐI ĐẾN ĐÍCH ---")
            print_path(current, n)
            print(f"Tổng số trạng thái đã xét (Expanded Nodes): {expanded_nodes}")
            print(f"Thời gian giải: {time.time() - start_time:.4f} giây")
            return

        expanded_nodes += 1
        
        r, c = current.blank_idx // n, current.blank_idx % n
        
        # Xác định các index lệch hợp lệ trên mảng 1D tương ứng (Lên, Xuống, Trái, Phải)
        moves = []
        if r > 0: moves.append(-n)     # Di chuyển lên
        if r < n - 1: moves.append(n)  # Di chuyển xuống
        if c > 0: moves.append(-1)     # Di chuyển sang trái
        if c < n - 1: moves.append(1)  # Di chuyển sang phải
        
        for offset in moves:
            new_blank_idx = current.blank_idx + offset
            
            # Tráo đổi phần tử nhanh trên List
            next_state = list(current.state_1d)
            next_state[current.blank_idx], next_state[new_blank_idx] = next_state[new_blank_idx], next_state[current.blank_idx]
            next_state_tuple = tuple(next_state)
            
            new_g = current.g + 1
            
            if next_state_tuple not in visited or new_g < visited[next_state_tuple]:
                visited[next_state_tuple] = new_g
                h = calculate_manhattan(next_state_tuple, target_pos, n)
                # Nhân thêm trọng số weight để định hướng tìm kiếm mạnh mẽ hơn cho ma trận lớn
                child = Node(current, next_state_tuple, new_blank_idx, new_g, int(h * weight))
                heappush(pq, child)
                
    print("Không tìm thấy đường đi giải bài toán.")

# --- KHỞI CHẠY THỬ NGHIỆM VỚI N = 6 (Ma trận 6x6) ---
if __name__ == "__main__":
    n = 6  # Thử nghiệm kích thước n > 5 theo yêu cầu của bạn
    print(f"Đang khởi tạo ma trận ngẫu nhiên kích thước {n}x{n}...")
    
    initial_matrix = generate_solvable_state(n)
    
    # Định nghĩa trạng thái đích mong muốn (Thứ tự tăng dần, ô trống 0 ở cuối)
    final_list = list(range(1, n*n)) + [0]
    final_matrix = [final_list[i*n:(i+1)*n] for i in range(n)]
    
    print("\nMa trận khởi đầu (Random):")
    for r in initial_matrix:
        print("\t".join(map(str, r)))
        
    print("\nMa trận đích (Target Ascending):")
    for r in final_matrix:
        print("\t".join(map(str, r)))
    
    print("\nĐang tiến hành giải bằng Weighted A*...")
    # Khuyến nghị: n=6 chọn weight từ 3.5 -> 5.0 để đạt tốc độ xử lý dưới 5 giây.
    solve_n_puzzle(initial_matrix, final_matrix, n, weight=4.0)