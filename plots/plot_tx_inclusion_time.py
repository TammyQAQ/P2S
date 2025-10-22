#!/usr/bin/env python3
"""
Transaction Inclusion Time Plotter
Creates visualizations showing transaction inclusion time distribution for P2S vs PoS
"""

import json
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

def load_latest_data(data_dir="data"):
    """Load the latest test data"""
    files = os.listdir(data_dir)
    
    # Try realistic simulation data first
    realistic_files = [f for f in files if f.startswith('realistic_block_simulation_')]
    if realistic_files:
        latest_file = max(realistic_files)
        with open(f"{data_dir}/{latest_file}", 'r') as f:
            return json.load(f)
    
    # Fallback to old format
    test_files = [f for f in files if f.startswith('p2s_performance_test_')]
    if not test_files:
        print("No test data found")
        return None
    
    latest_file = max(test_files)
    with open(f"{data_dir}/{latest_file}", 'r') as f:
        return json.load(f)

def create_inclusion_time_plots(data):
    """Create single horizontal violin plot for transaction inclusion time"""
    # Check data format and extract accordingly
    if 'p2s_blocks' in data and 'pos_blocks' in data:
        # New realistic format - block-level data
        p2s_times = [block['total_time'] for block in data['p2s_blocks']]
        pos_times = [block['total_time'] for block in data['pos_blocks']]
        title_suffix = " (Block Processing Time)"
    else:
        # Old format - transaction-level data
        p2s_times = [tx['total_duration'] for tx in data['p2s_raw_data']]
        pos_times = [tx['total_duration'] for tx in data['pos_raw_data']]
        title_suffix = " (Transaction Inclusion Time)"
    
    # Create DataFrame for easier plotting
    df_data = []
    for time in pos_times:
        df_data.append({'Protocol': 'PoS', 'Processing Time (s)': time})
    for time in p2s_times:
        df_data.append({'Protocol': 'P2S', 'Processing Time (s)': time})
    
    df = pd.DataFrame(df_data)
    
    # Set seaborn style
    sns.set_style("whitegrid")
    sns.set_palette("Blues")
    
    # Create single violin plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Horizontal violin plot
    sns.violinplot(data=df, y='Protocol', x='Processing Time (s)', ax=ax, inner='box', split=False)
    ax.set_title(f'P2S vs PoS Processing Time Distribution{title_suffix}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Processing Time (seconds)', fontsize=12)
    ax.set_ylabel('Protocol', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save to figures directory
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/inclusion_time_violin.png', 
               dpi=300, bbox_inches='tight')
    
    print(f"\n[PLOTS] Processing time violin plot saved to figures/ directory")
    
    # Print statistics
    p2s_mean = np.mean(p2s_times)
    pos_mean = np.mean(pos_times)
    overhead = p2s_mean - pos_mean
    overhead_pct = (overhead / pos_mean) * 100
    
    print(f"\n📊 STATISTICS:")
    print(f"  P2S Mean: {p2s_mean:.3f}s")
    print(f"  PoS Mean: {pos_mean:.3f}s")
    print(f"  Overhead: {overhead:.3f}s ({overhead_pct:.1f}%)")
    
    # Don't show plot in headless mode
    # plt.show()


def main():
    """Main function"""
    try:
        data = load_latest_data()
        
        if data:
            print("Creating transaction inclusion time visualizations...")
            create_inclusion_time_plots(data)
            print("\n✅ All plots created successfully!")
        else:
            print("No data available for plotting")
            
    except ImportError as e:
        print(f"Error: Missing required library - {e}")
        print("Please install required packages:")
        print("pip install seaborn matplotlib pandas numpy")
    except Exception as e:
        print(f"Error creating plots: {e}")

if __name__ == "__main__":
    main()
