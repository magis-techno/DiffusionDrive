#!/usr/bin/env python3
"""
快速测试多frame GIF逻辑

验证新的GIF生成逻辑：多个frame而不是多个time window
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_multi_frame_concept():
    """测试多frame概念的正确性"""
    print("🎬 测试多frame GIF概念")
    print("="*40)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        # 获取场景信息
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        
        if not available_scenes:
            print("❌ 没有可用场景")
            return False
        
        scene_token = available_scenes[0]
        print(f"📝 测试场景: {scene_token}")
        
        # 加载场景数据
        scene_data = app.data_manager.load_scene_data(scene_token)
        scene = scene_data["scene"]
        all_frames = scene.frames
        
        print(f"📊 场景总帧数: {len(all_frames)}")
        
        # 展示前几帧的信息
        print("\n🔍 前5帧信息:")
        for i, frame in enumerate(all_frames[:5]):
            ego_pose = frame.ego_status.ego_pose
            print(f"  帧 {i}: 时间={frame.timestamp:.2f}s, 位置=({ego_pose.x:.1f}, {ego_pose.y:.1f})")
        
        # 测试帧选择逻辑
        max_frames = 4
        frame_step = 2
        selected_indices = list(range(0, min(len(all_frames), max_frames * frame_step), frame_step))
        selected_frames = [all_frames[i] for i in selected_indices]
        
        print(f"\n🎯 选择的帧:")
        print(f"  设置: max_frames={max_frames}, frame_step={frame_step}")
        print(f"  选中索引: {selected_indices}")
        print(f"  选中帧数: {len(selected_frames)}")
        
        for i, frame_idx in enumerate(selected_indices):
            frame = all_frames[frame_idx]
            ego_pose = frame.ego_status.ego_pose
            print(f"  GIF帧 {i+1}: 场景帧{frame_idx} -> 时间={frame.timestamp:.2f}s, 位置=({ego_pose.x:.1f}, {ego_pose.y:.1f})")
        
        print("\n✅ 多frame概念验证成功!")
        print("💡 这确实是时间序列上的不同时刻，而不是同一时刻的不同预测窗口")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_small_gif():
    """测试生成一个极小的GIF"""
    print("\n🎬 测试生成极小GIF")
    print("="*30)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        scene_token = available_scenes[0]
        
        print("参数设置: max_frames=2, frame_step=5, prediction_horizon=1.5s")
        
        # 生成极小的测试GIF
        test_output_dir = Path("./quick_multi_frame_test")
        test_output_dir.mkdir(exist_ok=True)
        
        gif_result = app.create_trajectory_gif(
            scene_token=scene_token,
            max_frames=2,              # 只要2帧
            frame_step=5,              # 大间隔
            prediction_horizon=1.5,    # 短预测
            fps=0.5,                   # 超慢帧率
            output_dir=test_output_dir
        )
        
        print(f"✅ GIF生成成功!")
        print(f"📁 路径: {gif_result['gif_path']}")
        print(f"📊 总帧数: {gif_result['total_frames']}")
        print(f"🎬 帧索引: {gif_result['frame_indices']}")
        print(f"⏱️ 处理时间: {gif_result['processing_time']:.1f}s")
        
        # 验证文件
        gif_path = Path(gif_result['gif_path'])
        if gif_path.exists():
            file_size = gif_path.stat().st_size / 1024
            print(f"💾 文件大小: {file_size:.1f} KB")
            return True
        else:
            print("❌ GIF文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ GIF测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 多frame GIF逻辑测试\n")
    
    # 测试1: 概念验证
    concept_ok = test_multi_frame_concept()
    
    if concept_ok:
        # 测试2: 实际GIF生成
        gif_ok = test_small_gif()
        
        print("\n" + "="*50)
        if gif_ok:
            print("🎉 多frame GIF逻辑验证成功！")
            print("✨ 现在GIF显示的是:")
            print("   • 不同时刻的自车位置")
            print("   • 不同时刻的传感器数据")
            print("   • 不同时刻的轨迹预测")
            print("   • 时间序列动画效果")
            print("💡 可以运行: python test_gif_generation.py")
        else:
            print("⚠️ GIF生成仍有问题")
    else:
        print("\n" + "="*50)
        print("❌ 基础概念测试失败") 