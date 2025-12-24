import numpy_compat
import os
import torch
from recbole.utils import init_seed, get_model
from recbole.config import Config
from recbole.data import create_dataset, data_preparation
import sys

# Patch for missing EduKGAT_D module in older checkpoints
try:
    import recbole.model.knowledge_aware_recommender.kgat as kgat_module
    # Alias the missing module to the standard KGAT module
    sys.modules['recbole.model.knowledge_aware_recommender.edukgat_d'] = kgat_module
    # Alias the missing class to the standard KGAT class
    if hasattr(kgat_module, 'KGAT'):
        setattr(kgat_module, 'EduKGAT_D', kgat_module.KGAT)
except ImportError:
    pass

def check_checkpoint_compatibility(checkpoint_path):
    """
    Check if a checkpoint file is compatible/loadable.
    
    Args:
        checkpoint_path (str): Path to the .pth file
        
    Returns:
        bool: True if compatible, False otherwise
        dict: Checkpoint info or error details
    """
    try:
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        
        info = {
            'epoch': checkpoint.get('epoch', 'Unknown'),
            'model_type': checkpoint.get('config', {}).get('model', 'Unknown'),
            'embedding_size': checkpoint.get('config', {}).get('embedding_size', 'Unknown')
        }
        return True, info
    except Exception as e:
        return False, {'error': str(e)}

def get_compatible_checkpoints(model_dir):
    """
    Get all compatible checkpoints in the directory.
    
    Args:
        model_dir (str): Directory containing model files
        
    Returns:
        tuple: (compatible_files, incompatible_files)
    """
    if not os.path.exists(model_dir):
        return [], []
        
    files = [f for f in os.listdir(model_dir) if f.endswith('.pth')]
    compatible = []
    incompatible = []
    
    for f in files:
        try:
            path = os.path.join(model_dir, f)
            # Basic verification - try to load with torch to check header
            # We don't fully load it here to save time
            checkpoint = torch.load(path, map_location='cpu')
            
            # Extract info if available
            info = {
                'epoch': checkpoint.get('epoch', 'Unknown'),
                'model_type': checkpoint.get('config', {}).get('model', 'Unknown'),
                'embedding_size': checkpoint.get('config', {}).get('embedding_size', 'Unknown')
            }
            
            compatible.append((f, info))
        except Exception as e:
            incompatible.append((f, str(e)))
            
    return compatible, incompatible

def load_trained_model(model_path, config_file=None):
    """
    Load a trained model and its dataset.
    
    Args:
        model_path (str): Path to the .pth model file
        config_file (str): Path to the config yaml file
        
    Returns:
        tuple: (model, dataset, config)
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")

    # Load checkpoint
    checkpoint = torch.load(model_path, map_location='cpu')
    
    # Load config
    saved_config = checkpoint['config']
    
    # Update config with external config file if provided
    if config_file and os.path.exists(config_file):
        # We assume RecBole's Config object can load from yaml
        # But here we might need to create a new Config and override 
        # or merge dictionaries.
        
        # Strategy: Create new config from file, then override with crucial saved params
        # or vice-versa. Best is to use the saved config but update data paths.
        
        # For simplicity, we stick to saved config but update data path if needed?
        # Actually, if we want to switch datasets (e.g. algo vs cpp), we MUST rely on the 
        # config_file passed in because the saved config has the OLD dataset path hardcoded.
        
        # Let's create a fresh config from the YAML file
        # and override model parameters from the checkpoint
        
        # Note: RecBole Config init takes (model, dataset, config_file_list)
        # We don't know the model class yet without config.
        # But we can get model name from saved config.
        model_name = saved_config['model']
        dataset_name = saved_config['dataset']
        
        # Initialize config from file
        config = Config(model=model_name, dataset=dataset_name, config_file_list=[config_file])
        
        # Merge saved_config INTO new config to preserve architecture (layers, embedding_size, etc.)
        # but KEEP the data_path, dataset and load_col from the new config file.
        # saved_config is often a RecBole Config object or a dict.
        saved_dict = getattr(saved_config, 'final_config_dict', saved_config)
        if isinstance(saved_dict, dict):
            for k, v in saved_dict.items():
                if k not in ['data_path', 'dataset', 'checkpoint_dir', 'model', 'load_col']:
                    config[k] = v
        
        # Resolve data_path to absolute to avoid CWD issues
        config_dir = os.path.dirname(os.path.abspath(config_file))
        config['data_path'] = os.path.abspath(os.path.join(config_dir, config['data_path']))
        print(f"INFO: Resolved data_path to: {config['data_path']}")
    else:
        config = saved_config

    # Init seed
    init_seed(config['seed'], config['reproducibility'])
    
    print(f"DEBUG: Final config load_col: {config['load_col']}")
    
    # Create dataset
    dataset = create_dataset(config)
    
    # Get model class
    model_class = get_model(config['model'])
    
    # Init model
    model = model_class(config, dataset).to(config['device'])
    
    # Load state dict
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    
    return model, dataset, config
