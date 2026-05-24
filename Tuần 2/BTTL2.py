import heapq
import random

# ==========================================
# CÁC HÀM HỖ TRỢ SINH ĐỒ THỊ NGẪU NHIÊN
# ==========================================
def get_city_label(index):
    """Chuyển đổi số nguyên thành chuỗi ký tự A-Z, AA-ZZ."""
    label = ""
    while index >= 0:
        label = chr(index % 26 + 65) + label
        index = index // 26 - 1
    return label

def generate_random_graph(n, edge_probability=0.6, min_cost=10, max_cost=99):
    """
    Sinh đồ thị ngẫu nhiên.
    edge_probability: Xác suất có đường nối giữa 2 đỉnh (0.0 đến 1.0).
    Nếu không có đường nối, chi phí coi như vô cực (không tồn tại cạnh).
    """
    labels = [get_city_label(i) for i in range(n)]
    graph = {label: {} for label in labels}
    
    for i in range(n):
        for j in range(i + 1, n):
            # random.random() sinh số từ 0.0 đến 1.0
            if random.random() <= edge_probability:
                cost = random.randint(min_cost, max_cost)
                # Đồ thị vô hướng
                graph[labels[i]][labels[j]] = cost
                graph[labels[j]][labels[i]] = cost
            # Nếu lớn hơn xác suất, cạnh không được thêm vào (vô cực)
            
    return graph

# ==========================================
# LÕI THUẬT TOÁN A* / DIJKSTRA TÌM ĐƯỜNG NGẮN NHẤT
# ==========================================
class PathNode:
    __slots__ = ['parent', 'node_id', 'g', 'h', 'f']
    def __init__(self, parent, node_id, g, h):
        self.parent = parent
        self.node_id = node_id
        self.g = g  # Chi phí thực tế từ điểm bắt đầu
        self.h = h  # Chi phí ước lượng đến đích (Heuristic)
        self.f = g + h # Tổng chi phí

    def __lt__(self, other):
        # Ưu tiên f nhỏ hơn, nếu f bằng nhau thì ưu tiên g lớn hơn (đã đi được xa hơn)
        if self.f == other.f:
            return self.g > other.g
        return self.f < other.f

def heuristic(current_id, target_id):
    """
    Vì đồ thị ngẫu nhiên không có tọa độ không gian (x, y), chúng ta không thể 
    tính khoảng cách đường chim bay (Euclide). Do đó, h = 0 là an toàn nhất.
    Khi h = 0 cho mọi đỉnh, thuật toán A* sẽ hoạt động như thuật toán Dijkstra.
    """
    return 0 

def solve_shortest_path(graph_dict, start_label, target_label):
    if start_label not in graph_dict or target_label not in graph_dict:
        print("Lỗi: Đỉnh bắt đầu hoặc đỉnh đích không tồn tại trong đồ thị.")
        return

    # Khởi tạo Node gốc
    initial_h = heuristic(start_label, target_label)
    root = PathNode(None, start_label, 0, initial_h)
    
    open_set = [root]
    
    # Dùng dictionary để lưu chi phí g tốt nhất đến từng đỉnh 
    # (giúp tránh việc thăm lại một đỉnh nếu chi phí g cao hơn)
    best_g = {start_label: 0}
    
    explored = set()
    
    while open_set:
        current = heapq.heappop(open_set)
        
        # Nếu đỉnh này đã được chốt với đường đi ngắn nhất
        if current.node_id in explored:
            continue
        explored.add(current.node_id)
        
        # KIỂM TRA ĐIỀU KIỆN DỪNG: Đã đến đích
        if current.node_id == target_label:
            path_nodes = []
            curr_trace = current
            while curr_trace:
                path_nodes.append(curr_trace)
                curr_trace = curr_trace.parent
            path_nodes.reverse()
            
            print(f"\n--- ĐƯỜNG ĐI TỐI ƯU TỪ {start_label} ĐẾN {target_label} ---")
            for i, node in enumerate(path_nodes):
                if i == 0:
                    print(f"Bắt đầu: {node.node_id:2} | g: {node.g:3}, h: {node.h:3}, f: {node.f:3}")
                else:
                    prev_lbl = path_nodes[i-1].node_id
                    print(f"Bước {i:2}: {prev_lbl:2} -> {node.node_id:2} | g: {node.g:3}, h: {node.h:3}, f: {node.f:3}")
            
            print("-" * 48)
            print(f"Tổng chi phí đường đi (Total Cost): {current.g}")
            return
            
        # Duyệt các đỉnh kề (chỉ duyệt những đỉnh có đường nối hợp lệ)
        for neighbor_label, edge_cost in graph_dict[current.node_id].items():
            if neighbor_label in explored:
                continue
                
            new_g = current.g + edge_cost
            
            # Chỉ thêm vào hàng đợi nếu tìm thấy đường ngắn hơn đến đỉnh neighbor này
            if neighbor_label not in best_g or new_g < best_g[neighbor_label]:
                best_g[neighbor_label] = new_g
                new_h = heuristic(neighbor_label, target_label)
                child = PathNode(current, neighbor_label, new_g, new_h)
                heapq.heappush(open_set, child)
                
    print(f"\n[!] KHÔNG TÌM THẤY ĐƯỜNG ĐI từ {start_label} đến {target_label}.")
    print("Nguyên nhân: Các đỉnh bị cô lập, đường đi bị đứt đoạn (Vô cực).")

# ==========================================
# CHẠY CHƯƠNG TRÌNH CHÍNH
# ==========================================
if __name__ == "__main__":
    while True:
        try:
            n_str = input("Nhập số lượng đỉnh n (Khuyến nghị 5 - 20): ")
            n = int(n_str)
            if n >= 2:
                break
            else:
                print("Lỗi: Số lượng đỉnh phải lớn hơn hoặc bằng 2.")
        except ValueError:
            print("Lỗi: Vui lòng nhập một số nguyên hợp lệ.")
            
    print(f"\n[!] Đang khởi tạo đồ thị ngẫu nhiên cho {n} đỉnh...")
    # Tỷ lệ 0.4 nghĩa là có khoảng 40% khả năng có đường nối giữa 2 đỉnh bất kỳ
    my_graph = generate_random_graph(n, edge_probability=0.4)
    
    # In ma trận kề ra màn hình để đối chiếu chi phí
    labels = list(my_graph.keys())
    print("\n--- MA TRẬN TRỌNG SỐ (INF = Không có đường nối) ---")
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

    # Yêu cầu người dùng chọn điểm đầu và cuối
    print("\nDanh sách các đỉnh:", ", ".join(labels))
    start_node = input(f"Nhập đỉnh BẮT ĐẦU (ví dụ A): ").strip().upper()
    end_node = input(f"Nhập đỉnh ĐÍCH (ví dụ {labels[-1]}): ").strip().upper()

    print(f"\n[!] Đang tìm đường đi ngắn nhất...")
    solve_shortest_path(my_graph, start_node, end_node)
