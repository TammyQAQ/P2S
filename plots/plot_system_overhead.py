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

# Removed plot_system_overhead function - statistics are printed instead

def main():
    data = load_latest_research_data()
    if data:
        # Statistics are printed by test scripts, no plot needed
        print("System overhead statistics are printed by test_system_overhead.py")
    else:
        print("❌ No data found. Run research_metrics_simulation.py first.")

if __name__ == "__main__":
    main()
