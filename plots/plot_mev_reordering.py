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

# Set style
sns.set_style("whitegrid")
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



def plot_avg_reordering_rate_comparison(data):
    """Plot average reordering rate comparison"""
    analysis = data['analysis']
    reorder_means = [
        analysis['p2s']['reordering_rate']['mean'],
        analysis['current_ethereum']['reordering_rate']['mean']
    ]
    labels = ['P2S', 'Current Ethereum']
    colors = ['#2ecc71', '#3498db']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    bars = ax.bar(labels, reorder_means, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Average Reordering Rate', fontsize=12)
    ax.set_title('Average Transaction Reordering Rate (Lower = Better)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, reorder_means):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/mev_avg_reordering_rate.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/mev_avg_reordering_rate.png")

def plot_avg_mev_extraction_comparison(data):
    """Plot average MEV extraction rate comparison with error bars"""
    analysis = data['analysis']
    p2s_mean = analysis['p2s']['mev_extraction_rate']['mean']
    eth_mean = analysis['current_ethereum']['mev_extraction_rate']['mean']
    p2s_std = analysis['p2s']['mev_extraction_rate']['std_dev']
    eth_std = analysis['current_ethereum']['mev_extraction_rate']['std_dev']
    
    mev_means = [p2s_mean, eth_mean]
    mev_stds = [p2s_std, eth_std]
    labels = ['P2S', 'Current Ethereum']
    colors = ['#2ecc71', '#3498db']
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    bars = ax.bar(labels, mev_means, color=colors, alpha=0.8, edgecolor='black', 
                  linewidth=2, width=0.6, yerr=mev_stds, capsize=10, error_kw={'linewidth': 2})
    
    # Add value labels
    for bar, val, std in zip(bars, mev_means, mev_stds):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + std + 0.02,
                f'{val:.3f}\n±{std:.3f}', ha='center', va='bottom', 
                fontsize=12, fontweight='bold')
    
    # Add reduction annotation
    reduction = ((eth_mean - p2s_mean) / eth_mean) * 100
    ax.annotate(f'{reduction:.1f}% reduction\nin MEV extraction', 
               xy=(0, p2s_mean), xytext=(0.5, (p2s_mean + eth_mean)/2),
               fontsize=13, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.8', facecolor='lightgreen', alpha=0.8),
               arrowprops=dict(arrowstyle='<->', color='green', lw=3))
    
    # Add comparison text
    comparison_text = f'P2S reduces MEV extraction by {reduction:.1f}%\n'
    comparison_text += f'({eth_mean - p2s_mean:.3f} absolute reduction)'
    ax.text(0.5, 0.95, comparison_text, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax.set_ylabel('Average MEV Extraction Rate', fontsize=13, fontweight='bold')
    ax.set_title('Average MEV Extraction Rate Comparison\n(Lower = Better)', 
                fontsize=15, fontweight='bold', pad=15)
    ax.set_ylim(0, max(mev_means) * 1.4)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/mev_avg_extraction_rate.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/mev_avg_extraction_rate.png")

def plot_total_mev_comparison(data):
    """Plot total MEV extracted comparison"""
    analysis = data['analysis']
    mev_totals = [
        analysis['p2s']['total_mev_extracted'],
        analysis['current_ethereum']['total_mev_extracted']
    ]
    labels = ['P2S', 'Current Ethereum']
    colors = ['#2ecc71', '#3498db']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    bars = ax.bar(labels, mev_totals, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Total MEV Extracted', fontsize=12)
    ax.set_title('Total MEV Extracted (Lower = Better)', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    for bar, val in zip(bars, mev_totals):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.2f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/mev_total_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/mev_total_comparison.png")

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
    plot_avg_reordering_rate_comparison(data)
    plot_avg_mev_extraction_comparison(data)
    plot_total_mev_comparison(data)
    
    # Print statistics instead of plotting trends over blocks
    print_mev_statistics(data)
    
    print("\n✅ All MEV reordering plots created successfully!")
    print("   Check the figures/ directory for output files")

if __name__ == "__main__":
    main()

