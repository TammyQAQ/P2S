#!/usr/bin/env python3
"""
System Overhead Test
Evaluates network latency, gas costs, and computational overhead in P2S vs PoS
"""

import json
import random
import statistics
import time
from datetime import datetime
from typing import Dict, List, Tuple
import os

class SystemOverheadSimulator:
    """Simulates system overhead for different consensus mechanisms"""
    
    def __init__(self):
        self.results = {
            'p2s_overhead': [],
            'pos_overhead': [],
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'num_transactions': 0,
                'num_blocks': 0
            }
        }
    
    def simulate_p2s_transaction_overhead(self, tx_complexity: float = 1.0) -> Dict:
        """Simulate P2S transaction overhead"""
        # P2S has two-phase processing: PHT + MT
        
        # Phase 1: PHT Creation
        pht_creation_time = random.uniform(0.01, 0.05) * tx_complexity
        pht_commitment_gas = random.randint(21000, 50000)  # Commitment creation
        pht_network_latency = random.uniform(0.05, 0.15)  # Network propagation
        
        # Phase 2: B1 Block Processing
        b1_processing_time = random.uniform(0.02, 0.08)
        b1_validation_gas = random.randint(10000, 30000)
        b1_network_latency = random.uniform(0.1, 0.2)
        
        # Phase 3: MT Creation
        mt_creation_time = random.uniform(0.02, 0.08) * tx_complexity
        mt_proof_gas = random.randint(30000, 80000)  # Proof generation
        mt_network_latency = random.uniform(0.05, 0.15)
        
        # Phase 4: B2 Block Processing
        b2_processing_time = random.uniform(0.02, 0.08)
        b2_validation_gas = random.randint(10000, 30000)
        b2_network_latency = random.uniform(0.1, 0.2)
        
        total_time = pht_creation_time + b1_processing_time + mt_creation_time + b2_processing_time
        total_network_latency = pht_network_latency + b1_network_latency + mt_network_latency + b2_network_latency
        total_gas = pht_commitment_gas + b1_validation_gas + mt_proof_gas + b2_validation_gas
        
        # Calculate gas cost (assuming 20 gwei gas price)
        gas_price_gwei = 20
        gas_cost_eth = (total_gas * gas_price_gwei) / 1e9
        gas_cost_usd = gas_cost_eth * 2000  # Assuming $2000/ETH
        
        # Computational overhead (CPU cycles)
        cpu_overhead = (pht_creation_time + mt_creation_time) * 1000  # Arbitrary units
        
        return {
            'total_time': total_time,
            'total_network_latency': total_network_latency,
            'total_gas': total_gas,
            'gas_cost_eth': gas_cost_eth,
            'gas_cost_usd': gas_cost_usd,
            'cpu_overhead': cpu_overhead,
            'pht_creation_time': pht_creation_time,
            'b1_processing_time': b1_processing_time,
            'mt_creation_time': mt_creation_time,
            'b2_processing_time': b2_processing_time,
            'pht_commitment_gas': pht_commitment_gas,
            'mt_proof_gas': mt_proof_gas,
            'tx_complexity': tx_complexity
        }
    
    def simulate_pos_transaction_overhead(self, tx_complexity: float = 1.0) -> Dict:
        """Simulate PoS transaction overhead"""
        # PoS has single-phase processing
        
        # Transaction Processing
        tx_processing_time = random.uniform(0.01, 0.03) * tx_complexity
        tx_gas = random.randint(21000, 100000)  # Standard transaction gas
        tx_network_latency = random.uniform(0.1, 0.2)  # Network propagation
        
        # Block Processing
        block_processing_time = random.uniform(0.02, 0.05)
        block_validation_gas = random.randint(5000, 15000)
        block_network_latency = random.uniform(0.1, 0.2)
        
        total_time = tx_processing_time + block_processing_time
        total_network_latency = tx_network_latency + block_network_latency
        total_gas = tx_gas + block_validation_gas
        
        # Calculate gas cost
        gas_price_gwei = 20
        gas_cost_eth = (total_gas * gas_price_gwei) / 1e9
        gas_cost_usd = gas_cost_eth * 2000
        
        # Computational overhead
        cpu_overhead = tx_processing_time * 1000  # Arbitrary units
        
        return {
            'total_time': total_time,
            'total_network_latency': total_network_latency,
            'total_gas': total_gas,
            'gas_cost_eth': gas_cost_eth,
            'gas_cost_usd': gas_cost_usd,
            'cpu_overhead': cpu_overhead,
            'tx_processing_time': tx_processing_time,
            'block_processing_time': block_processing_time,
            'tx_gas': tx_gas,
            'tx_complexity': tx_complexity
        }
    
    def simulate_network_conditions(self, base_latency: float, congestion: float) -> float:
        """Simulate network conditions"""
        # Add congestion-based latency
        congestion_latency = base_latency * (1 + congestion * 2)
        
        # Add jitter
        jitter = random.uniform(-0.05, 0.05)
        
        return max(0.01, congestion_latency + jitter)
    
    def simulate_block_overhead(self, num_transactions: int, protocol: str = 'p2s') -> Dict:
        """Simulate block-level overhead"""
        if protocol == 'p2s':
            # P2S: Two blocks (B1 + B2)
            b1_size = num_transactions * 0.5  # PHTs are smaller
            b2_size = num_transactions * 1.0  # MTs are full size
            
            b1_processing = random.uniform(0.1, 0.3) * (b1_size / 100)
            b2_processing = random.uniform(0.1, 0.3) * (b2_size / 100)
            
            b1_network = random.uniform(0.2, 0.5) * (b1_size / 100)
            b2_network = random.uniform(0.2, 0.5) * (b2_size / 100)
            
            total_processing = b1_processing + b2_processing
            total_network = b1_network + b2_network
            
            # Gas overhead for two blocks
            b1_gas = int(b1_size * 1000)
            b2_gas = int(b2_size * 1000)
            total_gas = b1_gas + b2_gas
            
            return {
                'total_processing_time': total_processing,
                'total_network_latency': total_network,
                'total_gas': total_gas,
                'b1_processing': b1_processing,
                'b2_processing': b2_processing,
                'b1_network': b1_network,
                'b2_network': b2_network,
                'num_blocks': 2
            }
        else:  # PoS
            # PoS: Single block
            block_size = num_transactions * 1.0
            
            block_processing = random.uniform(0.1, 0.3) * (block_size / 100)
            block_network = random.uniform(0.2, 0.5) * (block_size / 100)
            
            total_gas = int(block_size * 1000)
            
            return {
                'total_processing_time': block_processing,
                'total_network_latency': block_network,
                'total_gas': total_gas,
                'num_blocks': 1
            }
    
    def run_simulation(self, num_transactions: int = 100, num_blocks: int = 100, 
                      network_congestion: float = 0.0):
        """Run complete system overhead simulation"""
        print("=" * 80)
        print("SYSTEM OVERHEAD SIMULATION")
        print("=" * 80)
        print(f"Transactions: {num_transactions}, Blocks: {num_blocks}")
        print(f"Network Congestion: {network_congestion:.1%}")
        print("=" * 80)
        
        self.results['metadata']['num_transactions'] = num_transactions
        self.results['metadata']['num_blocks'] = num_blocks
        self.results['metadata']['network_congestion'] = network_congestion
        
        p2s_tx_overheads = []
        pos_tx_overheads = []
        p2s_block_overheads = []
        pos_block_overheads = []
        
        # Simulate transaction-level overhead
        print("\n[TRANSACTION OVERHEAD]")
        for i in range(num_transactions):
            complexity = random.uniform(0.5, 2.0)
            
            p2s_overhead = self.simulate_p2s_transaction_overhead(complexity)
            pos_overhead = self.simulate_pos_transaction_overhead(complexity)
            
            # Apply network conditions
            p2s_overhead['total_network_latency'] = self.simulate_network_conditions(
                p2s_overhead['total_network_latency'], network_congestion
            )
            pos_overhead['total_network_latency'] = self.simulate_network_conditions(
                pos_overhead['total_network_latency'], network_congestion
            )
            
            p2s_tx_overheads.append(p2s_overhead)
            pos_tx_overheads.append(pos_overhead)
        
        # Simulate block-level overhead
        print("\n[BLOCK OVERHEAD]")
        for block_num in range(num_blocks):
            p2s_block = self.simulate_block_overhead(num_transactions, 'p2s')
            pos_block = self.simulate_block_overhead(num_transactions, 'pos')
            
            # Apply network conditions
            p2s_block['total_network_latency'] = self.simulate_network_conditions(
                p2s_block['total_network_latency'], network_congestion
            )
            pos_block['total_network_latency'] = self.simulate_network_conditions(
                pos_block['total_network_latency'], network_congestion
            )
            
            p2s_block_overheads.append(p2s_block)
            pos_block_overheads.append(pos_block)
        
        self.results['p2s_overhead'] = {
            'transaction': p2s_tx_overheads,
            'block': p2s_block_overheads
        }
        self.results['pos_overhead'] = {
            'transaction': pos_tx_overheads,
            'block': pos_block_overheads
        }
        
        # Calculate aggregate statistics
        self.calculate_aggregate_stats()
        
        # Print analysis
        self.print_analysis()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def calculate_aggregate_stats(self):
        """Calculate aggregate statistics"""
        p2s_tx = self.results['p2s_overhead']['transaction']
        pos_tx = self.results['pos_overhead']['transaction']
        p2s_block = self.results['p2s_overhead']['block']
        pos_block = self.results['pos_overhead']['block']
        
        def aggregate_tx(overheads, key):
            values = [o[key] for o in overheads]
            return {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
                'min': min(values),
                'max': max(values),
                'p95': sorted(values)[int(len(values) * 0.95)] if values else 0.0
            }
        
        def aggregate_block(overheads, key):
            values = [o[key] for o in overheads]
            return {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
                'min': min(values),
                'max': max(values)
            }
        
        self.results['analysis'] = {
            'transaction': {
                'p2s': {
                    'total_time': aggregate_tx(p2s_tx, 'total_time'),
                    'network_latency': aggregate_tx(p2s_tx, 'total_network_latency'),
                    'gas': aggregate_tx(p2s_tx, 'total_gas'),
                    'gas_cost_usd': aggregate_tx(p2s_tx, 'gas_cost_usd'),
                    'cpu_overhead': aggregate_tx(p2s_tx, 'cpu_overhead')
                },
                'pos': {
                    'total_time': aggregate_tx(pos_tx, 'total_time'),
                    'network_latency': aggregate_tx(pos_tx, 'total_network_latency'),
                    'gas': aggregate_tx(pos_tx, 'total_gas'),
                    'gas_cost_usd': aggregate_tx(pos_tx, 'gas_cost_usd'),
                    'cpu_overhead': aggregate_tx(pos_tx, 'cpu_overhead')
                }
            },
            'block': {
                'p2s': {
                    'processing_time': aggregate_block(p2s_block, 'total_processing_time'),
                    'network_latency': aggregate_block(p2s_block, 'total_network_latency'),
                    'gas': aggregate_block(p2s_block, 'total_gas')
                },
                'pos': {
                    'processing_time': aggregate_block(pos_block, 'total_processing_time'),
                    'network_latency': aggregate_block(pos_block, 'total_network_latency'),
                    'gas': aggregate_block(pos_block, 'total_gas')
                }
            }
        }
        
        # Calculate overhead ratios
        p2s_tx_time = self.results['analysis']['transaction']['p2s']['total_time']['mean']
        pos_tx_time = self.results['analysis']['transaction']['pos']['total_time']['mean']
        time_overhead = ((p2s_tx_time - pos_tx_time) / pos_tx_time) * 100 if pos_tx_time > 0 else 0.0
        
        p2s_tx_gas = self.results['analysis']['transaction']['p2s']['gas']['mean']
        pos_tx_gas = self.results['analysis']['transaction']['pos']['gas']['mean']
        gas_overhead = ((p2s_tx_gas - pos_tx_gas) / pos_tx_gas) * 100 if pos_tx_gas > 0 else 0.0
        
        p2s_tx_cost = self.results['analysis']['transaction']['p2s']['gas_cost_usd']['mean']
        pos_tx_cost = self.results['analysis']['transaction']['pos']['gas_cost_usd']['mean']
        cost_overhead = ((p2s_tx_cost - pos_tx_cost) / pos_tx_cost) * 100 if pos_tx_cost > 0 else 0.0
        
        self.results['analysis']['overhead_ratios'] = {
            'time_overhead_pct': time_overhead,
            'gas_overhead_pct': gas_overhead,
            'cost_overhead_pct': cost_overhead
        }
    
    def print_analysis(self):
        """Print analysis results"""
        print("\n" + "=" * 80)
        print("SYSTEM OVERHEAD ANALYSIS")
        print("=" * 80)
        
        analysis = self.results['analysis']
        
        print(f"\n{'Metric':<30} {'P2S':<20} {'PoS':<20} {'Overhead %':<15}")
        print("-" * 85)
        
        # Transaction-level metrics
        p2s_tx_time = analysis['transaction']['p2s']['total_time']['mean']
        pos_tx_time = analysis['transaction']['pos']['total_time']['mean']
        tx_time_oh = analysis['overhead_ratios']['time_overhead_pct']
        print(f"{'Tx Processing Time (s)':<30} {p2s_tx_time:<20.4f} {pos_tx_time:<20.4f} {tx_time_oh:<15.1f}")
        
        p2s_tx_lat = analysis['transaction']['p2s']['network_latency']['mean']
        pos_tx_lat = analysis['transaction']['pos']['network_latency']['mean']
        tx_lat_oh = ((p2s_tx_lat - pos_tx_lat) / pos_tx_lat * 100) if pos_tx_lat > 0 else 0.0
        print(f"{'Tx Network Latency (s)':<30} {p2s_tx_lat:<20.4f} {pos_tx_lat:<20.4f} {tx_lat_oh:<15.1f}")
        
        p2s_tx_gas = analysis['transaction']['p2s']['gas']['mean']
        pos_tx_gas = analysis['transaction']['pos']['gas']['mean']
        tx_gas_oh = analysis['overhead_ratios']['gas_overhead_pct']
        print(f"{'Tx Gas (units)':<30} {p2s_tx_gas:<20.0f} {pos_tx_gas:<20.0f} {tx_gas_oh:<15.1f}")
        
        p2s_tx_cost = analysis['transaction']['p2s']['gas_cost_usd']['mean']
        pos_tx_cost = analysis['transaction']['pos']['gas_cost_usd']['mean']
        tx_cost_oh = analysis['overhead_ratios']['cost_overhead_pct']
        print(f"{'Tx Cost (USD)':<30} ${p2s_tx_cost:<19.4f} ${pos_tx_cost:<19.4f} {tx_cost_oh:<15.1f}")
        
        p2s_tx_cpu = analysis['transaction']['p2s']['cpu_overhead']['mean']
        pos_tx_cpu = analysis['transaction']['pos']['cpu_overhead']['mean']
        tx_cpu_oh = ((p2s_tx_cpu - pos_tx_cpu) / pos_tx_cpu * 100) if pos_tx_cpu > 0 else 0.0
        print(f"{'Tx CPU Overhead':<30} {p2s_tx_cpu:<20.2f} {pos_tx_cpu:<20.2f} {tx_cpu_oh:<15.1f}")
        
        # Block-level metrics
        print(f"\n{'BLOCK-LEVEL METRICS':<30}")
        print("-" * 85)
        
        p2s_blk_time = analysis['block']['p2s']['processing_time']['mean']
        pos_blk_time = analysis['block']['pos']['processing_time']['mean']
        blk_time_oh = ((p2s_blk_time - pos_blk_time) / pos_blk_time * 100) if pos_blk_time > 0 else 0.0
        print(f"{'Block Processing (s)':<30} {p2s_blk_time:<20.4f} {pos_blk_time:<20.4f} {blk_time_oh:<15.1f}")
        
        p2s_blk_lat = analysis['block']['p2s']['network_latency']['mean']
        pos_blk_lat = analysis['block']['pos']['network_latency']['mean']
        blk_lat_oh = ((p2s_blk_lat - pos_blk_lat) / pos_blk_lat * 100) if pos_blk_lat > 0 else 0.0
        print(f"{'Block Network Latency (s)':<30} {p2s_blk_lat:<20.4f} {pos_blk_lat:<20.4f} {blk_lat_oh:<15.1f}")
        
        p2s_blk_gas = analysis['block']['p2s']['gas']['mean']
        pos_blk_gas = analysis['block']['pos']['gas']['mean']
        blk_gas_oh = ((p2s_blk_gas - pos_blk_gas) / pos_blk_gas * 100) if pos_blk_gas > 0 else 0.0
        print(f"{'Block Gas (units)':<30} {p2s_blk_gas:<20.0f} {pos_blk_gas:<20.0f} {blk_gas_oh:<15.1f}")
        
        print("\n" + "=" * 80)
        print("INTERPRETATION:")
        print("=" * 80)
        print("• Processing Time: Time to process transaction/block")
        print("• Network Latency: Time for network propagation")
        print("• Gas: Computational cost in gas units")
        print("• Cost: Financial cost in USD")
        print("• CPU Overhead: Computational resource usage")
        print("=" * 80)
    
    def save_results(self):
        """Save results to JSON file"""
        os.makedirs('data', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/system_overhead_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[SAVE] Results saved to {filename}")

def main():
    """Main function"""
    import sys
    
    num_transactions = 100
    num_blocks = 100
    congestion = 0.0
    
    if len(sys.argv) > 1:
        try:
            num_transactions = int(sys.argv[1])
        except ValueError:
            print("Error: Number of transactions must be an integer")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            num_blocks = int(sys.argv[2])
        except ValueError:
            print("Error: Number of blocks must be an integer")
            sys.exit(1)
    
    if len(sys.argv) > 3:
        try:
            congestion = float(sys.argv[3])
        except ValueError:
            print("Error: Network congestion must be a float (0.0-1.0)")
            sys.exit(1)
    
    print(f"Starting system overhead simulation...")
    print(f"Transactions: {num_transactions}, Blocks: {num_blocks}, Congestion: {congestion:.1%}")
    
    simulator = SystemOverheadSimulator()
    results = simulator.run_simulation(num_transactions, num_blocks, congestion)
    
    print(f"\n[COMPLETE] Simulation finished!")
    print(f"Check results in data/system_overhead_*.json")

if __name__ == "__main__":
    main()

