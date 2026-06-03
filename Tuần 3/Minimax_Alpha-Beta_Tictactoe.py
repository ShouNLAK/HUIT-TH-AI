import networkx as nx
import matplotlib.pyplot as plt
import time

# =============================================================================
# 1. KHỞI TẠO DỮ LIỆU & HÀM HỖ TRỢ
# =============================================================================

# Dữ liệu đầu vào
classes_data = [
    {"id": "Toan_10A", "teacher": "Thầy A", "group": "10A"},
    {"id": "Tin_10A",  "teacher": "Cô B",   "group": "10A"},
    {"id": "Toan_10B", "teacher": "Thầy A", "group": "10B"},
    {"id": "Tin_10B",  "teacher": "Thầy C", "group": "10B"},
    {"id": "Ly_10A",   "teacher": "Cô D",   "group": "10A"},
    {"id": "Ly_10B",   "teacher": "Cô D",   "group": "10B"},
    {"id": "Hoa_10A",  "teacher": "Thầy E", "group": "10A"},
    {"id": "Hoa_10B",  "teacher": "Thầy E", "group": "10B"},

]
node_names = [item["id"] for item in classes_data]

# Bảng màu hiển thị (Hex codes) tương ứng với các Ca học (Slot)
# Màu xám: Chưa tô
UNCOLORED = '#d9d9d9'
# Các màu: Đỏ, Xanh dương, Xanh lá, Cam, Tím, Vàng...
PALETTE = ['#ff6666', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffff99']

# =============================================================================
# 2. XÂY DỰNG ĐỒ THỊ XUNG ĐỘT
# =============================================================================
G = nx.Graph()
G.add_nodes_from(node_names)

print("--- ĐANG XÂY DỰNG ĐỒ THỊ ---")
n = len(classes_data)
for i in range(n):
    for j in range(i + 1, n):
        c1, c2 = classes_data[i], classes_data[j]
        # Ràng buộc: Cùng Giáo viên HOẶC Cùng Lớp SV -> Xung đột
        if c1["teacher"] == c2["teacher"] or c1["group"] == c2["group"]:
            G.add_edge(node_names[i], node_names[j])
            # In ra console để sinh viên thấy logic
            # print(f"Nối cạnh {node_names[i]} - {node_names[j]}")

# =============================================================================
# 3. CHUẨN BỊ MÔ PHỎNG (VISUALIZATION SETUP)
# =============================================================================
# Tính toán vị trí các đỉnh cố định (để khi tô màu đỉnh không bị chạy lung tung)
pos = nx.spring_layout(G, seed=100)

# Hàm vẽ đồ thị cập nhật theo trạng thái màu
def draw_step(current_colors, title_text):
    plt.clf() # Xóa hình cũ

    # Vẽ các cạnh (mờ)
    nx.draw_networkx_edges(G, pos, alpha=0.3, width=1.5)

    # Vẽ các đỉnh với màu hiện tại
    colors_to_draw = [current_colors.get(node, UNCOLORED) for node in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=colors_to_draw, node_size=1800, edgecolors='k')

    # Vẽ tên đỉnh
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight='bold')

    plt.title(title_text, fontsize=14)
    plt.axis('off')
    plt.draw()
    plt.pause(1.5) # Dừng 1.5 giây để sinh viên kịp nhìn

# =============================================================================
# 4. THỰC THI THUẬT TOÁN & MÔ PHỎNG TỪNG BƯỚC
# =============================================================================
plt.figure(figsize=(10, 7))

# --- BƯỚC 0: HIỂN THỊ ĐỒ THỊ GỐC ---
current_node_colors = {node: UNCOLORED for node in G.nodes()}
print("Hiển thị đồ thị gốc...")
draw_step(current_node_colors, "BƯỚC 0: Đồ thị xung đột ban đầu (Chưa tô màu)")

# --- BƯỚC 1: TÍNH BẬC & SẮP XẾP (CHIẾN LƯỢC THAM LAM) ---
# Sắp xếp đỉnh theo bậc giảm dần (Node nào nhiều xung đột nhất xử lý trước)
sorted_nodes = sorted(G.nodes(), key=lambda x: G.degree[x], reverse=True)

print("\nThứ tự ưu tiên tô màu (Dựa trên bậc):")
print(" -> ".join(sorted_nodes))

# --- BƯỚC 2: VÒNG LẶP TÔ MÀU ---
solution = {} # Lưu kết quả dạng {Node: Color_Index}

for i, node in enumerate(sorted_nodes):
    # Tìm màu phù hợp đầu tiên
    # Lấy danh sách màu của các hàng xóm đã được tô
    neighbor_colors = {solution[n] for n in G.neighbors(node) if n in solution}

    # Chọn màu nhỏ nhất (0, 1, 2...) không trùng với hàng xóm
    color_index = 0
    while color_index in neighbor_colors:
        color_index += 1

    # Gán màu
    solution[node] = color_index

    # Cập nhật màu hiển thị (Hex code)
    hex_color = PALETTE[color_index % len(PALETTE)]
    current_node_colors[node] = hex_color

    # --- CẬP NHẬT HÌNH ẢNH ---
    step_title = f"BƯỚC {i+1}: Tô đỉnh {node} (Bậc {G.degree[node]})\n-> Chọn màu: Ca {color_index + 1}"
    draw_step(current_node_colors, step_title)

# --- BƯỚC CUỐI: HOÀN THÀNH ---
draw_step(current_node_colors, "HOÀN THÀNH: Thời khóa biểu tối ưu")
print("\nĐã hoàn thành mô phỏng! Đóng cửa sổ đồ thị để xem kết quả text.")
plt.show()

# =============================================================================
# 5. IN KẾT QUẢ DẠNG BẢNG TEXT
# =============================================================================
print("\n" + "="*40)
print(f"{'MÔN HỌC':<12} | {'GIÁO VIÊN':<10} | {'THỜI GIAN'}")
print("="*40)

# Sắp xếp kết quả theo Ca học
sorted_schedule = sorted(solution.items(), key=lambda x: x[1])

for node, color_idx in sorted_schedule:
    details = next(d for d in classes_data if d["id"] == node)
    time_slot = f"Ca {color_idx + 1}"
    print(f"{node:<12} | {details['teacher']:<10} | {time_slot}")
print("="*40)