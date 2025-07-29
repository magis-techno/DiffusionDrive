#!/usr/bin/env python3
"""
测试metric_cache修复

验证'TrajectroryDataManager' object has no attribute 'metric_cache'错误是否已解决
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_metric_cache_access():
    """测试metric_cache访问修复"""
    print("🗄️ 测试metric_cache访问修复")
    print("="*40)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        print(f"✅ 应用初始化成功")
        
        # 检查data_manager的属性
        dm = app.data_manager
        print(f"📊 DataManager属性检查:")
        print(f"  • 有metric_cache_loader: {hasattr(dm, 'metric_cache_loader')}")
        print(f"  • 有scene_loader: {hasattr(dm, 'scene_loader')}")
        
        if hasattr(dm, 'metric_cache_loader') and dm.metric_cache_loader:
            print(f"  • metric_cache_loader类型: {type(dm.metric_cache_loader)}")
            print(f"  • metric cache包含场景数: {len(dm.metric_cache_loader.tokens)}")
        else:
            print(f"  • metric_cache_loader: None (这是正常的，如果没有cache)")
        
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        
        if not available_scenes:
            print("❌ 没有可用场景")
            return False
        
        scene_token = available_scenes[0]
        print(f"\n📝 测试场景: {scene_token}")
        
        # 这里是之前出错的关键测试
        print(f"\n🎯 测试get_trajectories_from_frame（之前的错误点）...")
        
        trajectories = dm.get_trajectories_from_frame(scene_token, 0, 3.0)
        
        print(f"  ✅ get_trajectories_from_frame成功执行")
        print(f"  📊 返回的轨迹: {list(trajectories.keys())}")
        
        for name, traj in trajectories.items():
            if traj is not None:
                print(f"    • {name}: {traj.shape}")
            else:
                print(f"    • {name}: None")
        
        return True
        
    except Exception as e:
        print(f"❌ metric_cache访问测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frame_data_loading():
    """测试frame数据加载（完整流程）"""
    print("\n📊 测试Frame数据加载完整流程")
    print("="*35)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        scene_token = available_scenes[0]
        
        print(f"📝 测试场景: {scene_token}")
        
        # 步骤1：加载frame数据
        print(f"\n1️⃣ 加载frame数据...")
        frame_data = app.data_manager.load_frame_data(scene_token, 0)
        print(f"  ✅ Frame数据加载成功")
        
        # 步骤2：获取轨迹（这里之前会出错）
        print(f"\n2️⃣ 获取轨迹数据...")
        trajectories = app.data_manager.get_trajectories_from_frame(scene_token, 0, 3.0)
        print(f"  ✅ 轨迹数据获取成功")
        
        # 步骤3：模型推理
        print(f"\n3️⃣ 模型推理...")
        agent_input = frame_data["scene"].get_agent_input()
        prediction_result = app.inference_engine.predict_trajectory(agent_input, frame_data["scene"])
        print(f"  ✅ 模型推理成功")
        
        # 步骤4：组合轨迹
        print(f"\n4️⃣ 组合轨迹...")
        all_trajectories = trajectories.copy()
        all_trajectories["prediction"] = prediction_result["trajectory"]
        print(f"  ✅ 轨迹组合成功，总计: {list(all_trajectories.keys())}")
        
        print(f"\n🎉 完整流程测试成功！")
        print(f"💡 metric_cache属性错误已完全修复")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 metric_cache修复验证\n")
    
    # 测试1: metric_cache访问修复
    cache_ok = test_metric_cache_access()
    
    if cache_ok:
        # 测试2: 完整流程测试
        flow_ok = test_frame_data_loading()
        
        print("\n" + "="*50)
        if flow_ok:
            print("🎉 所有测试通过!")
            print("✅ 'TrajectroryDataManager' object has no attribute 'metric_cache' 已修复")
            print("✅ Frame数据加载完整流程正常")
            print("💡 现在可以安全运行Frame序列GIF功能")
        else:
            print("⚠️ 完整流程测试失败，但metric_cache访问已修复")
    else:
        print("\n" + "="*50)
        print("❌ metric_cache访问修复验证失败") 