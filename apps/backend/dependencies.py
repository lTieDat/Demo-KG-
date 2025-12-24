import os

import traceback
from utils.models import load_trained_model
from item_utils import load_item_details
try:
    from recbole.utils import init_seed
except ImportError:
    pass

class ModelManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.dataset = None
            cls._instance.config = None
            cls._instance.item_details = None
            cls._instance.current_subject = None
        return cls._instance

    def _detect_subject_from_filename(self, filename: str) -> str:
        """Detect subject from model filename."""
        filename_lower = filename.lower()
        if 'algo' in filename_lower or 'ctdl' in filename_lower:
            return 'algorithm'
        elif 'cpp' in filename_lower:
            return 'cpp'
        return None

    def _get_config_file(self, subject: str) -> str:
        """Get config file path for subject."""
        base_path = os.path.dirname(__file__)
        if subject == 'algorithm':
            return os.path.join(base_path, 'config_algo.yaml')
        return os.path.join(base_path, 'config_cpp.yaml')

    def load_model(self, model_path: str):
        """Load a model from the specified path."""
        try:
            filename = os.path.basename(model_path)
            subject = self._detect_subject_from_filename(filename)
            
            # Fallback to cpp if subject not detected, or handle error
            if not subject:
                print(f"Warning: Could not detect subject from {filename}, defaulting to 'cpp'")
                subject = 'cpp'
            
            self.current_subject = subject
            config_file = self._get_config_file(subject)
            
            print(f"Loading model for subject: {subject} using config: {config_file}")
            
            # Load model and dataset
            self.model, self.dataset, self.config = load_trained_model(model_path, config_file)
            
            # Verify model was loaded successfully
            if self.model is None or self.dataset is None:
                raise Exception("Model or dataset failed to load")
            
            # Load item details for this subject
            self.item_details = load_item_details(subject)
            
            return True
        except Exception as e:
            print(f"CRITICAL ERROR loading model: {e}")
            traceback.print_exc()
            raise e

    def get_model(self):
        return self.model, self.dataset, self.config

    def get_item_details(self):
        return self.item_details

    def get_current_subject(self):
        return self.current_subject

def get_model_manager():
    return ModelManager()
