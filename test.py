# from recbole.quick_start import run_recbole

# run_recbole(model="KGCN", config_file_list=["config.yaml"])

import torch

checkpoint = torch.load(
    "E:/DoAn/RecBole/saved/KGCN-Apr-20-2025_11-17-38.pth",
    map_location="cpu",  # hoặc "cuda" nếu dùng GPU
    weights_only=False,
)
print(checkpoint.keys())
