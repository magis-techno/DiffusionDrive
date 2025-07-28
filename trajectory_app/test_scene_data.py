#!/usr/bin/env python3
"""
测试场景数据结构

验证load_scene_data返回的数据结构和agent_input获取方式
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_scene_data_structure():
    """测试场景数据结构"""
    print("🔍 测试场景数据结构")
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
        
        # 测试加载场景数据
        print("\n1️⃣ 测试 load_scene_data:")
        scene_data = app.data_manager.load_scene_data(scene_token)
        
        print("📊 返回的字段:")
        for key in scene_data.keys():
            print(f"  ✅ {key}: {type(scene_data[key])}")
        
        # 测试获取agent_input
        print("\n2️⃣ 测试 agent_input 获取:")
        if "scene" in scene_data:
            scene = scene_data["scene"]
            print(f"  ✅ scene对象: {type(scene)}")
            
            # 测试get_agent_input方法
            try:
                agent_input = scene.get_agent_input()
                print(f"  ✅ agent_input: {type(agent_input)}")
                print(f"  📝 agent_input 属性: {dir(agent_input)[:5]}...")
                return True
            except Exception as e:
                print(f"  ❌ 获取agent_input失败: {e}")
                return False
        else:
            print("  ❌ scene_data中没有scene字段")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gif_workflow():
    """测试GIF生成的关键步骤"""
    print("\n🎬 测试GIF生成工作流")
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
        
        print("步骤1: 加载场景数据...")
        scene_data = app.data_manager.load_scene_data(scene_token)
        print("  ✅ 场景数据加载成功")
        
        print("步骤2: 获取现有轨迹...")
        existing_trajectories = app.data_manager.get_all_trajectories(scene_token)
        print(f"  ✅ 找到 {len(existing_trajectories)} 个现有轨迹")
        
        print("步骤3: 获取agent_input...")
        agent_input = scene_data["scene"].get_agent_input()
        print("  ✅ agent_input获取成功")
        
        print("步骤4: 测试推理...")
        prediction_result = app.inference_engine.predict_trajectory(
            agent_input, scene_data["scene"]
        )
        print("  ✅ 轨迹预测成功")
        
        print("步骤5: 同步轨迹...")
        all_trajectories = app.data_manager.synchronize_trajectories({
            **existing_trajectories,
            "prediction": prediction_result["trajectory"]
        }, time_horizon=4.0, dt=0.1)
        print(f"  ✅ 轨迹同步成功，包含: {list(all_trajectories.keys())}")
        
        print("\n🎉 工作流测试通过！GIF生成应该能正常工作")
        return True
        
    except Exception as e:
        print(f"❌ 工作流测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 场景数据结构测试\n")
    
    # 测试1: 数据结构
    structure_ok = test_scene_data_structure()
    
    if structure_ok:
        # 测试2: 工作流
        workflow_ok = test_gif_workflow()
        
        print("\n" + "="*50)
        if workflow_ok:
            print("🎉 所有测试通过！")
            print("💡 现在可以安全运行: python test_gif_generation.py")
        else:
            print("⚠️ 工作流测试失败，但数据结构正常")
    else:
        print("\n" + "="*50)
        print("❌ 基础数据结构测试失败")
        print("💡 请检查应用配置和数据路径") 