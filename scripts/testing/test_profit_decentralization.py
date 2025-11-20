#!/usr/bin/env python3
"""
Profit Decentralization Test
Compares profit distribution among validators in P2S vs Current Ethereum (Flashbots-dominated)
Note: Current Ethereum is ~90% Flashbots/MEV-Boost, so we simulate it as such
"""

import json
import random
import statistics
import time
from datetime import datetime
from typing import Dict, List, Tuple
from collections import defaultdict
import os

class ProfitDecentralizationSimulator:
    """Simulates profit distribution across different consensus mechanisms"""
    
    def __init__(self):
        self.results = {
            'p2s_profits': {},
            'current_ethereum_profits': {},  # Current Ethereum (MEV-Boost/Flashbots relays)
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'num_validators': 0,
                'num_blocks': 0,
                'description': 'Current Ethereum uses MEV-Boost/Flashbots relays (post-2023)'
            }
        }
    
    def create_validator_set(self, num_validators: int, stake_distribution: str = 'realistic') -> List[Dict]:
        """Create a set of validators with different stake distributions"""
        validators = []
        
        if stake_distribution == 'realistic':
            # Realistic distribution: few large validators, many small ones
            for i in range(num_validators):
                if i < num_validators * 0.1:  # Top 10% have large stakes
                    stake = random.randint(10000, 50000)
                elif i < num_validators * 0.3:  # Next 20% have medium stakes
                    stake = random.randint(5000, 10000)
                else:  # Bottom 70% have small stakes
                    stake = random.randint(1000, 5000)
                
                validators.append({
                    'id': f'validator_{i}',
                    'stake': stake,
                    'total_profit': 0.0,
                    'blocks_proposed': 0,
                    'mev_profit': 0.0
                })
        elif stake_distribution == 'uniform':
            # Uniform distribution
            stake = 10000
            for i in range(num_validators):
                validators.append({
                    'id': f'validator_{i}',
                    'stake': stake,
                    'total_profit': 0.0,
                    'blocks_proposed': 0,
                    'mev_profit': 0.0
                })
        elif stake_distribution == 'centralized':
            # Highly centralized: one validator has most stake
            for i in range(num_validators):
                if i == 0:
                    stake = 50000
                else:
                    stake = random.randint(100, 1000)
                validators.append({
                    'id': f'validator_{i}',
                    'stake': stake,
                    'total_profit': 0.0,
                    'blocks_proposed': 0,
                    'mev_profit': 0.0
                })
        
        return validators
    
    def simulate_p2s_profit_distribution(self, validators: List[Dict], num_blocks: int) -> Dict:
        """Simulate P2S profit distribution"""
        print(f"[P2S] Simulating profit distribution for {num_blocks} blocks...")
        
        # Reset profits
        for v in validators:
            v['total_profit'] = 0.0
            v['blocks_proposed'] = 0
            v['mev_profit'] = 0.0
        
        total_stake = sum(v['stake'] for v in validators)
        
        for block_num in range(num_blocks):
            # Select proposer based on stake-weighted random selection
            # P2S: More decentralized due to anti-MEV mechanisms
            proposer = self.select_p2s_proposer(validators, total_stake)
            
            # Calculate block rewards
            base_reward = 2.0  # Base block reward
            mev_reward = 0.0  # P2S reduces MEV extraction
            
            # P2S distributes rewards more evenly
            # Validators get rewards proportional to stake, but MEV is reduced
            proposer['total_profit'] += base_reward
            proposer['blocks_proposed'] += 1
            
            # Other validators get attestation rewards (smaller)
            attestation_reward = 0.1
            for v in validators:
                if v['id'] != proposer['id'] and random.random() < 0.9:  # 90% attestation rate
                    v['total_profit'] += attestation_reward * (v['stake'] / total_stake)
        
        return {v['id']: v['total_profit'] for v in validators}
    
    def simulate_pos_profit_distribution(self, validators: List[Dict], num_blocks: int) -> Dict:
        """Simulate PoS profit distribution"""
        print(f"[PoS] Simulating profit distribution for {num_blocks} blocks...")
        
        # Reset profits
        for v in validators:
            v['total_profit'] = 0.0
            v['blocks_proposed'] = 0
            v['mev_profit'] = 0.0
        
        total_stake = sum(v['stake'] for v in validators)
        
        for block_num in range(num_blocks):
            # Select proposer based on stake-weighted random selection
            proposer = self.select_pos_proposer(validators, total_stake)
            
            # Calculate block rewards
            base_reward = 2.0  # Base block reward
            mev_reward = random.uniform(0.5, 2.0)  # PoS allows MEV extraction
            
            proposer['total_profit'] += base_reward + mev_reward
            proposer['mev_profit'] += mev_reward
            proposer['blocks_proposed'] += 1
            
            # Other validators get attestation rewards
            attestation_reward = 0.1
            for v in validators:
                if v['id'] != proposer['id'] and random.random() < 0.9:
                    v['total_profit'] += attestation_reward * (v['stake'] / total_stake)
        
        return {v['id']: v['total_profit'] for v in validators}
    
    def simulate_current_ethereum_profit_distribution(self, validators: List[Dict], num_blocks: int) -> Dict:
        """Simulate Current Ethereum profit distribution (MEV-Boost/Flashbots relays)"""
        print(f"[Current Ethereum] Simulating profit distribution for {num_blocks} blocks...")
        print(f"   Using MEV-Boost/Flashbots relay model (post-2023 Ethereum)")
        
        # Reset profits
        for v in validators:
            v['total_profit'] = 0.0
            v['blocks_proposed'] = 0
            v['mev_profit'] = 0.0
        
        total_stake = sum(v['stake'] for v in validators)
        
        # Current Ethereum: Validators use MEV-Boost relays (Flashbots, etc.)
        # Top validators get better MEV extraction through relays
        top_validators = sorted(validators, key=lambda x: x['stake'], reverse=True)[:int(len(validators) * 0.1)]
        top_validator_ids = {v['id'] for v in top_validators}
        
        for block_num in range(num_blocks):
            # Select proposer
            proposer = self.select_pos_proposer(validators, total_stake)
            
            # Base block reward
            base_reward = 2.0
            proposer['total_profit'] += base_reward
            proposer['blocks_proposed'] += 1
            
            # Current Ethereum: All blocks use MEV-Boost relays
            # Top validators get better MEV extraction through premium relays
            if proposer['id'] in top_validator_ids:
                # Top validators: High MEV extraction through premium relays
                mev_reward = random.uniform(1.0, 3.0)
            else:
                # Other validators: Moderate MEV extraction through standard relays
                mev_reward = random.uniform(0.5, 2.0)
            
            proposer['total_profit'] += mev_reward
            proposer['mev_profit'] += mev_reward
            
            # Attestation rewards
            attestation_reward = 0.1
            for v in validators:
                if v['id'] != proposer['id'] and random.random() < 0.9:
                    v['total_profit'] += attestation_reward * (v['stake'] / total_stake)
        
        return {v['id']: v['total_profit'] for v in validators}
    
    def select_p2s_proposer(self, validators: List[Dict], total_stake: int) -> Dict:
        """Select proposer in P2S (more decentralized)"""
        # P2S uses stake-weighted selection with reputation factor
        # This slightly favors smaller validators to increase decentralization
        weights = []
        for v in validators:
            # Add small bonus for smaller validators to increase decentralization
            decentralization_bonus = 1.0 - (v['stake'] / total_stake) * 0.1
            weight = v['stake'] * decentralization_bonus
            weights.append(weight)
        
        total_weight = sum(weights)
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return validators[i]
        
        return validators[-1]
    
    def select_pos_proposer(self, validators: List[Dict], total_stake: int) -> Dict:
        """Select proposer in PoS (stake-weighted)"""
        weights = [v['stake'] for v in validators]
        total_weight = sum(weights)
        r = random.uniform(0, total_weight)
        
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if r <= cumulative:
                return validators[i]
        
        return validators[-1]
    
    def calculate_gini_coefficient(self, profits: Dict) -> float:
        """Calculate Gini coefficient for profit distribution"""
        profit_values = sorted([p for p in profits.values() if p > 0])
        if len(profit_values) == 0:
            return 0.0
        
        n = len(profit_values)
        mean_profit = statistics.mean(profit_values)
        
        if mean_profit == 0:
            return 0.0
        
        # Calculate Gini coefficient
        gini_sum = 0
        for i in range(n):
            for j in range(n):
                gini_sum += abs(profit_values[i] - profit_values[j])
        
        gini = gini_sum / (2 * n * n * mean_profit)
        return gini
    
    def calculate_concentration_metrics(self, profits: Dict) -> Dict:
        """Calculate concentration metrics (top 10%, top 50%, etc.)"""
        profit_values = sorted([p for p in profits.values() if p > 0], reverse=True)
        if len(profit_values) == 0:
            return {
                'top_10_pct': 0.0,
                'top_50_pct': 0.0,
                'herfindahl_index': 0.0
            }
        
        total_profit = sum(profit_values)
        n = len(profit_values)
        
        # Top 10% share
        top_10_count = max(1, int(n * 0.1))
        top_10_profit = sum(profit_values[:top_10_count])
        top_10_pct = (top_10_profit / total_profit) * 100 if total_profit > 0 else 0.0
        
        # Top 50% share
        top_50_count = max(1, int(n * 0.5))
        top_50_profit = sum(profit_values[:top_50_count])
        top_50_pct = (top_50_profit / total_profit) * 100 if total_profit > 0 else 0.0
        
        # Herfindahl-Hirschman Index (HHI)
        profit_shares = [p / total_profit for p in profit_values if total_profit > 0]
        hhi = sum(share ** 2 for share in profit_shares) * 10000
        
        return {
            'top_10_pct': top_10_pct,
            'top_50_pct': top_50_pct,
            'herfindahl_index': hhi
        }
    
    def calculate_validator_participation(self, validators: List[Dict]) -> Dict:
        """Calculate validator participation metrics"""
        total_blocks = sum(v['blocks_proposed'] for v in validators)
        if total_blocks == 0:
            return {
                'participation_rate': 0.0,
                'active_validators': 0,
                'total_validators': len(validators)
            }
        
        active_validators = sum(1 for v in validators if v['blocks_proposed'] > 0)
        participation_rate = (active_validators / len(validators)) * 100
        
        return {
            'participation_rate': participation_rate,
            'active_validators': active_validators,
            'total_validators': len(validators)
        }
    
    def run_simulation(self, num_validators: int = 100, num_blocks: int = 1000):
        """Run complete profit decentralization simulation"""
        print("=" * 80)
        print("PROFIT DECENTRALIZATION SIMULATION")
        print("=" * 80)
        print(f"Validators: {num_validators}, Blocks: {num_blocks}")
        print("=" * 80)
        
        # Create validator set
        validators = self.create_validator_set(num_validators, stake_distribution='realistic')
        self.results['metadata']['num_validators'] = num_validators
        self.results['metadata']['num_blocks'] = num_blocks
        
        # Simulate each protocol
        p2s_validators = [v.copy() for v in validators]
        current_ethereum_validators = [v.copy() for v in validators]
        
        p2s_profits = self.simulate_p2s_profit_distribution(p2s_validators, num_blocks)
        current_ethereum_profits = self.simulate_current_ethereum_profit_distribution(
            current_ethereum_validators, num_blocks
        )
        
        self.results['p2s_profits'] = p2s_profits
        self.results['current_ethereum_profits'] = current_ethereum_profits
        
        # Calculate metrics
        p2s_gini = self.calculate_gini_coefficient(p2s_profits)
        ethereum_gini = self.calculate_gini_coefficient(current_ethereum_profits)
        
        p2s_concentration = self.calculate_concentration_metrics(p2s_profits)
        ethereum_concentration = self.calculate_concentration_metrics(current_ethereum_profits)
        
        p2s_participation = self.calculate_validator_participation(p2s_validators)
        ethereum_participation = self.calculate_validator_participation(current_ethereum_validators)
        
        # Store analysis
        self.results['analysis'] = {
            'p2s': {
                'gini_coefficient': p2s_gini,
                'concentration': p2s_concentration,
                'participation': p2s_participation,
                'total_profit': sum(p2s_profits.values()),
                'mean_profit': statistics.mean(list(p2s_profits.values())),
                'median_profit': statistics.median(list(p2s_profits.values()))
            },
            'current_ethereum': {
                'gini_coefficient': ethereum_gini,
                'concentration': ethereum_concentration,
                'participation': ethereum_participation,
                'total_profit': sum(current_ethereum_profits.values()),
                'mean_profit': statistics.mean(list(current_ethereum_profits.values())),
                'median_profit': statistics.median(list(current_ethereum_profits.values()))
            }
        }
        
        # Print results
        self.print_analysis()
        
        # Save results
        self.save_results()
        
        return self.results
    
    def print_analysis(self):
        """Print analysis results"""
        print("\n" + "=" * 80)
        print("PROFIT DECENTRALIZATION ANALYSIS")
        print("=" * 80)
        
        analysis = self.results['analysis']
        
        print(f"\n{'Metric':<30} {'P2S':<20} {'Current Ethereum':<20}")
        print("-" * 70)
        
        eth_analysis = analysis['current_ethereum']
        print(f"{'Gini Coefficient':<30} {analysis['p2s']['gini_coefficient']:<20.3f} {eth_analysis['gini_coefficient']:<20.3f}")
        print(f"{'Top 10% Share (%)':<30} {analysis['p2s']['concentration']['top_10_pct']:<20.1f} {eth_analysis['concentration']['top_10_pct']:<20.1f}")
        print(f"{'Top 50% Share (%)':<30} {analysis['p2s']['concentration']['top_50_pct']:<20.1f} {eth_analysis['concentration']['top_50_pct']:<20.1f}")
        print(f"{'HHI Index':<30} {analysis['p2s']['concentration']['herfindahl_index']:<20.1f} {eth_analysis['concentration']['herfindahl_index']:<20.1f}")
        print(f"{'Participation Rate (%)':<30} {analysis['p2s']['participation']['participation_rate']:<20.1f} {eth_analysis['participation']['participation_rate']:<20.1f}")
        print(f"{'Total Profit':<30} {analysis['p2s']['total_profit']:<20.2f} {eth_analysis['total_profit']:<20.2f}")
        print(f"{'Mean Profit':<30} {analysis['p2s']['mean_profit']:<20.2f} {eth_analysis['mean_profit']:<20.2f}")
        print(f"{'Median Profit':<30} {analysis['p2s']['median_profit']:<20.2f} {eth_analysis['median_profit']:<20.2f}")
        print(f"\nNote: Current Ethereum simulated as post-2023 Ethereum using MEV-Boost/Flashbots relays")
        
        print("\n" + "=" * 80)
        print("INTERPRETATION:")
        print("=" * 80)
        print("• Lower Gini Coefficient = More decentralized profit distribution")
        print("• Lower Top 10% Share = More profit spread across validators")
        print("• Lower HHI = Less concentration (HHI < 1500 = competitive, > 2500 = highly concentrated)")
        print("• Higher Participation Rate = More validators actively participating")
        print("=" * 80)
    
    def save_results(self):
        """Save results to JSON file"""
        os.makedirs('data', exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"data/profit_decentralization_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n[SAVE] Results saved to {filename}")

def main():
    """Main function"""
    import sys
    
    num_validators = 100
    num_blocks = 1000
    
    if len(sys.argv) > 1:
        try:
            num_validators = int(sys.argv[1])
        except ValueError:
            print("Error: Number of validators must be an integer")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            num_blocks = int(sys.argv[2])
        except ValueError:
            print("Error: Number of blocks must be an integer")
            sys.exit(1)
    
    print(f"Starting profit decentralization simulation...")
    print(f"Validators: {num_validators}, Blocks: {num_blocks}")
    
    simulator = ProfitDecentralizationSimulator()
    results = simulator.run_simulation(num_validators, num_blocks)
    
    print(f"\n[COMPLETE] Simulation finished!")
    print(f"Check results in data/profit_decentralization_*.json")

if __name__ == "__main__":
    main()

