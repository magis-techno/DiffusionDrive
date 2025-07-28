# 轨迹预测应用快速开始指南

## 🚀 当前功能概览

### ✅ 已实现功能
- **轨迹预测与可视化** - 基于DiffusionDrive的实时轨迹推理
- **多轨迹对比** - 预测轨迹 vs 真实轨迹 vs PDM-Closed轨迹
- **BEV可视化** - 修复坐标系，正确的鸟瞰视角显示
- **前视图轨迹投影** - 轨迹实时投影到摄像头图像（新功能！）
- **GIF动画生成** - 时间演化的轨迹动画（新功能！）
- **批量处理** - 多场景自动化处理
- **设备优化** - 智能GPU/CPU设备管理

### 🔮 即将推出
- **BEV语义分割可视化** - 显示模型的语义理解
- **注意力权重可视化** - 模型关注点热力图
- **Diffusion过程可视化** - 轨迹去噪演化过程
- **多尺度特征可视化** - 深层特征分析

---

## 📁 快速安装

### 1. 环境设置
```bash
# 设置环境变量
export OPENSCENE_DATA_ROOT="/path/to/your/openscene/data"
export NAVSIM_EXP_ROOT="/path/to/your/navsim/experiments"

# 安装依赖
pip install Pillow  # GIF生成支持
```

### 2. 验证安装
```bash
cd trajectory_app
python quick_test.py
```

期望输出：
```
🎉 数据结构修复 通过
🎉 代码修复 通过
🎉 导入测试 通过
🎉 设备设置 通过
🎉 环境设置 通过

📊 测试结果: 5/5 项通过
🎉 所有测试通过! 可以运行 tutorial notebook 了!
```

---

## 🎯 核心使用场景

### 场景 1: 单场景轨迹分析
```python
from trajectory_app import TrajectoryPredictionApp

# 初始化应用
app = TrajectoryPredictionApp("./config/default_config.yaml")
app.initialize()

# 预测单个场景
result = app.predict_single_scene(
    scene_token="your_scene_token",
    time_window=(0, 3.0),
    save_visualization=True
)

print(f"预测完成! 可视化保存到: {result['visualization']['save_path']}")
```

### 场景 2: 生成轨迹演化GIF
```python
# 生成时间演化动画
gif_result = app.create_trajectory_gif(
    scene_token="your_scene_token",
    total_duration=6.0,        # 6秒总时长
    window_size=3.0,           # 3秒时间窗口
    step_size=0.5,             # 0.5秒步长
    fps=2.0                    # 2帧每秒
)

print(f"GIF已生成: {gif_result['gif_path']}")
print(f"总帧数: {gif_result['total_frames']}")
```

### 场景 3: 批量场景处理
```python
# 批量处理多个场景
scene_tokens = ["scene1", "scene2", "scene3"]
results = app.predict_batch_scenes(
    scene_tokens=scene_tokens,
    time_window=(0, 3.0),
    output_dir="./batch_results"
)

print(f"批量处理完成! 成功处理 {len(results)} 个场景")
```

---

## 🎨 可视化效果展示

### 1. 综合视图布局
```
┌─────────────────┬──────────────┬──────────────┐
│                 │ 前视图       │ 轨迹对比图   │
│                 │ (轨迹投影)   │              │
│   BEV 视图      ├──────────────┼──────────────┤
│   (修复坐标系)  │ 摄像头视图   │ 统计面板     │
│                 │              │              │
└─────────────────┴──────────────┴──────────────┘
```

### 2. 轨迹类型显示
- 🔴 **模型预测轨迹** - 红色实线，圆形标记
- 🟢 **真实轨迹** - 绿色实线，方形标记  
- 🔵 **PDM-Closed轨迹** - 蓝色虚线，三角标记

### 3. 坐标系修复
- **修复前**: X轴对称错误 ❌
- **修复后**: 正确的90°旋转 ✅
- **验证方法**: 轨迹对比图逆时针90° = BEV视图

---

## 📊 性能指标

### 推理性能
- **GPU模式**: ~0.2s/场景
- **CPU模式**: ~1.8s/场景
- **内存使用**: < 8GB
- **设备**: 自动检测并优化

### GIF生成性能
- **6秒动画**: ~5-10s生成时间
- **文件大小**: 通常2-5MB
- **帧率**: 支持0.5-5.0 fps

---

## 🛠️ 高级配置

### 可视化配置
```yaml
# config/default_config.yaml
visualization:
  bev:
    figure_size: [12, 8]
    layers: ["map", "annotations", "lidar"]
  
  trajectory_styles:
    prediction:
      color: "#DC143C"  # 红色
      width: 3
      alpha: 0.8
    
    ground_truth:
      color: "#2E8B57"  # 绿色  
      width: 3
      alpha: 0.9
```

### 模型配置
```yaml
model:
  type: "diffusiondrive"
  checkpoint_path: "/path/to/your/model.pth"
  device: "auto"  # auto, cpu, cuda
```

---

## 🐛 常见问题

### Q1: 设备不匹配错误
```
RuntimeError: Input type (torch.FloatTensor) and weight type (torch.cuda.FloatTensor) should be the same
```
**解决方案**: 已自动修复! 应用会自动处理设备转移。

### Q2: 坐标系显示错误
```
轨迹在BEV视图中显示异常
```
**解决方案**: 已修复坐标系映射! BEV现在正确显示。

### Q3: GIF生成失败
```
PIL或内存相关错误
```
**解决方案**: 
```bash
pip install Pillow --upgrade
# 或减少时间窗口/帧数
```

### Q4: 数据加载错误
```
AttributeError: 'SceneMetadata' object has no attribute 'scenario_type'
```
**解决方案**: 已修复数据结构问题! 重启kernel即可。

---

## 📚 学习路径

### 初学者
1. **运行Tutorial** - `trajectory_prediction_tutorial.ipynb`
2. **查看示例** - 理解基本可视化
3. **生成第一个GIF** - 体验动画功能

### 进阶用户
1. **批量处理** - 处理多个场景
2. **自定义配置** - 调整可视化参数
3. **性能优化** - GPU/CPU模式切换

### 开发者
1. **阅读TodoList** - `FEATURE_VISUALIZATION_TODOLIST.md`
2. **参与开发** - 实现特征可视化功能
3. **贡献代码** - 提交改进和新功能

---

## 🎯 下一步计划

### 立即开始
- [ ] **Phase 2**: BEV语义分割可视化
- [ ] **Phase 3**: 注意力权重可视化

### 本月目标
- [ ] 完成4个核心特征可视化
- [ ] 性能优化和稳定性提升
- [ ] 用户界面改进

### 长期目标
- [ ] 交互式可视化界面
- [ ] 实时分析工具
- [ ] 与其他模型的集成

---

## 🤝 获取帮助

### 文档资源
- 📖 **完整文档**: `trajectory_app/README.md`
- 🔧 **设备修复**: `trajectory_app/DEVICE_FIX.md`
- 🎯 **坐标修复**: `trajectory_app/COORDINATE_FIX.md`
- 📋 **开发计划**: `trajectory_app/FEATURE_VISUALIZATION_TODOLIST.md`

### 快速验证
```bash
# 运行快速测试
python trajectory_app/quick_test.py

# 运行完整教程
jupyter notebook trajectory_app/tutorial/trajectory_prediction_tutorial.ipynb
```

---

🎉 **恭喜! 你现在可以开始使用完整的轨迹预测和可视化功能了!**

从最简单的单场景预测开始，然后尝试GIF动画生成，最后探索批量处理功能。期待看到你创建的精彩轨迹可视化! 🚗✨ 