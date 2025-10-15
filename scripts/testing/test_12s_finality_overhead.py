#!/usr/bin/env python3
"""
P2S 12-Second Finality Overhead Test
Tests the system overhead and latency impact of achieving 12-second finality
"""

import time
import json
import statistics
import threading
from datetime import datetime
from typing import List, Dict, Any, Tuple
import subprocess
import sys
import concurrent.futures

class P2S12SecondOverheadTest:
    def __init__(self):
        self.results = {
            'b1_timing': [],
            'b2_timing': [],
            'total_timing': [],
            'network_overhead': [],
            'cryptographic_overhead': [],
            'consensus_overhead': [],
            'metadata': {
                'test_start': datetime.now().isoformat(),
                'target_finality': 12.0,  # 12 seconds
                'b1_target': 6.0,          # 6 seconds
                'b2_target': 6.0,         # 6 seconds
                'test_duration': 0,
                'total_transactions': 0
            }
        }
    
    def simulate_b1_block_overhead(self, num_transactions: int = 50) -> List[Dict[str, Any]]:
        """Simulate B1 block creation overhead with 6-second target"""
        print(f"[B1] Testing B1 block overhead with {num_transactions} transactions...")
        
        measurements = []
        for i in range(num_transactions):
            print(f"[B1] Transaction {i+1}/{num_transactions}")
            
            # Start timing
            start_time = time.time()
            
            # Simulate B1 block components
            pht_creation = self.simulate_pht_creation()
            network_propagation = self.simulate_network_propagation()
            block_proposal = self.simulate_block_proposal()
            consensus_validation = self.simulate_consensus_validation()
            
            # End timing
            end_time = time.time()
            total_latency = end_time - start_time
            
            measurement = {
                'transaction_id': i + 1,
                'start_time': start_time,
                'end_time': end_time,
                'total_latency': total_latency,
                'pht_creation': pht_creation,
                'network_propagation': network_propagation,
                'block_proposal': block_proposal,
                'consensus_validation': consensus_validation,
                'target_met': total_latency <= 6.0,
                'timestamp': datetime.now().isoformat()
            }
            
            measurements.append(measurement)
            status = "✅" if measurement['target_met'] else "❌"
            print(f"[B1] Transaction {i+1} completed in {total_latency:.3f}s {status}")
        
        return measurements
    
    def simulate_b2_block_overhead(self, num_transactions: int = 50) -> List[Dict[str, Any]]:
        """Simulate B2 block creation overhead with 6-second target"""
        print(f"[B2] Testing B2 block overhead with {num_transactions} transactions...")
        
        measurements = []
        for i in range(num_transactions):
            print(f"[B2] Transaction {i+1}/{num_transactions}")
            
            # Start timing
            start_time = time.time()
            
            # Simulate B2 block components
            mt_creation = self.simulate_mt_creation()
            network_propagation = self.simulate_network_propagation()
            block_proposal = self.simulate_block_proposal()
            consensus_validation = self.simulate_consensus_validation()
            
            # End timing
            end_time = time.time()
            total_latency = end_time - start_time
            
            measurement = {
                'transaction_id': i + 1,
                'start_time': start_time,
                'end_time': end_time,
                'total_latency': total_latency,
                'mt_creation': mt_creation,
                'network_propagation': network_propagation,
                'block_proposal': block_proposal,
                'consensus_validation': consensus_validation,
                'target_met': total_latency <= 6.0,
                'timestamp': datetime.now().isoformat()
            }
            
            measurements.append(measurement)
            status = "✅" if measurement['target_met'] else "❌"
            print(f"[B2] Transaction {i+1} completed in {total_latency:.3f}s {status}")
        
        return measurements
    
    def simulate_pht_creation(self) -> float:
        """Simulate PHT creation with optimized timing"""
        # Simulate cryptographic commitment creation (optimized)
        time.sleep(0.05)  # 50ms for commitment creation
        return 0.05
    
    def simulate_mt_creation(self) -> float:
        """Simulate MT creation with optimized timing"""
        # Simulate proof generation (optimized)
        time.sleep(0.05)  # 50ms for proof generation
        return 0.05
    
    def simulate_network_propagation(self) -> float:
        """Simulate network propagation with optimized timing"""
        # Simulate P2P gossip (optimized for 6s target)
        time.sleep(0.3)  # 300ms for network propagation
        return 0.3
    
    def simulate_block_proposal(self) -> float:
        """Simulate block proposal with optimized timing"""
        # Simulate validator selection and block construction (optimized)
        time.sleep(0.4)  # 400ms for block proposal
        return 0.4
    
    def simulate_consensus_validation(self) -> float:
        """Simulate consensus validation with optimized timing"""
        # Simulate consensus validation (optimized)
        time.sleep(0.25)  # 250ms for consensus validation
        return 0.25
    
    def test_parallel_processing(self, num_transactions: int = 20) -> Dict[str, Any]:
        """Test parallel processing capabilities"""
        print(f"[PARALLEL] Testing parallel processing with {num_transactions} transactions...")
        
        start_time = time.time()
        
        # Test parallel B1 and B2 processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit B1 and B2 tasks in parallel
            b1_future = executor.submit(self.simulate_b1_block_overhead, num_transactions)
            b2_future = executor.submit(self.simulate_b2_block_overhead, num_transactions)
            
            # Wait for completion
            b1_results = b1_future.result()
            b2_results = b2_future.result()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate parallel efficiency
        sequential_time = sum(m['total_latency'] for m in b1_results) + sum(m['total_latency'] for m in b2_results)
        parallel_efficiency = (sequential_time / total_time) * 100 if total_time > 0 else 0
        
        return {
            'total_time': total_time,
            'sequential_time': sequential_time,
            'parallel_efficiency': parallel_efficiency,
            'b1_results': b1_results,
            'b2_results': b2_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def test_network_congestion_impact(self, congestion_levels: List[float] = [0.1, 0.3, 0.5, 0.7]) -> Dict[str, Any]:
        """Test impact of network congestion on 12-second finality"""
        print(f"[CONGESTION] Testing network congestion impact...")
        
        results = {}
        for congestion in congestion_levels:
            print(f"[CONGESTION] Testing {congestion*100:.0f}% congestion level...")
            
            # Simulate congestion by adding delay
            congestion_delay = congestion * 2.0  # Up to 2 seconds delay
            
            start_time = time.time()
            
            # Simulate B1 block with congestion
            b1_start = time.time()
            time.sleep(0.05 + congestion_delay)  # PHT creation + congestion
            b1_end = time.time()
            
            # Simulate B2 block with congestion
            b2_start = time.time()
            time.sleep(0.05 + congestion_delay)  # MT creation + congestion
            b2_end = time.time()
            
            end_time = time.time()
            total_time = end_time - start_time
            
            results[f'{congestion*100:.0f}%'] = {
                'congestion_level': congestion,
                'congestion_delay': congestion_delay,
                'b1_time': b1_end - b1_start,
                'b2_time': b2_end - b2_start,
                'total_time': total_time,
                'target_met': total_time <= 12.0,
                'timestamp': datetime.now().isoformat()
            }
        
        return results
    
    def calculate_statistics(self, measurements: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate timing statistics"""
        latencies = [m['total_latency'] for m in measurements]
        
        return {
            'mean': statistics.mean(latencies),
            'median': statistics.median(latencies),
            'min': min(latencies),
            'max': max(latencies),
            'std_dev': statistics.stdev(latencies) if len(latencies) > 1 else 0,
            'p95': self.percentile(latencies, 95),
            'p99': self.percentile(latencies, 99),
            'target_compliance': sum(1 for m in measurements if m['target_met']) / len(measurements) * 100
        }
    
    def percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def run_comprehensive_test(self, num_transactions: int = 30):
        """Run comprehensive 12-second finality test"""
        print("=" * 80)
        print("P2S 12-SECOND FINALITY OVERHEAD TEST")
        print("=" * 80)
        print(f"Target: 12-second total finality (B1: 6s + B2: 6s)")
        print(f"Testing with {num_transactions} transactions per block")
        print("=" * 80)
        
        start_time = time.time()
        
        # Test B1 block overhead
        print("\n[PHASE 1] B1 Block Overhead Test")
        print("-" * 50)
        b1_measurements = self.simulate_b1_block_overhead(num_transactions)
        self.results['b1_timing'] = b1_measurements
        
        # Test B2 block overhead
        print("\n[PHASE 2] B2 Block Overhead Test")
        print("-" * 50)
        b2_measurements = self.simulate_b2_block_overhead(num_transactions)
        self.results['b2_timing'] = b2_measurements
        
        # Test parallel processing
        print("\n[PHASE 3] Parallel Processing Test")
        print("-" * 50)
        parallel_results = self.test_parallel_processing(num_transactions // 2)
        self.results['parallel_processing'] = parallel_results
        
        # Test network congestion
        print("\n[PHASE 4] Network Congestion Impact Test")
        print("-" * 50)
        congestion_results = self.test_network_congestion_impact()
        self.results['network_congestion'] = congestion_results
        
        end_time = time.time()
        self.results['metadata']['test_duration'] = end_time - start_time
        self.results['metadata']['total_transactions'] = num_transactions * 2
        
        # Calculate statistics
        b1_stats = self.calculate_statistics(b1_measurements)
        b2_stats = self.calculate_statistics(b2_measurements)
        
        # Print results
        self.print_comprehensive_results(b1_stats, b2_stats, parallel_results, congestion_results)
        
        # Save results
        self.save_results()
        
        return b1_stats, b2_stats, parallel_results, congestion_results
    
    def print_comprehensive_results(self, b1_stats: Dict[str, float], b2_stats: Dict[str, float], 
                                   parallel_results: Dict[str, Any], congestion_results: Dict[str, Any]):
        """Print comprehensive test results"""
        print("\n" + "=" * 80)
        print("12-SECOND FINALITY TEST RESULTS")
        print("=" * 80)
        
        # B1 Block Results
        print(f"\n{'B1 BLOCK RESULTS':<50}")
        print("-" * 50)
        print(f"Target Time:           6.0 seconds")
        print(f"Average Time:          {b1_stats['mean']:.3f} seconds")
        print(f"Median Time:           {b1_stats['median']:.3f} seconds")
        print(f"Min Time:              {b1_stats['min']:.3f} seconds")
        print(f"Max Time:              {b1_stats['max']:.3f} seconds")
        print(f"95th Percentile:       {b1_stats['p95']:.3f} seconds")
        print(f"Target Compliance:     {b1_stats['target_compliance']:.1f}%")
        
        # B2 Block Results
        print(f"\n{'B2 BLOCK RESULTS':<50}")
        print("-" * 50)
        print(f"Target Time:           6.0 seconds")
        print(f"Average Time:           {b2_stats['mean']:.3f} seconds")
        print(f"Median Time:           {b2_stats['median']:.3f} seconds")
        print(f"Min Time:               {b2_stats['min']:.3f} seconds")
        print(f"Max Time:               {b2_stats['max']:.3f} seconds")
        print(f"95th Percentile:        {b2_stats['p95']:.3f} seconds")
        print(f"Target Compliance:      {b2_stats['target_compliance']:.1f}%")
        
        # Total Finality Results
        total_avg = b1_stats['mean'] + b2_stats['mean']
        total_compliance = min(b1_stats['target_compliance'], b2_stats['target_compliance'])
        
        print(f"\n{'TOTAL FINALITY RESULTS':<50}")
        print("-" * 50)
        print(f"Target Time:           12.0 seconds")
        print(f"Average Time:           {total_avg:.3f} seconds")
        print(f"Target Compliance:      {total_compliance:.1f}%")
        
        # Parallel Processing Results
        print(f"\n{'PARALLEL PROCESSING RESULTS':<50}")
        print("-" * 50)
        print(f"Parallel Efficiency:    {parallel_results['parallel_efficiency']:.1f}%")
        print(f"Total Parallel Time:     {parallel_results['total_time']:.3f} seconds")
        print(f"Sequential Time:         {parallel_results['sequential_time']:.3f} seconds")
        
        # Network Congestion Results
        print(f"\n{'NETWORK CONGESTION IMPACT':<50}")
        print("-" * 50)
        for level, result in congestion_results.items():
            status = "✅" if result['target_met'] else "❌"
            print(f"{level} Congestion:         {result['total_time']:.3f}s {status}")
        
        # Recommendations
        print(f"\n{'RECOMMENDATIONS':<50}")
        print("-" * 50)
        
        if total_compliance >= 95:
            print("✅ EXCELLENT: 12-second finality target achievable")
        elif total_compliance >= 80:
            print("⚠️  GOOD: 12-second finality mostly achievable with optimization")
        elif total_compliance >= 60:
            print("⚠️  MODERATE: Significant optimization needed")
        else:
            print("❌ POOR: Major redesign required")
        
        print("\nOptimization Priorities:")
        if b1_stats['target_compliance'] < b2_stats['target_compliance']:
            print("1. Optimize B1 block processing")
            print("2. Improve PHT creation and network propagation")
        else:
            print("1. Optimize B2 block processing")
            print("2. Improve MT creation and consensus validation")
        
        print("3. Implement parallel processing")
        print("4. Optimize network protocols")
        print("5. Add hardware acceleration for cryptography")
    
    def save_results(self):
        """Save results to JSON file"""
        import os
        
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/p2s_12s_finality_test_{timestamp}.json"
        
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
        num_transactions = 30
    
    print(f"Starting P2S 12-second finality overhead test with {num_transactions} transactions per block")
    print("This test simulates the system overhead required to achieve 12-second finality")
    
    tester = P2S12SecondOverheadTest()
    b1_stats, b2_stats, parallel_results, congestion_results = tester.run_comprehensive_test(num_transactions)
    
    print("\n[COMPLETE] 12-second finality overhead test finished!")
    print("Check the results above to see if the system can achieve 12-second finality")

if __name__ == "__main__":
    main()
