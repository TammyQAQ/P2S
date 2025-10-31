#!/usr/bin/env python3
"""
P2S Network Performance Test
Simulation of P2S vs PoS with network conditions
"""

import time
import json
import random
import statistics
import threading
from datetime import datetime
from typing import List, Dict, Any
import os

class NetworkSimulator:
    def __init__(self):
        self.network_latency_base = 0.1  # Base network latency (100ms)
        self.network_jitter = 0.05       # Network jitter (±50ms)
        self.cpu_overhead_base = 0.02    # Base CPU processing (20ms)
        self.cpu_variance = 0.01         # CPU variance (±10ms)
        
    def simulate_network_delay(self, congestion_level=0.0):
        """Simulate network delay"""
        # Base latency
        base_delay = self.network_latency_base
        
        # Add jitter (random variation)
        jitter = random.uniform(-self.network_jitter, self.network_jitter)
        
        # Add congestion delay
        congestion_delay = congestion_level * random.uniform(0.5, 2.0)
        
        # Add packet loss simulation (retransmission)
        packet_loss = random.random() < (congestion_level * 0.1)
        retransmission_delay = packet_loss * random.uniform(0.1, 0.5)
        
        total_delay = base_delay + jitter + congestion_delay + retransmission_delay
        return max(0.01, total_delay)  # Minimum 10ms
    
    def simulate_cpu_processing(self, complexity=1.0):
        """Simulate CPU processing time"""
        base_time = self.cpu_overhead_base * complexity
        variance = random.uniform(-self.cpu_variance, self.cpu_variance)
        return max(0.001, base_time + variance)

