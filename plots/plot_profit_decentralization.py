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

# Set style
sns.set_style("whitegrid")
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
    
    ax.plot(p2s_profits, p2s_cdf, label='P2S', linewidth=3, color='#2ecc71', zorder=3)
    ax.plot(ethereum_profits, eth_cdf, label='Current Ethereum', linewidth=3, color='#3498db', zorder=2)
    
    # Add vertical lines for mean and median
    ax.axvline(p2s_mean, color='#27ae60', linestyle='--', linewidth=2, alpha=0.7, label=f'P2S Mean: {p2s_mean:.2f}')
    ax.axvline(eth_mean, color='#2980b9', linestyle='--', linewidth=2, alpha=0.7, label=f'Ethereum Mean: {eth_mean:.2f}')
    ax.axvline(p2s_median, color='#27ae60', linestyle=':', linewidth=1.5, alpha=0.5)
    ax.axvline(eth_median, color='#2980b9', linestyle=':', linewidth=1.5, alpha=0.5)
    
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

def plot_gini_coefficient(data):
    """Plot Gini coefficient comparison with detailed statistics"""
    analysis = data['analysis']
    p2s_gini = analysis['p2s']['gini_coefficient']
    eth_gini = analysis['current_ethereum']['gini_coefficient']
    gini_values = [p2s_gini, eth_gini]
    labels = ['P2S', 'Current Ethereum']
    colors = ['#2ecc71', '#3498db']
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    bars = ax.bar(labels, gini_values, color=colors, alpha=0.8, edgecolor='black', linewidth=2, width=0.6)
    
    # Add reference lines for interpretation
    ax.axhline(y=0.3, color='green', linestyle='--', linewidth=1.5, alpha=0.5, label='Highly Equal')
    ax.axhline(y=0.5, color='orange', linestyle='--', linewidth=1.5, alpha=0.5, label='Moderate Inequality')
    ax.axhline(y=0.7, color='red', linestyle='--', linewidth=1.5, alpha=0.5, label='High Inequality')
    
    # Add value labels with improvement percentage
    for i, (bar, val) in enumerate(zip(bars, gini_values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{val:.3f}', ha='center', va='bottom', fontsize=13, fontweight='bold')
        
        # Add improvement indicator
        if i == 0:
            improvement = ((eth_gini - p2s_gini) / eth_gini) * 100
            ax.annotate(f'{improvement:.1f}% more\ndecentralized', 
                       xy=(bar.get_x() + bar.get_width()/2., height),
                       xytext=(bar.get_x() + bar.get_width()/2., height - 0.1),
                       ha='center', fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7),
                       arrowprops=dict(arrowstyle='->', color='green', lw=2))
    
    # Add comparison text
    diff = eth_gini - p2s_gini
    comparison_text = f'P2S reduces inequality by {diff:.3f} ({((diff/eth_gini)*100):.1f}%)\n'
    comparison_text += f'compared to Current Ethereum'
    ax.text(0.5, 0.95, comparison_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_ylabel('Gini Coefficient', fontsize=13, fontweight='bold')
    ax.set_title('Profit Decentralization Comparison\n(Lower Gini = More Decentralized)', 
                fontsize=15, fontweight='bold', pad=15)
    ax.set_ylim(0, max(gini_values) * 1.35)
    ax.legend(fontsize=10, loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/profit_gini_coefficient.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/profit_gini_coefficient.png")

def plot_top10_share(data):
    """Plot top 10% profit share with comparison"""
    analysis = data['analysis']
    p2s_top10 = analysis['p2s']['concentration']['top_10_pct']
    eth_top10 = analysis['current_ethereum']['concentration']['top_10_pct']
    top10_values = [p2s_top10, eth_top10]
    labels = ['P2S', 'Current Ethereum']
    colors = ['#2ecc71', '#3498db']
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    bars = ax.bar(labels, top10_values, color=colors, alpha=0.8, edgecolor='black', linewidth=2, width=0.6)
    
    # Add reference line for ideal (10% if perfectly equal)
    ax.axhline(y=10, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Perfect Equality (10%)')
    
    # Add value labels
    for bar, val in zip(bars, top10_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=13, fontweight='bold')
    
    # Add improvement annotation
    improvement = ((eth_top10 - p2s_top10) / eth_top10) * 100
    ax.annotate(f'{improvement:.1f}% less\nconcentrated', 
               xy=(0, p2s_top10), xytext=(0.5, (p2s_top10 + eth_top10)/2),
               fontsize=12, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.8', facecolor='lightgreen', alpha=0.8),
               arrowprops=dict(arrowstyle='<->', color='green', lw=3))
    
    # Add comparison text
    comparison_text = f'P2S reduces top 10% concentration by {improvement:.1f}%\n'
    comparison_text += f'({eth_top10 - p2s_top10:.1f} percentage points)'
    ax.text(0.5, 0.95, comparison_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_ylabel('Top 10% Share (%)', fontsize=13, fontweight='bold')
    ax.set_title('Profit Concentration: Top 10% Validators\n(Lower = More Decentralized)', 
                fontsize=15, fontweight='bold', pad=15)
    ax.set_ylim(0, max(top10_values) * 1.3)
    ax.legend(fontsize=10, loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/profit_top10_share.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/profit_top10_share.png")

def plot_herfindahl_index(data):
    """Plot Herfindahl-Hirschman Index"""
    analysis = data['analysis']
    hhi_values = [
        analysis['p2s']['concentration']['herfindahl_index'],
        analysis['current_ethereum']['concentration']['herfindahl_index']
    ]
    labels = ['P2S', 'Current Ethereum']
    colors = ['#2ecc71', '#3498db']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    bars = ax.bar(labels, hhi_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('HHI Index', fontsize=12)
    ax.set_title('Market Concentration (Lower = Less Concentrated)', fontsize=14, fontweight='bold')
    ax.axhline(y=1500, color='orange', linestyle='--', linewidth=2, label='Competitive Threshold')
    ax.axhline(y=2500, color='red', linestyle='--', linewidth=2, label='Concentrated Threshold')
    ax.set_ylim(0, max(hhi_values) * 1.2)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, hhi_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.0f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/profit_herfindahl_index.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/profit_herfindahl_index.png")

def plot_participation_rate(data):
    """Plot validator participation rate"""
    analysis = data['analysis']
    participation_values = [
        analysis['p2s']['participation']['participation_rate'],
        analysis['current_ethereum']['participation']['participation_rate']
    ]
    labels = ['P2S', 'Current Ethereum']
    colors = ['#2ecc71', '#3498db']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    bars = ax.bar(labels, participation_values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Participation Rate (%)', fontsize=12)
    ax.set_title('Validator Participation Rate (Higher = Better)', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, participation_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/profit_participation_rate.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/profit_participation_rate.png")

def plot_profit_distribution_boxplot(data):
    """Plot profit distribution with violin plot and statistics"""
    p2s_profits = list(data['p2s_profits'].values())
    ethereum_profits = list(data['current_ethereum_profits'].values())
    
    analysis = data['analysis']
    p2s_mean = analysis['p2s']['mean_profit']
    eth_mean = analysis['current_ethereum']['mean_profit']
    p2s_median = analysis['p2s']['median_profit']
    eth_median = analysis['current_ethereum']['median_profit']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Violin plot
    parts = ax1.violinplot([p2s_profits, ethereum_profits], positions=[1, 2], 
                           widths=0.6, showmeans=True, showmedians=True)
    for pc, color in zip(parts['bodies'], ['#2ecc71', '#3498db']):
        pc.set_facecolor(color)
        pc.set_alpha(0.7)
    
    parts['cmeans'].set_colors(['darkgreen', 'darkblue'])
    parts['cmedians'].set_colors(['black', 'black'])
    parts['cmeans'].set_linewidths(2)
    parts['cmedians'].set_linewidths(2)
    
    ax1.set_xticks([1, 2])
    ax1.set_xticklabels(['P2S', 'Current Ethereum'], fontsize=12, fontweight='bold')
    ax1.set_ylabel('Profit per Validator', fontsize=12, fontweight='bold')
    ax1.set_title('Profit Distribution (Violin Plot)', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Right: Box plot with statistics
    bp = ax2.boxplot([p2s_profits, ethereum_profits], labels=['P2S', 'Current Ethereum'],
                     patch_artist=True, widths=0.6, showmeans=True)
    for patch, color in zip(bp['boxes'], ['#2ecc71', '#3498db']):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
        patch.set_edgecolor('black')
        patch.set_linewidth(2)
    
    for mean_line, color in zip(bp['means'], ['darkgreen', 'darkblue']):
        mean_line.set_color(color)
        mean_line.set_linewidth(2)
    for median_line in bp['medians']:
        median_line.set_color('black')
        median_line.set_linewidth(2)
    
    # Add statistics annotations
    stats_text = f'P2S:\n  Mean: {p2s_mean:.2f}\n  Median: {p2s_median:.2f}\n  Std: {np.std(p2s_profits):.2f}\n\n'
    stats_text += f'Ethereum:\n  Mean: {eth_mean:.2f}\n  Median: {eth_median:.2f}\n  Std: {np.std(ethereum_profits):.2f}'
    
    ax2.text(0.98, 0.02, stats_text, transform=ax2.transAxes, fontsize=10,
            verticalalignment='bottom', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax2.set_ylabel('Profit per Validator', fontsize=12, fontweight='bold')
    ax2.set_title('Profit Distribution (Box Plot)', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    plt.suptitle('Profit Distribution Comparison', fontsize=15, fontweight='bold', y=1.02)
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
    plot_gini_coefficient(data)
    plot_top10_share(data)
    plot_herfindahl_index(data)
    plot_participation_rate(data)
    plot_profit_distribution_boxplot(data)
    
    # Print statistics
    print_profit_statistics(data)
    
    print("\n✅ All profit decentralization plots created successfully!")
    print("   Check the figures/ directory for output files")

if __name__ == "__main__":
    main()

