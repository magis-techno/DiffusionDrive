#!/usr/bin/env python3
"""
测试ego_pose修复

验证numpy数组访问问题是否已解决
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_ego_pose_access():
    """测试ego_pose数据访问"""
    print("🔍 测试ego_pose数据访问")
    print("="*40)
    
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
        print(f"📝 测试场景: {scene_token}")
        
        # 测试frame数据加载
        print("\n1️⃣ 测试Frame数据加载...")
        frame_data = app.data_manager.load_frame_data(scene_token, 0)
        
        print(f"  ✅ Frame 0数据加载成功")
        print(f"  📊 Frame索引: {frame_data['frame_idx']}")
        print(f"  ⏰ 时间戳: {frame_data['metadata']['timestamp']:.2f}s")
        
        # 检查ego_pose数据类型
        ego_pose = frame_data['map']['ego_pose']
        print(f"  🎯 ego_pose类型: {type(ego_pose)}")
        print(f"  📐 ego_pose形状: {ego_pose.shape if hasattr(ego_pose, 'shape') else 'No shape'}")
        print(f"  📍 ego_pose值: [{ego_pose[0]:.2f}, {ego_pose[1]:.2f}, {ego_pose[2]:.2f}]")
        
        # 测试轨迹提取
        print("\n2️⃣ 测试轨迹提取...")
        trajectories = app.data_manager.get_trajectories_from_frame(scene_token, 0, 3.0)
        
        print(f"  ✅ 轨迹提取成功")
        print(f"  📊 可用轨迹: {list(trajectories.keys())}")
        
        # 检查metric cache状态
        if app.data_manager.metric_cache_loader:
            print(f"  🗄️ 找到metric cache，包含 {len(app.data_manager.metric_cache_loader.tokens)} 个场景")
        else:
            print(f"  ⚠️ 未找到metric cache")
        
        for traj_name, trajectory in trajectories.items():
            if trajectory is not None:
                print(f"  📝 {traj_name}: {trajectory.shape} - [{trajectory[0, 0]:.2f}, {trajectory[0, 1]:.2f}, {trajectory[0, 2]:.2f}]")
            else:
                print(f"  📝 {traj_name}: None")
        
        return True
        
    except Exception as e:
        print(f"❌ ego_pose访问测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frame_sequence_generation():
    """测试Frame序列生成"""
    print("\n🎬 测试Frame序列生成")
    print("="*30)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        scene_token = available_scenes[0]
        
        print(f"📝 测试场景: {scene_token}")
        
        # 测试处理单个frame
        print("\n🎯 测试处理单个Frame...")
        
        frame_data = app.data_manager.load_frame_data(scene_token, 0)
        existing_trajectories = app.data_manager.get_trajectories_from_frame(scene_token, 0, 3.0)
        
        # 测试轨迹预测
        agent_input = frame_data["scene"].get_agent_input()
        prediction_result = app.inference_engine.predict_trajectory(
            agent_input, frame_data["scene"]
        )
        
        print(f"  ✅ Frame 0处理成功")
        print(f"  📊 预测轨迹点数: {len(prediction_result['trajectory']) if prediction_result['trajectory'] is not None else 0}")
        
        # 测试可视化
        all_trajectories = existing_trajectories.copy()
        all_trajectories["prediction"] = prediction_result["trajectory"]
        
        frame_viz = app.visualizer.visualize_single_frame(
            frame_data=frame_data,
            trajectories=all_trajectories,
            prediction_horizon=3.0,
            title=f"Test Frame 0"
        )
        
        print(f"  ✅ Frame可视化成功")
        print(f"  📐 图像尺寸: {frame_viz.size}")
        
        return True
        
    except Exception as e:
        print(f"❌ Frame序列生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_gif_generation():
    """测试简单GIF生成"""
    print("\n🎞️ 测试简单GIF生成")
    print("="*25)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        scene_token = available_scenes[0]
        
        print(f"📝 测试场景: {scene_token}")
        
        # 生成最小的Frame序列GIF
        test_output_dir = Path("./ego_pose_fix_test")
        test_output_dir.mkdir(exist_ok=True)
        
        print("\n🎯 生成最小Frame序列GIF...")
        result = app.create_frame_sequence_gif(
            scene_token=scene_token,
            start_frame_idx=0,      # 从第0帧开始
            num_frames=3,           # 只生成3帧（最小测试）
            frame_step=2,           # 每隔1帧取一次
            prediction_horizon=3.0, # 每个frame预测3秒
            fps=1.0,                # 慢速，便于观察
            output_dir=test_output_dir
        )
        
        print(f"✅ GIF生成成功!")
        print(f"📁 文件路径: {result['gif_path']}")
        print(f"🎬 总帧数: {result['frames']}")
        print(f"📊 Frame范围: {result['frame_range']}")
        print(f"⏱️ 处理时间: {result['processing_time']:.2f}s")
        
        # 验证文件
        gif_path = Path(result['gif_path'])
        if gif_path.exists():
            file_size = gif_path.stat().st_size
            print(f"💾 文件大小: {file_size / 1024:.1f} KB")
            print(f"✅ 文件验证成功")
        else:
            print(f"❌ 文件不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ GIF生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 ego_pose修复验证测试\n")
    
    # 测试1: ego_pose数据访问
    access_ok = test_ego_pose_access()
    
    if access_ok:
        # 测试2: Frame序列生成
        sequence_ok = test_frame_sequence_generation()
        
        if sequence_ok:
            # 测试3: 简单GIF生成
            gif_ok = test_simple_gif_generation()
            
            print("\n" + "="*50)
            if gif_ok:
                print("🎉 所有测试通过!")
                print("✅ ego_pose numpy数组访问问题已修复")
                print("✅ Frame序列GIF功能正常工作")
                print("💡 现在可以安全运行完整的Frame序列GIF功能")
            else:
                print("⚠️ GIF生成测试失败，但基础功能正常")
        else:
            print("\n" + "="*50)
            print("❌ Frame序列生成测试失败")
    else:
        print("\n" + "="*50)
        print("❌ ego_pose访问测试失败") 