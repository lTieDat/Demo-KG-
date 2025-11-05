# app.py - Refactored with Clean Architecture
import streamlit as st
import os
import sys
import torch

# --- Patch torch.load để luôn weights_only=False ---
_real_torch_load = torch.load


def torch_load_compatible(*args, **kwargs):
    kwargs["weights_only"] = False
    return _real_torch_load(*args, **kwargs)


torch.load = torch_load_compatible

# Import components và services
from components.sidebar import SidebarComponent
from components.student_selection import StudentSelectionComponent
from components.recommendation import RecommendationComponent
from components.ai_explanation import AIExplanationComponent
from services.model_service import ModelService
from styles.custom_css import get_custom_css
from item_utils import load_item_details, get_item_display_info

# LLM Explainer
try:
    from llm_explainer import LLMExplainer, OllamaExplainer, LocalLLMExplainer

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Cấu hình
MODEL_DIR = r"saved"
RECBOLE_MODEL_DIR = r"E:\DoAn\RecBole\saved"
sys.path.append(r"E:\DoAn\RecBole")

# Page config
st.set_page_config(
    page_title="KGCN Exercise Recommender",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


def main():
    """Main application"""
    # Header
    st.title("Hệ thống gợi ý bài tập KGCN")
    st.markdown(
        "*Sử dụng Knowledge Graph Convolutional Network để gợi ý bài tập cho sinh viên*"
    )

    # Initialize services
    model_service = ModelService(MODEL_DIR, RECBOLE_MODEL_DIR)

    # Initialize components
    sidebar_component = SidebarComponent(model_service)
    student_component = StudentSelectionComponent()
    recommendation_component = RecommendationComponent()
    ai_component = AIExplanationComponent(LLM_AVAILABLE)

    # Render sidebar
    load_method, model_path, config, model, dataset = (
        sidebar_component.render_model_selection()
    )

    # Main content
    if config is not None and model is not None and dataset is not None:
        # Get student options
        student_options = student_component.get_student_options(dataset)
        sorted_student_codes = sorted(student_options.keys())

        # Render dataset info
        sidebar_component.render_dataset_info(dataset, student_options)
        sidebar_component.render_statistics(sorted_student_codes)

        # Render student selection
        user_id, selected_student, topk, input_method = student_component.render(
            dataset
        )

        # Store user_id2token in session state for AI component
        st.session_state.user_id2token = dataset.field2id_token[dataset.uid_field]

        # Generate recommendations button
        if st.button("Tạo gợi ý bài tập", type="primary"):
            if user_id is None or user_id <= 0:
                st.error("Vui lòng chọn sinh viên hợp lệ trước khi tạo gợi ý!")
            else:
                # Clear old explanation
                if "explanation" in st.session_state:
                    del st.session_state.explanation

                try:
                    with st.spinner("Đang tạo gợi ý..."):
                        recs = model_service.get_top_k_recommendations(
                            model, dataset, user_id, topk=topk
                        )
                        item_details = load_item_details()

                    # Get student code
                    user_id2token = dataset.field2id_token[dataset.uid_field]
                    student_code = (
                        selected_student
                        if selected_student
                        else (
                            user_id2token[user_id]
                            if user_id < len(user_id2token)
                            else f"User_{user_id}"
                        )
                    )

                    # Save to session state FIRST before rendering
                    st.session_state.current_recs = recs
                    st.session_state.current_user = user_id
                    st.session_state.current_items = item_details

                    # Render recommendations
                    recommendation_component.render_recommendations(
                        recs, item_details, student_code, topk
                    )

                except Exception as e:
                    st.error(f"Lỗi khi tạo gợi ý: {str(e)}")
                    st.error("Chi tiết lỗi:")
                    st.code(str(e))

        # Render AI explanation section
        ai_component.render()

    else:
        st.warning("Vui lòng chọn và load model trước khi sử dụng")


if __name__ == "__main__":
    main()
