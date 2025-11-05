"""
Recommendation Component - Hiển thị kết quả gợi ý bài tập
"""

import streamlit as st
import pandas as pd
from item_utils import get_item_display_info


class RecommendationComponent:
    """Component quản lý hiển thị recommendation"""

    def __init__(self):
        pass

    def render_recommendations(self, recs, item_details, student_code, topk):
        """Render danh sách recommendation dưới dạng cards hiện đại"""
        st.success(f"Top {topk} gợi ý bài tập cho sinh viên **{student_code}**")

        # Hiển thị kết quả dưới dạng grid cards
        self._render_recommendation_grid(recs, item_details)

        # Hiển thị chi tiết trong expander
        self._render_detailed_info(recs, item_details)

    def _render_recommendation_grid(self, recs, item_details):
        """Render grid layout cho recommendations"""
        cols_per_row = 2

        for i in range(0, len(recs), cols_per_row):
            cols = st.columns(cols_per_row)
            for j in range(cols_per_row):
                if i + j < len(recs):
                    item_internal_id, item_external_id, score = recs[i + j]
                    item_info = get_item_display_info(item_external_id, item_details)

                    with cols[j]:
                        self._render_card(i + j + 1, item_external_id, item_info, score)

    def _render_card(self, rank, item_id, item_info, score):
        """Render một recommendation card với design hiện đại"""
        difficulty_color = self._get_difficulty_color(item_info["difficulty"])

        card_html = f"""
        <div class="recommendation-card">
            <div class="card-rank">#{rank}</div>
            <div class="card-header">
                <h3 class="card-title">Bài tập {item_id}</h3>
            </div>
            <div class="card-body">
                <div class="card-exercise-title">
                    {item_info['title']}
                </div>
                <div class="card-info-row">
                    <span class="card-label">Chủ đề:</span>
                    <span class="card-value">{item_info['topic']}</span>
                </div>
                <div class="card-info-row">
                    <span class="card-label">Chủ đề phụ:</span>
                    <span class="card-value">{item_info['sub_topic']}</span>
                </div>
                <div class="card-info-row">
                    <span class="card-label">Độ khó:</span>
                    <span class="difficulty-badge" style="background-color: {difficulty_color};">
                        {item_info['difficulty']}
                    </span>
                </div>
                <div class="card-score">
                    Điểm dự đoán: <strong>{score:.4f}</strong>
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    def _get_difficulty_color(self, difficulty):
        """Lấy màu tương ứng với độ khó"""
        difficulty_colors = {
            "Dễ": "#4CAF50",
            "Trung bình": "#FF9800",
            "Khó": "#F44336",
        }
        return difficulty_colors.get(difficulty, "#9E9E9E")

    def _render_detailed_info(self, recs, item_details):
        """Render thông tin chi tiết trong expander"""
        with st.expander("Chi tiết kết quả"):
            st.write("**Giải thích:**")
            st.write("- **STT**: Thứ tự gợi ý (cao đến thấp)")
            st.write("- **Mã bài tập**: Mã bài tập được gợi ý")
            st.write("- **Tên bài tập**: Tên đầy đủ của bài tập")
            st.write("- **Chủ đề**: Chủ đề chính của bài tập")
            st.write("- **Chủ đề phụ**: Chủ đề phụ của bài tập")
            st.write("- **Độ khó**: Mức độ khó của bài tập")

            st.write("**Bảng tóm tắt:**")
            df_data = []
            for i, (item_internal_id, item_external_id, score) in enumerate(recs, 1):
                item_info = get_item_display_info(item_external_id, item_details)
                df_data.append(
                    {
                        "STT": i,
                        "Mã bài tập": item_external_id,
                        "Tên bài tập": item_info["title"],
                        "Chủ đề": item_info["topic"],
                        "Độ khó": item_info["difficulty"],
                        "Điểm": f"{score:.4f}",
                    }
                )
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
