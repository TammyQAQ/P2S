#!/usr/bin/env python3
"""
Research Question 3: System Overhead
Grouped bar chart comparing latency and cost between P2S and Ethereum PoS
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
import glob

plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12

def load_latest_research_data(data_dir="data"):
    """Load the latest research metrics data"""
    files = glob.glob(f"{data_dir}/research_metrics_*.json")
    if not files:
        print("No research metrics data found. Run research_metrics_simulation.py first.")
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def plot_system_overhead(data: Dict):
    """Grouped bar chart: Compare key overhead metrics"""
    protocols = ['p2s', 'ethereum_pos']
    protocol_labels = ['P2S', 'Ethereum PoS']
    colors = ['#2E86AB', '#A23B72']
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Extract overhead data
    mean_latencies = []
    mean_costs = []
    
    for protocol in protocols:
        if protocol in data.get('overhead_metrics', {}):
            mean_latencies.append(data['overhead_metrics'][protocol].get('mean_latency', 0))
            mean_costs.append(data['overhead_metrics'][protocol].get('mean_cost', 0))
        else:
            mean_latencies.append(0)
            mean_costs.append(0)
    
    # Plot 1: Network Latency
    bars1 = ax1.bar(protocol_labels, mean_latencies, color=colors, alpha=0.8, 
                   edgecolor='black', linewidth=2)
    for bar, val in zip(bars1, mean_latencies):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(mean_latencies) * 0.02,
                f'{val:.3f}s', ha='center', va='bottom', fontsize=13, fontweight='bold')
    
    ax1.set_ylabel('Mean Network Latency (seconds)', fontsize=14, fontweight='bold')
    ax1.set_title('Network Latency Comparison', fontsize=15, fontweight='bold', pad=15)
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax1.set_ylim(0, max(mean_latencies) * 1.2 if mean_latencies else 1)
    
    # Plot 2: Gas Cost
    bars2 = ax2.bar(protocol_labels, mean_costs, color=colors, alpha=0.8, 
                   edgecolor='black', linewidth=2)
    for bar, val in zip(bars2, mean_costs):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(mean_costs) * 0.02,
                f'{val:.4f} ETH', ha='center', va='bottom', fontsize=13, fontweight='bold')
    
    ax2.set_ylabel('Mean Gas Cost per Block (ETH)', fontsize=14, fontweight='bold')
    ax2.set_title('Gas Cost Comparison', fontsize=15, fontweight='bold', pad=15)
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax2.set_ylim(0, max(mean_costs) * 1.2 if mean_costs else 1)
    
    plt.suptitle('System Overhead: Latency and Cost Comparison', 
                 fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/system_overhead.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: figures/system_overhead.png")
    plt.close()

def main():
    data = load_latest_research_data()
    if data:
        plot_system_overhead(data)
    else:
        print("❌ No data found. Run research_metrics_simulation.py first.")

if __name__ == "__main__":
    main()
