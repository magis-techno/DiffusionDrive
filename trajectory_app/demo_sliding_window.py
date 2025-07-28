#!/usr/bin/env python3
"""
滑动窗口轨迹GIF演示脚本

快速体验新的时间标注和轨迹渐变功能
"""

import sys
from pathlib import Path
import time

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def main():
    """主演示函数"""
    print("🎬 滑动窗口轨迹GIF演示")
    print("="*50)
    print("🆕 新功能特性:")
    print("  • ⏰ 时间标注 (1s, 2s, 3s, 4s 标记)")
    print("  • 🌈 轨迹渐变色 (红→橙→黄→绿→蓝)")
    print("  • 👻 历史轨迹淡化显示")
    print("  • 📊 四象限可视化布局")
    print("  • 🎯 2Hz采样，4秒预测")
    print()
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        # 创建应用
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        # 获取应用信息
        print("📊 获取应用信息...")
        app_info = app.get_app_info()
        
        print(f"✅ 模型类型: {app_info['model']['model_type']}")
        print(f"✅ 可用场景: {app_info['data']['num_scenes']}")
        print(f"✅ 数据分割: {app_info['config']['data_split']}")
        
        # 选择场景
        available_scenes = app_info['data']['available_scenes']
        if not available_scenes:
            print("❌ 没有可用场景，请检查数据路径")
            return
        
        scene_token = available_scenes[0]
        print(f"\n🎯 选择场景: {scene_token}")
        
        # 配置演示参数
        demo_params = {
            "sampling_rate": 2.0,          # 2Hz采样 (每0.5秒)
            "total_duration": 6.0,         # 6秒时间线
            "prediction_horizon": 4.0,     # 4秒预测
            "show_history": True,          # 显示历史
            "history_fade_steps": 4,       # 保持4帧历史
            "fps": 3.0                     # 3fps播放
        }
        
        print(f"\n⚙️ 演示参数:")
        print(f"  • 采样频率: {demo_params['sampling_rate']}Hz (每{1/demo_params['sampling_rate']:.1f}秒一帧)")
        print(f"  • 时间线长度: {demo_params['total_duration']}秒")
        print(f"  • 预测窗口: {demo_params['prediction_horizon']}秒")
        print(f"  • 历史显示: {demo_params['history_fade_steps']}帧淡化")
        print(f"  • 播放帧率: {demo_params['fps']}fps")
        
        expected_frames = int(demo_params['total_duration'] * demo_params['sampling_rate']) + 1
        expected_duration = expected_frames / demo_params['fps']
        
        print(f"\n📊 预期结果:")
        print(f"  • GIF帧数: {expected_frames}帧")
        print(f"  • GIF时长: {expected_duration:.1f}秒")
        print(f"  • 时间标记: 1s⚫, 2s🔲, 3s◆, 4s⭐")
        print(f"  • 颜色渐变: 🔴→🟠→🟡→🟢→🔵")
        
        # 确认演示
        print(f"\n🚀 准备生成滑动窗口GIF演示...")
        print("⏳ 预计处理时间: 30-60秒")
        
        # 开始生成
        start_time = time.time()
        
        result = app.create_sliding_window_gif(
            scene_token=scene_token,
            output_dir=Path("./demo_output"),
            **demo_params
        )
        
        processing_time = time.time() - start_time
        
        # 显示结果
        print(f"\n🎉 演示GIF生成成功!")
        print(f"📁 文件路径: {result['sliding_gif']}")
        print(f"⏱️ 处理时间: {processing_time:.1f}秒")
        
        metadata = result['metadata']
        print(f"\n📊 生成统计:")
        print(f"  • 实际帧数: {metadata['total_frames']}")
        print(f"  • 文件大小: {metadata['file_size_mb']:.1f} MB")
        print(f"  • 采样点数: {len(metadata['actual_sampling_times'])}")
        print(f"  • 平均处理: {processing_time/metadata['total_frames']:.2f}秒/帧")
        
        # 播放建议
        print(f"\n🎬 观看建议:")
        print(f"  • 打开文件: {result['sliding_gif']}")
        print(f"  • 关注轨迹: 观察红色到蓝色的时间进程")
        print(f"  • 注意标记: 1s/2s/3s/4s时间点位置")
        print(f"  • 历史对比: 当前预测 vs 历史预测的变化")
        print(f"  • 多视角: BEV + 摄像头 + 对比图 + 状态面板")
        
        # 快速验证GIF
        gif_path = Path(result['sliding_gif'])
        if gif_path.exists():
            from PIL import Image
            with Image.open(gif_path) as img:
                print(f"\n✅ GIF验证:")
                print(f"  • 格式: {img.format}")
                print(f"  • 尺寸: {img.size[0]}×{img.size[1]}")
                
                # 计算实际帧数
                frame_count = 0
                try:
                    while True:
                        img.seek(frame_count)
                        frame_count += 1
                except EOFError:
                    pass
                
                print(f"  • 帧数: {frame_count}")
                if frame_count == metadata['total_frames']:
                    print(f"  ✅ 帧数匹配")
                else:
                    print(f"  ⚠️ 帧数差异 (预期: {metadata['total_frames']})")
        
        print(f"\n🏆 演示完成! 享受你的滑动窗口轨迹GIF!")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        print("\n🔧 排错建议:")
        print("  1. 检查配置文件: trajectory_app/config/default_config.yaml")
        print("  2. 验证数据路径: navsim_log_path 是否正确")
        print("  3. 确认模型权重: checkpoint_path 是否存在")
        print("  4. 运行基础测试: python test_sliding_window_gif.py")
        
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 