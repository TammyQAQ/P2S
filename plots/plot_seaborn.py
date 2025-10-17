#!/usr/bin/env python3
"""
Block Time Distribution Plotter with Seaborn
Creates beautiful visualizations showing how many transactions take how long
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
    test_files = [f for f in files if f.startswith('p2s_performance_test_')]
    
    if not test_files:
        print("No test data found")
        return None
    
    latest_file = max(test_files)
    with open(f"{data_dir}/{latest_file}", 'r') as f:
        return json.load(f)

def create_seaborn_plots(data):
    """Create beautiful seaborn plots"""
    # Extract data
    p2s_times = [tx['total_duration'] for tx in data['p2s_raw_data']]
    pos_times = [tx['total_duration'] for tx in data['pos_raw_data']]
    
    # Create DataFrame for easier plotting
    df_data = []
    for time in pos_times:
        df_data.append({'Protocol': 'PoS', 'Block Time (s)': time})
    for time in p2s_times:
        df_data.append({'Protocol': 'P2S', 'Block Time (s)': time})
    
    df = pd.DataFrame(df_data)
    
    # Set seaborn style
    sns.set_style("whitegrid")
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('P2S vs PoS Block Time Distribution Analysis', fontsize=16, fontweight='bold')
    
    # Plot 1: Histogram comparison
    ax1 = axes[0, 0]
    sns.histplot(data=df, x='Block Time (s)', hue='Protocol', bins=15, alpha=0.7, ax=ax1)
    ax1.set_title('Block Time Distribution Histogram')
    ax1.set_xlabel('Block Time (seconds)')
    ax1.set_ylabel('Number of Transactions')
    
    # Plot 2: Box plot comparison
    ax2 = axes[0, 1]
    sns.boxplot(data=df, x='Protocol', y='Block Time (s)', ax=ax2)
    ax2.set_title('Block Time Distribution (Box Plot)')
    ax2.set_xlabel('Protocol')
    ax2.set_ylabel('Block Time (seconds)')
    
    # Plot 3: Violin plot
    ax3 = axes[1, 0]
    sns.violinplot(data=df, x='Protocol', y='Block Time (s)', ax=ax3)
    ax3.set_title('Block Time Distribution (Violin Plot)')
    ax3.set_xlabel('Protocol')
    ax3.set_ylabel('Block Time (seconds)')
    
    # Plot 4: Cumulative distribution
    ax4 = axes[1, 1]
    
    # Calculate cumulative distributions
    pos_sorted = np.sort(pos_times)
    p2s_sorted = np.sort(p2s_times)
    pos_cumulative = np.arange(1, len(pos_sorted) + 1) / len(pos_sorted)
    p2s_cumulative = np.arange(1, len(p2s_sorted) + 1) / len(p2s_sorted)
    
    ax4.plot(pos_sorted, pos_cumulative, label='PoS', linewidth=2, marker='o', markersize=4)
    ax4.plot(p2s_sorted, p2s_cumulative, label='P2S', linewidth=2, marker='s', markersize=4)
    ax4.set_title('Cumulative Distribution Function')
    ax4.set_xlabel('Block Time (seconds)')
    ax4.set_ylabel('Cumulative Probability')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    ax4.set_ylim(0, 1)
    
    plt.tight_layout()
    
    # Save to figures directory
    os.makedirs('figures', exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f'figures/block_time_distribution_seaborn_{timestamp}.png', 
               dpi=300, bbox_inches='tight')
    
    # Also save to plots directory
    os.makedirs('plots', exist_ok=True)
    plt.savefig(f'plots/block_time_distribution_seaborn_{timestamp}.png', 
               dpi=300, bbox_inches='tight')
    
    print(f"\n[PLOTS] Seaborn charts saved to figures/ and plots/ directories")
    
    # Create additional detailed plots
    create_detailed_plots(df, p2s_times, pos_times)
    
    # Don't show plot in headless mode
    # plt.show()

def create_detailed_plots(df, p2s_times, pos_times):
    """Create additional detailed plots"""
    
    # Plot 5: Time range comparison
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))
    
    # Define time ranges
    time_ranges = [
        (0, 0.5, 'Very Fast (<0.5s)'),
        (0.5, 1.0, 'Fast (0.5-1.0s)'),
        (1.0, 1.5, 'Medium (1.0-1.5s)'),
        (1.5, 2.0, 'Slow (1.5-2.0s)'),
        (2.0, 3.0, 'Very Slow (2.0-3.0s)'),
        (3.0, float('inf'), 'Extremely Slow (>3.0s)')
    ]
    
    pos_counts = []
    p2s_counts = []
    range_labels = []
    
    for min_time, max_time, label in time_ranges:
        pos_count = sum(1 for t in pos_times if min_time <= t < max_time)
        p2s_count = sum(1 for t in p2s_times if min_time <= t < max_time)
        
        pos_counts.append(pos_count)
        p2s_counts.append(p2s_count)
        range_labels.append(label)
    
    # Create grouped bar chart
    x = np.arange(len(range_labels))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, pos_counts, width, label='PoS', alpha=0.8, color='skyblue')
    bars2 = ax.bar(x + width/2, p2s_counts, width, label='P2S', alpha=0.8, color='orange')
    
    ax.set_xlabel('Block Time Ranges')
    ax.set_ylabel('Number of Transactions')
    ax.set_title('Transaction Count by Block Time Range')
    ax.set_xticks(x)
    ax.set_xticklabels(range_labels, rotation=45, ha='right')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    for bar in bars2:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # Save detailed plot
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plt.savefig(f'figures/time_range_comparison_{timestamp}.png', 
               dpi=300, bbox_inches='tight')
    plt.savefig(f'plots/time_range_comparison_{timestamp}.png', 
               dpi=300, bbox_inches='tight')
    
    print(f"[PLOTS] Time range comparison chart saved")

def main():
    """Main function"""
    try:
        data = load_latest_data()
        
        if data:
            print("Creating seaborn visualizations...")
            create_seaborn_plots(data)
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
