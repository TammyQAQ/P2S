#!/usr/bin/env python3
"""
System Overhead Plotting
Creates individual plots comparing transaction throughput and latency in P2S vs PoS
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
    """Load the latest system overhead data"""
    files = glob.glob(f"{data_dir}/system_overhead_*.json")
    if not files:
        return None
    
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def plot_transaction_throughput(data):
    """Plot transaction processing time distribution"""
    p2s_tx = data['p2s_overhead']['transaction']
    pos_tx = data['pos_overhead']['transaction']
    
    p2s_tx_time = [t['total_time'] for t in p2s_tx]
    pos_tx_time = [t['total_time'] for t in pos_tx]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(pos_tx_time, bins=30, alpha=0.6, label='Current Ethereum', color=ETH_COLOR, 
            edgecolor='black', linewidth=1)
    ax.hist(p2s_tx_time, bins=30, alpha=0.6, label='P2S', color=P2S_COLOR, 
            edgecolor='black', linewidth=1)
    
    ax.set_xlabel('Processing Time (seconds)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Transaction Processing Time Distribution', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/overhead_transaction_throughput.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/overhead_transaction_throughput.png")

def plot_network_latency(data):
    """Plot network latency distribution"""
    p2s_tx = data['p2s_overhead']['transaction']
    pos_tx = data['pos_overhead']['transaction']
    
    p2s_tx_latency = [t['total_network_latency'] for t in p2s_tx]
    pos_tx_latency = [t['total_network_latency'] for t in pos_tx]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(pos_tx_latency, bins=30, alpha=0.6, label='Current Ethereum', color=ETH_COLOR, 
            edgecolor='black', linewidth=1)
    ax.hist(p2s_tx_latency, bins=30, alpha=0.6, label='P2S', color=P2S_COLOR, 
            edgecolor='black', linewidth=1)
    
    ax.set_xlabel('Network Latency (seconds)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Transaction Network Latency Distribution', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/overhead_network_latency.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/overhead_network_latency.png")

def plot_gas_cost_distribution(data):
    """Plot gas cost distribution"""
    p2s_tx = data['p2s_overhead']['transaction']
    pos_tx = data['pos_overhead']['transaction']
    
    p2s_tx_gas = [t['total_gas'] for t in p2s_tx]
    pos_tx_gas = [t['total_gas'] for t in pos_tx]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(pos_tx_gas, bins=30, alpha=0.6, label='Current Ethereum', color=ETH_COLOR, 
            edgecolor='black', linewidth=1)
    ax.hist(p2s_tx_gas, bins=30, alpha=0.6, label='P2S', color=P2S_COLOR, 
            edgecolor='black', linewidth=1)
    
    ax.set_xlabel('Gas (units)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Transaction Gas Usage Distribution', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/overhead_gas_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/overhead_gas_distribution.png")





def plot_overhead_ratios(data):
    """Plot overhead ratios - P2S overhead compared to Current Ethereum"""
    overhead_ratios = data['analysis']['overhead_ratios']
    overhead_values = [
        overhead_ratios['time_overhead_pct'],
        overhead_ratios['gas_overhead_pct'],
        overhead_ratios['cost_overhead_pct']
    ]
    overhead_labels = ['Processing\nTime', 'Gas\nUsage', 'Transaction\nCost']
    
    # Use seaborn color palette with consistent colors
    colors = sns.color_palette("Set2", 3)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    bars = ax.bar(overhead_labels, overhead_values, color=colors, alpha=0.8, 
                   edgecolor='black', linewidth=2, width=0.6)
    ax.set_ylabel('Overhead (%)', fontsize=13, fontweight='bold')
    ax.set_title('P2S Overhead Compared to Current Ethereum\n(Positive = P2S has higher overhead)', 
                fontsize=15, fontweight='bold', pad=15)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1.5)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Add value labels
    for bar, val in zip(bars, overhead_values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 5,
                f'{val:.1f}%', ha='center', va='bottom', 
                fontsize=13, fontweight='bold')
    
    # Add explanation text
    explanation = 'Overhead = ((P2S - Ethereum) / Ethereum) × 100%\n'
    explanation += 'Shows how much more overhead P2S has compared to Current Ethereum'
    ax.text(0.5, 0.95, explanation, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/overhead_ratios.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/overhead_ratios.png")

def print_block_statistics(data):
    """Print block time statistics (no plot needed if no trend)"""
    analysis = data['analysis']
    p2s_proc_mean = analysis['block']['p2s']['processing_time']['mean']
    pos_proc_mean = analysis['block']['pos']['processing_time']['mean']
    p2s_proc_std = analysis['block']['p2s']['processing_time']['std_dev']
    pos_proc_std = analysis['block']['pos']['processing_time']['std_dev']
    
    p2s_net_mean = analysis['block']['p2s']['network_latency']['mean']
    pos_net_mean = analysis['block']['pos']['network_latency']['mean']
    p2s_net_std = analysis['block']['p2s']['network_latency']['std_dev']
    pos_net_std = analysis['block']['pos']['network_latency']['std_dev']
    
    p2s_total_mean = p2s_proc_mean + p2s_net_mean
    pos_total_mean = pos_proc_mean + pos_net_mean
    
    overhead_proc = ((p2s_proc_mean - pos_proc_mean) / pos_proc_mean) * 100
    overhead_net = ((p2s_net_mean - pos_net_mean) / pos_net_mean) * 100
    overhead_total = ((p2s_total_mean - pos_total_mean) / pos_total_mean) * 100
    
    print("\n" + "=" * 80)
    print("BLOCK TIME STATISTICS")
    print("=" * 80)
    print(f"\nBlock Processing Time:")
    print(f"  Current Ethereum: {pos_proc_mean:.3f}s ± {pos_proc_std:.3f}s")
    print(f"  P2S:              {p2s_proc_mean:.3f}s ± {p2s_proc_std:.3f}s")
    print(f"  Overhead:         {overhead_proc:.1f}%")
    
    print(f"\nBlock Network Latency:")
    print(f"  Current Ethereum: {pos_net_mean:.3f}s ± {pos_net_std:.3f}s")
    print(f"  P2S:              {p2s_net_mean:.3f}s ± {p2s_net_std:.3f}s")
    print(f"  Overhead:         {overhead_net:.1f}%")
    
    print(f"\nTotal Block Time (Processing + Network):")
    print(f"  Current Ethereum: {pos_total_mean:.3f}s")
    print(f"  P2S:              {p2s_total_mean:.3f}s")
    print(f"  Overhead:         {overhead_total:.1f}%")
    print("=" * 80)

def plot_block_time_comparison(data):
    """Plot block time comparison with detailed statistics"""
    p2s_block = data['p2s_overhead']['block']
    pos_block = data['pos_overhead']['block']
    
    # Calculate total block time (processing + network latency)
    p2s_blk_total_time = [b['total_processing_time'] + b['total_network_latency'] for b in p2s_block]
    pos_blk_total_time = [b['total_processing_time'] + b['total_network_latency'] for b in pos_block]
    
    analysis = data['analysis']
    p2s_proc_mean = analysis['block']['p2s']['processing_time']['mean']
    p2s_net_mean = analysis['block']['p2s']['network_latency']['mean']
    pos_proc_mean = analysis['block']['pos']['processing_time']['mean']
    pos_net_mean = analysis['block']['pos']['network_latency']['mean']
    
    p2s_total_mean = p2s_proc_mean + p2s_net_mean
    pos_total_mean = pos_proc_mean + pos_net_mean
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Left: Block time distribution
    ax1.hist(pos_blk_total_time, bins=40, alpha=0.6, label='Current Ethereum', 
            color=ETH_COLOR, edgecolor='black', linewidth=1)
    ax1.hist(p2s_blk_total_time, bins=40, alpha=0.6, label='P2S', 
            color=P2S_COLOR, edgecolor='black', linewidth=1)
    
    # Add mean lines
    ax1.axvline(pos_total_mean, color=ETH_COLOR, linestyle='--', linewidth=2, 
               label=f'Ethereum Mean: {pos_total_mean:.3f}s')
    ax1.axvline(p2s_total_mean, color=P2S_COLOR, linestyle='--', linewidth=2,
               label=f'P2S Mean: {p2s_total_mean:.3f}s')
    
    ax1.set_xlabel('Total Block Time (seconds)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax1.set_title('Block Time Distribution', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10, framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Right: Block time comparison bar chart
    block_time_means = [pos_total_mean, p2s_total_mean]
    labels = ['Current Ethereum', 'P2S']
    
    bars = ax2.bar(labels, block_time_means, color=[ETH_COLOR, P2S_COLOR], alpha=0.8, 
                   edgecolor='black', linewidth=2, width=0.6)
    
    # Add value labels
    for bar, val in zip(bars, block_time_means):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{val:.3f}s', ha='center', va='bottom', fontsize=13, fontweight='bold')
    
    # Add overhead annotation
    overhead = ((p2s_total_mean - pos_total_mean) / pos_total_mean) * 100
    ax2.annotate(f'{overhead:.1f}% overhead', 
               xy=(1, p2s_total_mean), xytext=(0.5, (p2s_total_mean + pos_total_mean)/2),
               fontsize=12, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round,pad=0.8', facecolor='lightyellow', alpha=0.8),
               arrowprops=dict(arrowstyle='<->', color='orange', lw=3))
    
    # Add breakdown text
    breakdown_text = f'Breakdown:\n'
    breakdown_text += f'Ethereum: {pos_proc_mean:.3f}s proc + {pos_net_mean:.3f}s net\n'
    breakdown_text += f'P2S: {p2s_proc_mean:.3f}s proc + {p2s_net_mean:.3f}s net\n'
    breakdown_text += f'Total overhead: {overhead:.1f}%'
    
    ax2.text(0.5, 0.95, breakdown_text, transform=ax2.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    ax2.set_ylabel('Block Time (seconds)', fontsize=12, fontweight='bold')
    ax2.set_title('Average Block Time Comparison', fontsize=13, fontweight='bold')
    ax2.set_ylim(0, max(block_time_means) * 1.3)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    plt.suptitle('Block Time Analysis: P2S vs Current Ethereum', 
                fontsize=15, fontweight='bold', y=1.02)
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/overhead_block_time.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/overhead_block_time.png")

def print_transaction_statistics(data):
    """Print transaction-level statistics"""
    analysis = data['analysis']
    
    p2s_time_mean = analysis['transaction']['p2s']['total_time']['mean']
    pos_time_mean = analysis['transaction']['pos']['total_time']['mean']
    p2s_time_std = analysis['transaction']['p2s']['total_time']['std_dev']
    pos_time_std = analysis['transaction']['pos']['total_time']['std_dev']
    
    p2s_lat_mean = analysis['transaction']['p2s']['network_latency']['mean']
    pos_lat_mean = analysis['transaction']['pos']['network_latency']['mean']
    p2s_lat_std = analysis['transaction']['p2s']['network_latency']['std_dev']
    pos_lat_std = analysis['transaction']['pos']['network_latency']['std_dev']
    
    p2s_gas_mean = analysis['transaction']['p2s']['gas']['mean']
    pos_gas_mean = analysis['transaction']['pos']['gas']['mean']
    
    p2s_cost_mean = analysis['transaction']['p2s']['gas_cost_usd']['mean']
    pos_cost_mean = analysis['transaction']['pos']['gas_cost_usd']['mean']
    
    overhead_time = analysis['overhead_ratios']['time_overhead_pct']
    overhead_gas = analysis['overhead_ratios']['gas_overhead_pct']
    overhead_cost = analysis['overhead_ratios']['cost_overhead_pct']
    
    print("\n" + "=" * 80)
    print("TRANSACTION STATISTICS")
    print("=" * 80)
    print(f"\nTransaction Processing Time:")
    print(f"  Current Ethereum: {pos_time_mean:.4f}s ± {pos_time_std:.4f}s")
    print(f"  P2S:              {p2s_time_mean:.4f}s ± {p2s_time_std:.4f}s")
    print(f"  Overhead:         {overhead_time:.1f}%")
    
    print(f"\nTransaction Network Latency:")
    print(f"  Current Ethereum: {pos_lat_mean:.4f}s ± {pos_lat_std:.4f}s")
    print(f"  P2S:              {p2s_lat_mean:.4f}s ± {p2s_lat_std:.4f}s")
    
    print(f"\nTransaction Gas Usage:")
    print(f"  Current Ethereum: {pos_gas_mean:.0f} units")
    print(f"  P2S:              {p2s_gas_mean:.0f} units")
    print(f"  Overhead:         {overhead_gas:.1f}%")
    
    print(f"\nTransaction Cost:")
    print(f"  Current Ethereum: ${pos_cost_mean:.4f}")
    print(f"  P2S:              ${p2s_cost_mean:.4f}")
    print(f"  Overhead:         {overhead_cost:.1f}%")
    print("=" * 80)

def plot_cost_vs_time_scatter(data):
    """Plot cost vs processing time scatter"""
    p2s_tx = data['p2s_overhead']['transaction']
    pos_tx = data['pos_overhead']['transaction']
    
    p2s_tx_time = [t['total_time'] for t in p2s_tx]
    p2s_tx_cost = [t['gas_cost_usd'] for t in p2s_tx]
    pos_tx_time = [t['total_time'] for t in pos_tx]
    pos_tx_cost = [t['gas_cost_usd'] for t in pos_tx]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.scatter(pos_tx_time, pos_tx_cost, alpha=0.5, label='Current Ethereum', color=ETH_COLOR, s=30)
    ax.scatter(p2s_tx_time, p2s_tx_cost, alpha=0.5, label='P2S', color=P2S_COLOR, s=30)
    
    ax.set_xlabel('Processing Time (seconds)', fontsize=12)
    ax.set_ylabel('Cost (USD)', fontsize=12)
    ax.set_title('Cost vs Processing Time', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/overhead_cost_vs_time.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("  ✓ Saved: figures/overhead_cost_vs_time.png")

def main():
    """Main function"""
    print("=" * 80)
    print("SYSTEM OVERHEAD PLOTTING")
    print("=" * 80)
    
    data = load_latest_data()
    if not data:
        print("⚠ No system overhead data found")
        print("   Run: python scripts/testing/test_system_overhead.py")
        return
    
    print("Creating system overhead plots...")
    plot_transaction_throughput(data)
    plot_network_latency(data)
    plot_gas_cost_distribution(data)
    plot_overhead_ratios(data)
    plot_block_time_comparison(data)
    plot_cost_vs_time_scatter(data)
    
    # Print statistics instead of plotting trends over blocks
    print_transaction_statistics(data)
    print_block_statistics(data)
    
    print("\n✅ All system overhead plots created successfully!")
    print("   Check the figures/ directory for output files")

if __name__ == "__main__":
    main()

