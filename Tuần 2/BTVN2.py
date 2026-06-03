import heapq
import random

# ============================================================
# 1. TRẠNG THÁI BAN ĐẦU (INITIAL STATE)
#    Bài toán Người Giao Hàng (TSP): xuất phát từ 1 thành phố,
#    thăm tất cả và quay về. Trạng thái = (thành phố hiện tại,
#    bitmask các thành phố đã thăm). Người/tác nhân đầu tiên:
#    thuật toán A* với heuristic MST.
# ============================================================
def initial_state(n, start_id):
    """
    Trả về (start_id, initial_mask):
      - start_id    : ID thành phố xuất phát (thường = 0).
      - initial_mask: bitmask chỉ thành phố xuất phát đã thăm.
    Người/tác nhân đầu tiên: thuật toán A* TSP.
    """
    initial_mask = 1 << start_id
    return start_id, initial_mask


# ============================================================
# 2. TRẠNG THÁI KẾT THÚC (TERMINAL STATE)
#    Đã thăm tất cả N thành phố (bitmask = 2^N - 1).
# ============================================================
def terminal(mask, n):
    """
    Trả về True nếu tất cả N thành phố đã được thăm.
    target_mask = (1 << n) - 1 nghĩa là tất cả bit = 1.
    """
    return mask == (1 << n) - 1


# ============================================================
# 3. HÀM CHUYỂN TRẠNG THÁI (SUCCESSORS)
#    Trả về iterator (nước_đi, trạng_thái_mới, chi_phí).
#    Nước đi = đi đến thành phố kế tiếp chưa thăm.
# ============================================================
def successors(matrix, current_id, mask, n):
    """
    Sinh tất cả thành phố chưa thăm còn có thể đi tới.
    Mỗi phần tử yield: (next_id, new_mask, edge_cost)
      - next_id  : thành phố tiếp theo (nước đi).
      - new_mask : bitmask sau khi thêm next_id vào đã thăm.
      - edge_cost: chi phí cạnh (current_id → next_id).
    Bỏ qua nếu không có cạnh nối (cost = inf).
    """
    for next_id in range(n):
        if not (mask & (1 << next_id)):
            cost = matrix[current_id][next_id]
            if cost != float('inf'):
                new_mask = mask | (1 << next_id)
                yield next_id, new_mask, cost


# ============================================================
# 4. HÀM LỢI ÍCH / HEURISTIC (UTILITY)
#    Ước lượng chi phí tối thiểu để hoàn thành hành trình.
#    Dùng MST (Minimum Spanning Tree) trên các thành phố chưa thăm.
#    Đây là heuristic admissible: không overestimate.
# ============================================================
def utility(matrix, mask, n, current_id, start_id):
    """
    Heuristic MST cho TSP (Admissible):
      h = MST(unvisited ∪ {current}) + min_edge_to_unvisited
                                      + min_edge_from_unvisited_to_start
    
    Thuật toán Prim với **min-heap** → O(k log k) thay vì O(k²) naive.
    k = số thành phố chưa thăm.

    Trả về: ước lượng chi phí tối thiểu để hoàn thành hành trình.
    """
    unvisited = [i for i in range(n) if not (mask & (1 << i))]
    if not unvisited:
        # Tất cả đã thăm → chỉ cần về điểm xuất phát
        return matrix[current_id][start_id]

    # --- Prim với min-heap O(k log k) ---
    # Tập nút cần đưa vào MST: unvisited
    in_mst = [False] * n
    # Khởi tạo: bắt đầu từ unvisited[0]
    s = unvisited[0]
    min_edge = [float('inf')] * n
    min_edge[s] = 0
    pq = [(0, s)]    # (trọng số, nút)
    mst_cost = 0

    while pq:
        w, u = heapq.heappop(pq)
        if in_mst[u]:
            continue
        if u not in (set(unvisited)):
            continue
        in_mst[u] = True
        mst_cost += w
        for v in unvisited:
            if not in_mst[v] and matrix[u][v] < min_edge[v]:
                min_edge[v] = matrix[u][v]
                heapq.heappush(pq, (matrix[u][v], v))

    # Chi phí tối thiểu từ current đến 1 thành phố chưa thăm
    min_to_unvisited = min(matrix[current_id][v] for v in unvisited)
    # Chi phí tối thiểu từ 1 thành phố chưa thăm về start
    min_to_start = min(matrix[v][start_id] for v in unvisited)

    return min_to_unvisited + mst_cost + min_to_start


# ============================================================
# CÁC HÀM HỖ TRỢ
# ============================================================
def get_city_label(index):
    label = ""
    while index >= 0:
        label = chr(index % 26 + 65) + label
        index = index // 26 - 1
    return label

