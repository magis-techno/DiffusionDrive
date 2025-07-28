#!/usr/bin/env python3
"""
GIF生成演示 - Notebook风格

这个脚本可以直接在Jupyter中运行，也可以作为独立脚本执行
"""

# 环境检查和设置
print("🎬 轨迹GIF生成演示")
print("="*50)

# 1. 导入必要的库
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path.cwd().parent.parent  # 假设在tutorial目录中运行
sys.path.insert(0, str(project_root))

try:
    from trajectory_app import TrajectoryPredictionApp
    print("✅ 轨迹应用导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保在正确的目录中运行此脚本")
    exit(1)

# 2. 检查Pillow库
try:
    from PIL import Image
    print("✅ Pillow库可用 - GIF生成支持已启用")
except ImportError:
    print("❌ Pillow库未安装!")
    print("请运行: pip install Pillow")
    exit(1)

# 3. 初始化应用
print("\n📱 初始化轨迹预测应用...")
config_path = "../config/default_config.yaml"
app = TrajectoryPredictionApp(config_path)

# 4. 获取应用信息
print("🔧 获取应用信息...")
app_info = app.get_app_info()

print(f"✅ 应用就绪")
print(f"📊 可用场景: {app_info['data']['num_scenes']}")
print(f"🗺️ 地图位置: {app_info['data']['num_map_locations']}")

# 5. 选择场景生成GIF
if app_info['data']['num_scenes'] > 0:
    available_scenes = app_info['data']['available_scenes']
    selected_scene = available_scenes[0]
    print(f"\n🎯 选择场景进行GIF生成: {selected_scene}")
    
    # 6. 生成GIF动画
    print("\n🎬 开始生成轨迹演化GIF...")
    print("参数设置:")
    print("  • 总时长: 6.0秒")
    print("  • 时间窗口: 3.0秒")
    print("  • 步长: 0.5秒")
    print("  • 帧率: 2.0 fps")
    
    try:
        print("正在生成GIF，请稍候...")
        gif_result = app.create_trajectory_gif(
            scene_token=selected_scene,
            total_duration=6.0,        # 6秒总时长
            window_size=3.0,           # 3秒时间窗口
            step_size=0.5,             # 0.5秒步长
            fps=2.0,                   # 2帧每秒
            output_dir=Path("./gif_output")
        )
        
        # 7. 显示结果
        print(f"\n🎉 GIF生成成功!")
        print(f"📁 保存路径: {gif_result['gif_path']}")
        print(f"📊 总帧数: {gif_result['total_frames']}")
        print(f"⏱️ 处理时间: {gif_result['processing_time']:.2f}s")
        print(f"💾 文件大小: {gif_result['file_size_mb']:.2f} MB")
        print(f"🎞️ 动画规格: {gif_result['fps']} fps")
        
        # 8. 显示时间窗口详情
        print(f"\n📝 时间窗口详情:")
        windows = gif_result['time_windows']
        for i, (start, end) in enumerate(windows[:8]):  # 显示前8个
            print(f"  帧 {i+1:2d}: {start:.1f}s - {end:.1f}s")
        
        if len(windows) > 8:
            print(f"  ... 还有 {len(windows) - 8} 个帧")
        
        # 9. 验证文件
        gif_file = Path(gif_result['gif_path'])
        if gif_file.exists():
            actual_size = gif_file.stat().st_size / (1024 * 1024)
            print(f"\n✅ 文件验证成功")
            print(f"📄 实际文件大小: {actual_size:.2f} MB")
            print(f"📁 文件位置: {gif_file.absolute()}")
            
            print(f"\n💡 如何查看GIF:")
            print(f"  • 在文件管理器中打开: {gif_file.parent}")
            print(f"  • 双击文件: {gif_file.name}")
            print(f"  • 或用浏览器打开查看动画效果")
        else:
            print(f"\n❌ 警告: GIF文件未找到")
            
    except Exception as e:
        print(f"\n❌ GIF生成失败: {e}")
        import traceback
        traceback.print_exc()
        
else:
    print("❌ 没有可用场景，请检查数据配置")

print(f"\n" + "="*50)
print("🎬 GIF生成演示完成")
print("现在你可以查看生成的轨迹演化动画了！") 