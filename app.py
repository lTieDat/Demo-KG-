# app.py
import streamlit as st
import os
import sys
import torch

# --- Patch torch.load để luôn weights_only=False ---
_real_torch_load = torch.load


def torch_load_compatible(*args, **kwargs):
    kwargs["weights_only"] = False
    return _real_torch_load(*args, **kwargs)


torch.load = torch_load_compatible  # override toàn cục

from recbole.quick_start import load_data_and_model
from recbole.data.interaction import Interaction
from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.utils import init_seed, init_logger
from recbole.model.knowledge_aware_recommender import KGCN

# Import utilities
from item_utils import load_item_details, get_item_display_info

# LLM Explainer (tích hợp Ollama)
try:
    from llm_explainer import LLMExplainer, OllamaExplainer, LocalLLMExplainer

    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    st.warning(
        "⚠️ LLM Explainer không available. Cài đặt thư viện: pip install openai requests"
    )

# Thư mục chứa model
MODEL_DIR = r"saved"  # Thư mục model local
RECBOLE_MODEL_DIR = r"E:\DoAn\RecBole\saved"  # Thư mục model RecBole gốc
sys.path.append(r"E:\DoAn\RecBole")


# Hàm kiểm tra compatibility của checkpoint
def check_checkpoint_compatibility(checkpoint_path, target_dataset="code-ptit-100k"):
    """
    Kiểm tra thông tin cơ bản của checkpoint và compatibility với dataset hiện tại
    """
    try:
        checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)

        info = {
            "filename": os.path.basename(checkpoint_path),
            "epoch": checkpoint.get("epoch", "N/A"),
            "score": checkpoint.get("best_valid_score", "N/A"),
            "dataset": "Unknown",
            "embedding_size": "Unknown",
            "user_count": "Unknown",
            "entity_count": "Unknown",
            "relation_count": "Unknown",
            "compatible": False,
            "compatibility_issues": [],
        }

        # Lấy thông tin từ config
        if "config" in checkpoint:
            config = checkpoint["config"]
            if hasattr(config, "final_config_dict"):
                config_dict = config.final_config_dict
            else:
                config_dict = dict(config) if hasattr(config, "__iter__") else {}

            info["dataset"] = config_dict.get("dataset", "Unknown")
            info["embedding_size"] = config_dict.get("embedding_size", "Unknown")

        # Lấy thông tin từ state_dict
        if "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
            if "user_embedding.weight" in state_dict:
                user_shape = state_dict["user_embedding.weight"].shape
                info["user_count"] = user_shape[0]

            if "entity_embedding.weight" in state_dict:
                entity_shape = state_dict["entity_embedding.weight"].shape
                info["entity_count"] = entity_shape[0]

            if "relation_embedding.weight" in state_dict:
                relation_shape = state_dict["relation_embedding.weight"].shape
                info["relation_count"] = relation_shape[0]

        # Kiểm tra compatibility với dataset target
        if info["dataset"] == target_dataset:
            info["compatible"] = True
        else:
            info["compatibility_issues"].append(
                f"Dataset mismatch: {info['dataset']} != {target_dataset}"
            )

        # Kiểm tra embedding size (nếu config hiện tại có embedding_size=32)
        if info["embedding_size"] != "Unknown" and info["embedding_size"] != 32:
            info["compatibility_issues"].append(
                f"Embedding size mismatch: {info['embedding_size']} != 32"
            )
            info["compatible"] = False

        return info

    except Exception as e:
        return {
            "filename": os.path.basename(checkpoint_path),
            "error": str(e),
            "compatible": False,
            "compatibility_issues": [f"Error loading: {str(e)}"],
        }


def get_compatible_checkpoints(checkpoint_dir, target_dataset="code-ptit-100k"):
    """
    Lấy danh sách các checkpoint tương thích với dataset hiện tại
    """
    all_models = [f for f in os.listdir(checkpoint_dir) if f.endswith(".pth")]
    compatible_models = []
    incompatible_models = []

    for model_file in all_models:
        model_path = os.path.join(checkpoint_dir, model_file)
        info = check_checkpoint_compatibility(model_path, target_dataset)

        if info["compatible"]:
            compatible_models.append((model_file, info))
        else:
            incompatible_models.append((model_file, info))

    return compatible_models, incompatible_models


