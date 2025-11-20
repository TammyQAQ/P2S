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

def print_mev_reordering_stats(data: Dict):
    """Print MEV reordering statistics instead of plotting"""
    protocols = ['p2s', 'ethereum_pos']
    protocol_labels = ['P2S', 'Ethereum PoS']
    
    print("\n" + "=" * 80)
    print("MEV REORDERING STATISTICS")
    print("=" * 80)
    
    mean_mev = []
    std_mev = []
    for protocol, label in zip(protocols, protocol_labels):
        if protocol in data.get('mev_reordering', {}):
            opportunities = data['mev_reordering'][protocol].get('opportunities', [])
            mean_val = np.mean(opportunities) if opportunities else 0
            std_val = np.std(opportunities) if len(opportunities) > 1 else 0
            mean_mev.append(mean_val)
            std_mev.append(std_val)
            print(f"\n{label}:")
            print(f"  Mean MEV Opportunity: {mean_val:.2f} ETH")
            print(f"  Std Dev: {std_val:.2f} ETH")
        else:
            mean_mev.append(0)
            std_mev.append(0)
    
    if mean_mev[1] > 0:
        reduction = ((mean_mev[1] - mean_mev[0]) / mean_mev[1]) * 100
        print(f"\nMEV Reduction: {reduction:.1f}%")
    print("=" * 80)

def main():
    data = load_latest_research_data()
    if data:
        print_mev_reordering_stats(data)
    else:
        print("❌ No data found. Run research_metrics_simulation.py first.")

if __name__ == "__main__":
    main()
