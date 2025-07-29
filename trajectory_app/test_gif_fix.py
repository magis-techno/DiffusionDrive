#!/usr/bin/env python3
"""
专门测试GIF生成修复

验证BytesIO缓冲区问题是否已经解决
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_image_buffer_fix():
    """测试PIL Image缓冲区修复"""
    print("🖼️ 测试PIL Image缓冲区修复")
    print("="*40)
    
    try:
        import io
        from PIL import Image
        import matplotlib.pyplot as plt
        import numpy as np
        
        print("1️⃣ 创建测试图像...")
        
        # 创建一个简单的测试图像
        fig, ax = plt.subplots(1, 1, figsize=(6, 4))
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        ax.plot(x, y, 'b-', linewidth=2, label='测试曲线')
        ax.set_title('GIF测试图像')
        ax.legend()
        
        # 模拟我们修复的方法
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        
        # 使用.copy()方法（修复后的方式）
        img_safe = Image.open(buf).copy()
        
        plt.close(fig)
        buf.close()  # 关闭缓冲区
        
        print("2️⃣ 测试图像保存...")
        
        # 尝试保存图像（这里之前会出错）
        test_output = Path("./test_image_fix.png")
        img_safe.save(test_output)
        
        print(f"  ✅ 图像保存成功: {test_output}")
        print(f"  📊 图像尺寸: {img_safe.size}")
        print(f"  🎨 图像模式: {img_safe.mode}")
        
        # 清理测试文件
        if test_output.exists():
            test_output.unlink()
            print("  🧹 清理测试文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 缓冲区测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gif_generation_pipeline():
    """测试完整的GIF生成流程"""
    print("\n🎬 测试GIF生成流程")
    print("="*30)
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        app = TrajectoryPredictionApp(str(config_path))
        
        # 获取场景
        app_info = app.get_app_info()
        available_scenes = app_info['data']['available_scenes']
        
        if not available_scenes:
            print("❌ 没有可用场景")
            return False
        
        scene_token = available_scenes[0]
        print(f"📝 测试场景: {scene_token}")
        
        # 测试短时长GIF生成
        print("\n🎯 生成测试GIF（极短时长）...")
        
        test_output_dir = Path("./gif_fix_test")
        test_output_dir.mkdir(exist_ok=True)
        
        # 使用新的Frame序列GIF方法
        gif_result = app.create_frame_sequence_gif(
            scene_token=scene_token,
            start_frame_idx=0,         # 从第0帧开始
            num_frames=5,              # 只生成5帧（快速测试）
            frame_step=2,              # 每隔1帧取一次
            prediction_horizon=3.0,    # 每个frame预测3秒
            fps=1.0,                   # 慢帧率，便于观察
            output_dir=test_output_dir
        )
        
        print(f"✅ Frame序列GIF生成成功!")
        print(f"📁 文件路径: {gif_result['gif_path']}")
        print(f"📊 Frame范围: {gif_result['frame_range']}")
        print(f"🎬 总帧数: {gif_result['frames']}")
        
        # 验证文件存在
        gif_path = Path(gif_result['gif_path'])
        if gif_path.exists():
            file_size = gif_path.stat().st_size
            print(f"💾 文件大小: {file_size / 1024:.1f} KB")
            
            # 验证是否是有效的GIF
            from PIL import Image
            with Image.open(gif_path) as img:
                print(f"🎞️ GIF格式: {img.format}")
                print(f"📐 GIF尺寸: {img.size}")
                
                # 计算帧数
                frame_count = 0
                try:
                    while True:
                        img.seek(frame_count)
                        frame_count += 1
                except EOFError:
                    pass
                print(f"🎬 总帧数: {frame_count}")
            
            return True
        else:
            print("❌ GIF文件未生成")
            return False
            
    except Exception as e:
        print(f"❌ GIF生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 GIF生成修复验证\n")
    
    # 测试1: 缓冲区修复
    buffer_ok = test_image_buffer_fix()
    
    if buffer_ok:
        print("\n" + "="*50)
        print("✅ 缓冲区修复验证通过")
        
        # 测试2: 完整GIF流程
        gif_ok = test_gif_generation_pipeline()
        
        print("\n" + "="*50)
        if gif_ok:
            print("🎉 所有GIF修复验证通过！")
            print("💡 现在可以安全运行完整的test_gif_generation.py")
        else:
            print("⚠️ GIF生成流程仍有问题")
    else:
        print("\n" + "="*50)
        print("❌ 基础缓冲区修复失败")
        print("💡 请检查PIL和matplotlib安装") 