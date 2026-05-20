import heapq

def a_star_graph_search(graph, heuristics, start, goal):
    """
    Thuật giải A* tìm đường đi ngắn nhất trong đồ thị.
    - graph: Từ điển chứa đồ thị {đỉnh: {đỉnh_kề: chi_phí}}
    - heuristics: Từ điển chứa giá trị h(n) {đỉnh: ước_lượng_đến_đích}
    """
    # Hàng đợi ưu tiên lưu trữ các node để xét duyệt (f_score, node)
    open_set = []
    heapq.heappush(open_set, (heuristics[start], start))
    
    # Lưu vết đường đi
    came_from = {}
    
    # Bản đồ chi phí thực tế g(n) từ điểm xuất phát đến node hiện tại
    g_score = {node: float('inf') for node in graph}
    g_score[start] = 0
    
    while open_set:
        # Lấy node có f(n) nhỏ nhất
        current_f, current = heapq.heappop(open_set)
        
        # Nếu đã đến đích, truy vết lại đường đi
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1], g_score[goal]
            
        # Duyệt qua các đỉnh kề
        for neighbor, cost in graph[current].items():
            # Chi phí g(n) tạm tính để đến neighbor
            tentative_g = g_score[current] + cost
            
            # Nếu tìm được đường đi tốt hơn
            if tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                
                # f(n) = g(n) + h(n)
                f_score = tentative_g + heuristics[neighbor]
                heapq.heappush(open_set, (f_score, neighbor))
                
    return None, float('inf') # Không tìm thấy đường đi

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    # Đồ thị mẫu: A, B, C, D, E, F
    graph = {
        'A': {'B': 2, 'C': 4},
        'B': {'A': 2, 'C': 1, 'D': 7},
        'C': {'A': 4, 'B': 1, 'E': 3},
        'D': {'B': 7, 'F': 1},
        'E': {'C': 3, 'D': 2, 'F': 5},
        'F': {'D': 1, 'E': 5}
    }
    
    # Heuristic giả định (ước lượng khoảng cách đến F)
    heuristics_to_F = {
        'A': 6, 'B': 5, 'C': 4, 'D': 1, 'E': 3, 'F': 0
    }
    
    start_node = 'A'
    goal_node = 'F'
    
    print("--- TÌM ĐƯỜNG ĐI TRÊN ĐỒ THỊ BẰNG A* ---")
    path, total_cost = a_star_graph_search(graph, heuristics_to_F, start_node, goal_node)
    
    if path:
        print(f"Đường đi tối ưu từ {start_node} đến {goal_node}: {' -> '.join(path)}")
        print(f"Tổng chi phí (Cost): {total_cost}")
    else:
        print("Không tìm thấy đường đi.")