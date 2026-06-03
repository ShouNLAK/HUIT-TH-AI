import numpy as np
import networkx as nx
from collections import defaultdict
import itertools
import warnings
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import silhouette_score, pairwise_distances
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.widgets import Button
from scipy.spatial.distance import cdist

warnings.filterwarnings("ignore")

# CẤU HÌNH THUẬT TOÁN
CONFIG = {
    "K_MEANS_CLUSTERS": 3,
    "GRID_SEARCH_MAX_K": 10,
    "KNN_NEIGHBORS": 3,
    "RANDOM_SEED": 42
}

# HÀM HỖ TRỢ HIỂN THỊ ĐỒ THỊ
def get_pos(G):
    if len(G.nodes) > 0 and 'coords' in G.nodes[list(G.nodes)[0]]:
        return {n: G.nodes[n]['coords'] for n in G.nodes}
    return nx.spring_layout(G, seed=CONFIG["RANDOM_SEED"])

def draw_graph(G, node_colors=None, title="Đồ thị"):
    plt.figure(figsize=(8, 6))
    plt.gcf().canvas.manager.set_window_title(title)
    pos = get_pos(G)
    if node_colors is None:
        node_colors = 'lightblue'
    nx.draw(G, pos, with_labels=True, node_color=node_colors, edge_color='gray', 
            node_size=700, font_size=9, font_weight='bold', cmap=plt.cm.tab20)
    plt.title(title, fontsize=14, color='darkred')
    plt.show(block=False)
    plt.pause(2)

def draw_tsp(G, path):
    plt.figure(figsize=(8, 6))
    plt.gcf().canvas.manager.set_window_title("Greedy TSP")
    pos = get_pos(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='#eeeeee', node_size=700)
    path_edges = list(zip(path, path[1:]))
    nx.draw_networkx_edges(G, pos, edgelist=path_edges, edge_color='red', width=2.5)
    plt.title("Lộ trình Greedy TSP", fontsize=14, color='darkred')
    plt.show(block=False)
    plt.pause(2)

def plot_gridsearch(X_features, k_list, scores, suggested_k=None):
    plt.figure(figsize=(12, 5))
    plt.gcf().canvas.manager.set_window_title("Grid Search Elbow Plot")
    
    plt.subplot(1, 2, 1)
    if X_features.shape[1] >= 2:
        plt.scatter(X_features[:, 0], X_features[:, 1], c='gray', marker='o', s=50, alpha=0.6)
    plt.title("Dữ liệu gốc (Original Data)")
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    
    plt.subplot(1, 2, 2)
    plt.plot(k_list, scores, 'bo-', linewidth=2, markersize=8)
    if suggested_k is not None:
        plt.axvline(x=suggested_k, color='r', linestyle='--', label=f'Gợi ý K={suggested_k}')
        plt.legend()
    plt.title("Chọn K bằng GridSearchCV (MSE/Inertia)")
    plt.xlabel("Số lượng cụm (K)")
    plt.ylabel("MSE / Inertia (Càng thấp càng tốt)")
    plt.grid(True)
    
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(3)

# DỮ LIỆU ĐẦU VÀO: CITY
data_source = [
    {"id": "Hanoi", "coords": [21.0285, 105.8542], "DanhSachDiemDuLich": ["VanMieu", "LangBac"]},
    {"id": "HCM", "coords": [10.8231, 106.6297], "DanhSachDiemDuLich": ["ChoBenThanh"]},
    {"id": "DaNang", "coords": [16.0471, 108.2068], "DanhSachDiemDuLich": ["BaNaHills"]},
    {"id": "Hue", "coords": [16.4637, 107.5909], "DanhSachDiemDuLich": ["KinhThanh"]},
    {"id": "HaiPhong", "coords": [20.8449, 106.6881], "DanhSachDiemDuLich": ["CatBa"]}
]

def build_graph(data):
    G = nx.Graph()
    id_key = list(data[0].keys())[0]
    node_names = [d[id_key] for d in data]
    for d in data:
        G.add_node(d[id_key], coords=d["coords"])
    
    for u, v in itertools.combinations(data, 2):
        dist = np.linalg.norm(np.array(u["coords"]) - np.array(v["coords"]))
        G.add_edge(u[id_key], v[id_key], weight=dist)
    return G, node_names

def extract_features(G, node_names):
    return np.array([G.nodes[n]["coords"] for n in node_names])
