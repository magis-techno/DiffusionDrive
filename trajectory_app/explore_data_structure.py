#!/usr/bin/env python3
"""
NavSim 数据结构探索脚本

这个脚本会加载真实的NavSim数据并打印所有相关数据结构的属性，
帮助我们理解真实的数据格式，避免在data_manager中出错。
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict
import traceback

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def print_object_attributes(obj: Any, obj_name: str, max_depth: int = 2, current_depth: int = 0):
    """
    递归打印对象的所有属性
    
    Args:
        obj: 要检查的对象
        obj_name: 对象名称
        max_depth: 最大递归深度
        current_depth: 当前递归深度
    """
    indent = "  " * current_depth
    print(f"{indent}📋 {obj_name} ({type(obj).__name__}):")
    
    if current_depth >= max_depth:
        print(f"{indent}  (最大深度已达到)")
        return
    
    try:
        # 获取所有属性
        attributes = [attr for attr in dir(obj) if not attr.startswith('_')]
        
        for attr in attributes:
            try:
                value = getattr(obj, attr)
                value_type = type(value).__name__
                
                # 简化显示
                if callable(value):
                    print(f"{indent}  🔧 {attr}() -> method")
                elif isinstance(value, (str, int, float, bool)):
                    print(f"{indent}  📝 {attr}: {value} ({value_type})")
                elif isinstance(value, (list, tuple)):
                    print(f"{indent}  📋 {attr}: {value_type}[{len(value)}]")
                    if len(value) > 0 and current_depth < max_depth - 1:
                        print_object_attributes(value[0], f"{attr}[0]", max_depth, current_depth + 1)
                elif hasattr(value, '__dict__') or hasattr(value, '__dataclass_fields__'):
                    print(f"{indent}  🔧 {attr}: {value_type}")
                    if current_depth < max_depth - 1:
                        print_object_attributes(value, attr, max_depth, current_depth + 1)
                else:
                    print(f"{indent}  📦 {attr}: {value_type}")
                    
            except Exception as e:
                print(f"{indent}  ❌ {attr}: Error accessing ({e})")
                
    except Exception as e:
        print(f"{indent}  ❌ Error getting attributes: {e}")

def explore_navsim_dataclasses():
    """探索NavSim数据类的结构"""
    print("🔍 探索 NavSim 数据类结构...")
    print("=" * 80)
    
    try:
        from navsim.common.dataclasses import Scene, Frame, EgoStatus, SceneMetadata, AgentInput
        
        print("\n📊 EgoStatus 类结构:")
        print("-" * 40)
        ego_status = EgoStatus.__dataclass_fields__
        for field_name, field_info in ego_status.items():
            print(f"  📝 {field_name}: {field_info.type}")
        
        print("\n📊 Frame 类结构:")
        print("-" * 40)
        frame_fields = Frame.__dataclass_fields__
        for field_name, field_info in frame_fields.items():
            print(f"  📝 {field_name}: {field_info.type}")
        
        print("\n📊 SceneMetadata 类结构:")
        print("-" * 40)
        metadata_fields = SceneMetadata.__dataclass_fields__
        for field_name, field_info in metadata_fields.items():
            print(f"  📝 {field_name}: {field_info.type}")
            
        print("\n✅ 数据类结构探索完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据类探索失败: {e}")
        traceback.print_exc()
        return False

def explore_real_scene_data():
    """探索真实的场景数据"""
    print("\n🔍 探索真实场景数据...")
    print("=" * 80)
    
    # 检查环境变量
    openscene_root = os.environ.get('OPENSCENE_DATA_ROOT')
    if not openscene_root:
        print("❌ OPENSCENE_DATA_ROOT 环境变量未设置")
        return False
    
    data_path = Path(openscene_root) / "navsim_logs" / "test"
    if not data_path.exists():
        print(f"❌ 数据路径不存在: {data_path}")
        return False
    
    try:
        from navsim.common.dataloader import SceneLoader
        from navsim.common.dataclasses import SceneFilter, SensorConfig
        
        print(f"📁 数据路径: {data_path}")
        
        # 创建SceneLoader
        scene_filter = SceneFilter(log_names=None, tokens=None)
        sensor_config = SensorConfig.build_no_sensors()  # 最小传感器配置以节省内存
        
        scene_loader = SceneLoader(
            data_path=data_path,
            sensor_blobs_path=Path(openscene_root) / "sensor_blobs" / "test",
            scene_filter=scene_filter,
            sensor_config=sensor_config
        )
        
        print(f"📊 找到 {len(scene_loader.tokens)} 个场景")
        
        if len(scene_loader.tokens) == 0:
            print("❌ 没有找到场景数据")
            return False
        
        # 取第一个场景进行详细分析
        first_token = scene_loader.tokens[0]
        print(f"\n🎯 分析第一个场景: {first_token}")
        
        scene = scene_loader.get_scene_from_token(first_token)
        
        print(f"\n📋 Scene 对象结构:")
        print_object_attributes(scene, "scene", max_depth=2)
        
        print(f"\n📋 SceneMetadata 对象结构:")
        print_object_attributes(scene.scene_metadata, "scene_metadata", max_depth=1)
        
        print(f"\n📋 第一个 Frame 对象结构:")
        if scene.frames:
            frame = scene.frames[0]
            print_object_attributes(frame, "frame[0]", max_depth=2)
            
            print(f"\n📋 EgoStatus 对象结构:")
            print_object_attributes(frame.ego_status, "ego_status", max_depth=1)
        
        # 测试我们需要的字段
        print(f"\n🧪 测试关键字段:")
        print("-" * 40)
        
        current_frame_idx = scene.scene_metadata.num_history_frames - 1
        current_frame = scene.frames[current_frame_idx]
        
        print(f"✅ scene.scene_metadata.log_name: {scene.scene_metadata.log_name}")
        print(f"✅ scene.scene_metadata.map_name: {scene.scene_metadata.map_name}")
        print(f"✅ scene.scene_metadata.num_history_frames: {scene.scene_metadata.num_history_frames}")
        print(f"✅ scene.scene_metadata.num_future_frames: {scene.scene_metadata.num_future_frames}")
        print(f"✅ current_frame.timestamp: {current_frame.timestamp}")
        print(f"✅ current_frame.token: {current_frame.token}")
        print(f"✅ len(scene.frames): {len(scene.frames)}")
        
        print(f"✅ ego_status.ego_pose: {current_frame.ego_status.ego_pose}")
        print(f"✅ ego_status.ego_velocity: {current_frame.ego_status.ego_velocity}")
        
        return True
        
    except Exception as e:
        print(f"❌ 真实数据探索失败: {e}")
        traceback.print_exc()
        return False

def test_corrected_metadata_extraction(scene, scene_token):
    """测试修正后的metadata提取逻辑"""
    print(f"\n🧪 测试修正后的 metadata 提取...")
    print("-" * 50)
    
    try:
        # 当前帧索引
        current_frame_idx = scene.scene_metadata.num_history_frames - 1
        current_frame = scene.frames[current_frame_idx]
        
        # 修正后的metadata提取
        metadata = {
            "token": scene_token,
            "scenario_type": "unknown",  # 固定值，因为NavSim没有scenario_type
            "log_name": scene.scene_metadata.log_name,
            "map_name": scene.scene_metadata.map_name,
            "timestamp": current_frame.timestamp,  # 修正：从frame获取，不是ego_status
            "num_history_frames": scene.scene_metadata.num_history_frames,
            "num_future_frames": scene.scene_metadata.num_future_frames,
            "total_frames": len(scene.frames)
        }
        
        print("✅ 修正后的 metadata 提取成功:")
        for key, value in metadata.items():
            print(f"  📝 {key}: {value}")
        
        return metadata
        
    except Exception as e:
        print(f"❌ metadata 提取失败: {e}")
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("🔍 NavSim 数据结构探索工具")
    print("=" * 80)
    print("这个工具会帮助我们理解NavSim的真实数据结构，")
    print("避免在 data_manager 中出现属性错误。")
    print()
    
    # 步骤1: 探索数据类结构
    step1_success = explore_navsim_dataclasses()
    
    # 步骤2: 探索真实数据
    step2_success = explore_real_scene_data()
    
    if step1_success and step2_success:
        print(f"\n🎉 数据结构探索完成!")
        print("=" * 80)
        print("\n📝 发现的关键信息:")
        print("  • EgoStatus 没有 timestamp 属性")
        print("  • timestamp 在 Frame 对象中")
        print("  • SceneMetadata 没有 scenario_type 属性")
        print("  • 应该使用 current_frame.timestamp")
        print("  • 所有需要的字段都存在且可访问")
        
        print(f"\n🔧 推荐的修复:")
        print("  1. 将 current_frame.ego_status.timestamp 改为 current_frame.timestamp")
        print("  2. 继续使用 'unknown' 作为 scenario_type")
        print("  3. 其他字段保持不变")
        
    else:
        print(f"\n❌ 数据结构探索未完全成功")
        print("请检查环境变量和数据路径设置")
    
    return step1_success and step2_success

if __name__ == "__main__":
    main() 