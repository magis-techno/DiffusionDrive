# 评估过程中的故障排除指南

## 线程资源耗尽问题

### 问题描述

在运行评估代码时，可能会遇到以下错误信息：

```
(wrapped_fn pid=43507) [ERROR:0@19.706] global parallel_impl.cpp:244 WorkerThread 70: Can't spawn new thread: res = 11
/mnt/sdb/DiffusionDrive/navsim/common/dataloader.py:40: TqdmMonitorWarning: tqdm:disabling monitor support (monitor_interval = 0) due to:
can't start new thread
```

这些错误表明系统无法创建更多线程，导致评估过程出现问题。

### 根本原因

问题的根本原因是系统线程资源耗尽：

1. **Ray 分布式工作器**：默认的 `ray_distributed` 配置会使用所有可用的 CPU 线程
2. **OpenCV 并行处理**：图像处理库会创建大量并行线程
3. **系统限制**：操作系统对单个用户可创建的线程数量有限制
4. **资源竞争**：多个组件同时创建线程导致资源竞争

### 解决方案

#### 方案1：使用单机线程池（推荐）

使用限制了工作线程数量的单机配置：

```bash
python $NAVSIM_DEVKIT_ROOT/navsim/planning/script/run_pdm_score.py \
        train_test_split=navtest \
        agent=diffusiondrive_agent \
        worker=single_machine_limited \
        agent.checkpoint_path=$CKPT \
        experiment_name=diffusiondrive_agent_eval
```

**优点：**
- 稳定性高，不依赖复杂的分布式配置
- 线程数量可控，避免资源耗尽
- 配置简单，易于调试

#### 方案2：使用限制线程的 Ray 配置

如果需要使用 Ray 的分布式能力：

```bash
python $NAVSIM_DEVKIT_ROOT/navsim/planning/script/run_pdm_score.py \
        train_test_split=navtest \
        agent=diffusiondrive_agent \
        worker=ray_distributed_limited \
        agent.checkpoint_path=$CKPT \
        experiment_name=diffusiondrive_agent_eval
```

#### 方案3：手动设置环境变量

在运行评估前设置线程限制：

```bash
# 限制各种库的线程使用
export OMP_NUM_THREADS=4
export OPENCV_NUM_THREADS=4  
export MKL_NUM_THREADS=4
export NUMEXPR_NUM_THREADS=4

# 设置系统资源限制
ulimit -u 4096

# 运行评估
python $NAVSIM_DEVKIT_ROOT/navsim/planning/script/run_pdm_score.py \
        train_test_split=navtest \
        agent=diffusiondrive_agent \
        worker=single_machine_limited \
        agent.checkpoint_path=$CKPT \
        experiment_name=diffusiondrive_agent_eval
```

#### 方案4：使用便捷脚本

使用预配置的评估脚本：

```bash
chmod +x scripts/evaluation/run_diffusiondrive_limited.sh
bash scripts/evaluation/run_diffusiondrive_limited.sh
```

### 配置文件说明

#### single_machine_limited.yaml

```yaml
_target_: nuplan.planning.utils.multithreading.worker_parallel.SingleMachineParallelExecutor
_convert_: 'all'
use_process_pool: false  # 使用线程池而非进程池
max_workers: 4          # 限制为4个工作线程
```

#### ray_distributed_limited.yaml

```yaml
_target_: nuplan.planning.utils.multithreading.worker_ray.RayDistributed
_convert_: 'all'
master_node_ip: null    
threads_per_node: 8     # 限制每个节点使用8个线程
debug_mode: false       
log_to_driver: true     
logs_subdir: 'logs'     
use_distributed: false  
```

### 性能考虑

**单机线程池 vs Ray 分布式：**

| 配置 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| single_machine_limited | 稳定、配置简单 | 并行度相对较低 | 中小规模评估、调试 |
| ray_distributed_limited | 并行度高、可扩展 | 配置复杂、资源需求高 | 大规模评估、生产环境 |

### 监控和调试

**检查系统资源：**

```bash
# 查看当前线程数量
ps -eLf | wc -l

# 查看系统限制
ulimit -a

# 监控内存使用
htop
```

**调整线程数量：**

根据你的系统配置调整 `max_workers` 参数：
- **8核CPU**：建议设置为 4-6 个工作线程
- **16核CPU**：建议设置为 8-12 个工作线程
- **32核CPU**：建议设置为 16-24 个工作线程

### 常见问题

**Q: 评估速度变慢了怎么办？**
A: 适当增加 `max_workers` 数量，但不要超过 CPU 核心数的 75%。

**Q: 仍然出现线程错误？**
A: 进一步减少 `max_workers` 数量，或设置更严格的环境变量限制。

**Q: Ray 相关错误？**
A: 切换到 `single_machine_limited` 配置，避免 Ray 的复杂性。

### 最佳实践

1. **优先使用 single_machine_limited**：对于大多数评估任务，这是最稳定的选择
2. **逐步调整参数**：从较小的 `max_workers` 开始，逐步增加到最优值
3. **监控系统资源**：在评估过程中监控 CPU、内存和线程使用情况
4. **设置环境变量**：始终设置线程限制环境变量作为额外保护

通过这些解决方案，可以有效避免评估过程中的线程资源耗尽问题，确保评估任务稳定运行。 