def run_greedy(G, node_names):
    print("\n--- THUẬT TOÁN GREEDY ---")
    if nx.is_weighted(G):
        unvisited = set(node_names)
        current = node_names[0]
        unvisited.remove(current)
        path = [current]
        total_dist = 0
        while unvisited:
            nxt = min(unvisited, key=lambda n: G[current][n]['weight'])
            total_dist += G[current][nxt]['weight']
            current = nxt
            path.append(current)
            unvisited.remove(current)
        print("Lộ trình Greedy:", " -> ".join(path))
        print("Tổng khoảng cách:", total_dist)
        draw_tsp(G, path)
        return path
    else:
        degrees = dict(G.degree())
        sorted_nodes = sorted(node_names, key=lambda x: degrees[x], reverse=True)
        solution = {}
        for node in sorted_nodes:
            neighbor_colors = {solution[n] for n in G.neighbors(node) if n in solution}
            color = next(c for c in range(len(node_names)+1) if c not in neighbor_colors)
            solution[node] = color
        print("Lịch xếp (Greedy Coloring):")
        for node, color in sorted(solution.items(), key=lambda x: x[1]):
            print(f"Ca {color+1}: {node}")
        
        colors = [solution.get(n, 0) for n in G.nodes]
        draw_graph(G, node_colors=colors, title="Greedy Graph Coloring")
        return solution
def run_gridsearch(X_features):
    print("\n--- THUẬT TOÁN GRID SEARCH (TÌM K CHO K-MEANS) ---")
    k_list, scores = [], []
    best_k = 2
    best_sil = -1
    
    max_k = min(CONFIG["GRID_SEARCH_MAX_K"], len(X_features) + 1)
    if max_k <= 2: max_k = 3
    for k in range(2, max_k):
        kmeans = KMeans(n_clusters=k, random_state=CONFIG["RANDOM_SEED"], n_init=10)
        labels = kmeans.fit_predict(X_features)
        score = kmeans.inertia_
        k_list.append(k)
        scores.append(score)
        
        if 1 < len(set(labels)) < len(X_features):
            sil = silhouette_score(X_features, labels)
            if sil > best_sil:
                best_sil = sil
                best_k = k
                
        print(f"K = {k}, MSE (Inertia) = {score:.2f}")
    
    print(f"=> Grid Search GỢI Ý chọn K = {best_k} (Dựa trên điểm phân cụm Silhouette cao nhất)")
    print("=> (Giá trị này chỉ dùng để tham khảo đồ thị. Thuật toán tiếp theo vẫn dùng K trong CONFIG)")
    if scores:
        plot_gridsearch(X_features, k_list, scores, suggested_k=best_k)
    return CONFIG["K_MEANS_CLUSTERS"]

def kmeans_init_centers(X, n_cluster):
    np.random.seed(CONFIG["RANDOM_SEED"])
    return X[np.random.choice(X.shape[0], n_cluster, replace=False)]

def kmeans_predict_labels(X, centers):
    D = cdist(X, centers)
    return np.argmin(D, axis = 1)

def kmeans_update_centers(X, labels, n_cluster):
    weights = np.bincount(labels, minlength=n_cluster)
    valid = weights > 0
    centers = np.zeros((n_cluster, X.shape[1]))
    for i in range(X.shape[1]):
        centers[valid, i] = np.bincount(labels, weights=X[:, i], minlength=n_cluster)[valid] / weights[valid]
    return centers

def kmeans_has_converged(centers, new_centers):
    return (set([tuple(a) for a in centers]) == set([tuple(a) for a in new_centers]))

def run_kmeans(X_features, node_names, G, k=None):
    if k is None:
        k = CONFIG["K_MEANS_CLUSTERS"]
    k = min(k, len(X_features))
    print(f"\n--- THUẬT TOÁN K-MEANS ITERATIVE (K={k}) ---")
    
    centers = kmeans_init_centers(X_features, k)
    labels = np.zeros(X_features.shape[0], dtype=int)
    
    history = []
    history.append((centers.copy(), labels.copy(), 'Init centers. Assigned all data as cluster 0'))
    
    times = 0
    while True:
        labels = kmeans_predict_labels(X_features, centers)
        history.append((centers.copy(), labels.copy(), f'Assigned label for data at time = {times + 1}'))
        
        new_centers = kmeans_update_centers(X_features, labels, k)
        if kmeans_has_converged(centers, new_centers):
            break
        centers = new_centers
        history.append((centers.copy(), labels.copy(), f'Update center position at time = {times + 1}'))
        times += 1

    print('Hoàn tất! Kmeans đã hội tụ sau', times, 'bước lặp')
    result = defaultdict(list)
    for i, label in enumerate(labels):
        result[label].append(node_names[i])
    for label, nodes in sorted(result.items()):
        print(f"Cụm {label+1}: {', '.join(nodes)}")
        
    # HIỂN THỊ INTERACTIVE VISUALIZATION TỪNG BƯỚC
    fig, ax = plt.subplots(figsize=(10, 7))
    fig.canvas.manager.set_window_title(f"K-Means Iterations (K={k})")
    plt.subplots_adjust(bottom=0.2)
    
    current_step = [0]
    plt_colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'orange', 'purple', 'brown'] # Không có w
    
    def draw_step(step):
        ax.clear()
        c, l, t = history[step]
        ax.set_title(f"[{step+1}/{len(history)}] {t}")
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        for i in range(k):
            data = X_features[l == i]
            if len(data) > 0:
                ax.plot(data[:, 0], data[:, 1], color=plt_colors[i%10], marker='^', linestyle='', markersize=8, label=f'cluster_{i}')
            ax.plot(c[i][0], c[i][1], color=plt_colors[(i+4)%10], marker='o', linestyle='', markersize=14, label=f'center_{i}')
        ax.legend()
        fig.canvas.draw_idle()

    draw_step(0)
    
    axprev = plt.axes([0.3, 0.05, 0.1, 0.075])
    axnext = plt.axes([0.6, 0.05, 0.1, 0.075])
    bprev = Button(axprev, 'Previous')
    bnext = Button(axnext, 'Next')
    
    def next_step(event):
        if current_step[0] < len(history) - 1:
            current_step[0] += 1
            draw_step(current_step[0])
    
    def prev_step(event):
        if current_step[0] > 0:
            current_step[0] -= 1
            draw_step(current_step[0])
            
    bnext.on_clicked(next_step)
    bprev.on_clicked(prev_step)
    
    print("Vui lòng tương tác với đồ thị K-Means (Next/Prev) và ĐÓNG cửa sổ để tiếp tục thuật toán...")
    plt.show() # Chờ người dùng tương tác xong mới đi tiếp
    
    draw_graph(G, node_colors=labels, title=f"Kết quả đồ thị K-Means (K={k})")
    return labels

