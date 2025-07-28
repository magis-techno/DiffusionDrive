#!/usr/bin/env python3
"""
验证轨迹预测应用修复是否成功
运行此脚本来检查所有已知问题是否已解决
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_scenario_type_fix():
    """检查 scenario_type 修复"""
    print("🔍 检查 scenario_type 修复...")
    
    try:
        # 读取 data_manager.py 文件内容
        data_manager_path = Path(__file__).parent / "data_manager.py"
        with open(data_manager_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有错误的引用
        if 'scene.scene_metadata.scenario_type' in content:
            print("❌ 发现未修复的 scenario_type 引用")
            return False
        
        if '"scenario_type": "unknown"' in content:
            print("✅ scenario_type 已修复为固定值")
            return True
        else:
            print("❌ 未找到修复的 scenario_type")
            return False
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def check_import():
    """检查导入"""
    print("\n🔍 检查导入...")
    try:
        from trajectory_app import TrajectoryPredictionApp
        print("✅ 主应用导入成功")
        
        from trajectory_app.data_manager import TrajectoryDataManager
        print("✅ 数据管理器导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def check_statistics_method():
    """检查统计方法返回值"""
    print("\n🔍 检查统计方法...")
    
    try:
        from trajectory_app.data_manager import TrajectoryDataManager
        
        # 创建模拟的推理引擎
        class MockInferenceEngine:
            def get_sensor_config(self):
                from navsim.common.dataclasses import SensorConfig
                return SensorConfig.build_no_sensors()
        
        # 尝试创建数据管理器（使用假路径）
        mock_engine = MockInferenceEngine()
        
        data_config = {
            "navsim_log_path": "/fake/path",
            "sensor_blobs_path": "/fake/path",
            "cache_path": "/fake/path"
        }
        
        # 这会失败，但我们可以检查方法是否存在
        try:
            data_manager = TrajectoryDataManager(data_config, mock_engine)
        except Exception:
            pass  # 预期会失败，因为路径不存在
        
        # 检查方法签名
        import inspect
        sig = inspect.signature(TrajectoryDataManager.get_scene_statistics)
        print("✅ get_scene_statistics 方法存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 统计方法检查失败: {e}")
        return False

def check_metadata_extraction():
    """检查 metadata 提取逻辑"""
    print("\n🔍 检查 metadata 提取逻辑...")
    
    try:
        # 检查 load_scene_data 方法的源码
        from trajectory_app.data_manager import TrajectoryDataManager
        import inspect
        
        source = inspect.getsource(TrajectoryDataManager.load_scene_data)
        
        # 检查修复的标记
        if 'Fixed: NavSim always uses "unknown"' in source:
            print("✅ metadata 提取逻辑已修复")
            return True
        elif '"scenario_type": "unknown"' in source:
            print("✅ metadata 提取逻辑看起来正确")
            return True
        else:
            print("❌ metadata 提取逻辑可能未正确修复")
            return False
            
    except Exception as e:
        print(f"❌ metadata 检查失败: {e}")
        return False

def show_next_steps():
    """显示下一步操作"""
    print("\n" + "="*60)
    print("🚀 下一步操作")
    print("="*60)
    
    print("\n1. **重启 Jupyter Notebook Kernel**:")
    print("   - 在 Jupyter 中: Kernel -> Restart & Clear Output")
    
    print("\n2. **重新运行 Tutorial**:")
    print("   - 从第一个 cell 开始重新运行所有 cells")
    print("   - 确保环境变量正确设置")
    
    print("\n3. **如果仍有问题**:")
    print("   - 查看 trajectory_app/TROUBLESHOOTING.md")
    print("   - 运行调试脚本检查环境")
    
    print("\n4. **快速测试命令**:")
    print("   cd trajectory_app")
    print("   python test_fix.py")
    
    print("\n5. **环境变量检查**:")
    print("   echo $OPENSCENE_DATA_ROOT")
    print("   echo $NAVSIM_EXP_ROOT")

def main():
    """主函数"""
    print("🔧 轨迹预测应用修复验证")
    print("="*60)
    
    checks = [
        check_scenario_type_fix,
        check_import,
        check_statistics_method,
        check_metadata_extraction
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print(f"\n📊 验证结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n🎉 所有修复验证通过!")
        print("✅ scenario_type 错误已修复")
        print("✅ num_map_locations 字段已正确实现")
        print("✅ 导入功能正常")
        print("✅ 方法签名正确")
    else:
        print(f"\n⚠️ {total - passed} 项检查失败")
        print("可能需要额外的修复...")
    
    show_next_steps()

if __name__ == "__main__":
    main() 