def generate_random_tsp_graph(n, min_cost=10, max_cost=99):
    """Sinh đồ thị TSP đầy đủ, đối xứng."""
    labels = [get_city_label(i) for i in range(n)]
    graph = {label: {} for label in labels}
    for i in range(n):
        for j in range(i + 1, n):
            cost = random.randint(min_cost, max_cost)
            graph[labels[i]][labels[j]] = cost
            graph[labels[j]][labels[i]] = cost
    return graph

class GraphNode:
    __slots__ = ['parent', 'node_id', 'mask', 'g', 'h', 'f']
    def __init__(self, parent, node_id, mask, g, h):
        self.parent  = parent
        self.node_id = node_id
        self.mask    = mask
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f


# ============================================================
# THUẬT TOÁN A* TSP SỬ DỤNG 4 THÀNH PHẦN
# ============================================================
def solve_tsp_astar(graph_dict, start_label):
    labels = list(graph_dict.keys())
    n = len(labels)
    label_to_id = {label: i for i, label in enumerate(labels)}
    id_to_label = {i: label for i, label in enumerate(labels)}

    matrix = [[float('inf')] * n for _ in range(n)]
    for u_label, neighbors in graph_dict.items():
        u = label_to_id[u_label]
        matrix[u][u] = 0
        for v_label, cost in neighbors.items():
            matrix[u][label_to_id[v_label]] = cost

    start_id = label_to_id[start_label]

    # --- 1. INITIAL STATE ---
    cur_id, init_mask = initial_state(n, start_id)
    target_mask = (1 << n) - 1

    # --- 4. UTILITY (heuristic ban đầu) ---
    h0 = utility(matrix, init_mask, n, cur_id, start_id)
    root = GraphNode(None, cur_id, init_mask, 0, h0)

    open_set = [root]
    explored = set()

    while open_set:
        current = heapq.heappop(open_set)
        state_key = (current.node_id, current.mask)
        if state_key in explored:
            continue
        explored.add(state_key)

        # --- 2. TERMINAL STATE ---
        if terminal(current.mask, n):
            total_cost = current.g + matrix[current.node_id][start_id]

            path_nodes = []
            curr_trace = current
            while curr_trace:
                path_nodes.append(curr_trace)
                curr_trace = curr_trace.parent
            path_nodes.reverse()

            print("\n--- ĐƯỜNG ĐI TỐI ƯU TSP (G, H, F) ---")
            for i, node in enumerate(path_nodes):
                lbl = id_to_label[node.node_id]
                if i == 0:
                    print(f"Bắt đầu: {lbl:2} | g:{node.g:4}, h:{node.h:4}, f:{node.f:4}")
                else:
                    prev_lbl = id_to_label[path_nodes[i-1].node_id]
                    print(f"Bước {i:2}: {prev_lbl:2} -> {lbl:2} | g:{node.g:4}, h:{node.h:4}, f:{node.f:4}")
            print(f"Về đích: {id_to_label[current.node_id]:2} -> {start_label:2} | g:{total_cost:4}")
            print("-" * 50)
            print(f"Tổng chi phí: {total_cost}")
            return

        # --- 3. SUCCESSORS (hàm chuyển trạng thái) ---
        for next_id, new_mask, edge_cost in successors(matrix, current.node_id, current.mask, n):
            new_g = current.g + edge_cost

            # --- 4. UTILITY (heuristic MST O(k log k)) ---
            new_h = utility(matrix, new_mask, n, next_id, start_id)
            child = GraphNode(current, next_id, new_mask, new_g, new_h)
            heapq.heappush(open_set, child)

    print("Không tìm thấy chu trình TSP hợp lệ.")


# ============================================================
# CHẠY CHƯƠNG TRÌNH CHÍNH
# ============================================================
if __name__ == "__main__":
    while True:
        try:
            n = int(input("Nhập số lượng thành phố n (khuyến nghị 4-15): "))
            if n >= 2:
                break
            print("Lỗi: Số thành phố phải >= 2.")
        except ValueError:
            print("Lỗi: Vui lòng nhập số nguyên hợp lệ.")

    print(f"\n[!] Đang khởi tạo đồ thị TSP ngẫu nhiên {n} thành phố...")
    tsp_graph = generate_random_tsp_graph(n)

    labels = list(tsp_graph.keys())
    print("\n--- MA TRẬN CHI PHÍ ---")
    print("     " + " ".join(f"{lbl:>3}" for lbl in labels))
    for u in labels:
        row = []
        for v in labels:
            if u == v:
                row.append("  0")
            else:
                row.append(f"{tsp_graph[u][v]:3}")
        print(f"{u:>2} | " + " ".join(row))

    print("\n[!] Đang giải bài toán Người Giao Hàng (TSP) bằng A*...")
    solve_tsp_astar(tsp_graph, 'A')
