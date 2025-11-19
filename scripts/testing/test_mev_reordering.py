#!/usr/bin/env python3
"""
MEV Reordering Test
Measures transaction reordering opportunities and MEV extraction in P2S vs Current Ethereum
Note: Current Ethereum is ~90% Flashbots/MEV-Boost, so we simulate it as such
"""

import json
import random
import statistics
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import os
import hashlib

class MEVReorderingSimulator:
    """Simulates MEV extraction through transaction reordering"""
    
    def __init__(self):
        self.results = {
            'p2s_reordering': [],
            'current_ethereum_reordering': [],
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'num_transactions': 0,
                'num_blocks': 0,
                'description': 'Current Ethereum uses MEV-Boost/Flashbots relays (post-2023)'
            }
        }
    
    def create_transaction(self, tx_id: int, value: float, gas_price: int, 
                          tx_type: str = 'normal') -> Dict:
        """Create a transaction with MEV potential"""
        tx_hash = hashlib.sha256(f"tx_{tx_id}_{time.time()}".encode()).hexdigest()
        
        # Calculate MEV potential based on transaction characteristics
        mev_potential = 0.0
        if tx_type == 'arbitrage':
            mev_potential = value * 0.05  # 5% arbitrage opportunity
        elif tx_type == 'liquidation':
            mev_potential = value * 0.10  # 10% liquidation bonus
        elif tx_type == 'sandwich':
            mev_potential = value * 0.03  # 3% sandwich profit
        elif tx_type == 'frontrun':
            mev_potential = value * 0.02  # 2% front-running profit
        
        return {
            'tx_id': tx_id,
            'tx_hash': tx_hash,
            'sender': f"0x{random.getrandbits(160):040x}",
            'recipient': f"0x{random.getrandbits(160):040x}",
            'value': value,
            'gas_price': gas_price,
            'timestamp': time.time(),
            'tx_type': tx_type,
            'mev_potential': mev_potential,
            'original_position': tx_id  # Original position in mempool
        }
    
    def create_transaction_pool(self, num_transactions: int) -> List[Dict]:
        """Create a pool of transactions with varying MEV potential"""
        transactions = []
        
        # Create mix of transaction types
        tx_types = ['normal'] * 70 + ['arbitrage'] * 10 + ['liquidation'] * 10 + ['sandwich'] * 5 + ['frontrun'] * 5
        
        for i in range(num_transactions):
            tx_type = random.choice(tx_types)
            value = random.uniform(100, 10000) if tx_type == 'normal' else random.uniform(1000, 50000)
            gas_price = random.randint(20, 100) if tx_type == 'normal' else random.randint(50, 200)
            
            tx = self.create_transaction(i, value, gas_price, tx_type)
            transactions.append(tx)
        
        return transactions
    
    def simulate_p2s_ordering(self, transactions: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Simulate P2S transaction ordering (MEV-resistant)"""
        # P2S: Transactions are ordered by PHT submission time and gas price
        # MEV extraction is difficult because details are hidden
        
        # Sort by timestamp (first come, first served) and gas price
        ordered_txs = sorted(transactions, key=lambda x: (x['timestamp'], -x['gas_price']))
        
        # Calculate reordering metrics
        reordering_events = []
        mev_extracted = 0.0
        
        for i, tx in enumerate(ordered_txs):
            original_pos = tx['original_position']
            new_pos = i
            
            if original_pos != new_pos:
                reordering_events.append({
                    'tx_id': tx['tx_id'],
                    'original_position': original_pos,
                    'new_position': new_pos,
                    'reordering_distance': abs(original_pos - new_pos),
                    'mev_potential': tx['mev_potential']
                })
            
            # P2S: Very limited MEV extraction due to hidden details
            # Only small MEV from gas price differences
            if tx['tx_type'] != 'normal' and random.random() < 0.1:  # 10% chance
                mev_extracted += tx['mev_potential'] * 0.1  # Only 10% of potential
        
        metrics = {
            'total_reorderings': len(reordering_events),
            'reordering_rate': len(reordering_events) / len(transactions) if transactions else 0.0,
            'avg_reordering_distance': statistics.mean([e['reordering_distance'] for e in reordering_events]) if reordering_events else 0.0,
            'mev_extracted': mev_extracted,
            'mev_extraction_rate': mev_extracted / sum(tx['mev_potential'] for tx in transactions) if transactions else 0.0,
            'entropy': self.calculate_entropy(ordered_txs)
        }
        
        return ordered_txs, metrics
    
    def simulate_pos_ordering(self, transactions: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Simulate PoS transaction ordering (MEV-vulnerable)"""
        # PoS: Validators can see all transaction details and reorder for MEV
        
        # Validator sees all transactions and reorders to maximize MEV
        # Sort by MEV potential (descending) and gas price
        ordered_txs = sorted(transactions, key=lambda x: (-x['mev_potential'], -x['gas_price']))
        
        # Calculate reordering metrics
        reordering_events = []
        mev_extracted = 0.0
        
        for i, tx in enumerate(ordered_txs):
            original_pos = tx['original_position']
            new_pos = i
            
            if original_pos != new_pos:
                reordering_events.append({
                    'tx_id': tx['tx_id'],
                    'original_position': original_pos,
                    'new_position': new_pos,
                    'reordering_distance': abs(original_pos - new_pos),
                    'mev_potential': tx['mev_potential']
                })
            
            # PoS: High MEV extraction rate
            if tx['tx_type'] != 'normal':
                extraction_rate = 0.7 if tx['tx_type'] == 'arbitrage' else 0.5
                mev_extracted += tx['mev_potential'] * extraction_rate
        
        metrics = {
            'total_reorderings': len(reordering_events),
            'reordering_rate': len(reordering_events) / len(transactions) if transactions else 0.0,
            'avg_reordering_distance': statistics.mean([e['reordering_distance'] for e in reordering_events]) if reordering_events else 0.0,
            'mev_extracted': mev_extracted,
            'mev_extraction_rate': mev_extracted / sum(tx['mev_potential'] for tx in transactions) if transactions else 0.0,
            'entropy': self.calculate_entropy(ordered_txs)
        }
        
        return ordered_txs, metrics
    
    def simulate_current_ethereum_ordering(self, transactions: List[Dict]) -> Tuple[List[Dict], Dict]:
        """Simulate Current Ethereum transaction ordering (MEV-Boost/Flashbots relays)"""
        # Current Ethereum: All blocks use MEV-Boost relays (Flashbots, etc.)
        # This is the standard way blocks are built post-2023
        
        # Separate transactions by MEV potential
        high_mev_txs = [tx for tx in transactions if tx['mev_potential'] > 10]
        normal_txs = [tx for tx in transactions if tx['mev_potential'] <= 10]
        
        # High MEV transactions prioritized through relays
        high_mev_ordered = sorted(high_mev_txs, key=lambda x: (-x['mev_potential'], -x['gas_price']))
        normal_ordered = sorted(normal_txs, key=lambda x: -x['gas_price'])
        
        ordered_txs = high_mev_ordered + normal_ordered
        
        # MEV extraction rates through relays
        mev_extraction_rate_high = 0.85  # High-value MEV transactions
        mev_extraction_rate_low = 0.25   # Lower-value MEV transactions
        
        # Calculate reordering metrics
        reordering_events = []
        mev_extracted = 0.0
        
        for i, tx in enumerate(ordered_txs):
            original_pos = tx['original_position']
            new_pos = i
            
            if original_pos != new_pos:
                reordering_events.append({
                    'tx_id': tx['tx_id'],
                    'original_position': original_pos,
                    'new_position': new_pos,
                    'reordering_distance': abs(original_pos - new_pos),
                    'mev_potential': tx['mev_potential']
                })
            
            # Extract MEV based on transaction type
            if tx['mev_potential'] > 10:
                mev_extracted += tx['mev_potential'] * mev_extraction_rate_high
            elif tx['tx_type'] != 'normal':
                mev_extracted += tx['mev_potential'] * mev_extraction_rate_low
        
        metrics = {
            'total_reorderings': len(reordering_events),
            'reordering_rate': len(reordering_events) / len(transactions) if transactions else 0.0,
            'avg_reordering_distance': statistics.mean([e['reordering_distance'] for e in reordering_events]) if reordering_events else 0.0,
            'mev_extracted': mev_extracted,
            'mev_extraction_rate': mev_extracted / sum(tx['mev_potential'] for tx in transactions) if transactions else 0.0,
            'entropy': self.calculate_entropy(ordered_txs)
        }
        
        return ordered_txs, metrics
    
    def calculate_entropy(self, transactions: List[Dict]) -> float:
        """Calculate ordering entropy (higher = more random/less predictable)"""
        if len(transactions) < 2:
            return 0.0
        
        # Calculate position changes
        position_changes = []
        for i, tx in enumerate(transactions):
            original_pos = tx['original_position']
            new_pos = i
            if original_pos != new_pos:
                position_changes.append(abs(original_pos - new_pos))
        
        if not position_changes:
            return 0.0
        
        # Entropy based on variance of position changes
        if len(position_changes) > 1:
            variance = statistics.variance(position_changes)
            entropy = variance / (len(transactions) ** 2)  # Normalized
        else:
            entropy = 0.0
        
        return entropy
    
    def run_simulation(self, num_transactions: int = 500, num_blocks: int = 10):
        """Run complete MEV reordering simulation"""
        print("=" * 80)
        print("MEV REORDERING SIMULATION")
        print("=" * 80)
        print(f"Transactions per block: {num_transactions}, Blocks: {num_blocks}")
        print("=" * 80)
        
        self.results['metadata']['num_transactions'] = num_transactions
        self.results['metadata']['num_blocks'] = num_blocks
        
        all_p2s_metrics = []
        all_ethereum_metrics = []
        
        for block_num in range(num_blocks):
            print(f"\n[BLOCK {block_num + 1}/{num_blocks}]")
            
            # Create transaction pool
            transactions = self.create_transaction_pool(num_transactions)
            
            # Add small random delays to simulate submission order
            for i, tx in enumerate(transactions):
                tx['timestamp'] = time.time() + random.uniform(0, 1.0) * (i / len(transactions))
            
            # Simulate each protocol
            p2s_ordered, p2s_metrics = self.simulate_p2s_ordering(transactions.copy())
            ethereum_ordered, ethereum_metrics = self.simulate_current_ethereum_ordering(transactions.copy())
            
            p2s_metrics['block_number'] = block_num
            ethereum_metrics['block_number'] = block_num
            
            all_p2s_metrics.append(p2s_metrics)
            all_ethereum_metrics.append(ethereum_metrics)
            
            print(f"  P2S: {p2s_metrics['reordering_rate']:.1%} reordering, {p2s_metrics['mev_extraction_rate']:.1%} MEV extracted")
            print(f"  Current Ethereum: {ethereum_metrics['reordering_rate']:.1%} reordering, {ethereum_metrics['mev_extraction_rate']:.1%} MEV extracted")
        
        self.results['p2s_reordering'] = all_p2s_metrics
        self.results['current_ethereum_reordering'] = all_ethereum_metrics
        
        # Calculate aggregate statistics
        self.calculate_aggregate_stats()
        
        # Print analysis
        self.print_analysis()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def calculate_aggregate_stats(self):
        """Calculate aggregate statistics across all blocks"""
        p2s_data = self.results['p2s_reordering']
        ethereum_data = self.results['current_ethereum_reordering']
        
        def aggregate(metrics_list, key):
            values = [m[key] for m in metrics_list]
            return {
                'mean': statistics.mean(values),
                'median': statistics.median(values),
                'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0,
                'min': min(values),
                'max': max(values)
            }
        
        self.results['analysis'] = {
            'p2s': {
                'reordering_rate': aggregate(p2s_data, 'reordering_rate'),
                'mev_extraction_rate': aggregate(p2s_data, 'mev_extraction_rate'),
                'avg_reordering_distance': aggregate(p2s_data, 'avg_reordering_distance'),
                'entropy': aggregate(p2s_data, 'entropy'),
                'total_mev_extracted': sum(m['mev_extracted'] for m in p2s_data)
            },
            'current_ethereum': {
                'reordering_rate': aggregate(ethereum_data, 'reordering_rate'),
                'mev_extraction_rate': aggregate(ethereum_data, 'mev_extraction_rate'),
                'avg_reordering_distance': aggregate(ethereum_data, 'avg_reordering_distance'),
                'entropy': aggregate(ethereum_data, 'entropy'),
                'total_mev_extracted': sum(m['mev_extracted'] for m in ethereum_data)
            }
        }
    
    def print_analysis(self):
        """Print analysis results"""
        print("\n" + "=" * 80)
        print("MEV REORDERING ANALYSIS")
        print("=" * 80)
        
        analysis = self.results['analysis']
        
        print(f"\n{'Metric':<35} {'P2S':<25} {'Current Ethereum':<25}")
        print("-" * 85)
        
        eth_analysis = analysis['current_ethereum']
        
        # Reordering Rate
        p2s_rr = analysis['p2s']['reordering_rate']['mean']
        eth_rr = eth_analysis['reordering_rate']['mean']
        print(f"{'Reordering Rate (mean)':<35} {p2s_rr:<25.3f} {eth_rr:<25.3f}")
        
        # MEV Extraction Rate
        p2s_mer = analysis['p2s']['mev_extraction_rate']['mean']
        eth_mer = eth_analysis['mev_extraction_rate']['mean']
        print(f"{'MEV Extraction Rate (mean)':<35} {p2s_mer:<25.3f} {eth_mer:<25.3f}")
        
        # Average Reordering Distance
        p2s_ard = analysis['p2s']['avg_reordering_distance']['mean']
        eth_ard = eth_analysis['avg_reordering_distance']['mean']
        print(f"{'Avg Reordering Distance':<35} {p2s_ard:<25.2f} {eth_ard:<25.2f}")
        
        # Total MEV Extracted
        p2s_tme = analysis['p2s']['total_mev_extracted']
        eth_tme = eth_analysis['total_mev_extracted']
        print(f"{'Total MEV Extracted':<35} {p2s_tme:<25.2f} {eth_tme:<25.2f}")
        
        # Entropy
        p2s_ent = analysis['p2s']['entropy']['mean']
        eth_ent = eth_analysis['entropy']['mean']
        print(f"{'Ordering Entropy (mean)':<35} {p2s_ent:<25.4f} {eth_ent:<25.4f}")
        
        print(f"\nNote: Current Ethereum simulated as post-2023 Ethereum using MEV-Boost/Flashbots relays")
        
        print("\n" + "=" * 80)
        print("INTERPRETATION:")
        print("=" * 80)
        print("• Lower Reordering Rate = Less transaction reordering")
        print("• Lower MEV Extraction Rate = Less MEV extracted by validators")
        print("• Lower Avg Reordering Distance = Smaller position changes")
        print("• Higher Entropy = More random/unpredictable ordering")
        print("=" * 80)
    
    def save_results(self):
        """Save results to JSON file"""
        os.makedirs('data', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/mev_reordering_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[SAVE] Results saved to {filename}")

def main():
    """Main function"""
    import sys
    
    num_transactions = 500
    num_blocks = 10
    
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
    
    print(f"Starting MEV reordering simulation...")
    print(f"Transactions per block: {num_transactions}, Blocks: {num_blocks}")
    
    simulator = MEVReorderingSimulator()
    results = simulator.run_simulation(num_transactions, num_blocks)
    
    print(f"\n[COMPLETE] Simulation finished!")
    print(f"Check results in data/mev_reordering_*.json")

if __name__ == "__main__":
    main()

