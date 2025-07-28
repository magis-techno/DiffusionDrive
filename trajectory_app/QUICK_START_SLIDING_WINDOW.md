# 🎬 滑动窗口轨迹GIF - 快速开始指南

## 🆕 什么是滑动窗口轨迹GIF？

滑动窗口轨迹GIF是一种全新的可视化方式，它模拟真实的自动驾驶过程：在连续的时间点上进行轨迹预测，每个时刻都基于当时的传感器数据重新预测未来4秒的轨迹。

### 🔄 与传统GIF的区别

| 特性 | 传统GIF | 滑动窗口GIF |
|------|---------|-------------|
| **数据来源** | 固定一帧传感器数据 | 连续多帧传感器数据 |
| **预测方式** | 单次预测+时间切片 | 每帧重新预测 |
| **真实性** | 静态数据展示 | 动态驾驶模拟 |
| **时间标注** | 简单时间窗口 | 精确时间标记点 |
| **历史对比** | 不支持 | 支持历史轨迹淡化 |

## 🚀 1分钟快速体验

### 步骤1: 运行演示脚本
```bash
cd trajectory_app
python demo_sliding_window.py
```

### 步骤2: 查看输出
脚本会自动生成演示GIF并显示详细信息：
```
🎉 演示GIF生成成功!
📁 文件路径: ./demo_output/sliding_trajectory_scene_xxx_6s.gif
⏱️ 处理时间: 45.2秒
📊 生成统计:
  • 实际帧数: 13
  • 文件大小: 4.2 MB
```

### 步骤3: 观看GIF
打开生成的GIF文件，观察以下特性：
- 🌈 **轨迹颜色变化**: 红色→蓝色表示0秒→4秒
- ⏰ **时间标记**: 注意1s⚫、2s🔲、3s◆、4s⭐标记
- 👻 **历史淡化**: 灰色虚线显示之前帧的预测
- 📊 **多视角**: 四个象限展示不同信息

## 🛠️ 自定义参数

### 基础参数配置

```python
from trajectory_app import TrajectoryPredictionApp

app = TrajectoryPredictionApp("config/default_config.yaml")

# 自定义参数生成GIF
result = app.create_sliding_window_gif(
    scene_token="your_scene_token",
    
    # 采样控制
    sampling_rate=2.0,          # 2Hz: 每0.5秒采样一次
    total_duration=8.0,         # 总时长8秒 → 17帧
    
    # 预测控制  
    prediction_horizon=4.0,     # 每次预测4秒轨迹
    
    # 历史显示
    show_history=True,          # 显示历史轨迹
    history_fade_steps=5,       # 保持5帧历史
    
    # 输出控制
    fps=4.0,                    # 4fps播放速度
    output_dir=Path("./my_gifs")
)
```

### 参数说明

| 参数 | 含义 | 推荐值 | 效果 |
|------|------|--------|------|
| `sampling_rate` | 采样频率(Hz) | 2.0 | 每0.5秒一帧，平衡质量和速度 |
| `total_duration` | 时间线长度(s) | 6-8 | 足够长展示轨迹变化 |
| `prediction_horizon` | 预测窗口(s) | 4.0 | 符合实际驾驶预测需求 |
| `history_fade_steps` | 历史帧数 | 3-5 | 不过多影响当前轨迹 |
| `fps` | 播放帧率 | 3-5 | 便于观察细节 |

## 🎨 可视化元素详解

### 四象限布局

```
┌─────────────────┬─────────────────┐
│   BEV View      │  Front Camera   │
│                 │                 │
│ • 地图图层       │ • 实时图像      │
│ • 轨迹+时间标注  │ • 轨迹投影      │
│ • 历史轨迹淡化   │ • 目标检测      │
└─────────────────┼─────────────────┤
│ Trajectory Comp │  Status Panel   │
│                 │                 │
│ • 轨迹对比图     │ • 时间信息      │
│ • GT vs 预测     │ • 帧数统计      │
│ • 本地坐标系     │ • 颜色图例      │
└─────────────────┴─────────────────┘
```

### 时间标注系统

| 时间点 | 标记符号 | 颜色 | 含义 |
|--------|----------|------|------|
| 1秒后 | ⚫ 圆点 | 黄色 | 短期预测 |
| 2秒后 | 🔲 方块 | 橙色 | 中期预测 |
| 3秒后 | ◆ 菱形 | 红色 | 长期预测 |
| 4秒后 | ⭐ 星形 | 紫色 | 最远预测 |

### 轨迹颜色编码

```
时间轴: 0s ────────────────→ 4s
颜色:   🔴 → 🟠 → 🟡 → 🟢 → 🔵
含义:   当前   近期   中期   远期   最远
透明度: 100%  100%  100%  100%  100%

历史轨迹:
帧-1: 70%透明度 (较新)
帧-2: 50%透明度
帧-3: 30%透明度  
帧-4: 15%透明度 (较旧)
```

## 🔧 故障排除

### 常见问题

#### 1. 没有可用场景
```
❌ 没有可用场景，请检查数据路径
```
**解决方案**:
- 检查 `config/default_config.yaml` 中的 `navsim_log_path`
- 确认数据目录存在且包含有效场景文件

#### 2. 模型推理错误
```
❌ RuntimeError: Input type and weight type should be the same
```
**解决方案**:
- 已自动修复设备不匹配问题
- 如仍有问题，检查GPU内存是否充足

#### 3. 生成的GIF过大
```
⚠️ 文件大小: 15.2 MB (过大)
```
**解决方案**:
- 减少 `total_duration` (如从8s降到4s)
- 降低 `sampling_rate` (如从2Hz降到1Hz)
- 减少 `history_fade_steps` (如从5降到3)

### 性能优化建议

| 优化目标 | 参数调整 | 预期效果 |
|----------|----------|----------|
| **快速测试** | `total_duration=2.0, sampling_rate=1.0` | 3帧，生成很快 |
| **平衡质量** | `total_duration=6.0, sampling_rate=2.0` | 13帧，中等质量 |
| **高质量** | `total_duration=10.0, sampling_rate=3.0` | 31帧，详细展示 |

## 📊 输出文件说明

### 文件命名规则
```
sliding_trajectory_{scene_token}_{duration}s.gif
例如: sliding_trajectory_abc123def456_6s.gif
```

### 元数据信息
生成完成后会返回详细元数据：
```python
{
    "sliding_gif": "/path/to/output.gif",
    "metadata": {
        "method": "sliding_window",
        "sampling_rate": 2.0,
        "total_frames": 13,
        "file_size_mb": 4.2,
        "processing_time": 45.2,
        "actual_sampling_times": [0.0, 0.5, 1.0, ...],
        # ... 更多信息
    }
}
```

## 🎯 下一步

1. **试验不同参数**: 调整采样率、时间长度，观察效果差异
2. **对比分析**: 生成多个场景的GIF，分析模型表现
3. **特征可视化**: 参考 `FEATURE_VISUALIZATION_TODOLIST.md` 了解后续发展计划

## 💡 专业提示

- **观察一致性**: 关注历史轨迹与当前预测的一致性
- **关注转弯**: 在转弯场景中，时间标注特别有用
- **速度感知**: 通过颜色渐变可以感知车辆的加减速
- **多视角验证**: 利用四象限布局验证预测的合理性

---

**🎉 享受你的滑动窗口轨迹GIF体验！**

如有问题，请参考：
- 🔧 `test_sliding_window_gif.py` - 完整测试
- 📋 `FEATURE_VISUALIZATION_TODOLIST.md` - 功能规划
- �� `README.md` - 完整文档 