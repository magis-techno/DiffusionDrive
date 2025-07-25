# 数据加载错误处理指南

## 概述

针对训练数据（特别是trainval数据集）中可能存在的文件缺失问题，我们已经实现了完善的错误处理机制。现在系统能够：

1. **优雅处理缺失文件**：当激光雷达点云文件或相机图像文件缺失时，系统会记录警告并继续处理其他数据
2. **详细的错误日志**：记录所有加载失败的文件路径和错误信息
3. **失败统计报告**：在缓存完成后提供详细的成功/失败统计
4. **继续执行**：单个文件的缺失不会中断整个训练或缓存过程

## 改进的组件

### 1. 数据加载 (`navsim/common/dataclasses.py`)

- **Lidar.from_paths()**: 当激光雷达文件缺失时返回空的Lidar对象
- **Cameras.from_camera_dict()**: 当相机图像文件缺失时返回空的Camera对象
- 所有错误都会记录到日志中，包含具体的文件路径

### 2. 数据集缓存 (`navsim/planning/training/dataset.py`)

- **Dataset.cache_dataset()**: 跟踪成功和失败的缓存操作
- **Dataset._cache_scene_with_token()**: 单个场景缓存失败不会中断整个过程
- 自动生成失败场景的token列表保存到 `failed_tokens.txt`

### 3. 多线程缓存 (`navsim/planning/script/run_dataset_caching.py`)

- **cache_features()**: 工作线程异常不会导致整个缓存任务失败
- 改进的日志记录，便于问题定位

## 使用方法

### 运行缓存时的新行为

现在运行数据集缓存时，你会看到类似这样的输出：

```bash
python navsim/planning/script/run_dataset_caching.py
```

```
INFO - Worker abc123: Starting to process 100 tokens from logs: ['log_001', 'log_002']
WARNING - Lidar file not found at /path/to/missing_file.pcd. Returning empty Lidar.
WARNING - Camera image file not found at /path/to/missing_image.jpg. Using empty camera.
INFO - Dataset caching completed: 95/100 scenes cached successfully
WARNING - Failed to cache 5 scenes. Failed tokens: ['token1', 'token2', 'token3', 'token4', 'token5']
INFO - Failed tokens saved to: /cache/path/failed_tokens.txt
```

### 检查缺失文件

我们提供了一个专用脚本来预先检查数据集中的缺失文件：

```bash
python scripts/evaluation/check_missing_files.py \
    --data_path /path/to/navsim/logs \
    --sensor_blobs_path /path/to/sensor/blobs \
    --output_file missing_files_report.txt
```

可选参数：
- `--log_names`: 指定要检查的特定日志文件
- `--max_scenes_per_log`: 限制每个日志检查的场景数量（用于快速测试）

### 分析失败的缓存

如果缓存过程中有失败的场景，系统会生成 `failed_tokens.txt` 文件。你可以：

1. **查看失败原因**：检查日志中的错误信息
2. **重新下载数据**：针对特定的缺失文件重新下载
3. **继续训练**：即使有部分数据缺失，也可以继续进行训练

### 恢复缺失的数据

如果发现大量数据缺失，建议：

1. **使用检查脚本**确定缺失文件的范围
2. **重新运行下载脚本**：
   ```bash
   # 重新下载trainval数据
   bash download/download_trainval.sh
   ```
3. **重新运行缓存**（系统会跳过已成功缓存的场景）

## 日志级别配置

可以通过设置日志级别来控制输出的详细程度：

```bash
# 详细模式（显示所有警告）
export PYTHONPATH=/path/to/project:$PYTHONPATH
python -c "import logging; logging.basicConfig(level=logging.WARNING)"

# 简洁模式（只显示错误）
python -c "import logging; logging.basicConfig(level=logging.ERROR)"
```

## 性能考虑

- **并行处理**：多个工作线程可以同时处理不同的数据，即使某些线程遇到错误
- **跳过缓存**：已成功缓存的场景在后续运行中会被跳过
- **内存效率**：空的Lidar/Camera对象占用极少内存

## 故障排除

### 常见问题

1. **"大量文件缺失"**
   - 解决方案：检查下载是否完整，重新运行下载脚本

2. **"工作线程全部失败"**
   - 解决方案：检查路径配置，确保数据目录权限正确

3. **"缓存进程卡住"**
   - 解决方案：检查磁盘空间，监控系统资源使用

### 获取帮助

如果遇到持续的数据加载问题：

1. 运行 `check_missing_files.py` 生成详细报告
2. 检查 `failed_tokens.txt` 中的失败模式
3. 查看完整的日志输出以了解具体错误

这些改进确保了即使在数据不完整的情况下，训练和评估流程也能够稳定运行。 