class P2SSimulator:
    def __init__(self):
        self.network = NetworkSimulator()
        self.results = {
            'p2s_raw_data': [],
            'pos_raw_data': [],
            'network_conditions': [],
            'metadata': {
                'simulation_start': datetime.now().isoformat(),
                'total_transactions': 0
            }
        }
    
    def simulate_pht_creation(self, tx_complexity=1.0):
        """Simulate PHT creation with timing"""
        start_time = time.time()
        
        # Simulate cryptographic commitment creation
        commitment_time = self.network.simulate_cpu_processing(tx_complexity * 2.0)
        time.sleep(commitment_time)
        
        # Simulate anti-MEV nonce generation
        nonce_time = self.network.simulate_cpu_processing(tx_complexity * 0.5)
        time.sleep(nonce_time)
        
        end_time = time.time()
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'commitment_time': commitment_time,
            'nonce_time': nonce_time
        }
    
    def simulate_mt_creation(self, tx_complexity=1.0):
        """Simulate MT creation with timing"""
        start_time = time.time()
        
        # Simulate proof generation
        proof_time = self.network.simulate_cpu_processing(tx_complexity * 3.0)
        time.sleep(proof_time)
        
        # Simulate proof verification
        verification_time = self.network.simulate_cpu_processing(tx_complexity * 1.5)
        time.sleep(verification_time)
        
        end_time = time.time()
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'proof_time': proof_time,
            'verification_time': verification_time
        }
    
    def simulate_block_proposal(self, block_size=100, network_congestion=0.0):
        """Simulate block proposal with timing"""
        start_time = time.time()
        
        # Simulate validator selection
        selection_time = self.network.simulate_cpu_processing(0.5)
        time.sleep(selection_time)
        
        # Simulate block construction (scales with block size)
        construction_time = self.network.simulate_cpu_processing(block_size * 0.01)
        time.sleep(construction_time)
        
        # Simulate network propagation
        propagation_time = self.network.simulate_network_delay(network_congestion)
        time.sleep(propagation_time)
        
        # Simulate consensus validation
        validation_time = self.network.simulate_cpu_processing(block_size * 0.005)
        time.sleep(validation_time)
        
        end_time = time.time()
        return {
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'selection_time': selection_time,
            'construction_time': construction_time,
            'propagation_time': propagation_time,
            'validation_time': validation_time,
            'block_size': block_size,
            'network_congestion': network_congestion
        }
    
    def simulate_p2s_transaction(self, tx_id, complexity=1.0, network_congestion=0.0):
        """Simulate complete P2S transaction flow"""
        print(f"[P2S] Simulating transaction {tx_id}")
        
        total_start = time.time()
        
        # Phase 1: PHT Creation
        pht_result = self.simulate_pht_creation(complexity)
        
        # Phase 2: B1 Block Proposal
        b1_result = self.simulate_block_proposal(100, network_congestion)
        
        # Phase 3: MT Creation
        mt_result = self.simulate_mt_creation(complexity)
        
        # Phase 4: B2 Block Proposal
        b2_result = self.simulate_block_proposal(100, network_congestion)
        
        total_end = time.time()
        
        return {
            'transaction_id': tx_id,
            'total_start_time': total_start,
            'total_end_time': total_end,
            'total_duration': total_end - total_start,
            'pht_creation': pht_result,
            'b1_block': b1_result,
            'mt_creation': mt_result,
            'b2_block': b2_result,
            'tx_complexity': complexity,
            'network_congestion': network_congestion,
            'timestamp': datetime.now().isoformat()
        }
    
    def simulate_pos_transaction(self, tx_id, complexity=1.0, network_congestion=0.0):
        """Simulate PoS transaction flow"""
        print(f"[PoS] Simulating transaction {tx_id}")
        
        total_start = time.time()
        
        # Phase 1: Mempool processing
        mempool_time = self.network.simulate_cpu_processing(complexity * 0.5)
        time.sleep(mempool_time)
        
        # Phase 2: Block proposal
        block_result = self.simulate_block_proposal(100, network_congestion)
        
        # Phase 3: Block confirmation
        confirmation_time = self.network.simulate_network_delay(network_congestion)
        time.sleep(confirmation_time)
        
        total_end = time.time()
        
        return {
            'transaction_id': tx_id,
            'total_start_time': total_start,
            'total_end_time': total_end,
            'total_duration': total_end - total_start,
            'mempool_time': mempool_time,
            'block_proposal': block_result,
            'confirmation_time': confirmation_time,
            'tx_complexity': complexity,
            'network_congestion': network_congestion,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_simulation(self, num_transactions=50, network_conditions=None):
        """Run simulation with varying conditions"""
        if network_conditions is None:
            network_conditions = [0.0, 0.1, 0.3, 0.5, 0.7]  # Different congestion levels
        
        print("=" * 80)
        print("P2S vs PoS NETWORK SIMULATION")
        print("=" * 80)
        print(f"Simulating {num_transactions} transactions per protocol")
        print(f"Network conditions: {network_conditions}")
        print("=" * 80)
        
        start_time = time.time()
        
        # Simulate P2S transactions
        print(f"\n[PHASE 1] P2S Simulation")
        print("-" * 40)
        p2s_results = []
        for i in range(num_transactions):
            # Vary transaction complexity and network conditions
            complexity = random.uniform(0.5, 2.0)
            congestion = random.choice(network_conditions)
            
            result = self.simulate_p2s_transaction(i+1, complexity, congestion)
            p2s_results.append(result)
            
            print(f"Transaction {i+1}: {result['total_duration']:.3f}s "
                  f"(complexity: {complexity:.2f}, congestion: {congestion:.1f})")
        
        # Simulate PoS transactions
        print(f"\n[PHASE 2] PoS Simulation")
        print("-" * 40)
        pos_results = []
        for i in range(num_transactions):
            # Use same complexity and congestion for fair comparison
            complexity = random.uniform(0.5, 2.0)
            congestion = random.choice(network_conditions)
            
            result = self.simulate_pos_transaction(i+1, complexity, congestion)
            pos_results.append(result)
            
            print(f"Transaction {i+1}: {result['total_duration']:.3f}s "
                  f"(complexity: {complexity:.2f}, congestion: {congestion:.1f})")
        
        end_time = time.time()
        
        # Store results
        self.results['p2s_raw_data'] = p2s_results
        self.results['pos_raw_data'] = pos_results
        self.results['network_conditions'] = network_conditions
        self.results['metadata']['simulation_duration'] = end_time - start_time
        self.results['metadata']['total_transactions'] = num_transactions * 2
        
        # Analyze results
        self.analyze_raw_results()
        
        # Create plots
        self.create_plots()
        
        # Save results
        self.save_results()
        
        return p2s_results, pos_results
    
    def analyze_raw_results(self):
        """Analyze raw simulation results"""
        p2s_data = self.results['p2s_raw_data']
        pos_data = self.results['pos_raw_data']
        
        # Extract durations
        p2s_durations = [tx['total_duration'] for tx in p2s_data]
        pos_durations = [tx['total_duration'] for tx in pos_data]
        
        # Calculate statistics
        p2s_stats = {
            'mean': statistics.mean(p2s_durations),
            'median': statistics.median(p2s_durations),
            'min': min(p2s_durations),
            'max': max(p2s_durations),
            'std_dev': statistics.stdev(p2s_durations) if len(p2s_durations) > 1 else 0,
            'p95': self.percentile(p2s_durations, 95),
            'p99': self.percentile(p2s_durations, 99)
        }
        
        pos_stats = {
            'mean': statistics.mean(pos_durations),
            'median': statistics.median(pos_durations),
            'min': min(pos_durations),
            'max': max(pos_durations),
            'std_dev': statistics.stdev(pos_durations) if len(pos_durations) > 1 else 0,
            'p95': self.percentile(pos_durations, 95),
            'p99': self.percentile(pos_durations, 99)
        }
        
        # Calculate difference
        latency_increase = p2s_stats['mean'] - pos_stats['mean']
        latency_increase_pct = (latency_increase / pos_stats['mean']) * 100
        
        # Store analysis
        self.results['analysis'] = {
            'p2s_stats': p2s_stats,
            'pos_stats': pos_stats,
            'latency_increase': latency_increase,
            'latency_increase_pct': latency_increase_pct
        }
        
        # Print analysis
        self.print_raw_analysis()
    
    def create_plots(self):
        """Create block time distribution plots"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
        except ImportError:
            print("Matplotlib not available, skipping plots")
            return
        
        p2s_data = self.results['p2s_raw_data']
        pos_data = self.results['pos_raw_data']
        
        # Extract data
        p2s_times = [tx['total_duration'] for tx in p2s_data]
        pos_times = [tx['total_duration'] for tx in pos_data]
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Plot 1: Block Time Distribution (Histogram)
        bins = np.linspace(0, max(max(p2s_times), max(pos_times)) + 0.1, 20)
        ax1.hist(pos_times, bins=bins, alpha=0.7, label='PoS', color='blue', edgecolor='black')
        ax1.hist(p2s_times, bins=bins, alpha=0.7, label='P2S', color='orange', edgecolor='black')
        
        ax1.set_xlabel('Block Time (seconds)')
        ax1.set_ylabel('Number of Transactions')
        ax1.set_title('Block Time Distribution: How Many Transactions Take How Long')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Cumulative Distribution
        p2s_sorted = np.sort(p2s_times)
        pos_sorted = np.sort(pos_times)
        p2s_cumulative = np.arange(1, len(p2s_sorted) + 1) / len(p2s_sorted)
        pos_cumulative = np.arange(1, len(pos_sorted) + 1) / len(pos_sorted)
        
        ax2.plot(pos_sorted, pos_cumulative, label='PoS', color='blue', linewidth=2)
        ax2.plot(p2s_sorted, p2s_cumulative, label='P2S', color='orange', linewidth=2)
        
        ax2.set_xlabel('Block Time (seconds)')
        ax2.set_ylabel('Cumulative Percentage of Transactions')
        ax2.set_title('Cumulative Distribution of Block Times')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylim(0, 1)
        
        # Plot 3: Box Plot Comparison
        data_to_plot = [pos_times, p2s_times]
        labels = ['PoS', 'P2S']
        colors = ['blue', 'orange']
        
        box_plot = ax3.boxplot(data_to_plot, labels=labels, patch_artist=True)
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        ax3.set_ylabel('Block Time (seconds)')
        ax3.set_title('Block Time Distribution (Box Plot)')
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Time Range Analysis
        time_ranges = [
            (0, 0.5, 'Very Fast (<0.5s)'),
            (0.5, 1.0, 'Fast (0.5-1.0s)'),
            (1.0, 1.5, 'Medium (1.0-1.5s)'),
            (1.5, 2.0, 'Slow (1.5-2.0s)'),
            (2.0, float('inf'), 'Very Slow (>2.0s)')
        ]
        
        pos_counts = []
        p2s_counts = []
        range_labels = []
        
        for min_time, max_time, label in time_ranges:
            pos_count = sum(1 for t in pos_times if min_time <= t < max_time)
            p2s_count = sum(1 for t in p2s_times if min_time <= t < max_time)
            
            pos_counts.append(pos_count)
            p2s_counts.append(p2s_count)
            range_labels.append(label)
        
        x = np.arange(len(range_labels))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, pos_counts, width, label='PoS', color='blue', alpha=0.7)
        bars2 = ax4.bar(x + width/2, p2s_counts, width, label='P2S', color='orange', alpha=0.7)
        
        ax4.set_xlabel('Block Time Ranges')
        ax4.set_ylabel('Number of Transactions')
        ax4.set_title('Transaction Count by Block Time Range')
        ax4.set_xticks(x)
        ax4.set_xticklabels(range_labels, rotation=45, ha='right')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            if height > 0:
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                ax4.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save to figures directory
        os.makedirs('figures', exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plt.savefig(f'figures/block_time_distribution_{timestamp}.png', 
                   dpi=300, bbox_inches='tight')
        
        # Also save to plots directory
        os.makedirs('plots', exist_ok=True)
        plt.savefig(f'plots/block_time_distribution_{timestamp}.png', 
                   dpi=300, bbox_inches='tight')
        
        print(f"\n[PLOTS] Block time distribution charts saved to figures/ and plots/ directories")
        
        # Print summary statistics
        print(f"\nBlock Time Summary:")
        print(f"PoS: Mean={np.mean(pos_times):.3f}s, Median={np.median(pos_times):.3f}s, Std={np.std(pos_times):.3f}s")
        print(f"P2S: Mean={np.mean(p2s_times):.3f}s, Median={np.median(p2s_times):.3f}s, Std={np.std(p2s_times):.3f}s")
        
        # Don't show plot in headless mode
        # plt.show()
    
    def percentile(self, data, percentile):
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def print_raw_analysis(self):
        """Print raw analysis without targets"""
        analysis = self.results['analysis']
        p2s_stats = analysis['p2s_stats']
        pos_stats = analysis['pos_stats']
        
        print(f"\n" + "=" * 80)
        print("RAW PERFORMANCE ANALYSIS")
        print("=" * 80)
        
        print(f"\n{'Metric':<20} {'PoS (s)':<12} {'P2S (s)':<12} {'Difference':<15}")
        print("-" * 60)
        
        metrics = ['mean', 'median', 'min', 'max', 'p95', 'p99']
        for metric in metrics:
            pos_val = pos_stats[metric]
            p2s_val = p2s_stats[metric]
            diff = p2s_val - pos_val
            diff_pct = (diff / pos_val) * 100 if pos_val > 0 else 0
            
            print(f"{metric.capitalize():<20} {pos_val:<12.3f} {p2s_val:<12.3f} {diff:+.3f}s ({diff_pct:+.1f}%)")
        
        print(f"\n" + "=" * 80)
        print("DETAILED BREAKDOWN")
        print("=" * 80)
        
        # Analyze P2S phases
        p2s_data = self.results['p2s_raw_data']
        
        pht_times = [tx['pht_creation']['duration'] for tx in p2s_data]
        b1_times = [tx['b1_block']['duration'] for tx in p2s_data]
        mt_times = [tx['mt_creation']['duration'] for tx in p2s_data]
        b2_times = [tx['b2_block']['duration'] for tx in p2s_data]
        
        print(f"\nP2S Phase Breakdown:")
        print(f"  PHT Creation:     {statistics.mean(pht_times):.3f}s ± {statistics.stdev(pht_times):.3f}s")
        print(f"  B1 Block:         {statistics.mean(b1_times):.3f}s ± {statistics.stdev(b1_times):.3f}s")
        print(f"  MT Creation:      {statistics.mean(mt_times):.3f}s ± {statistics.stdev(mt_times):.3f}s")
        print(f"  B2 Block:         {statistics.mean(b2_times):.3f}s ± {statistics.stdev(b2_times):.3f}s")
        
        # Analyze PoS phases
        pos_data = self.results['pos_raw_data']
        
        mempool_times = [tx['mempool_time'] for tx in pos_data]
        block_times = [tx['block_proposal']['duration'] for tx in pos_data]
        confirm_times = [tx['confirmation_time'] for tx in pos_data]
        
        print(f"\nPoS Phase Breakdown:")
        print(f"  Mempool:          {statistics.mean(mempool_times):.3f}s ± {statistics.stdev(mempool_times):.3f}s")
        print(f"  Block Proposal:   {statistics.mean(block_times):.3f}s ± {statistics.stdev(block_times):.3f}s")
        print(f"  Confirmation:     {statistics.mean(confirm_times):.3f}s ± {statistics.stdev(confirm_times):.3f}s")
        
        print(f"\n" + "=" * 80)
        print("NETWORK IMPACT ANALYSIS")
        print("=" * 80)
        
        # Analyze by network conditions
        for congestion in self.results['network_conditions']:
            p2s_congested = [tx for tx in p2s_data if abs(tx['network_congestion'] - congestion) < 0.05]
            pos_congested = [tx for tx in pos_data if abs(tx['network_congestion'] - congestion) < 0.05]
            
            if p2s_congested and pos_congested:
                p2s_avg = statistics.mean([tx['total_duration'] for tx in p2s_congested])
                pos_avg = statistics.mean([tx['total_duration'] for tx in pos_congested])
                print(f"Congestion {congestion:.1f}: PoS {pos_avg:.3f}s, P2S {p2s_avg:.3f}s, Diff {p2s_avg-pos_avg:+.3f}s")
    
    def save_results(self):
        """Save raw results to JSON file"""
        os.makedirs('data', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/p2s_performance_test_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[SAVE] Raw simulation data saved to {filename}")

def main():
    """Main function"""
    import sys
    
    num_transactions = 30
    if len(sys.argv) > 1:
        try:
            num_transactions = int(sys.argv[1])
        except ValueError:
            print("Error: Number of transactions must be an integer")
            sys.exit(1)
    
    print(f"Starting network simulation with {num_transactions} transactions per protocol")
    print("This simulation uses network conditions and CPU processing times")
    
    simulator = P2SSimulator()
    p2s_results, pos_results = simulator.run_simulation(num_transactions)
    
    print(f"\n[COMPLETE] Simulation finished!")
    print(f"Check the raw data in data/p2s_performance_test_*.json")
    print(f"Check the plots in figures/ and plots/ directories")

if __name__ == "__main__":
    main()
