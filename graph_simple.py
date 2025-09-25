from pyvis.network import Network
import random

# Load mapping với hard-coded names cho topic và difficulty
entity_map = {}
topic_names = {
    "t.00001": "Sinh ke tiep",
    "t.00002": "Sap xep - Tim kiem",
    "t.00003": "Quy hoach dong",
    "t.00004": "Quay lui - Nhanh can",
    "t.00005": "Giai thuat tham lam",
    "t.00006": "Chia va tri",
    "t.00007": "Ngan xep",
    "t.00008": "Hang doi",
    "t.00009": "Duyet do thi",
    "t.00010": "Do thi nang cao",
    "t.00011": "Cay nhi phan",
}

difficulty_names = {
    "d.00001": "Do kho 1 (De)",
    "d.00002": "Do kho 2 (Trung binh)",
    "d.00003": "Do kho 3 (Kho)",
    "d.00004": "Do kho 4 (Rat kho)",
    "d.00005": "Do kho 5 (Cuc kho)",
}

with open("dataset/code-ptit-100k-new.link", "r", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 2:
            name, entity_id = parts
            if entity_id.startswith("m.") or entity_id.startswith("u."):
                entity_map[entity_id] = name

entity_map.update(topic_names)
entity_map.update(difficulty_names)

print(f"Loaded {len(entity_map)} entity mappings")

# Load difficulty mapping
difficulty_map = {}
with open("dataset/code-ptit-100k.item", "r", encoding="utf-8") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) >= 5:
            item_id = parts[0]
            difficulty = parts[4]
            difficulty_map[item_id] = difficulty

# Load KG triples
edges = []
user_item_edges = []
topic_edges = []
difficulty_edges = []
subtopic_edges = []

print("Loading KG triples...")

with open("dataset/code-ptit-100k-updated.kg", "r", encoding="utf-8") as f:
    next(f)
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) == 3:
            h, r, t = parts
            if r == "item.has_topic.topic":
                topic_edges.append((h, t, r))
            elif r == "item.has_difficulty.difficulty":
                difficulty_edges.append((h, t, r))
            elif r == "item.has_subtopic.subtopic":
                subtopic_edges.append((h, t, r))
            else:
                user_item_edges.append((h, t, r))

print(
    f"User-Item: {len(user_item_edges)}, Topic: {len(topic_edges)}, Difficulty: {len(difficulty_edges)}, Subtopic: {len(subtopic_edges)}"
)

# Sample edges với ít kết nối hơn để giảm mật độ
sample_size = 200  # Giảm từ 500 xuống 200
user_item_sample = random.sample(
    user_item_edges, min(sample_size, len(user_item_edges))
)
edges = user_item_sample + topic_edges + difficulty_edges + subtopic_edges

print(f"Total edges: {len(edges)}")


def get_label(x):
    base_label = entity_map.get(x, x)
    if x.startswith("m.") and base_label in difficulty_map:
        difficulty = difficulty_map[base_label]
        if difficulty:
            return f"{base_label} (Lvl {difficulty})"
    return base_label


def get_color(x):
    if x.startswith("m."):
        return "#87CEEB"  # Màu skyblue cho tất cả items
    elif x.startswith("u."):
        return "#FFA500"
    elif x.startswith("t."):
        return "#98FB98"
    elif x.startswith("d."):
        return "#FFB6C1"
    return "lightgreen"


# Create graph với kích thước lớn hơn
net = Network(height="900px", width="100%", directed=True, notebook=False)
net.toggle_physics(True)

# Thêm legend nodes (ẩn nhưng hiển thị trong chú thích)
legend_nodes = [
    {
        "id": "legend_item",
        "label": "Items (Bài tập)",
        "color": "#87CEEB",
        "physics": False,
        "x": -500,
        "y": -200,
    },
    {
        "id": "legend_user",
        "label": "Users",
        "color": "#FFA500",
        "physics": False,
        "x": -500,
        "y": -150,
    },
    {
        "id": "legend_topic",
        "label": "Topics",
        "color": "#98FB98",
        "physics": False,
        "x": -500,
        "y": -100,
    },
    {
        "id": "legend_difficulty",
        "label": "Difficulties",
        "color": "#FFB6C1",
        "physics": False,
        "x": -500,
        "y": -50,
    },
    {
        "id": "legend_other",
        "label": "Other Entities",
        "color": "lightgreen",
        "physics": False,
        "x": -500,
        "y": 0,
    },
]

