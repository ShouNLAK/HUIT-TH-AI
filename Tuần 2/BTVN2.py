import heapq
import random

# ==========================================
# CÁC HÀM HỖ TRỢ SINH ĐỒ THỊ NGẪU NHIÊN
# ==========================================
def get_city_label(index):
    """Chuyển đổi số nguyên thành chuỗi ký tự A-Z, AA-ZZ (Giống cột Excel)."""
    label = ""
    while index >= 0:
        label = chr(index % 26 + 65) + label
        index = index // 26 - 1
    return label

def generate_random_tsp_graph(n, min_cost=10, max_cost=99):
    """Sinh đồ thị TSP đầy đủ, đối xứng với chi phí ngẫu nhiên."""
    labels = [get_city_label(i) for i in range(n)]
    graph = {label: {} for label in labels}
    
    for i in range(n):
        for j in range(i + 1, n):
            cost = random.randint(min_cost, max_cost)
            # Đồ thị đối xứng (Khoảng cách A->B bằng B->A)
            graph[labels[i]][labels[j]] = cost
            graph[labels[j]][labels[i]] = cost
            
    return graph

# ==========================================
# LÕI THUẬT TOÁN A* CHO TSP (GIỮ NGUYÊN)
# ==========================================
class GraphNode:
    __slots__ = ['parent', 'node_id', 'mask', 'g', 'h', 'f']
    def __init__(self, parent, node_id, mask, g, h):
        self.parent = parent
        self.node_id = node_id
        self.mask = mask
        self.g = g
        self.h = h
        self.f = g + h

    def __lt__(self, other):
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f

def mst_heuristic_mask(matrix, mask, n, current_node, start_node):
    unvisited = [i for i in range(n) if not (mask & (1 << i))]
    if not unvisited:
        return matrix[current_node][start_node]

    in_mst = [False] * n
    min_edge = [float('inf')] * n
    
    start_mst = unvisited[0]
    min_edge[start_mst] = 0
    mst_cost = 0
    
    for _ in range(len(unvisited)):
        u = -1
        for v in unvisited:
            if not in_mst[v] and (u == -1 or min_edge[v] < min_edge[u]):
                u = v
                
        if min_edge[u] == float('inf'): 
            break
            
        in_mst[u] = True
        mst_cost += min_edge[u]
        
        for v in unvisited:
            if not in_mst[v] and matrix[u][v] < min_edge[v]:
                min_edge[v] = matrix[u][v]

    min_to_unvisited = min(matrix[current_node][v] for v in unvisited)
    min_to_start = min(matrix[v][start_node] for v in unvisited)
    
    return min_to_unvisited + mst_cost + min_to_start

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
            v = label_to_id[v_label]
            matrix[u][v] = cost

    start_id = label_to_id[start_label]
    initial_mask = 1 << start_id
    target_mask = (1 << n) - 1
    
    initial_h = mst_heuristic_mask(matrix, initial_mask, n, start_id, start_id)
    root = GraphNode(None, start_id, initial_mask, 0, initial_h)
    
    open_set = [root]
    explored = set()
    
    while open_set:
        current = heapq.heappop(open_set)
        
        state_key = (current.node_id, current.mask)
        if state_key in explored:
            continue
        explored.add(state_key)
        
        if current.mask == target_mask:
            total_cost = current.g + matrix[current.node_id][start_id]
            
            path_nodes = []
            curr_trace = current
            while curr_trace:
                path_nodes.append(curr_trace)
                curr_trace = curr_trace.parent
            path_nodes.reverse()
            
            print("\n--- ĐƯỜNG ĐI TỐI ƯU VÀ THÔNG SỐ (G, H, F) ---")
            for i, node in enumerate(path_nodes):
                u_lbl = id_to_label[node.node_id]
                if i == 0:
                    print(f"Bắt đầu: {u_lbl:2} | g: {node.g:3}, h: {node.h:3}, f: {node.f:3}")
                else:
                    prev_lbl = id_to_label[path_nodes[i-1].node_id]
                    print(f"Bước {i:2}: {prev_lbl:2} -> {u_lbl:2} | g: {node.g:3}, h: {node.h:3}, f: {node.f:3}")
            
            print(f"Về đích: {id_to_label[current.node_id]:2} -> {start_label:2} | g: {total_cost:3}, h:   0, f: {total_cost:3}")
            print("-" * 48)
            print(f"Tổng chi phí (Total Cost): {total_cost}")
            return
            
        for neighbor in range(n):
            if not (current.mask & (1 << neighbor)) and matrix[current.node_id][neighbor] != float('inf'):
                new_mask = current.mask | (1 << neighbor)
                new_g = current.g + matrix[current.node_id][neighbor]
                new_h = mst_heuristic_mask(matrix, new_mask, n, neighbor, start_id)
                
                child = GraphNode(current, neighbor, new_mask, new_g, new_h)
                heapq.heappush(open_set, child)
                
    print("Không tìm thấy chu trình TSP hợp lệ.")

# ==========================================
# CHẠY CHƯƠNG TRÌNH CHÍNH
# ==========================================
if __name__ == "__main__":
    while True:
        try:
            n_str = input("Nhập số lượng thành phố n (Khuyến nghị 4 - 15): ")
            n = int(n_str)
            if n >= 2:
                break
            else:
                print("Lỗi: Số lượng thành phố phải lớn hơn hoặc bằng 2.")
        except ValueError:
            print("Lỗi: Vui lòng nhập một số nguyên hợp lệ.")
            
    print(f"\n[!] Đang khởi tạo đồ thị ngẫu nhiên cho {n} thành phố...")
    tsp_graph = generate_random_tsp_graph(n)
    
    # In ma trận kề ra màn hình để đối chiếu chi phí
    labels = list(tsp_graph.keys())
    print("\n--- MA TRẬN CHI PHÍ (GRAPH) ---")
    print("     " + " ".join(f"{lbl:>3}" for lbl in labels))
    for u in labels:
        row = []
        for v in labels:
            if u == v:
                row.append("  0")
            else:
                row.append(f"{tsp_graph[u][v]:3}")
        print(f"{u:>2} | " + " ".join(row))

    print("\n[!] Đang giải bài toán Người giao hàng bằng A*...")
    start_city = 'A'
    solve_tsp_astar(tsp_graph, start_city)
