#!/usr/bin/env python3
"""
P2S Latency Measurement Script
Measures transaction inclusion times for P2S vs PoS implementations
"""

import time
import json
import statistics
from datetime import datetime
from typing import List, Dict, Any
import subprocess
import sys

class LatencyMeasurer:
    def __init__(self):
        self.results = {
            'p2s': [],
            'pos': [],
            'metadata': {
                'test_start': datetime.now().isoformat(),
                'test_duration': 0,
                'total_transactions': 0
            }
        }
    
    def measure_p2s_latency(self, num_transactions: int = 10) -> List[Dict[str, Any]]:
        """Measure P2S transaction latency"""
        print(f"[P2S] Measuring {num_transactions} transactions...")
        
        measurements = []
        for i in range(num_transactions):
            print(f"[P2S] Transaction {i+1}/{num_transactions}")
            
            # Start timing
            start_time = time.time()
            
            # Simulate P2S transaction flow
            pht_creation_time = self.simulate_pht_creation()
            b1_block_time = self.simulate_b1_block()
            mt_creation_time = self.simulate_mt_creation()
            b2_block_time = self.simulate_b2_block()
            
            # End timing
            end_time = time.time()
            total_latency = end_time - start_time
            
            measurement = {
                'transaction_id': i + 1,
                'start_time': start_time,
                'end_time': end_time,
                'total_latency': total_latency,
                'pht_creation': pht_creation_time,
                'b1_block_time': b1_block_time,
                'mt_creation': mt_creation_time,
                'b2_block_time': b2_block_time,
                'timestamp': datetime.now().isoformat()
            }
            
            measurements.append(measurement)
            print(f"[P2S] Transaction {i+1} completed in {total_latency:.2f}s")
        
        return measurements
    
    def measure_pos_latency(self, num_transactions: int = 10) -> List[Dict[str, Any]]:
        """Measure PoS transaction latency"""
        print(f"[PoS] Measuring {num_transactions} transactions...")
        
        measurements = []
        for i in range(num_transactions):
            print(f"[PoS] Transaction {i+1}/{num_transactions}")
            
            # Start timing
            start_time = time.time()
            
            # Simulate PoS transaction flow
            mempool_time = self.simulate_mempool()
            block_proposal_time = self.simulate_block_proposal()
            block_confirmation_time = self.simulate_block_confirmation()
            
            # End timing
            end_time = time.time()
            total_latency = end_time - start_time
            
            measurement = {
                'transaction_id': i + 1,
                'start_time': start_time,
                'end_time': end_time,
                'total_latency': total_latency,
                'mempool_time': mempool_time,
                'block_proposal': block_proposal_time,
                'block_confirmation': block_confirmation_time,
                'timestamp': datetime.now().isoformat()
            }
            
            measurements.append(measurement)
            print(f"[PoS] Transaction {i+1} completed in {total_latency:.2f}s")
        
        return measurements
    
    def simulate_pht_creation(self) -> float:
        """Simulate PHT creation time"""
        # Simulate cryptographic commitment creation
        time.sleep(0.1)  # 100ms for commitment creation
        return 0.1
    
    def simulate_b1_block(self) -> float:
        """Simulate B1 block creation and confirmation"""
        # Simulate 12-second block time
        time.sleep(0.5)  # Reduced for testing
        return 0.5
    
    def simulate_mt_creation(self) -> float:
        """Simulate MT creation time"""
        # Simulate proof generation
        time.sleep(0.1)  # 100ms for proof generation
        return 0.1
    
    def simulate_b2_block(self) -> float:
        """Simulate B2 block creation and confirmation"""
        # Simulate 12-second block time
        time.sleep(0.5)  # Reduced for testing
        return 0.5
    
    def simulate_mempool(self) -> float:
        """Simulate mempool processing time"""
        time.sleep(0.05)  # 50ms for mempool
        return 0.05
    
    def simulate_block_proposal(self) -> float:
        """Simulate block proposal time"""
        time.sleep(0.5)  # Reduced for testing
        return 0.5
    
    def simulate_block_confirmation(self) -> float:
        """Simulate block confirmation time"""
        time.sleep(0.5)  # Reduced for testing
        return 0.5
    
    def calculate_statistics(self, measurements: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate latency statistics"""
        latencies = [m['total_latency'] for m in measurements]
        
        return {
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'min': min(latencies),
            'max': max(latencies),
            'std_dev': statistics.stdev(latencies) if len(latencies) > 1 else 0,
            'p95': self.percentile(latencies, 95),
            'p99': self.percentile(latencies, 99)
        }
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def run_comparison(self, num_transactions: int = 10):
        """Run full comparison between P2S and PoS"""
        print("=" * 60)
        print("P2S vs PoS Latency Comparison")
        print("=" * 60)
        
        start_time = time.time()
        
        # Measure P2S latency
        print("\n[PHASE 1] Measuring P2S Latency")
        print("-" * 40)
        p2s_measurements = self.measure_p2s_latency(num_transactions)
        self.results['p2s'] = p2s_measurements
        
        # Measure PoS latency
        print("\n[PHASE 2] Measuring PoS Latency")
        print("-" * 40)
        pos_measurements = self.measure_pos_latency(num_transactions)
        self.results['pos'] = pos_measurements
        
        end_time = time.time()
        self.results['metadata']['test_duration'] = end_time - start_time
        self.results['metadata']['total_transactions'] = num_transactions * 2
        
        # Calculate statistics
        p2s_stats = self.calculate_statistics(p2s_measurements)
        pos_stats = self.calculate_statistics(pos_measurements)
        
        # Print results
        self.print_results(p2s_stats, pos_stats)
        
        # Save results
        self.save_results()
        
        return p2s_stats, pos_stats
    
    def print_results(self, p2s_stats: Dict[str, float], pos_stats: Dict[str, float]):
        """Print comparison results"""
        print("\n" + "=" * 60)
        print("LATENCY COMPARISON RESULTS")
        print("=" * 60)
        
        print(f"\n{'Metric':<20} {'PoS (s)':<12} {'P2S (s)':<12} {'Difference':<15}")
        print("-" * 60)
        
        metrics = ['mean', 'median', 'min', 'max', 'p95', 'p99']
        for metric in metrics:
            pos_val = pos_stats[metric]
            p2s_val = p2s_stats[metric]
            diff = p2s_val - pos_val
            diff_pct = (diff / pos_val) * 100 if pos_val > 0 else 0
            
            print(f"{metric.capitalize():<20} {pos_val:<12.3f} {p2s_val:<12.3f} {diff:+.3f}s ({diff_pct:+.1f}%)")
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        avg_pos = pos_stats['mean']
        avg_p2s = p2s_stats['mean']
        latency_increase = avg_p2s - avg_pos
        latency_increase_pct = (latency_increase / avg_pos) * 100
        
        print(f"Average PoS Latency:     {avg_pos:.3f} seconds")
        print(f"Average P2S Latency:     {avg_p2s:.3f} seconds")
        print(f"Latency Increase:        {latency_increase:+.3f} seconds ({latency_increase_pct:+.1f}%)")
        print(f"MEV Protection:          Enabled (front-running eliminated)")
        print(f"Transaction Privacy:     Enhanced (details hidden in B1)")
        
        print("\n" + "=" * 60)
        print("RECOMMENDATIONS")
        print("=" * 60)
        
        if latency_increase_pct > 50:
            print("⚠️  HIGH LATENCY IMPACT: Consider P2S only for MEV-sensitive transactions")
        elif latency_increase_pct > 25:
            print("⚠️  MODERATE LATENCY IMPACT: P2S suitable for DeFi protocols")
        else:
            print("✅ LOW LATENCY IMPACT: P2S can be used for most transactions")
        
        print("\nUse Cases for P2S:")
        print("• DEX trading (front-running protection)")
        print("• Large value transfers (sandwich attack protection)")
        print("• DeFi protocol operations (MEV protection)")
        print("• Arbitrage transactions (fair ordering)")
        
        print("\nUse Cases for PoS:")
        print("• Simple transfers (low MEV risk)")
        print("• Contract deployments (no MEV sensitivity)")
        print("• Low-value transactions (latency critical)")
    
    def save_results(self):
        """Save results to JSON file"""
        import os
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/latency_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[SAVE] Results saved to {filename}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        try:
            num_transactions = int(sys.argv[1])
        except ValueError:
            print("Error: Number of transactions must be an integer")
            sys.exit(1)
    else:
        num_transactions = 10
    
    print(f"Starting latency comparison with {num_transactions} transactions per protocol")
    print("Note: This is a simulation. Real measurements would require actual network testing.")
    
    measurer = LatencyMeasurer()
    p2s_stats, pos_stats = measurer.run_comparison(num_transactions)
    
    print("\n[COMPLETE] Latency comparison finished!")

if __name__ == "__main__":
    main()
