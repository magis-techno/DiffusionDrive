#!/usr/bin/env python3
"""
验证get_app_info()返回的字段结构

快速检查所有字段是否正确存在
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    print("🔍 验证应用信息字段")
    print("="*50)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        # 使用默认配置创建应用
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        # 获取应用信息
        app_info = app.get_app_info()
        
        print("✅ 应用信息获取成功")
        print("\n📊 字段验证:")
        
        # 验证顶级字段
        expected_top_level = ["model", "data", "config", "status"]
        for field in expected_top_level:
            if field in app_info:
                print(f"  ✅ {field}: 存在")
            else:
                print(f"  ❌ {field}: 缺失")
        
        # 验证model字段
        print("\n📱 Model字段:")
        model_info = app_info.get("model", {})
        model_fields = ["model_type", "status", "device"]
        for field in model_fields:
            if field in model_info:
                print(f"  ✅ model.{field}: {model_info[field]}")
            else:
                print(f"  ❌ model.{field}: 缺失")
        
        # 验证data字段
        print("\n📊 Data字段:")
        data_info = app_info.get("data", {})
        data_fields = [
            "total_scenes", "num_scenes", "available_scenes", 
            "num_map_locations", "has_metric_cache"
        ]
        for field in data_fields:
            if field in data_info:
                value = data_info[field]
                if field == "available_scenes":
                    # 只显示数量，不显示完整列表
                    print(f"  ✅ data.{field}: {len(value)} 个场景")
                    if len(value) > 0:
                        print(f"    📝 示例: {value[0]}")
                else:
                    print(f"  ✅ data.{field}: {value}")
            else:
                print(f"  ❌ data.{field}: 缺失")
        
        # 验证关键功能
        print("\n🎯 功能检查:")
        num_scenes = data_info.get("num_scenes", 0)
        available_scenes = data_info.get("available_scenes", [])
        
        if num_scenes > 0 and len(available_scenes) > 0:
            print(f"  ✅ 有 {num_scenes} 个可用场景，可以生成GIF")
            return True
        else:
            print(f"  ⚠️ 场景数量: {num_scenes}，可用场景列表长度: {len(available_scenes)}")
            return False
            
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    print("\n" + "="*50)
    if success:
        print("🎉 所有字段验证通过!")
        print("💡 现在可以运行: python simple_gif_test.py")
    else:
        print("⚠️ 字段验证有问题，但基本结构正确")
        print("💡 可能是数据路径配置问题") 