#!/usr/bin/env python3
"""
Profit Decentralization Plotting
Creates individual plots comparing profit distribution in P2S vs PoS vs Flashbots
"""

import json
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Set style with coherent colors
sns.set_theme(style="white")
# Use a consistent color palette: P2S = green, Current Ethereum = blue
P2S_COLOR = '#2ecc71'  # Green
ETH_COLOR = '#3498db'  # Blue
COLORS = [P2S_COLOR, ETH_COLOR]
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

def load_latest_data(data_dir="data"):
    """Load the latest profit decentralization data"""
    files = glob.glob(f"{data_dir}/profit_decentralization_*.json")
    if not files:
        return None
    
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def plot_profit_distribution_cdf(data):
    """Plot profit distribution CDF with statistics"""
    p2s_profits = sorted(list(data['p2s_profits'].values()))
    ethereum_profits = sorted(list(data['current_ethereum_profits'].values()))
    
    analysis = data['analysis']
    p2s_mean = analysis['p2s']['mean_profit']
    eth_mean = analysis['current_ethereum']['mean_profit']
    p2s_median = analysis['p2s']['median_profit']
    eth_median = analysis['current_ethereum']['median_profit']
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    p2s_cdf = np.arange(1, len(p2s_profits) + 1) / len(p2s_profits)
    eth_cdf = np.arange(1, len(ethereum_profits) + 1) / len(ethereum_profits)
    
    ax.plot(p2s_profits, p2s_cdf, label='P2S', linewidth=3, color=P2S_COLOR, zorder=3)
    ax.plot(ethereum_profits, eth_cdf, label='Current Ethereum', linewidth=3, color=ETH_COLOR, zorder=2)
    
    # Add vertical lines for mean and median
    ax.axvline(p2s_mean, color=P2S_COLOR, linestyle='--', linewidth=2, alpha=0.7, label=f'P2S Mean: {p2s_mean:.2f}')
    ax.axvline(eth_mean, color=ETH_COLOR, linestyle='--', linewidth=2, alpha=0.7, label=f'Ethereum Mean: {eth_mean:.2f}')
    ax.axvline(p2s_median, color=P2S_COLOR, linestyle=':', linewidth=1.5, alpha=0.5)
    ax.axvline(eth_median, color=ETH_COLOR, linestyle=':', linewidth=1.5, alpha=0.5)
    
    # Add statistics text box
    stats_text = f'P2S: Mean={p2s_mean:.2f}, Median={p2s_median:.2f}\n'
    stats_text += f'Ethereum: Mean={eth_mean:.2f}, Median={eth_median:.2f}\n'
    stats_text += f'Difference: {eth_mean - p2s_mean:.2f} ({((eth_mean - p2s_mean)/p2s_mean)*100:.1f}% higher)'
    
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_xlabel('Profit per Validator', fontsize=13, fontweight='bold')
    ax.set_ylabel('Cumulative Distribution', fontsize=13, fontweight='bold')
    ax.set_title('Profit Distribution Comparison (CDF)', fontsize=15, fontweight='bold', pad=15)
    ax.legend(fontsize=11, loc='lower right', framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/profit_distribution_cdf.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/profit_distribution_cdf.png")









def plot_profit_distribution_boxplot(data):
    """Plot profit distribution box plot with seaborn styling"""
    p2s_profits = list(data['p2s_profits'].values())
    ethereum_profits = list(data['current_ethereum_profits'].values())
    
    analysis = data['analysis']
    p2s_mean = analysis['p2s']['mean_profit']
    eth_mean = analysis['current_ethereum']['mean_profit']
    p2s_median = analysis['p2s']['median_profit']
    eth_median = analysis['current_ethereum']['median_profit']
    
    # Prepare data for seaborn
    df_data = []
    for profit in p2s_profits:
        df_data.append({'Protocol': 'P2S', 'Profit': profit})
    for profit in ethereum_profits:
        df_data.append({'Protocol': 'Current Ethereum', 'Profit': profit})
    
    df = pd.DataFrame(df_data)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Create box plot with seaborn using consistent colors
    bp = sns.boxplot(data=df, x='Protocol', y='Profit', ax=ax, 
                     palette=[P2S_COLOR, ETH_COLOR], width=0.6,
                     showmeans=True, meanprops={'marker': 'D', 'markerfacecolor': 'white', 
                                               'markeredgecolor': 'black', 'markersize': 8})
    
    # Add statistics annotations
    stats_text = f'P2S:\n  Mean: {p2s_mean:.2f}\n  Median: {p2s_median:.2f}\n  Std: {np.std(p2s_profits):.2f}\n\n'
    stats_text += f'Current Ethereum:\n  Mean: {eth_mean:.2f}\n  Median: {eth_median:.2f}\n  Std: {np.std(ethereum_profits):.2f}'
    
    ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_ylabel('Profit per Validator', fontsize=13, fontweight='bold')
    ax.set_xlabel('Protocol', fontsize=13, fontweight='bold')
    ax.set_title('Profit Distribution Comparison', fontsize=15, fontweight='bold', pad=15)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/profit_distribution_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/profit_distribution_boxplot.png")

def print_profit_statistics(data):
    """Print profit decentralization statistics"""
    analysis = data['analysis']
    
    p2s_gini = analysis['p2s']['gini_coefficient']
    eth_gini = analysis['current_ethereum']['gini_coefficient']
    
    p2s_top10 = analysis['p2s']['concentration']['top_10_pct']
    eth_top10 = analysis['current_ethereum']['concentration']['top_10_pct']
    
    p2s_hhi = analysis['p2s']['concentration']['herfindahl_index']
    eth_hhi = analysis['current_ethereum']['concentration']['herfindahl_index']
    
    p2s_participation = analysis['p2s']['participation']['participation_rate']
    eth_participation = analysis['current_ethereum']['participation']['participation_rate']
    
    p2s_mean = analysis['p2s']['mean_profit']
    eth_mean = analysis['current_ethereum']['mean_profit']
    p2s_median = analysis['p2s']['median_profit']
    eth_median = analysis['current_ethereum']['median_profit']
    
    improvement_gini = ((eth_gini - p2s_gini) / eth_gini) * 100
    improvement_top10 = ((eth_top10 - p2s_top10) / eth_top10) * 100
    improvement_hhi = ((eth_hhi - p2s_hhi) / eth_hhi) * 100
    
    print("\n" + "=" * 80)
    print("PROFIT DECENTRALIZATION STATISTICS")
    print("=" * 80)
    print(f"\nGini Coefficient (Lower = More Decentralized):")
    print(f"  Current Ethereum: {eth_gini:.3f}")
    print(f"  P2S:              {p2s_gini:.3f}")
    print(f"  Improvement:      {improvement_gini:.1f}% more decentralized")
    
    print(f"\nTop 10% Profit Share:")
    print(f"  Current Ethereum: {eth_top10:.1f}%")
    print(f"  P2S:              {p2s_top10:.1f}%")
    print(f"  Improvement:      {improvement_top10:.1f}% less concentrated")
    
    print(f"\nHerfindahl-Hirschman Index (Lower = Less Concentrated):")
    print(f"  Current Ethereum: {eth_hhi:.0f}")
    print(f"  P2S:              {p2s_hhi:.0f}")
    print(f"  Improvement:      {improvement_hhi:.1f}% less concentrated")
    
    print(f"\nValidator Participation Rate:")
    print(f"  Current Ethereum: {eth_participation:.1f}%")
    print(f"  P2S:              {p2s_participation:.1f}%")
    
    print(f"\nAverage Profit per Validator:")
    print(f"  Current Ethereum: {eth_mean:.2f} (median: {eth_median:.2f})")
    print(f"  P2S:              {p2s_mean:.2f} (median: {p2s_median:.2f})")
    print("=" * 80)

def main():
    """Main function"""
    print("=" * 80)
    print("PROFIT DECENTRALIZATION PLOTTING")
    print("=" * 80)
    
    data = load_latest_data()
    if not data:
        print("⚠ No profit decentralization data found")
        print("   Run: python scripts/testing/test_profit_decentralization.py")
        return
    
    print("Creating profit decentralization plots...")
    plot_profit_distribution_cdf(data)
    plot_profit_distribution_boxplot(data)
    
    # Print statistics
    print_profit_statistics(data)
    
    print("\n✅ All profit decentralization plots created successfully!")
    print("   Check the figures/ directory for output files")

if __name__ == "__main__":
    main()