# Thêm legend nodes trước
for legend in legend_nodes:
    net.add_node(
        legend["id"],
        label=legend["label"],
        color=legend["color"],
        physics=legend["physics"],
        x=legend["x"],
        y=legend["y"],
        fixed=True,
        font={"size": 12, "color": "black"},
    )

added_nodes = set()
for h, t, r in edges:
    h_label, t_label = get_label(h), get_label(t)
    if h not in added_nodes:
        net.add_node(h, label=h_label, color=get_color(h))
        added_nodes.add(h)
    if t not in added_nodes:
        net.add_node(t, label=t_label, color=get_color(t))
        added_nodes.add(t)
    net.add_edge(h, t, label=r)

print(f"Added {len(added_nodes)} nodes and {len(edges)} edges")

# Tùy chỉnh options với physics mạnh hơn để giãn mật độ
net.set_options(
    """
var options = {
  "physics": {
    "enabled": true,
    "stabilization": {"iterations": 200},
    "barnesHut": {
      "gravitationalConstant": -80000,
      "centralGravity": 0.3,
      "springLength": 150,
      "springConstant": 0.04,
      "damping": 0.09,
      "avoidOverlap": 1
    }
  },
  "nodes": {
    "font": {"size": 12},
    "borderWidth": 2,
    "size": 25,
    "margin": 10
  },
  "edges": {
    "color": {"inherit": true},
    "width": 1,
    "length": 200,
    "arrows": {"to": {"enabled": true, "scaleFactor": 0.8}},
    "smooth": {
      "enabled": true,
      "type": "continuous"
    }
  },
  "interaction": {
    "navigationButtons": true,
    "keyboard": true,
    "zoomView": true,
    "dragView": true
  },
  "layout": {
    "improvedLayout": true,
    "clusterThreshold": 150
  }
}
"""
)

net.save_graph("kg_full_visual.html")

# Thêm custom HTML với legend
legend_html = """
<div style="position: absolute; top: 10px; left: 10px; background: white; 
           border: 2px solid #ccc; border-radius: 10px; padding: 15px; 
           box-shadow: 0 4px 8px rgba(0,0,0,0.1); z-index: 1000;">
    <h4 style="margin-top: 0; color: #333;">🎨 Chú thích màu sắc</h4>
    <div style="display: flex; flex-direction: column; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 20px; height: 20px; background-color: #87CEEB; border-radius: 50%; border: 1px solid #666;"></div>
            <span style="font-size: 13px;">📝 Items (Bài tập)</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 20px; height: 20px; background-color: #FFA500; border-radius: 50%; border: 1px solid #666;"></div>
            <span style="font-size: 13px;">👤 Users</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 20px; height: 20px; background-color: #98FB98; border-radius: 50%; border: 1px solid #666;"></div>
            <span style="font-size: 13px;">📚 Topics</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 20px; height: 20px; background-color: #FFB6C1; border-radius: 50%; border: 1px solid #666;"></div>
            <span style="font-size: 13px;">⚖️ Difficulties</span>
        </div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <div style="width: 20px; height: 20px; background-color: lightgreen; border-radius: 50%; border: 1px solid #666;"></div>
            <span style="font-size: 13px;">🔹 Other Entities</span>
        </div>
    </div>
</div>
"""

# Đọc file HTML đã tạo và thêm legend
try:
    with open("kg_full_visual.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # Thêm legend vào sau thẻ body
    html_content = html_content.replace(
        '<div class="card-body"></div>', f'<div class="card-body"></div>{legend_html}'
    )

    # Nếu không tìm thấy card-body, thêm vào sau body
    if legend_html not in html_content:
        html_content = html_content.replace("<body>", f"<body>{legend_html}")

    with open("kg_full_visual.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("✅ Graph saved with legend!")

except Exception as e:
    print(f"❌ Error adding legend: {e}")
    print("📄 Graph saved without legend!")

print("\n🎨 Màu sắc nodes:")
print("   � #87CEEB: Items (Bài tập)")
print("   🟠 #FFA500: Users")
print("   💚 #98FB98: Topics")
print("   🩷 #FFB6C1: Difficulties")
print("   � lightgreen: Other Entities")
