#!/usr/bin/env python3
"""
Test script for BEV semantic segmentation feature visualization

This script tests the newly implemented BEV semantic map visualization functionality.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_bev_semantic_features():
    """Test BEV semantic features visualization"""
    
    print("🎨" + "="*60)
    print("🧪 测试 BEV 语义分割特征可视化")
    print("="*60)
    
    try:
        # Import required modules
        from app import TrajectoryPredictionApp
        from feature_visualizer import FeatureVisualizer
        import matplotlib.pyplot as plt
        import numpy as np
        
        print("✅ 成功导入所有必需模块")
        
        # Initialize application
        print("\n📦 初始化轨迹预测应用...")
        
        # Create a minimal test config
        # Note: Using a minimal config to avoid dependency on environment variables
        config = {
            "model": {
                "type": "diffusiondrive",
                "checkpoint_path": None,  # Will use default/latest checkpoint
                "lr": 6e-4
            },
            "data": {
                "navsim_log_path": os.environ.get("OPENSCENE_DATA_ROOT", "/tmp") + "/navsim_logs/test",
                "sensor_blobs_path": os.environ.get("OPENSCENE_DATA_ROOT", "/tmp") + "/sensor_blobs/test",
                "cache_path": os.environ.get("NAVSIM_EXP_ROOT", "/tmp") + "/metric_cache"
            },
            "visualization": {
                "time_windows": [1.0, 3.0, 6.0],
                "save_formats": ["png"],
                "figure_sizes": {
                    "comprehensive": [20, 12],
                    "simple_bev": [10, 8]
                }
            }
        }
            
        app = TrajectoryPredictionApp(config)
        print("✅ 应用初始化成功")
        
        # Get a random scene
        print("\n🎲 获取随机测试场景...")
        random_scenes = app.get_random_scenes(n_scenes=1)
        if not random_scenes:
            raise ValueError("无法获取测试场景")
        
        test_scene = random_scenes[0]
        print(f"✅ 选择测试场景: {test_scene[:12]}...")
        
        # Predict trajectory with features
        print("\n🔮 进行轨迹预测和特征提取...")
        result = app.predict_single_scene(
            scene_token=test_scene,
            time_window=(0, 3.0),
            save_visualization=True,
            output_dir="./test_output"
        )
        print("✅ 轨迹预测完成")
        
        # Check extracted features
        print("\n🎨 检查提取的特征:")
        extracted_features = result.get("extracted_features", {})
        
        if not extracted_features:
            print("⚠️  未提取到任何特征")
            return False
            
        for feature_name, feature_data in extracted_features.items():
            print(f"  📊 {feature_name}:")
            if isinstance(feature_data, dict):
                for key, value in feature_data.items():
                    if hasattr(value, 'shape'):
                        print(f"    - {key}: {value.shape} ({value.dtype})")
                    else:
                        print(f"    - {key}: {type(value)}")
            else:
                print(f"    - 数据类型: {type(feature_data)}")
        
        # Test BEV semantic features specifically
        if "bev_semantic_map" in extracted_features:
            print("\n🎯 测试 BEV 语义分割特征:")
            semantic_data = extracted_features["bev_semantic_map"]
            
            # Test feature visualizer
            print("  📈 创建特征可视化器...")
            feature_viz = FeatureVisualizer()
            
            # Test semantic map visualization
            print("  🗺️  创建语义分割可视化...")
            fig_semantic, axes_semantic = feature_viz.visualize_bev_semantic_map(
                semantic_data["predictions"],
                confidence_map=semantic_data.get("confidence"),
                overlay_alpha=0.8,
                show_legend=True,
                title="测试 - BEV语义分割"
            )
            
            # Save the semantic visualization
            test_output_dir = Path("./test_output")
            test_output_dir.mkdir(exist_ok=True)
            semantic_save_path = test_output_dir / f"test_bev_semantic_{test_scene[:8]}.png"
            fig_semantic.savefig(semantic_save_path, dpi=300, bbox_inches='tight')
            print(f"  💾 语义分割图已保存: {semantic_save_path}")
            
            # Test comprehensive feature view
            print("  🎨 创建综合特征视图...")
            fig_comprehensive, axes_comprehensive = feature_viz.create_comprehensive_feature_view(
                extracted_features,
                save_path=test_output_dir / f"test_comprehensive_features_{test_scene[:8]}.png"
            )
            print(f"  💾 综合特征图已保存")
            
            # Display basic statistics
            predictions = semantic_data["predictions"]
            unique_classes, counts = np.unique(predictions, return_counts=True)
            total_pixels = np.sum(counts)
            
            print(f"\n📊 语义分割统计:")
            for class_id, count in zip(unique_classes, counts):
                if class_id in feature_viz.bev_semantic_classes:
                    class_info = feature_viz.bev_semantic_classes[class_id]
                    percentage = (count / total_pixels) * 100
                    print(f"    {class_info['name']} (ID {class_id}): {count:,} 像素 ({percentage:.1f}%)")
            
            print("✅ BEV语义分割特征测试成功!")
            
        else:
            print("⚠️  未找到BEV语义分割特征")
            return False
        
        # Check visualization results
        viz_info = result["visualization"]
        print(f"\n🖼️  可视化结果:")
        print(f"  📁 保存路径: {viz_info['save_path']}")
        print(f"  🎨 包含特征: {viz_info.get('has_features', False)}")
        print(f"  📊 特征类型: {viz_info.get('feature_types', [])}")
        
        print(f"\n🎉 测试完成! 检查 ./test_output 目录查看生成的可视化结果")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bev_semantic_features()
    sys.exit(0 if success else 1)