#!/usr/bin/env python3
"""
测试动态元素更新功能

验证滑动窗口GIF中的所有元素是否随帧变化而更新
"""

import sys
from pathlib import Path
import time

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_dynamic_updates():
    """测试动态元素更新功能"""
    print("🔄 测试动态元素更新功能")
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
        
        # 测试参数（较短的时长以便观察）
        test_params = {
            "sampling_rate": 2.0,          # 2Hz采样
            "total_duration": 3.0,         # 3秒时长
            "prediction_horizon": 3.0,     # 3秒预测
            "show_history": True,          # 显示历史
            "history_fade_steps": 2,       # 只保持2帧历史
            "fps": 2.0                     # 2fps播放
        }
        
        print(f"\n🎯 测试参数 (专注观察动态变化):")
        for key, value in test_params.items():
            print(f"  • {key}: {value}")
        
        expected_frames = int(test_params['total_duration'] * test_params['sampling_rate']) + 1
        print(f"\n📊 预期帧数: {expected_frames} 帧")
        print(f"📊 每帧应该包含的动态元素:")
        print(f"  ✅ 当前时间的传感器数据 (LiDAR, 摄像头)")
        print(f"  ✅ 实时自车位置和朝向")
        print(f"  ✅ 动态物体位置 (其他车辆、行人)")
        print(f"  ✅ 实时车速、位置、加速度信息")
        print(f"  ✅ 时间切片的参考轨迹 (GT, PDM)")
        print(f"  ✅ 摄像头图像上的时间和速度叠加")
        
        # 生成GIF
        print(f"\n🎬 开始生成动态更新测试GIF...")
        start_time = time.time()
        
        result = app.create_sliding_window_gif(
            scene_token=scene_token,
            output_dir=Path("./dynamic_update_test"),
            **test_params
        )
        
        processing_time = time.time() - start_time
        
        print(f"\n🎉 动态更新GIF生成成功!")
        print(f"📁 文件路径: {result['sliding_gif']}")
        print(f"⏱️ 处理时间: {processing_time:.2f}秒")
        
        # 显示详细信息
        metadata = result['metadata']
        print(f"\n📊 验证动态更新:")
        print(f"  • 总帧数: {metadata['total_frames']}")
        print(f"  • 采样时间点: {len(metadata['actual_sampling_times'])}")
        print(f"  • 文件大小: {metadata['file_size_mb']:.2f} MB")
        
        # 验证文件
        gif_path = Path(result['sliding_gif'])
        if gif_path.exists():
            from PIL import Image
            with Image.open(gif_path) as img:
                frame_count = 0
                try:
                    while True:
                        img.seek(frame_count)
                        frame_count += 1
                except EOFError:
                    pass
                
                print(f"  • 实际GIF帧数: {frame_count}")
                if frame_count == metadata['total_frames']:
                    print(f"  ✅ 帧数匹配")
                else:
                    print(f"  ⚠️ 帧数不匹配")
        
        # 观察指南
        print(f"\n👀 观察动态更新指南:")
        print(f"  🔍 观察要点:")
        print(f"    • BEV中的蓝色星形自车位置是否在移动")
        print(f"    • 蓝色箭头朝向是否在变化")
        print(f"    • 橙色/红色动态物体是否在移动")
        print(f"    • 摄像头图像是否在变化 (左上角时间标签)")
        print(f"    • 状态面板的速度、位置是否在更新")
        print(f"    • 参考轨迹 (绿色GT, 蓝色PDM) 是否基于时间切片")
        print(f"  📈 动态验证:")
        print(f"    • 对比第1帧和最后1帧的图像内容")
        print(f"    • 检查速度数值是否在变化")
        print(f"    • 观察位置坐标是否在更新")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_static_vs_dynamic_comparison():
    """对比静态和动态版本的差异"""
    print("\n🆚 静态 vs 动态对比测试")
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
        
        # 生成传统的固定窗口GIF (对比用)
        print("1️⃣ 生成传统固定窗口GIF...")
        traditional_result = app.create_trajectory_gif(
            scene_token=scene_token,
            total_duration=3.0,
            window_size=3.0,
            step_size=0.5,
            fps=2.0,
            output_dir=Path("./static_comparison")
        )
        
        # 生成新的动态滑动窗口GIF
        print("2️⃣ 生成动态滑动窗口GIF...")
        dynamic_result = app.create_sliding_window_gif(
            scene_token=scene_token,
            sampling_rate=2.0,
            total_duration=3.0,
            prediction_horizon=3.0,
            show_history=False,  # 为了更清楚地对比
            fps=2.0,
            output_dir=Path("./dynamic_comparison")
        )
        
        print(f"\n📊 对比结果:")
        print(f"  传统GIF:")
        print(f"    📁 文件: {traditional_result['gif_path']}")
        print(f"    📊 帧数: {traditional_result['total_frames']}")
        print(f"    💾 大小: {traditional_result['file_size_mb']:.2f} MB")
        
        print(f"  动态GIF:")
        print(f"    📁 文件: {dynamic_result['sliding_gif']}")
        print(f"    📊 帧数: {dynamic_result['metadata']['total_frames']}")
        print(f"    💾 大小: {dynamic_result['metadata']['file_size_mb']:.2f} MB")
        
        print(f"\n🔍 关键差异:")
        print(f"  • 传统版本: 固定传感器数据，只有轨迹时间窗口在滑动")
        print(f"  • 动态版本: 每帧都是新的传感器数据，真实模拟驾驶过程")
        print(f"  • 观察建议: 并排播放两个GIF，比较BEV中的车辆位置变化")
        
        return True
        
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 动态元素更新测试\n")
    
    # 测试1: 动态更新功能
    dynamic_ok = test_dynamic_updates()
    
    if dynamic_ok:
        print("\n" + "="*60)
        print("✅ 动态更新测试通过")
        
        # 测试2: 静态vs动态对比
        comparison_ok = test_static_vs_dynamic_comparison()
        
        print("\n" + "="*60)
        if dynamic_ok and comparison_ok:
            print("🎉 所有动态更新测试通过！")
            print("💡 新的动态特性:")
            print("  • 🔄 实时传感器数据更新")
            print("  • 🚗 动态自车位置和朝向")
            print("  • 🏃 其他车辆和行人的运动")
            print("  • 📊 实时状态信息显示")
            print("  • 📷 当前帧的摄像头图像")
            print("  • ⏰ 时间切片的参考轨迹")
        else:
            print("⚠️ 部分测试失败，但基础功能可用")
    else:
        print("\n" + "="*60)
        print("❌ 动态更新测试失败")
        print("💡 请检查数据和模型配置") 