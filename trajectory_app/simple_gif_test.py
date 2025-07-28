#!/usr/bin/env python3
"""
最简化的GIF生成测试

只测试核心功能，避免复杂的依赖
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_pillow_only():
    """只测试Pillow的GIF生成能力"""
    print("🧪 测试Pillow GIF生成...")
    
    try:
        from PIL import Image, ImageDraw
        
        # 创建5帧简单动画
        frames = []
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
        
        for i, color in enumerate(colors):
            # 创建图像
            img = Image.new('RGB', (300, 200), color=color)
            draw = ImageDraw.Draw(img)
            
            # 添加文字
            text = f"Frame {i+1}/5"
            draw.text((50, 80), text, fill=(255, 255, 255))
            
            # 画一个移动的圆
            x = 50 + i * 40
            draw.ellipse([x-10, 100-10, x+10, 100+10], fill=(255, 255, 255))
            
            frames.append(img)
        
        # 保存GIF
        output_path = Path("./simple_test.gif")
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=800,  # 800ms per frame
            loop=0
        )
        
        if output_path.exists():
            size_kb = output_path.stat().st_size / 1024
            print(f"✅ Pillow GIF生成成功!")
            print(f"📁 文件: {output_path.absolute()}")
            print(f"💾 大小: {size_kb:.1f} KB")
            print(f"🎞️ 5帧，800ms每帧")
            
            # 验证文件可读
            try:
                test_img = Image.open(output_path)
                print(f"✅ GIF文件验证成功: {test_img.size}")
                test_img.close()
                return True
            except Exception as e:
                print(f"❌ GIF文件损坏: {e}")
                return False
        else:
            print("❌ GIF文件生成失败")
            return False
            
    except ImportError:
        print("❌ Pillow库未安装! 请运行: pip install Pillow")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_trajectory_app_basic():
    """测试轨迹应用的基本功能"""
    print("\n🚗 测试轨迹应用基本功能...")
    
    try:
        from trajectory_app import TrajectoryPredictionApp
        print("✅ 轨迹应用导入成功")
        
        # 检查默认配置是否存在
        config_path = Path(__file__).parent / "config" / "default_config.yaml"
        if not config_path.exists():
            print(f"❌ 配置文件不存在: {config_path}")
            return False
        
        print(f"✅ 配置文件存在: {config_path}")
        
        # 尝试创建应用实例（但不一定要有数据）
        try:
            app = TrajectoryPredictionApp(str(config_path))
            print("✅ 应用实例创建成功")
            
            # 获取应用信息
            try:
                app_info = app.get_app_info()
                print(f"✅ 应用信息获取成功")
                print(f"📊 模型类型: {app_info['model']}")
                print(f"📊 可用场景: {app_info['data']['num_scenes']}")
                
                if app_info['data']['num_scenes'] > 0:
                    print("✅ 有可用场景，可以进行GIF生成测试")
                    return True
                else:
                    print("⚠️ 没有可用场景，但应用基本功能正常")
                    return True
                    
            except Exception as e:
                print(f"❌ 获取应用信息失败: {e}")
                return False
                
        except Exception as e:
            print(f"❌ 应用初始化失败: {e}")
            print("可能是数据路径或模型路径配置问题")
            return False
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False

if __name__ == "__main__":
    print("🚀 简化GIF生成测试")
    print("="*50)
    
    # 测试1: Pillow基础功能
    pillow_ok = test_pillow_only()
    
    # 测试2: 轨迹应用基础功能
    app_ok = test_trajectory_app_basic()
    
    print("\n" + "="*50)
    print("📊 测试结果:")
    print(f"  Pillow GIF生成: {'✅ 通过' if pillow_ok else '❌ 失败'}")
    print(f"  轨迹应用基础: {'✅ 通过' if app_ok else '❌ 失败'}")
    
    if pillow_ok and app_ok:
        print("\n🎉 基础功能测试通过!")
        print("💡 现在可以尝试运行完整的GIF生成测试")
        print("📝 运行: python test_gif_generation.py")
    elif pillow_ok:
        print("\n⚠️ Pillow功能正常，但轨迹应用有问题")
        print("💡 请检查数据路径和模型配置")
    else:
        print("\n❌ 基础测试失败")
        print("💡 请先安装Pillow: pip install Pillow") 