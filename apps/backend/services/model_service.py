"""
Model Service - Xử lý logic load và quản lý model
"""
import os
import torch
import streamlit as st
from recbole.quick_start import load_data_and_model
from recbole.data.interaction import Interaction
from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.utils import init_seed
from recbole.model.knowledge_aware_recommender import KGCN


class ModelService:
    """Service để quản lý việc load và sử dụng model"""

    def __init__(self, model_dir, recbole_dir):
        self.model_dir = model_dir
        self.recbole_dir = recbole_dir

    def check_checkpoint_compatibility(
        self, checkpoint_path, target_dataset="cpp"
    ):
        """Kiểm tra thông tin cơ bản của checkpoint và compatibility với dataset hiện tại"""
        try:
            checkpoint = torch.load(
                checkpoint_path, map_location="cpu", weights_only=False
            )

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

            # Kiểm tra embedding size
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

    def get_compatible_checkpoints(self, target_dataset="cpp"):
        """Lấy danh sách các checkpoint tương thích với dataset hiện tại"""
        all_models = [
            f for f in os.listdir(self.recbole_dir) if f.endswith(".pth")
        ]
        compatible_models = []
        incompatible_models = []

        for model_file in all_models:
            model_path = os.path.join(self.recbole_dir, model_file)
            info = self.check_checkpoint_compatibility(model_path, target_dataset)

            if info["compatible"]:
                compatible_models.append((model_file, info))
            else:
                incompatible_models.append((model_file, info))

        return compatible_models, incompatible_models

    def load_trained_model(self, model_path, config_file="config.yaml"):
        """Load model KGCN từ checkpoint đã trained với config gốc"""
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
                st.info("🔄 Đang thử phương pháp custom...")

                # Fallback: Sử dụng config local và override state_dict
                if os.path.exists(config_file):
                    config = Config(model="KGCN", config_file_list=[config_file])

                    # Khởi tạo dataset với config local
                    init_seed(config["seed"], config["reproducibility"])
                    dataset = create_dataset(config)
                    train_data, valid_data, test_data = data_preparation(
                        config, dataset
                    )

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

    def get_top_k_recommendations(self, model, dataset, user_id, topk=10):
        """Lấy top-k recommendation cho user"""
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
                        item_external_id = item_id2token.get(
                            item_internal_id, f"Item_{item_internal_id}"
                        )
                    elif hasattr(item_id2token, "__getitem__"):
                        try:
                            item_external_id = item_id2token[item_internal_id]
                        except (IndexError, KeyError):
                            item_external_id = f"Item_{item_internal_id}"
                    else:
                        item_external_id = f"Item_{item_internal_id}"

                    score = float(topk_scores[i].item())
                    results.append((item_internal_id, item_external_id, score))

                return results

        except Exception as e:
            raise Exception(f"Lỗi trong get_top_k_recommendations: {str(e)}")