# Hàm load model từ checkpoint
def load_trained_model(model_path, config_file="config.yaml"):
    """
    Load model KGCN từ checkpoint đã trained với config gốc
    """
    try:
        # Load checkpoint để lấy thông tin
        checkpoint = torch.load(model_path, map_location="cpu")

        # Hiển thị thông tin checkpoint
        if "config" in checkpoint:
            original_config = checkpoint["config"]
            if hasattr(original_config, "final_config_dict"):
                config_dict = original_config.final_config_dict
            else:
                config_dict = (
                    dict(original_config)
                    if hasattr(original_config, "__iter__")
                    else {}
                )

            dataset_name = config_dict.get("dataset", "Unknown")
            embedding_size = config_dict.get("embedding_size", "Unknown")
            st.info(f"📋 Dataset gốc: {dataset_name}")
            st.info(f"🔧 Embedding dim: {embedding_size}")

        # Thử sử dụng RecBole's load_data_and_model trước
        try:
            st.info("🔄 Đang load model bằng RecBole's method...")
            config, model, dataset, train_data, valid_data, test_data = (
                load_data_and_model(model_path)
            )

            st.success(
                f"✅ Đã load model thành công! Epoch: {checkpoint.get('epoch', 'N/A')}"
            )
            st.info(
                f"📊 Best validation score: {checkpoint.get('best_valid_score', 'N/A')}"
            )

            return config, model, dataset

        except Exception as recbole_error:
            st.warning(f"⚠️ RecBole method failed: {str(recbole_error)}")
            st.info("� Đang thử phương pháp custom...")

            # Fallback: Sử dụng config local và override state_dict
            if os.path.exists(config_file):
                config = Config(model="KGCN", config_file_list=[config_file])

                # Khởi tạo dataset với config local
                init_seed(config["seed"], config["reproducibility"])
                dataset = create_dataset(config)
                train_data, valid_data, test_data = data_preparation(config, dataset)

                # Khởi tạo model với config local
                model = KGCN(config, dataset).to(config["device"])

                # Thử load state_dict từ checkpoint
                try:
                    model.load_state_dict(checkpoint["state_dict"], strict=False)
                    model.eval()

                    st.warning(
                        "⚠️ Loaded với strict=False (có thể một số weights không match)"
                    )
                    st.success(
                        f"✅ Model loaded! Epoch: {checkpoint.get('epoch', 'N/A')}"
                    )
                    st.info(
                        f"📊 Best validation score: {checkpoint.get('best_valid_score', 'N/A')}"
                    )

                    return config, model, dataset

                except Exception as strict_error:
                    st.error(f"❌ Không thể load state_dict: {str(strict_error)}")
                    return None, None, None

            else:
                st.error(
                    "❌ Không tìm thấy config.yaml và không thể load từ checkpoint"
                )
                return None, None, None

    except Exception as e:
        st.error(f"❌ Lỗi khi load model: {str(e)}")
        return None, None, None


# Hàm load model cũ (backup)
def load_model_old(model_path):
    config, model, dataset, train_data, valid_data, test_data = load_data_and_model(
        model_path
    )
    return config, model, dataset


