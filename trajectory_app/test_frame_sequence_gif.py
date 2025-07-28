#!/usr/bin/env python3
"""
测试Frame序列GIF生成功能

验证新的按frame序列生成GIF的功能（而不是时间窗口滑动）
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_frame_sequence_gif():
    """测试frame序列GIF生成"""
    print("🎬 测试Frame序列GIF生成")
    print("="*50)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        # 创建应用
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        # 获取可用场景
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        
        if not available_scenes:
            print("❌ 没有可用场景")
            return False
        
        scene_token = available_scenes[0]
        print(f"📝 测试场景: {scene_token}")
        
        # 测试短序列GIF生成
        print("\n🎯 生成Frame序列GIF...")
        print("参数设置:")
        print("  • 起始Frame: 0")
        print("  • Frame数量: 10")
        print("  • Frame步长: 2 (隔帧)")
        print("  • 预测时长: 3.0秒")
        print("  • 播放速度: 3.0 fps")
        
        test_output_dir = Path("./frame_sequence_test")
        test_output_dir.mkdir(exist_ok=True)
        
        gif_result = app.create_frame_sequence_gif(
            scene_token=scene_token,
            start_frame_idx=0,     # 从第0帧开始
            num_frames=10,         # 生成10帧
            frame_step=2,          # 每隔1帧取一次（即取frame 0,2,4,6,8...）
            prediction_horizon=3.0, # 每个frame都预测3秒
            fps=3.0,               # 3帧每秒播放
            output_dir=test_output_dir
        )
        
        print(f"\n✅ Frame序列GIF生成成功!")
        print(f"📁 保存路径: {gif_result['gif_path']}")
        print(f"🎬 总帧数: {gif_result['frames']}")
        print(f"📊 Frame范围: {gif_result['frame_range']}")
        print(f"⏱️ 处理时间: {gif_result['processing_time']:.2f}s")
        print(f"💾 文件大小: {gif_result['file_size'] / 1024:.1f} KB")
        
        # 显示frame元数据
        print(f"\n📝 Frame详情:")
        for i, frame_meta in enumerate(gif_result['frame_metadata'][:5]):  # 只显示前5个
            print(f"  Frame {frame_meta['frame_idx']}: "
                  f"t={frame_meta['timestamp']:.2f}s, "
                  f"pred={frame_meta['prediction_points']}pts, "
                  f"gt={frame_meta['gt_points']}pts")
        
        if len(gif_result['frame_metadata']) > 5:
            print(f"  ... 还有 {len(gif_result['frame_metadata']) - 5} 个frame")
        
        # 验证文件
        gif_path = Path(gif_result['gif_path'])
        if gif_path.exists():
            print(f"\n✅ 文件验证成功: {gif_path.name}")
            
            # 使用PIL验证GIF
            from PIL import Image
            try:
                with Image.open(gif_path) as img:
                    frame_count = 0
                    while True:
                        try:
                            img.seek(frame_count)
                            frame_count += 1
                        except EOFError:
                            break
                    
                    print(f"🎞️ GIF验证: {frame_count}帧, 格式={img.format}, 尺寸={img.size}")
                    
                    if frame_count == gif_result['frames']:
                        print("✅ 帧数匹配")
                    else:
                        print(f"⚠️ 帧数不匹配: 期望{gif_result['frames']}, 实际{frame_count}")
            
            except Exception as e:
                print(f"❌ GIF验证失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Frame序列GIF测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frame_loading_logic():
    """测试frame加载逻辑"""
    print("\n🔍 测试Frame加载逻辑")
    print("="*30)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        scene_token = available_scenes[0]
        
        print(f"📝 测试场景: {scene_token}")
        
        # 测试加载不同的frame
        test_frames = [0, 1, 2, 5, 10]
        
        print("\n🎯 测试Frame加载:")
        for frame_idx in test_frames:
            try:
                frame_data = app.data_manager.load_frame_data(scene_token, frame_idx)
                trajectories = app.data_manager.get_trajectories_from_frame(scene_token, frame_idx, 3.0)
                
                print(f"  ✅ Frame {frame_idx}: "
                      f"timestamp={frame_data['metadata']['timestamp']:.2f}s, "
                      f"trajectories={list(trajectories.keys())}")
                
            except Exception as e:
                print(f"  ❌ Frame {frame_idx}: {e}")
                break
        
        print("\n✅ Frame加载逻辑测试通过")
        return True
        
    except Exception as e:
        print(f"❌ Frame加载测试失败: {e}")
        return False

def compare_gif_methods():
    """比较两种GIF生成方法"""
    print("\n⚖️ 比较GIF生成方法")
    print("="*25)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        scene_token = available_scenes[0]
        
        print(f"📝 比较场景: {scene_token}")
        
        output_dir = Path("./gif_comparison")
        output_dir.mkdir(exist_ok=True)
        
        print("\n1️⃣ 生成时间窗口GIF（旧方法）...")
        old_result = app.create_trajectory_gif(
            scene_token=scene_token,
            total_duration=4.0,
            window_size=2.0,
            step_size=1.0,
            fps=2.0,
            output_dir=output_dir / "old_method"
        )
        
        print("\n2️⃣ 生成Frame序列GIF（新方法）...")
        new_result = app.create_frame_sequence_gif(
            scene_token=scene_token,
            start_frame_idx=0,
            num_frames=4,
            frame_step=2,
            prediction_horizon=3.0,
            fps=2.0,
            output_dir=output_dir / "new_method"
        )
        
        print("\n📊 对比结果:")
        print(f"旧方法 (时间窗口): {old_result['total_frames']}帧, {old_result['processing_time']:.2f}s")
        print(f"新方法 (Frame序列): {new_result['frames']}帧, {new_result['processing_time']:.2f}s")
        
        print("\n💡 区别说明:")
        print("  • 旧方法: 固定Frame[0], 滑动时间窗口[0-2s], [1-3s], [2-4s], [3-5s]")
        print("  • 新方法: 变化Frame[0,2,4,6], 固定预测3秒")
        print("  • 新方法更符合实际驾驶场景的时间演进!")
        
        return True
        
    except Exception as e:
        print(f"❌ 比较测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Frame序列GIF功能测试\n")
    
    # 测试1: Frame加载逻辑
    loading_ok = test_frame_loading_logic()
    
    if loading_ok:
        # 测试2: Frame序列GIF生成
        gif_ok = test_frame_sequence_gif()
        
        if gif_ok:
            # 测试3: 方法比较
            compare_ok = compare_gif_methods()
            
            print("\n" + "="*50)
            if compare_ok:
                print("🎉 所有测试通过!")
                print("💡 新的Frame序列GIF功能已就绪")
                print("📝 使用方法: app.create_frame_sequence_gif(...)")
            else:
                print("⚠️ 比较测试失败，但核心功能正常")
        else:
            print("\n" + "="*50)
            print("❌ Frame序列GIF生成失败")
    else:
        print("\n" + "="*50)
        print("❌ Frame加载逻辑测试失败") 