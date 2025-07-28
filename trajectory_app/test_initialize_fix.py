#!/usr/bin/env python3
"""
测试initialize方法修复

简单验证app.initialize()方法是否正常工作
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_initialize_method():
    """测试initialize方法"""
    print("🧪 测试 initialize 方法修复")
    print("="*40)
    
    try:
        # 1. 导入应用类
        from trajectory_app import TrajectoryPredictionApp
        print("✅ 成功导入 TrajectoryPredictionApp")
        
        # 2. 创建应用实例
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        print(f"📝 使用配置文件: {config_path}")
        
        app = TrajectoryPredictionApp(str(config_path))
        print("✅ 成功创建应用实例")
        
        # 3. 检查initialize方法是否存在
        if hasattr(app, 'initialize'):
            print("✅ initialize 方法存在")
        else:
            print("❌ initialize 方法不存在")
            return False
        
        # 4. 检查初始状态
        print(f"📊 初始化状态: {app._initialized}")
        
        # 5. 调用initialize方法
        print("\n🔧 调用 initialize() 方法...")
        try:
            info = app.initialize()
            print("✅ initialize() 调用成功")
            
            # 6. 检查返回结果
            if isinstance(info, dict):
                print("✅ 返回类型正确 (dict)")
                
                # 检查关键字段
                expected_keys = ['model', 'data', 'config', 'status']
                for key in expected_keys:
                    if key in info:
                        print(f"✅ 包含字段: {key}")
                    else:
                        print(f"⚠️ 缺少字段: {key}")
                
                # 显示数据信息
                if 'data' in info:
                    data_info = info['data']
                    print(f"\n📊 数据信息:")
                    print(f"  • 可用场景: {data_info.get('num_scenes', 'N/A')}")
                    print(f"  • 地图位置: {data_info.get('num_map_locations', 'N/A')}")
                
                return True
            else:
                print(f"❌ 返回类型错误: {type(info)}")
                return False
                
        except Exception as e:
            print(f"❌ initialize() 调用失败: {e}")
            print("这可能是环境配置问题，请检查:")
            print("  • 环境变量 OPENSCENE_DATA_ROOT")
            print("  • 环境变量 NAVSIM_EXP_ROOT") 
            print("  • 模型文件路径")
            return False
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_initialize_method()
    
    print("\n" + "="*40)
    if success:
        print("🎉 initialize 方法修复验证成功!")
        print("现在可以运行 test_gif_generation.py 了")
    else:
        print("❌ initialize 方法修复验证失败")
        print("请检查错误信息并重试") 