def visualize_knn_mechanism(X, y, test_point, k=3):
    plt.figure(figsize=(10, 6))
    plt.gcf().canvas.manager.set_window_title(f"K-NN Láng giềng gần nhất (K={k})")
    
    cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF'])
    plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_bold, edgecolor='k', s=100)
    
    plt.scatter(test_point[0][0], test_point[0][1], c='gold', marker='*', s=400, edgecolor='k', label='Điểm Test mới')
    
    distances = pairwise_distances(test_point, X)[0]
    k_actual = min(k, len(X))
    nearest_indices = np.argpartition(distances, k_actual-1)[:k_actual]
    
    for idx in nearest_indices:
        neighbor = X[idx]
        plt.plot([test_point[0][0], neighbor[0]], [test_point[0][1], neighbor[1]], 'k--', alpha=0.5)
        
    plt.title(f"Minh họa cơ chế K-NN với K = {k}", fontsize=14)
    plt.legend()
    plt.show(block=False)
    plt.pause(2)

def plot_decision_boundaries(X, y, k_values):
    x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
    y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
    
    h = min((x_max - x_min)/50, (y_max - y_min)/50)
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    
    plt.figure(figsize=(15, 5))
    plt.gcf().canvas.manager.set_window_title("K-NN Decision Boundaries")
    cmap_light = ListedColormap(['#FFAAAA', '#AAFFAA', '#AAAAFF', '#FFFFAA', '#FFAAFF', '#AAFFFF'])
    cmap_bold = ListedColormap(['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF'])
    
    num_plots = len([k for k in k_values if k <= len(X)])
    if num_plots == 0: return
    
    plot_idx = 1
    for k in k_values:
        if k > len(X): continue
        clf = KNeighborsClassifier(n_neighbors=k)
        clf.fit(X, y)
        Z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)
        
        plt.subplot(1, num_plots, plot_idx)
        plt.contourf(xx, yy, Z, cmap=cmap_light, alpha=0.8)
        plt.scatter(X[:, 0], X[:, 1], c=y, cmap=cmap_bold, edgecolor='k', s=50)
        plt.xlim(xx.min(), xx.max())
        plt.ylim(yy.min(), yy.max())
        plt.title(f"Ranh giới với K = {k}")
        plot_idx += 1
        
    plt.tight_layout()
    plt.show(block=False)
    plt.pause(3)

def run_knn(X_train, y_train, node_names, new_feature):
    print("\n--- THUẬT TOÁN K-NN (DỰ ĐOÁN CHO DỮ LIỆU MỚI) ---")
    if len(set(y_train)) < 2:
        print("Không đủ số lượng cụm (ít nhất 2) để huấn luyện KNN.")
        return 0
        
    neighbors = min(CONFIG["KNN_NEIGHBORS"], len(X_train))
    knn = KNeighborsClassifier(n_neighbors=neighbors)
    knn.fit(X_train, y_train)
    pred = knn.predict([new_feature])[0]
    
    visualize_knn_mechanism(X_train, y_train, np.array([new_feature]), k=neighbors)
    plot_decision_boundaries(X_train, y_train, k_values=[1, min(3, len(X_train)), min(5, len(X_train))])
    
    print(f"=> Dự đoán điểm mới thuộc Cụm: {pred+1}")
    return pred

if __name__ == "__main__":
    print("Khởi tạo đồ thị...")
    G, node_names = build_graph(data_source)
    X_features = extract_features(G, node_names)
    
    draw_graph(G, title="Đồ thị Khởi tạo")
    run_greedy(G, node_names)
    run_gridsearch(X_features)
    labels = run_kmeans(X_features, node_names, G)
    new_feat = X_features[0] * 0.9
    run_knn(X_features, labels, node_names, new_feat)

    print("\nHoàn tất thực thi! Đóng cửa sổ đồ họa (nếu có) để kết thúc.")
    plt.show()
