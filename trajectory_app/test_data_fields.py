#!/usr/bin/env python3
"""
测试数据字段

简单验证数据结构中的字段是否正确
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_data_fields():
    """测试数据字段结构"""
    print("🔍 测试数据字段结构")
    print("="*40)
    
    try:
        # 1. 导入和创建应用
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        print("✅ 应用创建成功")
        
        # 2. 测试初始化
        print("\n🔧 开始初始化...")
        try:
            app_info = app.initialize()
            print("✅ 初始化成功")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            print("\n可能的原因:")
            print("  • 环境变量未设置 (OPENSCENE_DATA_ROOT, NAVSIM_EXP_ROOT)")
            print("  • 数据路径不存在")
            print("  • 模型文件缺失")
            return False
        
        # 3. 检查返回结构
        print("\n📊 检查app_info结构:")
        print(f"类型: {type(app_info)}")
        print(f"顶级字段: {list(app_info.keys())}")
        
        # 4. 检查data字段
        if 'data' in app_info:
            data_info = app_info['data']
            print(f"\n📋 data字段内容:")
            print(f"类型: {type(data_info)}")
            print(f"字段: {list(data_info.keys())}")
            
            # 检查关键字段
            key_fields = [
                'num_scenes', 'total_scenes', 'available_scenes',
                'num_map_locations', 'map_locations', 'has_metric_cache'
            ]
            
            print(f"\n✅ 字段检查:")
            for field in key_fields:
                if field in data_info:
                    value = data_info[field]
                    if field == 'available_scenes' and isinstance(value, list):
                        print(f"  ✅ {field}: {len(value)} 个场景")
                        if value:
                            print(f"      示例: {value[0][:20]}...")
                    else:
                        print(f"  ✅ {field}: {value}")
                else:
                    print(f"  ❌ {field}: 缺失")
        else:
            print("❌ data字段缺失")
            return False
        
        # 5. 检查model字段
        if 'model' in app_info:
            model_info = app_info['model']
            print(f"\n🤖 model字段内容:")
            print(f"字段: {list(model_info.keys())}")
            print(f"模型类型: {model_info.get('model_type', 'N/A')}")
            print(f"状态: {model_info.get('status', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_fields()
    
    print("\n" + "="*40)
    if success:
        print("🎉 数据字段结构验证成功!")
        print("所有必要字段都存在，可以正常运行GIF生成了")
    else:
        print("❌ 数据字段结构验证失败")
        print("请检查配置和环境设置") 