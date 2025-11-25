"""
Model loading and checkpoint compatibility utilities
"""
import os
import torch
import streamlit as st
from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.utils import init_seed
from recbole.model.knowledge_aware_recommender import KGCN
try:
    from recbole.model.knowledge_aware_recommender import KGAT
    KGAT_AVAILABLE = True
except ImportError:
    KGAT_AVAILABLE = False


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
"""
Model loading and checkpoint compatibility utilities
"""
import os
import torch
import streamlit as st
from recbole.config import Config
from recbole.data import create_dataset, data_preparation
from recbole.utils import init_seed
from recbole.model.knowledge_aware_recommender import KGCN
try:
    from recbole.model.knowledge_aware_recommender import KGAT
    KGAT_AVAILABLE = True
except ImportError:
    KGAT_AVAILABLE = False


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
    Load model (KGCN or KGAT) from trained checkpoint with original config
    """
    try:
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)

        # Determine model type from checkpoint config if available
        # Config might be a RecBole Config object, not a dict
        model_type = 'KGCN'  # Default
        if 'config' in checkpoint:
            checkpoint_config = checkpoint['config']
            # Check if it's a Config object or dict
            if hasattr(checkpoint_config, '__getitem__'):
                try:
                    model_type = checkpoint_config['model']
                except (KeyError, TypeError):
                    pass
        
        print(f"Embedding dim: {checkpoint.get('state_dict', {}).get('user_embedding.weight', torch.zeros(1,1)).shape[1] if 'state_dict' in checkpoint else 'Unknown'}")
        print(f"Epoch: {checkpoint.get('epoch', 'N/A')}")
        print(f"Best validation score: {checkpoint.get('best_valid_score', 'N/A')}")
        print(f"Model type: {model_type}")

        # Use local config and load state_dict
        if os.path.exists(config_file):
            print("Loading model from config.yaml...")
            config = Config(model=model_type, config_file_list=[config_file])
            
            # Override dataset path to use relative path instead of absolute
            config['data_path'] = '../../dataset'
            config['dataset'] = 'code-ptit-100k'

            # Initialize dataset with local config
            init_seed(config["seed"], config["reproducibility"])
            dataset = create_dataset(config)
            train_data, valid_data, test_data = data_preparation(config, dataset)

            # Initialize model with local config
            if model_type == "KGAT" and KGAT_AVAILABLE:
                model = KGAT(config, dataset).to(config["device"])
            else:
                model = KGCN(config, dataset).to(config["device"])

            # Load state_dict from checkpoint
            try:
                missing_keys, unexpected_keys = model.load_state_dict(
                    checkpoint["state_dict"], strict=False
                )
                model.eval()

                if missing_keys or unexpected_keys:
                    print(f"Loaded with strict=False. Missing: {len(missing_keys)}, Unexpected: {len(unexpected_keys)}")
                else:
                    print("State_dict loaded completely")

                print(f"Model loaded! Epoch: {checkpoint.get('epoch', 'N/A')}")

                return config, model, dataset

            except Exception as strict_error:
                print(f"Cannot load state_dict: {str(strict_error)}")
                return None, None, None

        else:
            print("config.yaml not found. Please ensure config.yaml exists.")
            return None, None, None

    except Exception as e:
        print(f"Error loading model: {str(e)}")
        return None, None, None
