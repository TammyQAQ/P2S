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
        print("No research metrics data found. Run research_metrics_simulation.py first.")
        return None
    latest_file = max(files, key=os.path.getctime)
    with open(latest_file, 'r') as f:
        return json.load(f)

def plot_profit_decentralization(data: Dict):
    """Lorenz Curve: Best visualization for profit distribution"""
    protocols = ['p2s', 'ethereum_pos']
    protocol_labels = ['P2S', 'Ethereum PoS']
    colors = ['#2E86AB', '#A23B72']
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Perfect equality line
    ax.plot([0, 1], [0, 1], 'k--', linewidth=2.5, label='Perfect Equality', alpha=0.6)
    
    # Extract profit data and plot Lorenz curves
    for protocol, label, color in zip(protocols, protocol_labels, colors):
        if protocol in data.get('profit_distribution', {}):
            profits = sorted(data['profit_distribution'][protocol].get('profits', []))
            gini = data['profit_distribution'][protocol].get('gini_coefficient', 0)
            
            if profits and sum(profits) > 0:
                # Calculate Lorenz curve
                n = len(profits)
                cumsum_profits = np.cumsum(profits)
                cumsum_profits = cumsum_profits / cumsum_profits[-1]
                cumsum_pop = np.arange(1, n + 1) / n
                
                ax.plot(cumsum_pop, cumsum_profits, label=f'{label} (Gini: {gini:.3f})', 
                       linewidth=3, color=color, marker='o', markersize=5)
    
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
    data = load_latest_research_data()
    if data:
        plot_profit_decentralization(data)
    else:
        print("❌ No data found. Run research_metrics_simulation.py first.")

if __name__ == "__main__":
    main()
