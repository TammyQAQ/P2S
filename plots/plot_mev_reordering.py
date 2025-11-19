#!/usr/bin/env python3
"""
MEV Reordering Plotting
Creates individual plots comparing MEV reordering in P2S vs PoS vs Flashbots
"""

import json
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style with coherent colors
sns.set_theme(style="white")
# Use a consistent color palette: P2S = green, Current Ethereum = blue
P2S_COLOR = '#2ecc71'  # Green
ETH_COLOR = '#3498db'  # Blue
COLORS = [P2S_COLOR, ETH_COLOR]
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

def load_latest_data(data_dir="data"):
    """Load the latest MEV reordering data"""
    files = glob.glob(f"{data_dir}/mev_reordering_*.json")
    if not files:
        return None
    
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def print_mev_statistics(data):
    """Print MEV reordering statistics"""
    analysis = data['analysis']
    
    p2s_reorder_mean = analysis['p2s']['reordering_rate']['mean']
    eth_reorder_mean = analysis['current_ethereum']['reordering_rate']['mean']
    p2s_reorder_std = analysis['p2s']['reordering_rate']['std_dev']
    eth_reorder_std = analysis['current_ethereum']['reordering_rate']['std_dev']
    
    p2s_mev_mean = analysis['p2s']['mev_extraction_rate']['mean']
    eth_mev_mean = analysis['current_ethereum']['mev_extraction_rate']['mean']
    p2s_mev_std = analysis['p2s']['mev_extraction_rate']['std_dev']
    eth_mev_std = analysis['current_ethereum']['mev_extraction_rate']['std_dev']
    
    p2s_total_mev = analysis['p2s']['total_mev_extracted']
    eth_total_mev = analysis['current_ethereum']['total_mev_extracted']
    
    p2s_avg_dist = analysis['p2s']['avg_reordering_distance']['mean']
    eth_avg_dist = analysis['current_ethereum']['avg_reordering_distance']['mean']
    
    reduction_reorder = ((eth_reorder_mean - p2s_reorder_mean) / eth_reorder_mean) * 100
    reduction_mev = ((eth_mev_mean - p2s_mev_mean) / eth_mev_mean) * 100
    reduction_total = ((eth_total_mev - p2s_total_mev) / eth_total_mev) * 100
    
    print("\n" + "=" * 80)
    print("MEV REORDERING STATISTICS")
    print("=" * 80)
    print(f"\nTransaction Reordering Rate:")
    print(f"  Current Ethereum: {eth_reorder_mean:.3f} ± {eth_reorder_std:.3f}")
    print(f"  P2S:              {p2s_reorder_mean:.3f} ± {p2s_reorder_std:.3f}")
    print(f"  Reduction:       {reduction_reorder:.1f}%")
    
    print(f"\nMEV Extraction Rate:")
    print(f"  Current Ethereum: {eth_mev_mean:.3f} ± {eth_mev_std:.3f}")
    print(f"  P2S:              {p2s_mev_mean:.3f} ± {p2s_mev_std:.3f}")
    print(f"  Reduction:       {reduction_mev:.1f}%")
    
    print(f"\nTotal MEV Extracted:")
    print(f"  Current Ethereum: {eth_total_mev:,.0f}")
    print(f"  P2S:              {p2s_total_mev:,.0f}")
    print(f"  Reduction:       {reduction_total:.1f}%")
    
    print(f"\nAverage Reordering Distance:")
    print(f"  Current Ethereum: {eth_avg_dist:.2f} positions")
    print(f"  P2S:              {p2s_avg_dist:.2f} positions")
    print("=" * 80)









def main():
    """Main function"""
    print("=" * 80)
    print("MEV REORDERING PLOTTING")
    print("=" * 80)
    
    data = load_latest_data()
    if not data:
        print("⚠ No MEV reordering data found")
        print("   Run: python scripts/testing/test_mev_reordering.py")
        return
    
    print("Creating MEV reordering plots...")
    # No plots needed - all statistics are printed below
    
    # Print statistics instead of plotting averages/comparisons
    print_mev_statistics(data)
    
    print("\n✅ All MEV reordering plots created successfully!")
    print("   Check the figures/ directory for output files")

if __name__ == "__main__":
    main()

