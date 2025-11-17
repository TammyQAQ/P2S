#!/usr/bin/env python3
"""
Cleanup Old Data Files
Removes old simulation and test data files, keeping only the latest
"""

import os
import glob
from pathlib import Path

def cleanup_data_directory(data_dir="data", keep_latest=2):
    """Clean up old data files, keeping only the latest N files of each type"""
    
    print("=" * 80)
    print("CLEANING UP OLD DATA FILES")
    print("=" * 80)
    
    if not os.path.exists(data_dir):
        print(f"❌ Data directory {data_dir} does not exist")
        return
    
    # File patterns to clean up
    patterns = {
        'research_metrics': 'research_metrics_*.json',
        'p2s_performance': 'p2s_performance_test_*.json',
        'realistic_block': 'realistic_block_simulation_*.json',
        'ethereum_blocks': 'ethereum_blocks_*.json'
    }
    
    total_deleted = 0
    total_size = 0
    
    for pattern_name, pattern in patterns.items():
        files = sorted(glob.glob(os.path.join(data_dir, pattern)), key=os.path.getmtime, reverse=True)
        
        if len(files) > keep_latest:
            to_delete = files[keep_latest:]
            print(f"\n📁 {pattern_name}:")
            print(f"   Found {len(files)} files, keeping {keep_latest} latest")
            
            for file_path in to_delete:
                try:
                    size = os.path.getsize(file_path)
                    os.remove(file_path)
                    total_deleted += 1
                    total_size += size
                    print(f"   🗑️  Deleted: {os.path.basename(file_path)} ({size/1024:.1f} KB)")
                except Exception as e:
                    print(f"   ⚠️  Error deleting {os.path.basename(file_path)}: {e}")
        else:
            print(f"\n📁 {pattern_name}: {len(files)} files (no cleanup needed)")
    
    print("\n" + "=" * 80)
    print(f"✅ Cleanup complete!")
    print(f"   Deleted: {total_deleted} files")
    print(f"   Freed: {total_size / 1024 / 1024:.2f} MB")
    print("=" * 80)

if __name__ == "__main__":
    cleanup_data_directory()

