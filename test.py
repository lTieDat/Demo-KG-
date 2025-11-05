# from recbole.quick_start import run_recbole

# run_recbole(model="KGCN", config_file_list=["config.yaml"])

import torch
from pathlib import Path
import os

# Use relative path instead of hard-coded absolute path
BASE_DIR = Path(__file__).parent.parent
RECBOLE_SAVED_DIR = BASE_DIR / "RecBole" / "saved"
MODEL_NAME = "KGCN-Apr-20-2025_11-17-38.pth"
MODEL_PATH = RECBOLE_SAVED_DIR / MODEL_NAME

if MODEL_PATH.exists():
    checkpoint = torch.load(
        str(MODEL_PATH),
        map_location="cpu",  # hoặc "cuda" nếu dùng GPU
        weights_only=False,
    )
    print(checkpoint.keys())
else:
    print(f"Model not found at: {MODEL_PATH}")
    print(f"Available directories: {list(RECBOLE_SAVED_DIR.parent.iterdir()) if RECBOLE_SAVED_DIR.parent.exists() else 'N/A'}")
