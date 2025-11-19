import os
import pandas as pd
from pathlib import Path


def load_item_details():
    """
    Load thông tin chi tiết về bài tập từ file .item

    Returns:
        dict: Dictionary mapping item_id -> item_info
    """
    # Sử dụng relative paths dựa trên vị trí của file này
    base_dir = Path(__file__).parent
    
    # Các đường dẫn có thể chứa file
    possible_paths = [
        base_dir / "dataset" / "code-ptit-100k.item",
        Path.cwd() / "dataset" / "code-ptit-100k.item",
        base_dir.parent / "Web" / "dataset" / "code-ptit-100k.item",
    ]

    item_file = None

    # Thử tất cả các đường dẫn có thể
    for path in possible_paths:
        if path.exists():
            item_file = str(path)
            print(f"Found item file at: {path}")
            break

    if item_file is None:
        print(f"Warning: Item file not found in any of these paths:")
        for path in possible_paths:
            print(f"  - {path}")
        return {}

    try:
        # Đọc file với tab separator
        df = pd.read_csv(item_file, sep="\t", encoding="utf-8")

        # Tạo dictionary mapping
        item_details = {}

        for _, row in df.iterrows():
            item_id = row["item_id:token_seq"]
            title = (
                row["title:token_seq"] if pd.notna(row["title:token_seq"]) else "N/A"
            )
            topic = (
                row["topic:token_seq"] if pd.notna(row["topic:token_seq"]) else "N/A"
            )
            sub_topic = (
                row["sub_topic:token_seq"]
                if pd.notna(row["sub_topic:token_seq"])
                else "N/A"
            )
            difficulty = (
                row["difficulty:token"] if pd.notna(row["difficulty:token"]) else "N/A"
            )

            item_details[item_id] = {
                "title": title,
                "topic": topic,
                "sub_topic": sub_topic,
                "difficulty": difficulty,
            }

        print(f"Loaded {len(item_details)} items from {item_file}")
        return item_details

    except Exception as e:
        print(f"Error loading item file {item_file}: {e}")
        return {}


def get_item_display_info(item_id, item_details):
    """
    Lấy thông tin hiển thị cho một bài tập

    Args:
        item_id: ID của bài tập
        item_details: Dictionary chứa thông tin bài tập

    Returns:
        dict: Thông tin để hiển thị trong card
    """
    if item_id in item_details:
        info = item_details[item_id]
        return {
            "title": info["title"],
            "topic": info["topic"],
            "sub_topic": info["sub_topic"],
            "difficulty": info["difficulty"],
        }
    else:
        return {
            "title": "Tên không xác định",
            "topic": "Chủ đề không xác định",
            "sub_topic": "Chủ đề con không xác định",
            "difficulty": "Độ khó không xác định",
        }


def get_card_html(item_id, item_info):
    """
    Tạo HTML card cho một bài tập

    Args:
        item_id: ID của bài tập
        item_info: Thông tin chi tiết bài tập

    Returns:
        str: HTML string cho card
    """
    return f"""
    <div style="
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    " onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
        <h4 style="color: #2c3e50; margin: 0 0 10px 0; font-weight: 600;">
            🎯 Bài tập {item_id}
        </h4>
        <div style="background: white; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <p style="margin: 5px 0; color: #34495e;"><strong>📝 Tên:</strong> {item_info['title']}</p>
            <p style="margin: 5px 0; color: #27ae60;"><strong>📚 Chủ đề:</strong> {item_info['topic']}</p>
            <p style="margin: 5px 0; color: #3498db;"><strong>🔍 Chủ đề con:</strong> {item_info['sub_topic']}</p>
            <p style="margin: 5px 0; color: #e74c3c;"><strong>⭐ Độ khó:</strong> {item_info['difficulty']}</p>
        </div>
    </div>
    """
