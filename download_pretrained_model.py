#!/usr/bin/env python3
"""
下载DiffusionDrive所需的预训练模型文件
"""

import os
import requests
from pathlib import Path
from huggingface_hub import hf_hub_download
import ssl
import urllib3

# 禁用SSL验证（如果需要）
ssl._create_default_https_context = ssl._create_unverified_context
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_resnet34_model():
    """下载ResNet-34预训练模型"""
    workspace_root = os.environ.get("NAVSIM_WORKSPACE_ROOT")
    if not workspace_root:
        print("ERROR: NAVSIM_WORKSPACE_ROOT environment variable not set!")
        return False
    
    bkb_dir = Path(workspace_root) / "bkb"
    bkb_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = bkb_dir / "pytorch_model.bin"
    
    if model_path.exists():
        print(f"Model already exists at {model_path}")
        # 验证文件是否有效
        try:
            import torch
            torch.load(model_path, map_location='cpu')
            print("✓ Existing model file is valid")
            return True
        except Exception as e:
            print(f"✗ Existing model file is invalid: {e}")
            print("Re-downloading...")
    
    try:
        print("Downloading ResNet-34 model from Hugging Face...")
        downloaded_path = hf_hub_download(
            repo_id="timm/resnet34.a1_in1k",
            filename="pytorch_model.bin",
            cache_dir=str(bkb_dir.parent / "hf_cache")
        )
        
        # 复制到目标位置
        import shutil
        shutil.copy2(downloaded_path, model_path)
        print(f"✓ Model downloaded successfully to {model_path}")
        
        # 验证下载的文件
        import torch
        torch.load(model_path, map_location='cpu')
        print("✓ Downloaded model file is valid")
        return True
        
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False

def download_plan_anchors():
    """下载计划锚点文件"""
    workspace_root = os.environ.get("NAVSIM_WORKSPACE_ROOT")
    if not workspace_root:
        print("ERROR: NAVSIM_WORKSPACE_ROOT environment variable not set!")
        return False
    
    anchor_dir = Path(workspace_root) / "plan_anchor"
    anchor_dir.mkdir(parents=True, exist_ok=True)
    
    anchor_path = anchor_dir / "kmeans_navsim_traj_20.npy"
    
    if anchor_path.exists():
        print(f"Anchor file already exists at {anchor_path}")
        # 验证文件是否有效
        try:
            import numpy as np
            np.load(anchor_path)
            print("✓ Existing anchor file is valid")
            return True
        except Exception as e:
            print(f"✗ Existing anchor file is invalid: {e}")
            print("Re-downloading...")
    
    try:
        print("Downloading plan anchor file...")
        url = "https://github.com/hustvl/DiffusionDrive/releases/download/DiffusionDrive_88p1_PDMS_Eval_file/kmeans_navsim_traj_20.npy"
        
        response = requests.get(url, stream=True, verify=False)
        response.raise_for_status()
        
        with open(anchor_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"✓ Anchor file downloaded successfully to {anchor_path}")
        
        # 验证下载的文件
        import numpy as np
        np.load(anchor_path)
        print("✓ Downloaded anchor file is valid")
        return True
        
    except Exception as e:
        print(f"✗ Download failed: {e}")
        return False

def main():
    print("=== DiffusionDrive Pretrained Model Downloader ===")
    
    # 检查环境变量
    workspace_root = os.environ.get("NAVSIM_WORKSPACE_ROOT")
    if not workspace_root:
        print("ERROR: Please set NAVSIM_WORKSPACE_ROOT environment variable first!")
        print("Example: export NAVSIM_WORKSPACE_ROOT=\"$HOME/navsim_workspace\"")
        return
    
    print(f"Using workspace: {workspace_root}")
    
    # 下载模型文件
    success1 = download_resnet34_model()
    success2 = download_plan_anchors()
    
    if success1 and success2:
        print("\n✓ All files downloaded successfully!")
        print("You can now run training/evaluation without network issues.")
    else:
        print("\n✗ Some downloads failed. Please check the errors above.")

if __name__ == "__main__":
    main() 