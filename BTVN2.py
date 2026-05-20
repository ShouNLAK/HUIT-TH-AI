import heapq

def mst_cost(graph, unvisited):
    """Tính chi phí Cây Khung Nhỏ Nhất (MST) bằng thuật giải Prim cho các đỉnh chưa thăm."""
    if not unvisited or len(unvisited) == 1:
        return 0
    
    unvisited_list = list(unvisited)
    start_node = unvisited_list[0]
    visited_mst = {start_node}
    edges = []
    
    for v in unvisited:
        if v != start_node:
            heapq.heappush(edges, (graph[start_node][v], start_node, v))
            
    total_mst_cost = 0
    while len(visited_mst) < len(unvisited):
        if not edges: break
        cost, u, v = heapq.heappop(edges)
        if v not in visited_mst:
            visited_mst.add(v)
            total_mst_cost += cost
            for next_v in unvisited:
                if next_v not in visited_mst:
                    heapq.heappush(edges, (graph[v][next_v], v, next_v))
                    
    return total_mst_cost

def tsp_a_star(graph, start):
    """Thuật giải A* cho bài toán Người giao hàng (TSP)."""
    nodes = set(graph.keys())
    
    # State: (current_node, visited_nodes)
    # Dùng frozenset cho tập visited để có thể băm (hash) và lưu vào cấu trúc set()
    initial_state = (start, frozenset([start]))
    
    # Hàng đợi: (f_score, g_score, state, path_history)
    open_set = []
    heapq.heappush(open_set, (0, 0, initial_state, [start]))
    
    # Lưu các trạng thái đã xét để tránh vòng lặp dư thừa
    explored = set()
    
    while open_set:
        f, g, (current, visited), path = heapq.heappop(open_set)
        
        if (current, visited) in explored:
            continue
        explored.add((current, visited))
        
        # Nếu đã thăm đủ tất cả các đỉnh
        if len(visited) == len(nodes):
            # Cần cộng thêm chi phí quay về đỉnh xuất phát
            return path + [start], g + graph[current][start]
            
        unvisited = nodes - visited
        for neighbor in unvisited:
            new_visited = frozenset(visited | {neighbor})
            new_g = g + graph[current][neighbor]
            
            # Tính Heuristic h(n)
            h_mst = mst_cost(graph, unvisited)
            # Khoảng cách từ đỉnh hiện tại đến tập chưa thăm (min)
            min_to_unvisited = min(graph[current][v] for v in unvisited)
            # Khoảng cách từ tập chưa thăm về điểm xuất phát (min)
            min_to_start = min(graph[v][start] for v in unvisited)
            
            h = min_to_unvisited + h_mst + min_to_start
            if len(unvisited) == 1:
                # Nếu chỉ còn 1 đỉnh, chi phí chính xác có thể tính ngay
                h = graph[current][neighbor] + graph[neighbor][start]
                
            new_f = new_g + h
            heapq.heappush(open_set, (new_f, new_g, (neighbor, new_visited), path + [neighbor]))
            
    return None, float('inf')

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    # Đồ thị đầy đủ cho TSP
    tsp_graph = {
        'A': {'A': 0, 'B': 10, 'C': 15, 'D': 20},
        'B': {'A': 10, 'B': 0, 'C': 35, 'D': 25},
        'C': {'A': 15, 'B': 35, 'C': 0, 'D': 30},
        'D': {'A': 20, 'B': 25, 'C': 30, 'D': 0}
    }
    
    start_city = 'A'
    
    print("--- BÀI TOÁN NGƯỜI GIAO HÀNG (TSP) BẰNG A* ---")
    path, total_cost = tsp_a_star(tsp_graph, start_city)
    
    if path:
        print(f"Hành trình tối ưu: {' -> '.join(path)}")
        print(f"Tổng chi phí (Cost): {total_cost}")
    else:
        print("Không tìm thấy chu trình hợp lệ.")