# Hàm lấy top-k recommendation
def get_top_k_recommendations(model, dataset, user_id, topk=10):
    """
    Lấy top-k recommendation cho user
    """
    try:
        model.eval()
        uid_field = dataset.uid_field
        iid_field = dataset.iid_field

        # Kiểm tra user_id hợp lệ
        if user_id >= dataset.user_num or user_id < 0:
            raise ValueError(
                f"User ID {user_id} không hợp lệ. Phải trong khoảng 0-{dataset.user_num-1}"
            )

        # Tạo input cho user
        user_inter = Interaction({uid_field: torch.tensor([user_id])})

        with torch.no_grad():
            scores = model.full_sort_predict(
                user_inter.to(model.device)
            )  # [1, num_items]
            scores = scores.view(-1)

            # Lấy top-k items
            topk_scores, topk_iids = torch.topk(scores, min(topk, len(scores)))

            # Convert về tên item nếu có mapping
            item_id2token = dataset.field2id_token[iid_field]

            results = []
            for i, iid in enumerate(topk_iids):
                item_internal_id = int(iid.item())

                # Xử lý item_id2token có thể là dict hoặc array
                if hasattr(item_id2token, "get"):
                    # Nếu là dictionary
                    item_external_id = item_id2token.get(
                        item_internal_id, f"Item_{item_internal_id}"
                    )
                elif hasattr(item_id2token, "__getitem__"):
                    # Nếu là array/list
                    try:
                        item_external_id = item_id2token[item_internal_id]
                    except (IndexError, KeyError):
                        item_external_id = f"Item_{item_internal_id}"
                else:
                    # Fallback
                    item_external_id = f"Item_{item_internal_id}"

                score = float(topk_scores[i].item())
                results.append((item_internal_id, item_external_id, score))

            return results

    except Exception as e:
        raise Exception(f"Lỗi trong get_top_k_recommendations: {str(e)}")


# ---------------- UI ----------------
st.title("🎯 Hệ thống gợi ý bài tập KGCN")
st.markdown(
    "*Sử dụng Knowledge Graph Convolutional Network để gợi ý bài tập cho sinh viên*"
)

# Tùy chọn load model
st.sidebar.header("⚙️ Cấu hình Model")
load_method = st.sidebar.radio(
    "Chọn phương thức load model:", ["Từ checkpoint (mới)", "Từ RecBole (cũ)"]
)

if load_method == "Từ checkpoint (mới)":
    # Lấy danh sách model tương thích và không tương thích
    compatible_models, incompatible_models = get_compatible_checkpoints(
        RECBOLE_MODEL_DIR
    )

    if compatible_models:
        st.sidebar.success(f"✅ {len(compatible_models)} model tương thích")

        # Tạo options cho selectbox với thông tin chi tiết
        model_options = []
        model_info_dict = {}

        for model_file, info in compatible_models:
            display_name = f"{model_file}"
            model_options.append(display_name)
            model_info_dict[display_name] = (model_file, info)

        selected_model = st.sidebar.selectbox("Chọn model tương thích:", model_options)

        if selected_model:
            model_file, info = model_info_dict[selected_model]
            model_path = os.path.join(RECBOLE_MODEL_DIR, model_file)

            # Hiển thị thông tin checkpoint
            with st.sidebar.expander("📋 Thông tin Checkpoint"):
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

        # Hiển thị thông tin về model không tương thích nếu có
        if incompatible_models:
            with st.sidebar.expander(
                f"⚠️ {len(incompatible_models)} model không tương thích"
            ):
                for model_file, info in incompatible_models:
                    st.write(f"**{model_file}**")
                    if "compatibility_issues" in info:
                        for issue in info["compatibility_issues"]:
                            st.write(f"  - {issue}")
                    st.write("---")
    else:
        st.sidebar.error("❌ Không có model nào tương thích với dataset hiện tại!")
        st.sidebar.write("Dataset yêu cầu: code-ptit-100k, embedding_size=64")

        # Hiển thị danh sách tất cả model để debug
        all_models = [f for f in os.listdir(RECBOLE_MODEL_DIR) if f.endswith(".pth")]
        if all_models:
            with st.sidebar.expander("📋 Tất cả model có sẵn"):
                for model_file in all_models:
                    model_path = os.path.join(RECBOLE_MODEL_DIR, model_file)
                    info = check_checkpoint_compatibility(model_path, "code-ptit-100k")
                    st.write(f"**{model_file}**")
                    if "compatibility_issues" in info:
                        for issue in info["compatibility_issues"]:
                            st.write(f"  - {issue}")
                    st.write("---")

        st.stop()

    # Load model
    config, model, dataset = load_trained_model(model_path)
