import os
import sys
from typing import Optional, Tuple, Any

# NumPy 2.0 compatibility patch
import numpy_compat

# Add current directory to sys.path to allow imports from utils, etc.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.models import load_trained_model
from item_utils import load_item_details

class ModelManager:
    _instance = None
    
    def __init__(self):
        self.config = None
        self.model = None
        self.dataset = None
        self.item_details = None
        self.current_model_path = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load_model(self, model_path: str) -> bool:
        try:
            # Check if already loaded
            if self.current_model_path == model_path and self.model is not None:
                return True
                
            print(f"Loading model from {model_path}...")
            config, model, dataset = load_trained_model(model_path, config_file="config.yaml")
            
            if model is not None:
                self.config = config
                self.model = model
                self.dataset = dataset
                self.current_model_path = model_path
                
                # Load item details if not loaded
                if self.item_details is None:
                    self.item_details = load_item_details()
                    
                return True
            return False
        except Exception as e:
            print(f"Error loading model: {e}")
            return False

    def get_model_components(self) -> Tuple[Any, Any, Any, Any]:
        return self.config, self.model, self.dataset, self.item_details

model_manager = ModelManager.get_instance()

def get_model_manager():
    return model_manager
