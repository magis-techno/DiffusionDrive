#!/usr/bin/env python3
"""
Script to check for missing data files in the navsim dataset.
This helps identify which sensor data files are missing before running training/caching.
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, List, Set
import pickle
import lzma
from tqdm import tqdm

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_file_exists(file_path: Path) -> bool:
    """Check if a file exists."""
    return file_path.exists() and file_path.is_file()


def load_scene_data(data_path: Path, log_name: str) -> List[Dict]:
    """Load scene data from a log file."""
    log_file = data_path / f"{log_name}.pkl"
    if not log_file.exists():
        logger.error(f"Log file not found: {log_file}")
        return []
    
    try:
        with lzma.open(log_file, "rb") as f:
            scenes_data = pickle.load(f)
        return scenes_data
    except Exception as e:
        logger.error(f"Failed to load log file {log_file}: {e}")
        return []


def check_missing_files(data_path: Path, sensor_blobs_path: Path, log_names: List[str] = None, max_scenes_per_log: int = None) -> Dict[str, List[str]]:
    """
    Check for missing sensor data files in the dataset.
    
    Args:
        data_path: Path to the navsim log data
        sensor_blobs_path: Path to the sensor blobs data
        log_names: List of log names to check. If None, check all logs.
        max_scenes_per_log: Maximum number of scenes to check per log (for quick testing)
    
    Returns:
        Dictionary with missing file information
    """
    
    missing_files = {
        'lidar': [],
        'cameras': [],
        'logs_not_found': []
    }
    
    # Get log files to process
    if log_names is None:
        log_files = [f.stem for f in data_path.glob("*.pkl")]
    else:
        log_files = log_names
    
    logger.info(f"Checking {len(log_files)} log files for missing sensor data...")
    
    for log_name in tqdm(log_files, desc="Checking logs"):
        scenes_data = load_scene_data(data_path, log_name)
        
        if not scenes_data:
            missing_files['logs_not_found'].append(log_name)
            continue
        
        # Limit scenes for quick testing
        if max_scenes_per_log:
            scenes_data = scenes_data[:max_scenes_per_log]
        
        for scene_idx, scene_dict in enumerate(scenes_data):
            try:
                # Check lidar file
                if 'lidar_path' in scene_dict:
                    lidar_path = sensor_blobs_path / scene_dict['lidar_path']
                    if not check_file_exists(lidar_path):
                        missing_files['lidar'].append(str(lidar_path))
                
                # Check camera files
                if 'cams' in scene_dict:
                    for cam_name, cam_data in scene_dict['cams'].items():
                        if 'data_path' in cam_data:
                            cam_path = sensor_blobs_path / cam_data['data_path']
                            if not check_file_exists(cam_path):
                                missing_files['cameras'].append(str(cam_path))
                                
            except Exception as e:
                logger.warning(f"Error checking scene {scene_idx} in log {log_name}: {e}")
                continue
    
    return missing_files


def main():
    parser = argparse.ArgumentParser(description="Check for missing data files in navsim dataset")
    parser.add_argument("--data_path", type=str, required=True, 
                       help="Path to navsim log data directory")
    parser.add_argument("--sensor_blobs_path", type=str, required=True,
                       help="Path to sensor blobs directory")
    parser.add_argument("--log_names", type=str, nargs="+", default=None,
                       help="Specific log names to check (without .pkl extension)")
    parser.add_argument("--max_scenes_per_log", type=int, default=None,
                       help="Maximum number of scenes to check per log (for quick testing)")
    parser.add_argument("--output_file", type=str, default="missing_files_report.txt",
                       help="Output file for missing files report")
    
    args = parser.parse_args()
    
    data_path = Path(args.data_path)
    sensor_blobs_path = Path(args.sensor_blobs_path)
    
    if not data_path.exists():
        logger.error(f"Data path does not exist: {data_path}")
        return
    
    if not sensor_blobs_path.exists():
        logger.error(f"Sensor blobs path does not exist: {sensor_blobs_path}")
        return
    
    logger.info("Starting missing files check...")
    missing_files = check_missing_files(
        data_path=data_path,
        sensor_blobs_path=sensor_blobs_path,
        log_names=args.log_names,
        max_scenes_per_log=args.max_scenes_per_log
    )
    
    # Report results
    total_missing_lidar = len(missing_files['lidar'])
    total_missing_cameras = len(missing_files['cameras'])
    total_missing_logs = len(missing_files['logs_not_found'])
    
    logger.info(f"Missing files check completed:")
    logger.info(f"  - Missing lidar files: {total_missing_lidar}")
    logger.info(f"  - Missing camera files: {total_missing_cameras}")
    logger.info(f"  - Missing log files: {total_missing_logs}")
    
    # Save detailed report
    with open(args.output_file, 'w') as f:
        f.write("Missing Files Report\n")
        f.write("===================\n\n")
        
        f.write(f"Summary:\n")
        f.write(f"  - Missing lidar files: {total_missing_lidar}\n")
        f.write(f"  - Missing camera files: {total_missing_cameras}\n")
        f.write(f"  - Missing log files: {total_missing_logs}\n\n")
        
        if missing_files['logs_not_found']:
            f.write("Missing Log Files:\n")
            for log_name in missing_files['logs_not_found']:
                f.write(f"  {log_name}\n")
            f.write("\n")
        
        if missing_files['lidar']:
            f.write("Missing Lidar Files:\n")
            for file_path in missing_files['lidar'][:100]:  # Limit to first 100
                f.write(f"  {file_path}\n")
            if len(missing_files['lidar']) > 100:
                f.write(f"  ... and {len(missing_files['lidar']) - 100} more\n")
            f.write("\n")
        
        if missing_files['cameras']:
            f.write("Missing Camera Files:\n")
            for file_path in missing_files['cameras'][:100]:  # Limit to first 100
                f.write(f"  {file_path}\n")
            if len(missing_files['cameras']) > 100:
                f.write(f"  ... and {len(missing_files['cameras']) - 100} more\n")
            f.write("\n")
    
    logger.info(f"Detailed report saved to: {args.output_file}")
    
    if total_missing_lidar > 0 or total_missing_cameras > 0:
        logger.warning("Some data files are missing. This may cause errors during training/caching.")
        logger.info("Consider re-downloading the affected data or using the error-tolerant caching.")
    else:
        logger.info("All checked sensor data files are present!")


if __name__ == "__main__":
    main() 