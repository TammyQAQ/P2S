#!/usr/bin/env python3
"""
Research Question 2: MEV Reordering Opportunities
Bar chart comparing mean MEV opportunity per block between P2S and Ethereum PoS
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

def plot_mev_reordering(data: Dict):
    """Bar chart: Clear comparison of MEV opportunities"""
    protocols = ['p2s', 'ethereum_pos']
    protocol_labels = ['P2S', 'Ethereum PoS']
    colors = ['#2E86AB', '#A23B72']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Extract MEV data
    mean_mev = []
    std_mev = []
    for protocol in protocols:
        if protocol in data.get('mev_reordering', {}):
            opportunities = data['mev_reordering'][protocol].get('opportunities', [])
            mean_val = np.mean(opportunities) if opportunities else 0
            std_val = np.std(opportunities) if len(opportunities) > 1 else 0
            mean_mev.append(mean_val)
            std_mev.append(std_val)
        else:
            mean_mev.append(0)
            std_mev.append(0)
    
    # Create bar chart with error bars
    bars = ax.bar(protocol_labels, mean_mev, color=colors, alpha=0.8, 
                  edgecolor='black', linewidth=2, yerr=std_mev, capsize=10, error_kw={'linewidth': 2})
    
    # Add value labels
    for bar, val, std in zip(bars, mean_mev, std_mev):
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + std + max(mean_mev) * 0.05,
                   f'{val:.2f} ETH', ha='center', va='bottom', fontsize=13, fontweight='bold')
    
    # Calculate reduction percentage
    if mean_mev[1] > 0:
        reduction = ((mean_mev[1] - mean_mev[0]) / mean_mev[1]) * 100
        ax.text(0.5, 0.95, f'MEV Reduction: {reduction:.1f}%', 
               transform=ax.transAxes, ha='center', fontsize=12, 
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
    
    ax.set_ylabel('Mean MEV Opportunity per Block (ETH)', fontsize=14, fontweight='bold')
    ax.set_title('MEV Reordering Opportunities Comparison', 
                fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    ax.set_ylim(0, max(mean_mev) * 1.3 if mean_mev else 1)
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/mev_reordering.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: figures/mev_reordering.png")
    plt.close()

def main():
    data = load_latest_research_data()
    if data:
        plot_mev_reordering(data)
    else:
        print("❌ No data found. Run research_metrics_simulation.py first.")

if __name__ == "__main__":
    main()
