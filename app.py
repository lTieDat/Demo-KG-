# app_refactored.py - Refactored with Clean Architecture
import streamlit as st
import os
import sys
import torch

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Patch DGL's edge_subgraph to handle preserve_nodes parameter
import dgl
_original_edge_subgraph = dgl.DGLGraph.edge_subgraph

def patched_edge_subgraph(self, edges, *args, **kwargs):
    # Remove preserve_nodes if present (not supported in DGL 1.1.2)
    kwargs.pop('preserve_nodes', None)
    return _original_edge_subgraph(self, edges, *args, **kwargs)

dgl.DGLGraph.edge_subgraph = patched_edge_subgraph

# Monkey-patch to handle missing KGCN_UserKG class
from recbole.model.knowledge_aware_recommender import KGCN
import recbole.model.knowledge_aware_recommender.kgcn as kgcn_module

# Add KGCN_UserKG as an alias to KGCN in the kgcn module
kgcn_module.KGCN_UserKG = KGCN

# Create a fake kgcn_userkg module that points to the kgcn module
sys.modules['recbole.model.knowledge_aware_recommender.kgcn_userkg'] = kgcn_module

# Import utilities
from item_utils import load_item_details, get_item_display_info
from styles import inject_custom_css
from utils.models import get_compatible_checkpoints, load_trained_model
from utils.recommendations import get_top_k_recommendations

# LLM Explainer
try:
    from llm_explainer import LLMExplainer, OllamaExplainer, LocalLLMExplainer, MistralCloudExplainer
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    st.warning(
        "LLM Explainer không available. Cài đặt thư viện: pip install openai requests mistralai"
    )

# Constants
MODEL_DIR = "saved"

# ============================================================================
# MAIN APP
# ============================================================================

# Inject custom CSS
inject_custom_css()

# Title
st.title("Hệ thống gợi ý bài tập Code PTIT")
st.markdown(
    "*Sử dụng Knowledge Graph Convolutional Network để gợi ý bài tập cho sinh viên*"
)

# ============================================================================
# SIDEBAR: Model Selection
# ============================================================================

st.sidebar.header("Cấu hình Model")

with st.spinner("Đang tải danh sách model..."):
    compatible_models, incompatible_models = get_compatible_checkpoints(MODEL_DIR)

if compatible_models:
    st.sidebar.success(f"{len(compatible_models)} model tương thích")

    # Tạo options cho selectbox
    model_options = []
    model_info_dict = {}

    for model_file, info in compatible_models:
        display_name = f"{model_file}"
        model_options.append(display_name)
        model_info_dict[display_name] = (model_file, info)

    selected_model = st.sidebar.selectbox("Chọn model tương thích:", model_options)

    if selected_model:
        model_file, info = model_info_dict[selected_model]
        model_path = os.path.join(MODEL_DIR, model_file)

        # Hiển thị thông tin checkpoint
        with st.sidebar.expander("Thông tin Checkpoint"):
            st.write(f"**Dataset:** {info['dataset']}")
            st.write(f"**Epoch:** {info['epoch']}")
            st.write(f"**Score:** {info['score']}")
            st.write(f"**Embedding size:** {info['embedding_size']}")
            st.write(
                f"**Users:** {info['user_count']:,}"
                if info["user_count"] != "Unknown"
                else "**Users:** Unknown"
            )
            st.write(
                f"**Entities:** {info['entity_count']:,}"
                if info["entity_count"] != "Unknown"
                else "**Entities:** Unknown"
            )
            st.write(
                f"**Relations:** {info['relation_count']:,}"
                if info["relation_count"] != "Unknown"
                else "**Relations:** Unknown"
            )

    # Hiển thị model không tương thích
    if incompatible_models:
        with st.sidebar.expander(
            f"{len(incompatible_models)} model không tương thích"
        ):
            for model_file, info in incompatible_models:
                st.write(f"**{model_file}**")
                if "compatibility_issues" in info:
                    for issue in info["compatibility_issues"]:
                        st.write(f"  - {issue}")
                st.write("---")
