import heapq
import random

# ============================================================
# 1. TRẠNG THÁI BAN ĐẦU (INITIAL STATE)
#    Đồ thị có N đỉnh (thành phố), đỉnh bắt đầu, đỉnh đích.
#    Trạng thái = đỉnh hiện tại đang xét. Không có khái niệm
#    "lượt" vì đây là bài toán tìm đường 1 tác nhân.
# ============================================================
def initial_state(graph_dict, start_label):
    """
    Trả về (start_label, 0):
      - start_label : nhãn đỉnh bắt đầu.
      - g = 0       : chi phí tích lũy ban đầu = 0.
    Người/tác nhân đầu tiên: thuật toán A*/Dijkstra.
    """
    return start_label, 0


# ============================================================
# 2. TRẠNG THÁI KẾT THÚC (TERMINAL STATE)
#    Kiểm tra đã đến đích chưa.
# ============================================================
def terminal(current_node, target_label):
    """
    Trả về True nếu đỉnh hiện tại là đỉnh đích.
    """
    return current_node == target_label


# ============================================================
# 3. HÀM CHUYỂN TRẠNG THÁI (SUCCESSORS)
#    Trả về iterator của (nước_đi, trạng_thái_mới, chi_phí).
#    Nước đi = cạnh (u → v) với trọng số.
# ============================================================
def successors(graph_dict, current_node, explored):
    """
    Sinh tất cả đỉnh kề của current_node chưa được chốt.
    Mỗi phần tử yield: (edge_cost, neighbor_label)
      - edge_cost     : chi phí cạnh đến đỉnh kề (nước đi).
      - neighbor_label: đỉnh kề (trạng thái mới).
    """
    for neighbor_label, edge_cost in graph_dict[current_node].items():
        if neighbor_label not in explored:
            yield edge_cost, neighbor_label


# ============================================================
# 4. HÀM LỢI ÍCH / HEURISTIC (UTILITY)
#    h = 0 vì đồ thị ngẫu nhiên không có tọa độ không gian.
#    Khi h = 0 → A* hoạt động như Dijkstra (admissible).
# ============================================================
def utility(current_node, target_label):
    """
    Heuristic h(n): ước lượng chi phí từ current_node đến target.
    Do đồ thị ngẫu nhiên không có tọa độ Euclid nên h = 0.
    → Đảm bảo tính admissible (không overestimate).
    → A* degenerates thành Dijkstra – luôn tìm đường ngắn nhất.
    """
    return 0


# ============================================================
# CÁC HÀM HỖ TRỢ
# ============================================================
def get_city_label(index):
    """Chuyển đổi số nguyên thành chuỗi A-Z, AA-ZZ."""
    label = ""
    while index >= 0:
        label = chr(index % 26 + 65) + label
        index = index // 26 - 1
    return label

def generate_random_graph(n, edge_probability=0.6, min_cost=10, max_cost=99):
    """
    Sinh đồ thị vô hướng ngẫu nhiên N đỉnh.
    edge_probability: xác suất có cạnh nối giữa 2 đỉnh.
    """
    labels = [get_city_label(i) for i in range(n)]
    graph = {label: {} for label in labels}
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() <= edge_probability:
                cost = random.randint(min_cost, max_cost)
                graph[labels[i]][labels[j]] = cost
                graph[labels[j]][labels[i]] = cost
    return graph


# ============================================================
# THUẬT TOÁN A*/DIJKSTRA SỬ DỤNG 4 THÀNH PHẦN
# ============================================================
class PathNode:
    __slots__ = ['parent', 'node_id', 'g', 'h', 'f']
    def __init__(self, parent, node_id, g, h):
        self.parent = parent
        self.node_id = node_id
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f


def solve_shortest_path(graph_dict, start_label, target_label):
    if start_label not in graph_dict or target_label not in graph_dict:
        print("Lỗi: Đỉnh bắt đầu hoặc đỉnh đích không tồn tại.")
        return

    # --- 1. INITIAL STATE ---
    start_node, g0 = initial_state(graph_dict, start_label)
    h0 = utility(start_node, target_label)   # 4. UTILITY
    root = PathNode(None, start_node, g0, h0)

    open_set = [root]
    best_g = {start_label: 0}
    explored = set()

    while open_set:
        current = heapq.heappop(open_set)

        if current.node_id in explored:
            continue
        explored.add(current.node_id)

        # --- 2. TERMINAL STATE ---
        if terminal(current.node_id, target_label):
            path_nodes = []
            curr_trace = current
            while curr_trace:
                path_nodes.append(curr_trace)
                curr_trace = curr_trace.parent
            path_nodes.reverse()

            print(f"\n--- ĐƯỜNG ĐI TỐI ƯU TỪ {start_label} ĐẾN {target_label} ---")
            for i, node in enumerate(path_nodes):
                if i == 0:
                    print(f"Bắt đầu: {node.node_id:2} | g:{node.g:4}, h:{node.h:4}, f:{node.f:4}")
                else:
                    prev = path_nodes[i-1].node_id
                    print(f"Bước {i:2}: {prev:2} -> {node.node_id:2} | g:{node.g:4}, h:{node.h:4}, f:{node.f:4}")
            print("-" * 50)
            print(f"Tổng chi phí: {current.g}")
            return

        # --- 3. SUCCESSORS (hàm chuyển trạng thái) ---
        for edge_cost, neighbor in successors(graph_dict, current.node_id, explored):
            new_g = current.g + edge_cost
            if neighbor not in best_g or new_g < best_g[neighbor]:
                best_g[neighbor] = new_g
                # --- 4. UTILITY (heuristic) ---
                new_h = utility(neighbor, target_label)
                child = PathNode(current, neighbor, new_g, new_h)
                heapq.heappush(open_set, child)

    print(f"\n[!] KHÔNG TÌM THẤY đường đi từ {start_label} đến {target_label}.")
    print("Nguyên nhân: các đỉnh bị cô lập hoặc đường đi bị đứt đoạn.")


# ============================================================
# CHẠY CHƯƠNG TRÌNH CHÍNH
# ============================================================
if __name__ == "__main__":
    while True:
        try:
            n = int(input("Nhập số lượng đỉnh n (khuyến nghị 5-20): "))
            if n >= 2:
                break
            print("Lỗi: Số đỉnh phải >= 2.")
        except ValueError:
            print("Lỗi: Vui lòng nhập số nguyên hợp lệ.")

    print(f"\n[!] Đang khởi tạo đồ thị ngẫu nhiên {n} đỉnh...")
    my_graph = generate_random_graph(n, edge_probability=0.4)

    labels = list(my_graph.keys())
    print("\n--- MA TRẬN TRỌNG SỐ (INF = Không có cạnh) ---")
    print("     " + " ".join(f"{lbl:>4}" for lbl in labels))
    for u in labels:
        row = []
        for v in labels:
            if u == v:
                row.append("   0")
            elif v in my_graph[u]:
                row.append(f"{my_graph[u][v]:4}")
            else:
                row.append(" INF")
        print(f"{u:>2} | " + " ".join(row))

    print("\nDanh sách các đỉnh:", ", ".join(labels))
    start_node = input("Nhập đỉnh BẮT ĐẦU (vd: A): ").strip().upper()
    end_node   = input(f"Nhập đỉnh ĐÍCH (vd: {labels[-1]}): ").strip().upper()

    print("\n[!] Đang tìm đường đi ngắn nhất...")
    solve_shortest_path(my_graph, start_node, end_node)
