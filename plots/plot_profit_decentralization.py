#!/usr/bin/env python3
"""
Research Question 1: Profit Decentralization
Lorenz Curve comparing profit distribution between P2S and Ethereum PoS
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
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def load_latest_test_data(data_dir="data"):
    """Load the latest profit decentralization test data"""
    files = glob.glob(f"{data_dir}/profit_decentralization_*.json")
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def plot_profit_decentralization(data: Dict):
    """Lorenz Curve: Best visualization for profit distribution"""
    # Use consistent colors
    P2S_COLOR = '#2ecc71'  # Green
    ETH_COLOR = '#3498db'  # Blue
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Perfect equality line
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2.5, label='Perfect Equality', alpha=0.6)
    
    # Try to get data from test data format first
    if 'p2s_profits' in data and 'current_ethereum_profits' in data:
        # Test data format
        p2s_profits = sorted(list(data['p2s_profits'].values()))
        eth_profits = sorted(list(data['current_ethereum_profits'].values()))
        
        if p2s_profits and eth_profits and sum(p2s_profits) > 0 and sum(eth_profits) > 0:
            # Calculate Lorenz curves
            for profits, label, color, gini in [
                (p2s_profits, 'P2S', P2S_COLOR, data.get('analysis', {}).get('p2s', {}).get('gini_coefficient', 0)),
                (eth_profits, 'Current Ethereum', ETH_COLOR, data.get('analysis', {}).get('current_ethereum', {}).get('gini_coefficient', 0))
            ]:
                n = len(profits)
                cumsum_profits = np.cumsum(profits)
                cumsum_profits = cumsum_profits / cumsum_profits[-1]
                cumsum_pop = np.arange(1, n + 1) / n
                
                ax.plot(cumsum_pop, cumsum_profits, label=f'{label} (Gini: {gini:.3f})', 
                       linewidth=3, color=color, marker='o', markersize=5)
        else:
            print("⚠ No valid profit data found")
            return
    else:
        # Research metrics format
        protocols = ['p2s', 'ethereum_pos']
        protocol_labels = ['P2S', 'Ethereum PoS']
        colors = [P2S_COLOR, ETH_COLOR]
        has_data = False
        
        for protocol, label, color in zip(protocols, protocol_labels, colors):
            if protocol in data.get('profit_distribution', {}):
                profits = sorted(data['profit_distribution'][protocol].get('profits', []))
                gini = data['profit_distribution'][protocol].get('gini_coefficient', 0)
                
                if profits and sum(profits) > 0:
                    has_data = True
                    n = len(profits)
                    cumsum_profits = np.cumsum(profits)
                    cumsum_profits = cumsum_profits / cumsum_profits[-1]
                    cumsum_pop = np.arange(1, n + 1) / n
                    
                    ax.plot(cumsum_pop, cumsum_profits, label=f'{label} (Gini: {gini:.3f})', 
                           linewidth=3, color=color, marker='o', markersize=5)
        
        if not has_data:
            print("⚠ No profit distribution data found")
            return
    
    ax.set_xlabel('Cumulative Fraction of Validators', fontsize=14, fontweight='bold')
    ax.set_ylabel('Cumulative Fraction of Profits', fontsize=14, fontweight='bold')
    ax.set_title('Profit Decentralization: Lorenz Curve Comparison', 
                fontsize=16, fontweight='bold', pad=20)
    ax.legend(loc='lower right', fontsize=12, framealpha=0.9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    
    plt.tight_layout()
    os.makedirs('figures', exist_ok=True)
    plt.savefig('figures/profit_decentralization.png', dpi=300, bbox_inches='tight')
    print("✅ Saved: figures/profit_decentralization.png")
    plt.close()

def main():
    # Try test data first, then research metrics
    data = load_latest_test_data()
    if not data:
        data = load_latest_research_data()
    
    if data:
        plot_profit_decentralization(data)
    else:
        print("❌ No data found. Run test_profit_decentralization.py or research_metrics_simulation.py first.")

if __name__ == "__main__":
    main()
