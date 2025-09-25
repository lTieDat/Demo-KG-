# def load_link_file(path):
#     link_ids = set()
#     with open(path, encoding="utf-8") as f:
#         next(f)  # bỏ header
#         for line in f:
#             parts = line.strip().split()
#             if len(parts) == 2:
#                 # chỉ lấy entity_id (vd: m.00001)
#                 link_ids.add(parts[1])
#     return link_ids


# def load_kg_file(path):
#     kg_ids = set()
#     with open(path, encoding="utf-8") as f:
#         next(f)  # bỏ header
#         for line in f:
#             parts = line.strip().split()
#             if len(parts) == 3:
#                 head, _, tail = parts
#                 kg_ids.add(head)
#                 kg_ids.add(tail)
#     return kg_ids


# if __name__ == "__main__":
#     link_file = "dataset/code-ptit-100k.link"
#     kg_file = "dataset/code-ptit-100k.kg"

#     link_ids = load_link_file(link_file)
#     kg_ids = load_kg_file(kg_file)

#     # ID có trong link nhưng không có trong kg
#     only_in_link = link_ids - kg_ids
#     # ID có trong kg nhưng không có trong link
#     only_in_kg = kg_ids - link_ids
#     # ID chung
#     common_ids = link_ids & kg_ids

#     print("📌 Chỉ có trong .link:", only_in_link)
#     print("📌 Chỉ có trong .kg:", only_in_kg)
#     print("📌 Có trong cả hai:", common_ids)


# def load_link_items(path):
#     link_items = set()
#     with open(path, encoding="utf-8") as f:
#         next(f)  # bỏ header
#         for line in f:
#             parts = line.strip().split()
#             if len(parts) == 2:
#                 # cột đầu tiên là item_id
#                 link_items.add(parts[0])
#     return link_items


# def load_inter_items(path):
#     inter_items = set()
#     with open(path, encoding="utf-8") as f:
#         next(f)  # bỏ header
#         for line in f:
#             parts = line.strip().split()
#             if len(parts) >= 1:
#                 inter_items.add(parts[0])  # item_id nằm ở cột đầu
#     return inter_items


# if __name__ == "__main__":
#     link_file = "dataset/code-ptit-100k.link"
#     inter_file = "dataset/code-ptit-100k.inter"

#     link_items = load_link_items(link_file)
#     inter_items = load_inter_items(inter_file)

#     # item có trong inter nhưng không có trong link
#     only_in_inter = inter_items - link_items
#     # item có trong link nhưng chưa từng xuất hiện trong inter
#     only_in_link = link_items - inter_items
#     # item chung
#     common_items = inter_items & link_items

#     print("📌 Chỉ có trong .inter:", only_in_inter)
#     print("📌 Chỉ có trong .link:", only_in_link)
#     print("📌 Có trong cả hai:", common_items)

#     # lưu vào file để kiểm tra
#     with open("result.txt", "w", encoding="utf-8") as f:
#         f.write("Chỉ có trong .inter:\n")
#         for item in only_in_inter:
#             f.write(f"{item}\n")
#         f.write("\nChỉ có trong .link:\n")
#         for item in only_in_link:
#             f.write(f"{item}\n")
#         f.write("\nCó trong cả hai:\n")
#         for item in common_items:
#             f.write(f"{item}\n")


def add_topic_to_link(item_file, link_file, output_file):
    # đọc topic từ file .item
    topics = {}
    topic_index = 1
    with open(item_file, encoding="utf-8") as f:
        header = next(f).strip().split("\t")
        topic_idx = header.index("sub_topic:token_seq")

        for line in f:
            parts = line.strip().split("\t")
            if len(parts) > topic_idx:
                topic_name = parts[topic_idx].strip()
                if topic_name != "N/A" and topic_name not in topics:
                    topics[topic_name] = f"t.{str(topic_index).zfill(5)}"
                    topic_index += 1

    # đọc mapping cũ trong .link
    old_lines = []
    with open(link_file, encoding="utf-8") as f:
        old_lines = f.readlines()

    # ghi file mới: gồm cả item cũ + topic mới
    with open(output_file, "w", encoding="utf-8") as fout:
        fout.writelines(old_lines)
        for topic, tid in topics.items():
            fout.write(f"{topic}\t{tid}\n")

    print(f"✅ Đã tạo file link mới: {output_file}")
    print(f"👉 Số lượng topic thêm: {len(topics)}")


if __name__ == "__main__":
    item_file = "dataset/code-ptit-100k.item"
    link_file = "dataset/code-ptit-100k.link"
    output_file = "dataset/code-ptit-100k-new.link."

    add_topic_to_link(item_file, link_file, output_file)
