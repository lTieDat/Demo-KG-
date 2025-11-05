"""
AI Explanation Component - Giao diện giải thích bằng AI
"""

import streamlit as st
from item_utils import get_item_display_info


class AIExplanationComponent:
    """Component quản lý AI explanation"""

    def __init__(self, llm_available=True):
        self.llm_available = llm_available

    def render(self):
        """Render giao diện AI explanation"""
        if not self.llm_available:
            st.warning(
                "⚠️ LLM Explainer không available. Cài đặt thư viện: pip install openai requests"
            )
            return None, None

        st.markdown(
            '<div class="section-header">🤖 Giải Thích Bằng AI (Ollama)</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)

        with col1:
            model_options = ["mistral", "llama2", "phi3:mini", "codellama"]
            model_name = st.selectbox(
                "Model:", model_options, index=0, key="global_ollama_model"
            )

        with col2:
            base_url = st.text_input(
                "Ollama URL:", "http://localhost:11434", key="global_ollama_url"
            )

        col_test, col_explain = st.columns(2)

        with col_test:
            self._render_test_connection(base_url)

        with col_explain:
            self._render_create_explanation(model_name, base_url)

        # Hiển thị explanation từ session state
        self._render_explanation_display()

        return model_name, base_url

    def _render_test_connection(self, base_url):
        """Test kết nối Ollama"""
        if st.button("Test kết nối", key="global_test_connection"):
            try:
                import requests

                response = requests.get(f"{base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m["name"] for m in models]
                    if model_names:
                        st.success(f"Models: {', '.join(model_names)}")
                    else:
                        st.warning("Chưa có model. Chạy: ollama pull mistral")
                else:
                    st.error("Server không phản hồi")
            except Exception as e:
                st.error(f"Lỗi: {str(e)}")
                st.info("Chạy: ollama serve")

    def _render_create_explanation(self, model_name, base_url):
        """Tạo giải thích từ AI"""
        if st.button("Tạo giải thích", type="primary", key="global_create_explanation"):
            if (
                "current_recs" not in st.session_state
                or not st.session_state.current_recs
            ):
                st.error("Vui lòng tạo gợi ý bài tập trước!")
            else:
                self._generate_explanation(model_name, base_url)

    def _generate_explanation(self, model_name, base_url):
        """Generate explanation từ Ollama"""
        try:
            from llm_explainer import OllamaExplainer

            user_id = st.session_state.current_user
            recs = st.session_state.current_recs
            item_details = st.session_state.current_items
            user_id2token = st.session_state.user_id2token

            student_code = (
                user_id2token[user_id]
                if user_id < len(user_id2token)
                else f"User_{user_id}"
            )

            rec_data = []
            for item_internal_id, item_external_id, score in recs:
                item_info = get_item_display_info(item_external_id, item_details)
                rec_data.append(
                    {
                        "title": item_info["title"],
                        "topic": item_info["topic"],
                        "difficulty": item_info["difficulty"],
                        "score": score,
                    }
                )

            explainer = OllamaExplainer(model_name, base_url)

            with st.spinner(f"Đang xử lý với {model_name}..."):
                explanation = explainer.explain_recommendations(student_code, rec_data)

            st.session_state.explanation = explanation
            st.success("Giải thích đã được tạo! Xem bên dưới.")

        except Exception as e:
            st.error(f"Lỗi Ollama: {str(e)}")
            st.info("Thử: ollama serve và ollama pull mistral")

    def _render_explanation_display(self):
        """Hiển thị explanation từ session state kèm danh sách recommendations"""
        if "explanation" in st.session_state and st.session_state.explanation:
            # Hiển thị lại danh sách recommendations nếu có
            if (
                "current_recs" in st.session_state
                and st.session_state.current_recs
                and "current_items" in st.session_state
            ):
                st.markdown("---")
                st.markdown("### Danh sách gợi ý bài tập:")

                recs = st.session_state.current_recs
                item_details = st.session_state.current_items

                # Hiển thị recommendations dưới dạng bảng nhỏ
                rec_data = []
                for i, (item_internal_id, item_external_id, score) in enumerate(
                    recs, 1
                ):
                    item_info = get_item_display_info(item_external_id, item_details)
                    rec_data.append(
                        {
                            "STT": i,
                            "Mã": item_external_id,
                            "Tên bài tập": (
                                item_info["title"][:50] + "..."
                                if len(item_info["title"]) > 50
                                else item_info["title"]
                            ),
                            "Chủ đề": item_info["topic"],
                            "Độ khó": item_info["difficulty"],
                            "Điểm": f"{score:.4f}",
                        }
                    )

                import pandas as pd

                df = pd.DataFrame(rec_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.markdown("---")

            # Hiển thị explanation
            st.markdown(
                '<div class="ai-explanation-container">', unsafe_allow_html=True
            )
            st.markdown("### Giải Thích Từ AI")

            st.markdown(
                f"""
                <div class="explanation-text">
                    {st.session_state.explanation}
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.button("Xóa giải thích", key="clear_explanation_global"):
                del st.session_state.explanation
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
