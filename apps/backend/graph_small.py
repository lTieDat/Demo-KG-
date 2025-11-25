from pyvis.network import Network
import random
from collections import defaultdict

# ==== Load mapping từ .link ====
entity_map = {}
with open("dataset/code-ptit-100k.link", "r", encoding="utf-8") as f:
    for line in f:
        item_or_user, entity_id = line.strip().split("\t")
        # map entity_id -> tên dễ hiểu
        if entity_id.startswith("m."):
            entity_map[entity_id] = f"{item_or_user}"
        elif entity_id.startswith("u."):
            entity_map[entity_id] = f"{item_or_user}"

# ==== Load và filter KG triples ====
edges = []
node_connections = defaultdict(int)

print("Analyzing node connections...")
# Đếm số connection của mỗi node
with open("dataset/code-ptit-100k.kg", "r", encoding="utf-8") as f:
    for line in f:
        h, r, t = line.strip().split("\t")
        node_connections[h] += 1
        node_connections[t] += 1

# Lấy top nodes có nhiều connection nhất
top_nodes = sorted(node_connections.items(), key=lambda x: x[1], reverse=True)[:50]
top_node_ids = {node[0] for node in top_nodes}

print(f"Top 10 nodes with most connections:")
for node, count in top_nodes[:10]:
    label = entity_map.get(node, node)
    print(f"  {label}: {count} connections")

print("Loading edges for top connected nodes...")
with open("dataset/code-ptit-100k.kg", "r", encoding="utf-8") as f:
    for line in f:
        h, r, t = line.strip().split("\t")
        if h in top_node_ids or t in top_node_ids:
            edges.append((h, t, r))

print(f"Selected {len(edges)} edges for visualization")


# ==== Hàm đổi entity_id -> label ====
def get_label(x):
    return entity_map.get(x, x)


def get_color(x):
    if x.startswith("m."):
        return "skyblue"  # item
    elif x.startswith("u."):
        return "orange"  # user
    return "lightgreen"  # entity khác


def get_node_size(x):
    # Kích thước node dựa trên số connections
    connections = node_connections.get(x, 1)
    return min(50, 10 + connections // 10)  # Size từ 10-50


# ==== Tạo graph với PyVis ====
net = Network(height="800px", width="100%", directed=True, notebook=False)
net.toggle_physics(True)

# Add nodes and edges
added_nodes = set()
for h, t, r in edges:
    h_label, t_label = get_label(h), get_label(t)

    # Add nodes only if not already added
    if h not in added_nodes:
        net.add_node(h, label=h_label, color=get_color(h), size=get_node_size(h))
        added_nodes.add(h)
    if t not in added_nodes:
        net.add_node(t, label=t_label, color=get_color(t), size=get_node_size(t))
        added_nodes.add(t)

    net.add_edge(h, t, label=r)

print(f"Created graph with {len(added_nodes)} nodes and {len(edges)} edges")

# ==== Xuất ra file HTML ====
try:
    net.save_graph("kg_small_visual.html")
    print("Graph đã được tạo: mở file 'kg_small_visual.html' trong browser để xem")
except Exception as e:
    print(f"Lỗi: {e}")