else:
    # Chọn model từ thư mục local
    models = [f for f in os.listdir(MODEL_DIR) if f.endswith(".pth")]
    if not models:
        st.sidebar.warning("⚠️ Không tìm thấy model nào trong thư mục saved/")
        st.stop()

    selected_model = st.sidebar.selectbox("Chọn model:", models)
    model_path = os.path.join(MODEL_DIR, selected_model)

    if selected_model:
        config, model, dataset = load_model_old(model_path)

# Giao diện prediction
if (
    "config" in locals()
    and config is not None
    and model is not None
    and dataset is not None
):
    # Lấy danh sách mã sinh viên
    uid_field = dataset.uid_field
    user_id2token = dataset.field2id_token[uid_field]

    # Tạo dictionary mapping từ mã sinh viên sang user_id (bỏ qua [PAD] và lọc mã sinh viên hợp lệ)
    student_options = {}
    for user_id in range(1, len(user_id2token)):  # Bỏ qua user_id=0 ([PAD])
        student_code = user_id2token[user_id]
        # Chỉ lấy các mã sinh viên có định dạng hợp lệ (bắt đầu bằng B và có ít nhất 8 ký tự)
        if (
            isinstance(student_code, str)
            and student_code.startswith("B")
            and len(student_code) >= 8
        ):
            student_options[student_code] = user_id

    # Sắp xếp theo mã sinh viên
    sorted_student_codes = sorted(student_options.keys())

    # Hiển thị thông tin dataset trong sidebar
    st.sidebar.header("📊 Thông tin Dataset")
    st.sidebar.metric("Tổng số user", f"{dataset.user_num:,}")
    st.sidebar.metric("Số sinh viên hợp lệ", f"{len(student_options):,}")
    st.sidebar.metric("Số bài tập", f"{dataset.item_num:,}")

    # Phân tích thống kê mã sinh viên
    year_stats = {}
    major_stats = {}
    for code in sorted_student_codes:
        # Năm (B23, B24, etc.)
        if len(code) >= 3:
            year = code[:3]
            year_stats[year] = year_stats.get(year, 0) + 1

        # Ngành (DCCN, DCPT, etc.)
        if len(code) >= 7:
            major = code[3:7]
            major_stats[major] = major_stats.get(major, 0) + 1

    with st.sidebar.expander("📈 Thống kê chi tiết"):
        st.write("**Theo năm:**")
        for year, count in sorted(year_stats.items()):
            st.write(f"- {year}: {count} sinh viên")

        st.write("**Theo ngành (top 5):**")
        top_majors = sorted(major_stats.items(), key=lambda x: x[1], reverse=True)[:5]
        for major, count in top_majors:
            st.write(f"- {major}: {count} sinh viên")

    st.subheader("🎓 Chọn sinh viên")

    # Tùy chọn nhập liệu
    input_method = st.radio(
        "Phương thức chọn sinh viên:", ["Dropdown mã sinh viên", "Nhập User ID"]
    )

    if input_method == "Dropdown mã sinh viên":
        # Tìm kiếm sinh viên
        search_term = st.text_input(
            "🔍 Tìm kiếm mã sinh viên (tùy chọn):",
            placeholder="Nhập mã sinh viên để tìm kiếm nhanh...",
            help="Nhập một phần mã sinh viên để lọc danh sách",
        )

        # Lọc danh sách nếu có tìm kiếm
        if search_term:
            filtered_codes = [
                code
                for code in sorted_student_codes
                if search_term.upper() in code.upper()
            ]
            if filtered_codes:
                display_codes = filtered_codes
                st.success(f"🎯 Tìm thấy {len(filtered_codes)} sinh viên phù hợp")
            else:
                st.warning(
                    f"⚠️ Không tìm thấy sinh viên nào với từ khóa '{search_term}'"
                )
                display_codes = sorted_student_codes
        else:
            display_codes = sorted_student_codes

        # Dropdown chọn mã sinh viên
        selected_student = st.selectbox(
            f"Chọn mã sinh viên ({len(display_codes)} sinh viên):",
            options=display_codes,
            index=0 if display_codes else None,
            help="Chọn mã sinh viên để xem gợi ý bài tập",
        )

        if selected_student and selected_student in student_options:
            user_id = student_options[selected_student]
            st.info(f"📋 Mã sinh viên: **{selected_student}** (User ID: {user_id})")
        else:
            st.warning("⚠️ Vui lòng chọn mã sinh viên hợp lệ")
            user_id = None

    else:
        # Input mã sinh viên dạng string
        student_code_input = st.text_input(
            "Nhập mã sinh viên (ví dụ: B21DCVT013):",
            placeholder="B21DCVT013",
            help="Nhập mã sinh viên bắt đầu bằng B và có ít nhất 8 ký tự",
        )

        user_id = None
        if student_code_input:
            # Tìm user_id từ mã sinh viên
            for uid, token in enumerate(user_id2token):
                if uid > 0 and token == student_code_input:  # Bỏ qua [PAD] tại index 0
                    user_id = uid
                    break

            if user_id:
                st.success(
                    f"✅ Tìm thấy sinh viên: **{student_code_input}** (User ID: {user_id})"
                )
            else:
                st.error(f"❌ Không tìm thấy mã sinh viên: **{student_code_input}**")
                st.info(
                    "💡 Gợi ý: Hãy thử nhập chính xác mã sinh viên từ danh sách hoặc sử dụng chế độ Dropdown"
                )

    # Chọn số lượng recommendation
    topk = st.selectbox(
        "Số lượng gợi ý bài tập:",
        options=[1, 2, 5, 10, 20],
        index=3,  # Mặc định chọn 10
        help="Chọn số lượng bài tập bạn muốn nhận gợi ý",
    )

    if st.button("🎯 Tạo gợi ý bài tập"):
        if user_id is None or user_id <= 0:
            st.error("❌ Vui lòng chọn sinh viên hợp lệ trước khi tạo gợi ý!")
        else:
            # Xóa giải thích cũ khi tạo gợi ý mới
            if "explanation" in st.session_state:
                del st.session_state.explanation

            try:
                with st.spinner("Đang tạo gợi ý..."):
                    recs = get_top_k_recommendations(model, dataset, user_id, topk=topk)

                    # Load thông tin chi tiết về bài tập từ file local
                    item_details = load_item_details()

                if input_method == "Dropdown mã sinh viên":
                    st.success(
                        f"✅ Top {topk} gợi ý bài tập cho sinh viên **{selected_student}**:"
                    )
                else:
                    student_code = (
                        user_id2token[user_id]
                        if user_id < len(user_id2token)
                        else f"User_{user_id}"
                    )
                    st.success(
                        f"✅ Top {topk} gợi ý bài tập cho **{student_code}** (ID: {user_id}):"
                    )

                # Hiển thị kết quả dưới dạng cards
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
                                # Tạo card cho mỗi bài tập
                                with st.container():
                                    st.markdown(
                                        f"""
                                    <div style="
                                        border: 1px solid #ddd;
                                        border-radius: 10px;
                                        padding: 15px;
                                        margin: 10px 0;
                                        background-color: #f9f9f9;
                                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                                    ">
                                        <h4 style="color: #1f77b4; margin-top: 0;">#{i+j+1} Bài tập {item_external_id}</h4>
                                        <p style="font-weight: bold; color: #333; margin: 5px 0;">
                                            📝 {item_info['title']}
                                        </p>
                                        <p style="color: #666; margin: 3px 0;">
                                            🏷️ <strong>Chủ đề:</strong> {item_info['topic']}
                                        </p>
                                        <p style="color: #666; margin: 3px 0;">
                                            🔖 <strong>Chủ đề phụ:</strong> {item_info['sub_topic']}
                                        </p>
                                        <p style="color: #666; margin: 3px 0;">
                                            ⭐ <strong>Độ khó:</strong> {item_info['difficulty']}
                                        </p>
                                    </div>
                                    """,
                                        unsafe_allow_html=True,
                                    )

                # Lưu kết quả vào session state để tránh mất dữ liệu
                if "current_recs" not in st.session_state:
                    st.session_state.current_recs = recs
                    st.session_state.current_user = user_id
                    st.session_state.current_items = item_details
                else:
                    st.session_state.current_recs = recs
                    st.session_state.current_user = user_id
                    st.session_state.current_items = item_details

                # Hiển thị thông tin chi tiết trong expander
                with st.expander("📊 Chi tiết kết quả"):
                    st.write("**Giải thích:**")
                    st.write("- **STT**: Thứ tự gợi ý (cao đến thấp)")
                    st.write("- **Mã bài tập**: Mã bài tập được gợi ý")
                    st.write("- **Tên bài tập**: Tên đầy đủ của bài tập")
                    st.write("- **Chủ đề**: Chủ đề chính của bài tập")
                    st.write("- **Chủ đề phụ**: Chủ đề phụ của bài tập")
                    st.write("- **Độ khó**: Mức độ khó của bài tập")

                    # Hiển thị bảng tóm tắt
                    st.write("**Bảng tóm tắt:**")
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
                    st.dataframe(df, width="stretch", hide_index=True)

            except Exception as e:
                st.error(f"❌ Lỗi khi tạo gợi ý: {str(e)}")
                st.error("Chi tiết lỗi:")
                st.code(str(e))

