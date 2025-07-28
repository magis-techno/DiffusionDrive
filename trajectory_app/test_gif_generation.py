#!/usr/bin/env python3
"""
GIF 生成测试脚本

独立测试轨迹GIF动画生成功能
"""

import sys
from pathlib import Path
import time

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_gif_generation():
    """测试GIF生成功能"""
    print("🎬 轨迹GIF生成测试")
    print("="*50)
    
    try:
        # 1. 导入必要的库
        from trajectory_app import TrajectoryPredictionApp
        print("✅ 导入成功")
        
        # 2. 检查Pillow是否可用
        try:
            from PIL import Image
            print("✅ Pillow库可用")
        except ImportError:
            print("❌ Pillow库未安装! 请运行: pip install Pillow")
            return False
        
        # 3. 初始化应用
        print("\n📱 初始化应用...")
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        # 4. 获取应用信息
        print("🔧 获取应用信息...")
        info = app.get_app_info()
        print(f"✅ 可用场景数: {info['data']['num_scenes']}")
        
        if info['data']['num_scenes'] == 0:
            print("❌ 没有可用场景! 请检查数据路径")
            return False
        
        # 5. 选择测试场景
        scene_token = info['data']['available_scenes'][0]
        print(f"🎯 选择场景: {scene_token}")
        
        # 6. 生成GIF
        print("\n🎬 生成GIF动画...")
        print("参数设置:")
        print("  • 总时长: 4.0秒")
        print("  • 时间窗口: 2.0秒")
        print("  • 步长: 0.5秒")
        print("  • 帧率: 2.0 fps")
        
        start_time = time.time()
        
        gif_result = app.create_trajectory_gif(
            scene_token=scene_token,
            total_duration=4.0,        # 较短的测试时长
            window_size=2.0,           # 较小的窗口
            step_size=0.5,             # 0.5秒步长
            fps=2.0,                   # 2帧每秒
            output_dir=Path("./gif_test_output")
        )
        
        processing_time = time.time() - start_time
        
        # 7. 显示结果
        print(f"\n🎉 GIF生成成功!")
        print(f"📁 保存路径: {gif_result['gif_path']}")
        print(f"📊 总帧数: {gif_result['total_frames']}")
        print(f"⏱️ 处理时间: {gif_result['processing_time']:.2f}s")
        print(f"💾 文件大小: {gif_result['file_size_mb']:.2f} MB")
        print(f"🎞️ 规格: {gif_result['fps']} fps, {gif_result['window_size']}s窗口")
        
        # 8. 验证文件存在
        gif_path = Path(gif_result['gif_path'])
        if gif_path.exists():
            file_size_mb = gif_path.stat().st_size / (1024 * 1024)
            print(f"✅ 文件确认存在，大小: {file_size_mb:.2f} MB")
            
            # 显示时间窗口详情
            print(f"\n📝 时间窗口详情:")
            for i, (start, end) in enumerate(gif_result['time_windows']):
                print(f"  帧 {i+1}: {start:.1f}s - {end:.1f}s")
            
            return True
        else:
            print(f"❌ GIF文件未找到: {gif_path}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pillow_gif():
    """测试Pillow GIF功能"""
    print("\n🧪 测试Pillow GIF功能...")
    
    try:
        from PIL import Image, ImageDraw
        import numpy as np
        
        # 创建简单的测试图像
        frames = []
        for i in range(5):
            # 创建200x200的RGB图像
            img = Image.new('RGB', (200, 200), color=(i*50, 100, 150))
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), f"Frame {i+1}", fill=(255, 255, 255))
            frames.append(img)
        
        # 保存为GIF
        test_gif_path = Path("./test_simple.gif")
        frames[0].save(
            test_gif_path,
            save_all=True,
            append_images=frames[1:],
            duration=500,  # 500ms per frame
            loop=0
        )
        
        if test_gif_path.exists():
            size_kb = test_gif_path.stat().st_size / 1024
            print(f"✅ Pillow GIF测试成功! 文件: {test_gif_path}, 大小: {size_kb:.1f} KB")
            # 清理测试文件
            test_gif_path.unlink()
            return True
        else:
            print("❌ Pillow GIF测试失败")
            return False
            
    except Exception as e:
        print(f"❌ Pillow测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始GIF生成测试\n")
    
    # 测试1: Pillow基础功能
    pillow_ok = test_pillow_gif()
    
    if pillow_ok:
        # 测试2: 完整GIF生成
        gif_ok = test_gif_generation()
        
        if gif_ok:
            print("\n" + "="*50)
            print("🎉 所有测试通过!")
            print("✅ GIF生成功能正常工作")
            print("📁 查看 ./gif_test_output/ 目录获取生成的GIF文件")
        else:
            print("\n" + "="*50)
            print("❌ GIF生成测试失败")
            print("请检查错误信息并重试")
    else:
        print("\n" + "="*50)
        print("❌ Pillow库测试失败")
        print("请先安装: pip install Pillow") 