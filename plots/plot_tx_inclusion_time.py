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
    test_files = [f for f in files if f.startswith('p2s_performance_test_')]
    
    if not test_files:
        print("No test data found")
        return None
    
    latest_file = max(test_files)
    with open(f"{data_dir}/{latest_file}", 'r') as f:
        return json.load(f)

def create_inclusion_time_plots(data):
    """Create single horizontal violin plot for transaction inclusion time"""
    # Extract data
    p2s_times = [tx['total_duration'] for tx in data['p2s_raw_data']]
    pos_times = [tx['total_duration'] for tx in data['pos_raw_data']]
    
    # Create DataFrame for easier plotting
    df_data = []
    for time in pos_times:
        df_data.append({'Protocol': 'PoS', 'Inclusion Time (s)': time})
    for time in p2s_times:
        df_data.append({'Protocol': 'P2S', 'Inclusion Time (s)': time})
    
    df = pd.DataFrame(df_data)
    
    # Set seaborn style
    sns.set_style("whitegrid")
    sns.set_palette("Blues")
    
    # Create single violin plot
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Horizontal violin plot
    sns.violinplot(data=df, y='Protocol', x='Inclusion Time (s)', ax=ax, inner='box', split=False)
    ax.set_title('Transaction Inclusion Time Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Inclusion Time (seconds)', fontsize=12)
    ax.set_ylabel('Protocol', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save to figures directory
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/inclusion_time_violin.png', 
               dpi=300, bbox_inches='tight')
    
    print(f"\n[PLOTS] Inclusion time violin plot saved to figures/ directory")
    
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