else:
    st.sidebar.error("Không có model nào tương thích với dataset hiện tại!")
    st.sidebar.write("Dataset yêu cầu: code-ptit-100k, embedding_size=64")

    # Hiển thị danh sách tất cả model để debug
    all_models = [f for f in os.listdir(MODEL_DIR) if f.endswith(".pth")]
    if all_models:
        with st.sidebar.expander("Tất cả model có sẵn"):
            for model_file in all_models:
                model_path = os.path.join(MODEL_DIR, model_file)
                from utils.models import check_checkpoint_compatibility
                info = check_checkpoint_compatibility(model_path, "code-ptit-100k")
                st.write(f"**{model_file}**")
                if "compatibility_issues" in info:
                    for issue in info["compatibility_issues"]:
                        st.write(f"  - {issue}**")
                st.write("---")

    st.stop()

# ============================================================================
# Load Model
# ============================================================================

with st.spinner("Đang load model..."):
    config, model, dataset = load_trained_model(model_path)

# ============================================================================
# MAIN INTERFACE: Student Selection & Recommendations
# ============================================================================

if (
    "config" in locals()
    and config is not None
    and model is not None
    and dataset is not None
):
    # Lấy danh sách mã sinh viên
    uid_field = dataset.uid_field
    user_id2token = dataset.field2id_token[uid_field]

    # Tạo dictionary mapping
    student_options = {}
    for user_id in range(1, len(user_id2token)):
        student_code = user_id2token[user_id]
        if (
            isinstance(student_code, str)
            and student_code.startswith("B")
            and len(student_code) >= 8
        ):
            student_options[student_code] = user_id

    sorted_student_codes = sorted(student_options.keys())

    # Dataset info in sidebar
    st.sidebar.header("Thông tin Dataset")
    st.sidebar.metric("Tổng số user", f"{dataset.user_num:,}")
    st.sidebar.metric("Số sinh viên hợp lệ", f"{len(student_options):,}")
    st.sidebar.metric("Số bài tập", f"{dataset.item_num:,}")

    # Thống kê
    year_stats = {}
    major_stats = {}
    for code in sorted_student_codes:
        if len(code) >= 3:
            year = code[:3]
            year_stats[year] = year_stats.get(year, 0) + 1
        if len(code) >= 7:
            major = code[3:7]
            major_stats[major] = major_stats.get(major, 0) + 1

    with st.sidebar.expander("Thống kê chi tiết"):
        st.write("**Theo năm:**")
        for year, count in sorted(year_stats.items()):
            st.write(f"- {year}: {count} sinh viên")

        st.write("**Theo ngành (top 5):**")
        top_majors = sorted(major_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        for major, count in top_majors:
            st.write(f"- {major}: {count} sinh viên")

    # ========================================================================
    # Student Selection
    # ========================================================================
    
    st.subheader("Chọn sinh viên")

    input_method = st.radio(
        "Phương thức chọn sinh viên:", ["Dropdown mã sinh viên", "Nhập User ID"]
    )

    if input_method == "Dropdown mã sinh viên":
        search_term = st.text_input(
            "Tìm kiếm mã sinh viên (tùy chọn):",
            placeholder="Nhập mã sinh viên để tìm kiếm nhanh...",
            help="Nhập một phần mã sinh viên để lọc danh sách",
        )

        if search_term:
            filtered_codes = [
                code
                for code in sorted_student_codes
                if search_term.upper() in code.upper()
            ]
            if filtered_codes:
                display_codes = filtered_codes
                st.success(f"Tìm thấy {len(filtered_codes)} sinh viên")
            else:
                st.warning(f"Không tìm thấy '{search_term}'")
                display_codes = sorted_student_codes
        else:
            display_codes = sorted_student_codes

        selected_student = st.selectbox(
            f"Chọn mã sinh viên ({len(display_codes)} sinh viên):",
            options=display_codes,
            index=0 if display_codes else None,
            help="Chọn mã sinh viên để xem gợi ý bài tập",
        )

        if selected_student and selected_student in student_options:
            user_id = student_options[selected_student]
            # Selected student - no notification needed
            pass
        else:
            st.warning("Vui lòng chọn mã sinh viên hợp lệ")
            user_id = None

    else:
        student_code_input = st.text_input(
            "Nhập mã sinh viên (ví dụ: B21DCVT013):",
            placeholder="B21DCVT013",
            help="Nhập mã sinh viên bắt đầu bằng B và có ít nhất 8 ký tự",
        )

        user_id = None
        if student_code_input:
            for uid, token in enumerate(user_id2token):
                if uid > 0 and token == student_code_input:
                    user_id = uid
                    break

            if user_id:
                st.success(f"Tìm thấy: {student_code_input}")
            else:
                st.error(f"Không tìm thấy: {student_code_input}")

    # ========================================================================
    # Generate Recommendations
    # ========================================================================
    
    topk = st.selectbox(
        "Số lượng gợi ý bài tập:",
        options=[1, 2, 5, 10, 20],
        index=3,
        help="Chọn số lượng bài tập bạn muốn nhận gợi ý",
    )

    if st.button("Tạo gợi ý bài tập"):
        if user_id is None or user_id <= 0:
            st.error("Vui lòng chọn sinh viên trước khi tạo gợi ý")
        else:
            # Xóa giải thích cũ
            if "explanation" in st.session_state:
                del st.session_state.explanation

            try:
                with st.spinner("Đang tạo gợi ý..."):
                    recs = get_top_k_recommendations(
                        model, dataset, user_id, topk=topk
                    )
                    item_details = load_item_details()

                if input_method == "Dropdown mã sinh viên":
                    st.success(f"Top {topk} gợi ý cho {selected_student}")
                else:
                    student_code = (
                        user_id2token[user_id]
                        if user_id < len(user_id2token)
                        else f"User_{user_id}"
                    )
                    st.success(f"Top {topk} gợi ý cho {student_code}")

                # Hiển thị kết quả
                cols_per_row = 2
                for i in range(0, len(recs), cols_per_row):
                    cols = st.columns(cols_per_row)
                    for j in range(cols_per_row):
                        if i + j < len(recs):
                            item_internal_id, item_external_id, score = recs[i + j]
                            item_info = get_item_display_info(
                                item_external_id, item_details
                            )

                            with cols[j]:
                                st.markdown(
                                    f"""
                                    <div class="recommendation-card">
                                        <h4>#{i+j+1} Bài tập {item_external_id}</h4>
                                        <p style="font-weight: bold; color: #333; margin: 5px 0;">
                                            {item_info['title']}
                                        </p>
                                        <p style="color: #666; margin: 3px 0;">
                                            <strong>Chủ đề:</strong> {item_info['topic']}
                                        </p>
                                        <p style="color: #666; margin: 3px 0;">
                                            <strong>Chủ đề phụ:</strong> {item_info['sub_topic']}
                                        </p>
                                        <p style="color: #666; margin: 3px 0;">
                                            <strong>Độ khó:</strong> {item_info['difficulty']}
                                        </p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True,
                                )

                # Lưu vào session state
                st.session_state.current_recs = recs
                st.session_state.current_user = user_id
                st.session_state.current_items = item_details

                # Chi tiết kết quả
                with st.expander("Chi tiết kết quả"):
                    st.write("**Giải thích:**")
                    st.write("- **STT**: Thứ tự gợi ý (cao đến thấp)")
                    st.write("- **Mã bài tập**: Mã bài tập được gợi ý")
                    st.write("- **Tên bài tập**: Tên đầy đủ của bài tập")
                    st.write("- **Chủ đề**: Chủ đề chính của bài tập")
                    st.write("- **Chủ đề phụ**: Chủ đề phụ của bài tập")
                    st.write("- **Độ khó**: Mức độ khó của bài tập")

                    import pandas as pd

                    df_data = []
                    for i, (item_internal_id, item_external_id, score) in enumerate(
                        recs, 1
                    ):
                        item_info = get_item_display_info(
                            item_external_id, item_details
                        )
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

            except Exception as e:
                st.toast(f"❌ Lỗi: {str(e)}", icon="❌")
                st.code(str(e))

    # ========================================================================
    # AI Explainer (simplified - keeping original logic)
    # ========================================================================
    
    if LLM_AVAILABLE:
        st.subheader("Giải Thích Bằng AI")

        ai_service = st.radio(
            "Chọn dịch vụ AI:",
            ["Mistral Cloud", "Ollama (Local)"],
            horizontal=True,
            key="ai_service_selector"
        )

        if ai_service == "Mistral Cloud":
            st.markdown("#### Cấu hình Mistral AI")
            
            mistral_api_key = os.getenv("MISTRALAI_API_KEY")
            
            if mistral_api_key:
                # API key loaded - no notification needed
                pass
            else:
                st.error("Không tìm thấy MISTRALAI_API_KEY trong .env")
            
            mistral_model = st.selectbox(
                "Model:",
                ["mistral-small-latest", "mistral-medium-latest", "mistral-large-latest"],
                index=0,
                key="mistral_model"
            )

            if st.button("Tạo giải thích với Mistral", type="primary", key="mistral_explain", disabled=not mistral_api_key):
                if "current_recs" not in st.session_state or not st.session_state.current_recs:
                    st.toast("⚠️ Tạo gợi ý trước!", icon="⚠️")
                else:
                    try:
                        user_id = st.session_state.current_user
                        recs = st.session_state.current_recs
                        item_details = st.session_state.current_items

                        student_code = (
                            user_id2token[user_id]
                            if user_id < len(user_id2token)
                            else f"User_{user_id}"
                        )

                        rec_data = []
                        for item_internal_id, item_external_id, score in recs:
                            item_info = get_item_display_info(item_external_id, item_details)
                            rec_data.append({
                                "title": item_info["title"],
                                "topic": item_info["topic"],
                                "difficulty": item_info["difficulty"],
                                "score": score,
                            })

                        explainer = MistralCloudExplainer(mistral_api_key, mistral_model)

                        with st.spinner(f"Đang xử lý với {mistral_model}..."):
                            explanation = explainer.explain_recommendations(student_code, rec_data)

                        st.session_state.explanation = explanation
                        st.success("Giải thích đã được tạo")

                    except Exception as e:
                        st.error(f"Lỗi Mistral AI: {str(e)}")

        else:  # Ollama (Local)
            st.markdown("#### Cấu hình Ollama")
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
                if st.button("Test kết nối", key="global_test_connection"):
                    with st.spinner("Đang kiểm tra kết nối..."):
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

            with col_explain:
                if st.button(
                    "Tạo giải thích", type="primary", key="global_create_explanation"
                ):
                    if (
                        "current_recs" not in st.session_state
                        or not st.session_state.current_recs
                    ):
                        st.warning("Vui lòng tạo gợi ý bài tập trước")
                    else:
                        try:
                            user_id = st.session_state.current_user
                            recs = st.session_state.current_recs
                            item_details = st.session_state.current_items

                            student_code = (
                                user_id2token[user_id]
                                if user_id < len(user_id2token)
                                else f"User_{user_id}"
                            )

                            rec_data = []
                            for item_internal_id, item_external_id, score in recs:
                                item_info = get_item_display_info(
                                    item_external_id, item_details
                                )
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
                                explanation = explainer.explain_recommendations(
                                    student_code, rec_data
                                )

                            st.session_state.explanation = explanation
                            st.success("Giải thích đã được tạo")

                        except Exception as e:
                            st.error(f"Lỗi Ollama: {str(e)}")

    # ========================================================================
    # Display AI Explanation
    # ========================================================================
    
    if LLM_AVAILABLE and "explanation" in st.session_state and st.session_state.explanation:
        st.markdown("---")
        st.subheader("💬 Phân tích từ AI")
        
        # Display explanation in a nice container
        st.markdown(st.session_state.explanation)
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("🗑️ Xóa giải thích", key="clear_explanation_global"):
                del st.session_state.explanation
                st.rerun()

else:
    st.warning("Vui lòng chọn và load model trước khi sử dụng")
