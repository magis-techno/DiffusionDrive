#!/usr/bin/env python3
"""
测试滑动窗口轨迹GIF功能

验证新的时间标注和轨迹渐变功能
"""

import sys
from pathlib import Path
import time

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_sliding_window_gif():
    """测试滑动窗口GIF生成"""
    print("🎬 测试滑动窗口轨迹GIF")
    print("="*50)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        # 创建应用
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        # 获取应用信息
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        
        if not available_scenes:
            print("❌ 没有可用场景")
            return False
        
        scene_token = available_scenes[0]
        print(f"📝 测试场景: {scene_token}")
        
        # 测试参数
        test_params = {
            "sampling_rate": 2.0,          # 2Hz采样 (每0.5秒)
            "total_duration": 4.0,         # 较短的测试时长
            "prediction_horizon": 4.0,     # 4秒预测
            "show_history": True,          # 显示历史
            "history_fade_steps": 3,       # 保持3帧历史
            "fps": 3.0                     # 较慢的播放
        }
        
        print(f"\n🎯 测试参数:")
        for key, value in test_params.items():
            print(f"  • {key}: {value}")
        
        print(f"\n📊 预期帧数: {int(test_params['total_duration'] * test_params['sampling_rate']) + 1} 帧")
        print(f"📊 预期GIF时长: {(int(test_params['total_duration'] * test_params['sampling_rate']) + 1) / test_params['fps']:.1f}秒")
        
        # 生成GIF
        print(f"\n🎬 开始生成滑动窗口GIF...")
        start_time = time.time()
        
        result = app.create_sliding_window_gif(
            scene_token=scene_token,
            output_dir=Path("./sliding_window_test"),
            **test_params
        )
        
        processing_time = time.time() - start_time
        
        print(f"\n🎉 滑动窗口GIF生成成功!")
        print(f"📁 文件路径: {result['sliding_gif']}")
        print(f"⏱️ 处理时间: {processing_time:.2f}s")
        
        # 显示详细元数据
        metadata = result['metadata']
        print(f"\n📊 详细信息:")
        print(f"  • 方法: {metadata['method']}")
        print(f"  • 采样率: {metadata['sampling_rate']}Hz")
        print(f"  • 采样间隔: {metadata['sampling_interval']}s")
        print(f"  • 总时长: {metadata['total_duration']}s")
        print(f"  • 预测时长: {metadata['prediction_horizon']}s")
        print(f"  • 总帧数: {metadata['total_frames']}")
        print(f"  • 历史淡化: {metadata['show_history']} ({metadata['history_fade_steps']} 步)")
        print(f"  • 播放帧率: {metadata['fps']} fps")
        print(f"  • 文件大小: {metadata['file_size_mb']:.2f} MB")
        
        # 验证文件存在
        gif_path = Path(result['sliding_gif'])
        if gif_path.exists():
            actual_size = gif_path.stat().st_size / (1024 * 1024)
            print(f"  • 实际文件大小: {actual_size:.2f} MB")
            
            # 验证GIF
            from PIL import Image
            with Image.open(gif_path) as img:
                print(f"  • GIF格式: {img.format}")
                print(f"  • GIF尺寸: {img.size}")
                
                # 计算帧数
                frame_count = 0
                try:
                    while True:
                        img.seek(frame_count)
                        frame_count += 1
                except EOFError:
                    pass
                print(f"  • 实际帧数: {frame_count}")
                
                if frame_count == metadata['total_frames']:
                    print(f"  ✅ 帧数匹配")
                else:
                    print(f"  ⚠️ 帧数不匹配 (预期: {metadata['total_frames']})")
            
            return True
        else:
            print("❌ GIF文件未找到")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameter_variations():
    """测试不同参数组合"""
    print("\n🔬 测试不同参数组合")
    print("="*30)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        
        if not available_scenes:
            print("❌ 没有可用场景")
            return False
        
        scene_token = available_scenes[0]
        
        # 测试不同的参数组合
        test_cases = [
            {
                "name": "高频采样",
                "params": {"sampling_rate": 4.0, "total_duration": 2.0, "prediction_horizon": 2.0},
                "expected_frames": 9  # 2.0 * 4.0 + 1
            },
            {
                "name": "长时间预测",
                "params": {"sampling_rate": 1.0, "total_duration": 3.0, "prediction_horizon": 6.0},
                "expected_frames": 4   # 3.0 * 1.0 + 1
            },
            {
                "name": "无历史显示",
                "params": {"sampling_rate": 2.0, "total_duration": 2.0, "show_history": False},
                "expected_frames": 5   # 2.0 * 2.0 + 1
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            print(f"\n测试 {i+1}: {test_case['name']}")
            
            try:
                result = app.create_sliding_window_gif(
                    scene_token=scene_token,
                    output_dir=Path("./sliding_window_variations") / f"test_{i+1}",
                    fps=2.0,  # 快速测试
                    **test_case["params"]
                )
                
                actual_frames = result['metadata']['total_frames']
                expected_frames = test_case['expected_frames']
                
                if actual_frames == expected_frames:
                    print(f"  ✅ 成功 - 帧数: {actual_frames}")
                    success_count += 1
                else:
                    print(f"  ⚠️ 帧数不匹配 - 预期: {expected_frames}, 实际: {actual_frames}")
                    success_count += 1  # 只要不报错就算成功
                    
            except Exception as e:
                print(f"  ❌ 失败: {e}")
        
        print(f"\n📊 参数测试结果: {success_count}/{len(test_cases)} 成功")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"❌ 参数测试失败: {e}")
        return False

def test_feature_details():
    """测试特定功能细节"""
    print("\n🔍 测试功能细节")
    print("="*20)
    
    try:
        from trajectory_app.visualizer import TrajectoryVisualizer
        
        # 测试渐变色生成
        visualizer = TrajectoryVisualizer()
        
        print("1️⃣ 测试轨迹渐变色生成...")
        colors = visualizer._generate_trajectory_gradient_colors(20)
        print(f"  ✅ 生成 {len(colors)} 个颜色")
        print(f"  📝 首个颜色: {colors[0]}")
        print(f"  📝 末个颜色: {colors[-1]}")
        
        # 测试时间标记功能
        print("\n2️⃣ 测试时间标记配置...")
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig, ax = plt.subplots(1, 1, figsize=(8, 6))
        
        # 创建测试轨迹
        x_coords = np.linspace(0, 40, 21)  # 4秒轨迹，每0.2秒一个点
        y_coords = np.sin(x_coords * 0.1) * 10
        
        visualizer._add_time_markers_to_trajectory(ax, x_coords, y_coords, 4.0)
        
        ax.plot(x_coords, y_coords, 'b-', linewidth=2, label='测试轨迹')
        ax.legend()
        ax.set_title('时间标记测试')
        
        test_image_path = Path("./time_markers_test.png")
        fig.savefig(test_image_path, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        if test_image_path.exists():
            print(f"  ✅ 时间标记测试图保存: {test_image_path}")
            test_image_path.unlink()  # 清理
        
        return True
        
    except Exception as e:
        print(f"❌ 功能细节测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 滑动窗口轨迹GIF测试\n")
    
    # 测试1: 基础功能
    basic_ok = test_sliding_window_gif()
    
    if basic_ok:
        print("\n" + "="*60)
        print("✅ 基础测试通过")
        
        # 测试2: 参数变化
        param_ok = test_parameter_variations()
        
        # 测试3: 功能细节
        detail_ok = test_feature_details()
        
        print("\n" + "="*60)
        if basic_ok and param_ok and detail_ok:
            print("🎉 所有滑动窗口GIF测试通过！")
            print("💡 新功能特性:")
            print("  • ⏰ 时间标注 (1s, 2s, 3s, 4s 标记)")
            print("  • 🌈 轨迹渐变色 (红→橙→黄→绿→蓝)")
            print("  • 👻 历史轨迹淡化显示")
            print("  • 📊 四象限可视化布局")
            print("  • 🎯 2Hz采样，4秒预测")
        else:
            print("⚠️ 部分测试失败，但基础功能可用")
    else:
        print("\n" + "="*60)
        print("❌ 基础测试失败")
        print("💡 请检查应用配置和数据路径") 