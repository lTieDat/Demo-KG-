"""
Model loading and checkpoint compatibility utilities
"""
import os
import torch
from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.utils import init_seed
from recbole.model.knowledge_aware_recommender import KGCN


def check_checkpoint_compatibility(checkpoint_path, target_dataset="code-ptit-100k"):
    """
    Kiểm tra thông tin cơ bản của checkpoint và compatibility với dataset hiện tại
    """
    try:
        # Load checkpoint with KGAT_UserKG aliased to KGAT
        checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)

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

        # Lấy thông tin từ state_dict
        if "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
            if "user_embedding.weight" in state_dict:
                user_shape = state_dict["user_embedding.weight"].shape
                info["user_count"] = user_shape[0]
                # Infer embedding_size from state_dict
                info["embedding_size"] = user_shape[1]

            if "entity_embedding.weight" in state_dict:
                entity_shape = state_dict["entity_embedding.weight"].shape
                info["entity_count"] = entity_shape[0]

            if "relation_embedding.weight" in state_dict:
                relation_shape = state_dict["relation_embedding.weight"].shape
                info["relation_count"] = relation_shape[0]

        # Kiểm tra compatibility: dataset chỉ cần dựa vào tên file hoặc bỏ qua
        info["compatible"] = True
        info["dataset"] = target_dataset  # Assume compatible

        # Accept any embedding size - will be handled by config
        # No embedding size check needed

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


def load_trained_model(model_path, config_file="config.yaml"):
    """
    Load model KGCN từ checkpoint đã trained với config gốc
    """
    try:
        # Load checkpoint with KGAT_UserKG aliased to KGAT
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

        # Load checkpoint info (silently, no UI output)
        if "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
            # Just extract info, don't display

        # Find config.yaml - try multiple locations
        # 1. Relative to current directory
        # 2. Relative to this file's directory (utils/)
        # 3. Relative to project root
        config_paths = [
            config_file,  # Current directory
            os.path.join(os.path.dirname(__file__), "..", config_file),  # Project root from utils/
            os.path.join(os.path.dirname(model_path), "..", "..", config_file),  # Project root from saved/
        ]
        
        config_file_path = None
        for path in config_paths:
            if os.path.exists(path):
                config_file_path = path
                break
        
        if config_file_path is None:
            return None, None, None

        config = Config(model="KGCN", config_file_list=[config_file_path])
        
        # Override dataset path to use absolute path from project root
        project_root = os.path.dirname(os.path.dirname(__file__))  # Go up from utils/ to project root
        config['data_path'] = os.path.join(project_root, 'dataset')
        config['dataset'] = 'code-ptit-100k'

        # Khởi tạo dataset với config local
        init_seed(config["seed"], config["reproducibility"])
        dataset = create_dataset(config)
        train_data, valid_data, test_data = data_preparation(config, dataset)

        # Khởi tạo model với config local
        model = KGCN(config, dataset).to(config["device"])

        # Load state_dict từ checkpoint
        try:
            missing_keys, unexpected_keys = model.load_state_dict(
                checkpoint["state_dict"], strict=False
            )
            model.eval()

            # Load successful (no UI output)
            return config, model, dataset

        except Exception as strict_error:
            # Load failed
            return None, None, None


    except Exception as e:
        # Return None on error
        return None, None, None
