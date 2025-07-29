#!/usr/bin/env python3
"""
测试增强Frame信息的GIF生成功能

验证新的Frame序列GIF是否显示清晰的frame变化信息
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_enhanced_frame_gif():
    """测试增强frame信息的GIF"""
    print("🎬 测试增强Frame序列GIF")
    print("="*50)
    
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
        
        # 生成增强的Frame序列GIF
        print("\n🎯 生成增强Frame序列GIF...")
        print("新特性:")
        print("  • 🎬 每个视图显示Frame编号")
        print("  • 📊 进度条显示frame进展")
        print("  • 🎨 颜色指示器显示frame变化")
        print("  • ⏰ 时间戳显示真实时间演进")
        
        test_output_dir = Path("./enhanced_frame_test")
        test_output_dir.mkdir(exist_ok=True)
        
        result = app.create_frame_sequence_gif(
            scene_token=scene_token,
            start_frame_idx=0,      # 从第0帧开始
            num_frames=8,           # 8帧，便于观察变化
            frame_step=2,           # 每隔1帧取一次（0,2,4,6,8,10,12,14）
            prediction_horizon=3.0, # 每个frame预测3秒
            fps=2.0,                # 慢速播放，便于观察
            output_dir=test_output_dir
        )
        
        print(f"\n✅ 增强Frame序列GIF生成成功!")
        print(f"📁 GIF路径: {result['gif_path']}")
        print(f"🎬 总帧数: {result['frames']}")
        print(f"📊 Frame范围: {result['frame_range']}")
        print(f"⏱️ 处理时间: {result['processing_time']:.2f}s")
        print(f"💾 文件大小: {result['file_size'] / 1024:.1f} KB")
        
        # 显示详细frame信息
        print(f"\n📝 Frame演进详情:")
        for i, frame_meta in enumerate(result['frame_metadata']):
            print(f"  🎬 GIF帧{i+1}: Frame {frame_meta['frame_idx']:03d} "
                  f"(t={frame_meta['timestamp']:.2f}s) - "
                  f"预测{frame_meta['prediction_points']}点, "
                  f"GT{frame_meta['gt_points']}点")
        
        # 验证文件并分析
        gif_path = Path(result['gif_path'])
        if gif_path.exists():
            from PIL import Image
            
            with Image.open(gif_path) as img:
                # 计算实际帧数
                gif_frames = 0
                try:
                    while True:
                        img.seek(gif_frames)
                        gif_frames += 1
                except EOFError:
                    pass
                
                print(f"\n🎞️ GIF验证:")
                print(f"  📐 尺寸: {img.size}")
                print(f"  🎬 帧数: {gif_frames}")
                print(f"  📊 期望帧数: {result['frames']}")
                
                if gif_frames == result['frames']:
                    print("  ✅ 帧数匹配")
                else:
                    print(f"  ⚠️ 帧数不匹配")
                
                # 输出观察指南
                print(f"\n👀 观察指南:")
                print(f"  1. 打开GIF文件: {gif_path}")
                print(f"  2. 注意看每一帧的变化:")
                print(f"     • BEV左上角的Frame编号应该在变化")
                print(f"     • 右上角的彩色方块应该改变颜色")
                print(f"     • 相机视图左上角的Frame编号应该更新")
                print(f"     • 底部信息栏显示详细frame信息和进度条")
                print(f"     • 时间戳应该随frame递增")
                print(f"  3. 这样的GIF展示真实时间演进，而不是固定frame!")
        
        return True
        
    except Exception as e:
        print(f"❌ 增强Frame序列GIF测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_old_vs_new():
    """对比旧方法和新方法的GIF效果"""
    print("\n⚖️ 对比旧方法 vs 新方法")
    print("="*30)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        scene_token = available_scenes[0]
        
        comparison_dir = Path("./gif_comparison_enhanced")
        comparison_dir.mkdir(exist_ok=True)
        
        print(f"📝 对比场景: {scene_token}")
        
        # 旧方法：时间窗口GIF
        print("\n1️⃣ 生成时间窗口GIF（旧方法）...")
        old_result = app.create_trajectory_gif(
            scene_token=scene_token,
            total_duration=3.0,     # 3秒总时长
            window_size=1.5,        # 1.5秒窗口
            step_size=0.5,          # 0.5秒步长
            fps=2.0,
            output_dir=comparison_dir / "old_method"
        )
        
        print(f"  ✅ 旧方法: {old_result['total_frames']}帧, {old_result['processing_time']:.1f}s")
        
        # 新方法：Frame序列GIF
        print("\n2️⃣ 生成Frame序列GIF（新方法）...")
        new_result = app.create_frame_sequence_gif(
            scene_token=scene_token,
            start_frame_idx=0,      
            num_frames=6,           # 6帧（相似的帧数）
            frame_step=2,
            prediction_horizon=3.0,
            fps=2.0,
            output_dir=comparison_dir / "new_method"
        )
        
        print(f"  ✅ 新方法: {new_result['frames']}帧, {new_result['processing_time']:.1f}s")
        
        print(f"\n📊 对比总结:")
        print(f"  旧方法GIF: {old_result['gif_path']}")
        print(f"  新方法GIF: {new_result['gif_path']}")
        
        print(f"\n💡 关键区别:")
        print(f"  🔸 旧方法: 固定Frame[0], 时间窗口滑动 [0-1.5s], [0.5-2.0s], [1.0-2.5s]...")
        print(f"  🔹 新方法: 变化Frame[0,2,4,6,8,10], 每个都预测3秒")
        print(f"  🔸 旧方法: 传感器数据不变，只是预测范围变化")
        print(f"  🔹 新方法: 传感器数据变化，环境动态演进")
        print(f"  🔸 旧方法: 模拟'如果我预测不同时长会怎样'")
        print(f"  🔹 新方法: 模拟'真实驾驶中随时间的预测'")
        print(f"\n🎯 新方法更符合实际应用场景！")
        
        return True
        
    except Exception as e:
        print(f"❌ 对比测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 增强Frame序列GIF测试\n")
    
    # 测试1: 增强frame信息的GIF
    enhanced_ok = test_enhanced_frame_gif()
    
    if enhanced_ok:
        # 测试2: 对比新旧方法
        compare_ok = compare_old_vs_new()
        
        print("\n" + "="*50)
        if compare_ok:
            print("🎉 所有测试完成!")
            print("📁 输出目录:")
            print("  • ./enhanced_frame_test/ - 增强Frame序列GIF")
            print("  • ./gif_comparison_enhanced/ - 新旧方法对比")
            print("\n💡 打开GIF文件观察frame变化效果!")
        else:
            print("⚠️ 对比测试失败，但核心功能正常")
    else:
        print("\n" + "="*50)
        print("❌ 增强Frame序列GIF测试失败") 