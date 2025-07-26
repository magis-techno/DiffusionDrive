#!/bin/bash

# Set environment variables to limit thread usage
export OMP_NUM_THREADS=4          # Limit OpenMP threads
export OPENCV_NUM_THREADS=4       # Limit OpenCV threads  
export MKL_NUM_THREADS=4          # Limit MKL threads
export NUMEXPR_NUM_THREADS=4      # Limit NumExpr threads

# Set system resource limits
ulimit -u 4096                    # Limit number of processes/threads per user

echo "Running DiffusionDrive evaluation with thread limitations..."
echo "OMP_NUM_THREADS=$OMP_NUM_THREADS"
echo "OPENCV_NUM_THREADS=$OPENCV_NUM_THREADS"

python $NAVSIM_DEVKIT_ROOT/navsim/planning/script/run_pdm_score.py \
        train_test_split=navtest \
        agent=diffusiondrive_agent \
        worker=ray_distributed_limited \
        agent.checkpoint_path=$CKPT \
        experiment_name=diffusiondrive_agent_eval_limited 