# ===== GIAO DIỆN OLLAMA (LUÔN HIỂN THỊ) =====
if LLM_AVAILABLE:
    st.subheader("🤖 Giải Thích Bằng AI (Ollama)")

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

    # Test connection và Create explanation
    col_test, col_explain = st.columns(2)

    with col_test:
        if st.button("🔍 Test kết nối", key="global_test_connection"):
            try:
                import requests

                response = requests.get(f"{base_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m["name"] for m in models]
                    if model_names:
                        st.success(f"✅ Models: {', '.join(model_names)}")
                    else:
                        st.warning("⚠️ Chưa có model. Chạy: `ollama pull mistral`")
                else:
                    st.error("❌ Server không phản hồi")
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")
                st.info("💡 Chạy: `ollama serve`")

    with col_explain:
        if st.button(
            "🤖 Tạo giải thích", type="primary", key="global_create_explanation"
        ):
            # Kiểm tra có kết quả gợi ý không
            if (
                "current_recs" not in st.session_state
                or not st.session_state.current_recs
            ):
                st.error("❌ Vui lòng tạo gợi ý bài tập trước!")
            else:
                try:
                    # Sử dụng dữ liệu từ session_state
                    user_id = st.session_state.current_user
                    recs = st.session_state.current_recs
                    item_details = st.session_state.current_items

                    # Chuẩn bị dữ liệu
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

                    # Lưu explanation vào session_state
                    st.session_state.explanation = explanation
                    st.success("✅ Giải thích đã được tạo! Xem bên dưới.")

                except Exception as e:
                    st.error(f"Lỗi Ollama: {str(e)}")
                    st.info("💡 Thử: `ollama serve` và `ollama pull mistral`")

# ===== HIỂN THỊ GIẢI THÍCH TỪ SESSION STATE =====
if LLM_AVAILABLE and "explanation" in st.session_state and st.session_state.explanation:
    st.subheader("💡 Giải Thích Từ AI")

    # Hiển thị đơn giản với st.info để đảm bảo màu text đúng
    st.info("🤖 **Phân tích từ AI:**")
    
    # Sử dụng st.text_area để hiển thị đầy đủ và có màu text rõ ràng
    st.text_area(
        label="",
        value=st.session_state.explanation,
        height=200,
        disabled=True,
        label_visibility="collapsed"
    )

    # Nút xóa giải thích
    if st.button("🗑️ Xóa giải thích", key="clear_explanation_global"):
        del st.session_state.explanation
        st.rerun()

else:
    st.warning("⚠️ Vui lòng chọn và load model trước khi sử dụng")
