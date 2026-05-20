import time
from heapq import heappush, heappop

# Kích thước khung 3x3
n = 10000000

# 4 hướng dịch chuyển: Xuống, Trái, Lên, Phải
rows = [ 1, 0, -1, 0 ]
cols = [ 0, -1, 0, 1 ]

class Node:
    def __init__(self, parent, mat, empty_tile_pos, g, h):
        self.parent = parent
        self.mat = mat
        self.empty_tile_pos = empty_tile_pos
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        # TỐI ƯU 1: Thêm Tie-breaker
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f

# TỐI ƯU 2: Tính sẵn từ điển đích (Target Dict) 1 lần duy nhất
def get_target_pos(final):
    target_pos = {}
    for i in range(n):
        for j in range(n):
            target_pos[final[i][j]] = (i, j)
    return target_pos

def calculateManhattan(mat, target_pos) -> int:
    dist = 0
    for i in range(n):
        for j in range(n):
            val = mat[i][j]
            if val != 0:
                target_x, target_y = target_pos[val]
                dist += abs(i - target_x) + abs(j - target_y)
    return dist

def newNode(mat, empty_tile_pos, new_empty_tile_pos, g, parent, target_pos) -> Node:
    # TỐI ƯU 3: Thay copy.deepcopy chậm chạp bằng List Comprehension siêu tốc
    new_mat = [list(row) for row in mat]
    x1, y1 = empty_tile_pos
    x2, y2 = new_empty_tile_pos

    new_mat[x1][y1], new_mat[x2][y2] = new_mat[x2][y2], new_mat[x1][y1]

    h = calculateManhattan(new_mat, target_pos)
    return Node(parent, new_mat, new_empty_tile_pos, g, h)

def printMatrix(mat):
    for i in range(n):
        for j in range(n):
            print("%d" % (mat[i][j]), end=" ")
        print()

def isSafe(x, y):
    return 0 <= x < n and 0 <= y < n

def printPath(root):
    if root is None:
        return
    printPath(root.parent)
    printMatrix(root.mat)
    print(f"Bước {root.g} | h = {root.h} | f = {root.f}\n")

def mat_to_tuple(mat):
    return tuple(tuple(row) for row in mat)

# BƯỚC BẢO VỆ: Kiểm tra tính giải được (Solvability)
def is_solvable(initial, final):
    def count_inversions(mat):
        arr = [val for row in mat for val in row if val != 0]
        inv = 0
        for i in range(len(arr)):
            for j in range(i + 1, len(arr)):
                if arr[i] > arr[j]:
                    inv += 1
        return inv
    return count_inversions(initial) % 2 == count_inversions(final) % 2

def solve(initial, empty_tile_pos, final):
    if not is_solvable(initial, final):
        print("Về mặt toán học, không thể biến đổi ma trận đầu thành ma trận đích!")
        return

    start_time = time.time()
    target_pos = get_target_pos(final)
    pq = []

    h_initial = calculateManhattan(initial, target_pos)
    root = Node(None, initial, empty_tile_pos, 0, h_initial)
    heappush(pq, root)

    visited = set()
    expanded_nodes = 0

    while pq:
        current = heappop(pq)
        state_tuple = mat_to_tuple(current.mat)

        if state_tuple in visited:
            continue

        visited.add(state_tuple)
        expanded_nodes += 1

        if current.h == 0:
            print("--- ĐÃ TÌM THẤY ĐƯỜNG ĐI ĐẾN ĐÍCH ---")
            printPath(current)
            print(f"Tổng số trạng thái đã xét: {expanded_nodes}")
            print(f"Thời gian giải: {time.time() - start_time:.4f} giây")
            return

        # SỬA LỖI TẠI ĐÂY: range(4) thay vì range(n) để duyệt đủ 4 hướng
        for i in range(4):
            new_x = current.empty_tile_pos[0] + rows[i]
            new_y = current.empty_tile_pos[1] + cols[i]

            if isSafe(new_x, new_y):
                child = newNode(current.mat, current.empty_tile_pos, [new_x, new_y],
                                current.g + 1, current, target_pos)

                if mat_to_tuple(child.mat) not in visited:
                    heappush(pq, child)

    print("Không tìm thấy đường đi giải puzzle này!")

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    initial = [ [ 0, 1, 3 ],
                [ 4, 2, 5 ],
                [ 7, 8, 6 ] ]

    final = [ [ 1, 2, 3 ],
              [ 4, 5, 6 ],
              [ 7, 8, 0 ] ]

    empty_tile_pos = [ 0, 0 ]

    print("Bắt đầu giải puzzle bằng A*...\n")
    solve(initial, empty_tile_pos, final)