#!/usr/bin/env python3
"""
P2S (Partial to Full) Agent-Based Simulation

This simulation demonstrates the P2S protocol which reduces MEV opportunities
by splitting block proposal into two coordinated steps:
1. Partial Transaction Commitment (B1)
2. Full Transaction Execution (B2)

Parameters:
- num_users: Number of users generating transactions
- num_proposers: Number of validators/proposers
- num_validators: Size of validator committee
- simulation_duration: Duration in seconds
- slot_time: Time per slot (12 seconds like Ethereum)
- block_time: Time per block
- max_block_size: Maximum transactions per block
- mev_attack_probability: Probability of MEV attacks
- transaction_frequency: How often users create transactions
"""

import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Dict
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from env.chain import Chain, Block
from env.user import User
from env.propsoer import Proposer
from env.transaction import Transaction, TransactionType

class P2SSimulation:
    def __init__(self, 
                 num_users: int = 50,
                 num_proposers: int = 10,
                 num_validators: int = 20,
                 simulation_duration: int = 3600,  # 1 hour
                 slot_time: int = 12,
                 block_time: int = 12,
                 max_block_size: int = 100,
                 mev_attack_probability: float = 0.3,
                 transaction_frequency: float = 5.0):
        
        self.num_users = num_users
        self.num_proposers = num_proposers
        self.num_validators = num_validators
        self.simulation_duration = simulation_duration
        self.slot_time = slot_time
        self.block_time = block_time
        self.max_block_size = max_block_size
        self.mev_attack_probability = mev_attack_probability
        self.transaction_frequency = transaction_frequency
        
        # Initialize chain
        self.chain = Chain(
            slot_time=slot_time,
            block_time=block_time,
            max_block_size=max_block_size
        )
        
        # Simulation results
        self.results = {
            "blocks": [],
            "mev_attacks": [],
            "proposer_stats": [],
            "user_stats": [],
            "chain_stats": []
        }
        
        self._setup_network()
    
    def _setup_network(self):
        """Setup the network with users, proposers, and validators"""
        print("Setting up P2S network...")
        
        # Create users
        for i in range(self.num_users):
            user = User(f"user_{i}", balance=random.randint(1000, 10000))
            self.chain.add_user(user)
        
        # Create proposers with varying stakes
        for i in range(self.num_proposers):
            stake = random.randint(100, 1000)
            proposer = Proposer(f"proposer_{i}", stake=stake)
            # Adjust MEV aggressiveness based on probability
            proposer.mev_aggressiveness = self.mev_attack_probability
            self.chain.add_proposer(proposer)
        
        # Create validator committee
        validators = [f"validator_{i}" for i in range(self.num_validators)]
        self.chain.set_validator_committee(validators)
        
        print(f"Network setup complete:")
        print(f"  - {self.num_users} users")
        print(f"  - {self.num_proposers} proposers")
        print(f"  - {self.num_validators} validators")
        print(f"  - MEV attack probability: {self.mev_attack_probability}")
    
    def run_simulation(self):
        """Run the complete P2S simulation"""
        print(f"\nStarting P2S simulation for {self.simulation_duration} seconds...")
        
        step_count = 0
        block_count = 0
        
        while self.chain.current_time < self.simulation_duration:
            # Run simulation step
            result = self.chain.run_simulation_step()
            
            if result:
                # Block was created
                block_count += 1
                self._record_block_result(result)
                
                if block_count % 10 == 0:
                    print(f"Block {block_count} created at time {self.chain.current_time}")
            
            step_count += 1
            
            # Record periodic stats
            if step_count % 100 == 0:
                self._record_periodic_stats()
        
        print(f"\nSimulation complete!")
        print(f"  - Total blocks: {len(self.chain.blocks)}")
        print(f"  - Total transactions: {sum(len(b.transactions) for b in self.chain.blocks)}")
        print(f"  - Simulation time: {self.chain.current_time} seconds")
    
    def _record_block_result(self, result: Dict):
        """Record results from a block creation"""
        block_1 = result["block_1"]
        block_2 = result["block_2"]
        mev_attacks = result["mev_attacks"]
        proposer = result["proposer"]
        
        # Record block information
        self.results["blocks"].append({
            "block_number": block_1.block_number,
            "proposer_id": proposer.proposer_id,
            "block_1_transactions": len(block_1.transactions),
            "block_2_transactions": len(block_2.transactions),
            "block_1_gas_fees": block_1.get_total_gas_fees(),
            "block_2_gas_fees": block_2.get_total_gas_fees(),
            "block_1_mev_potential": block_1.get_total_mev_potential(),
            "block_2_mev_potential": block_2.get_total_mev_potential(),
            "timestamp": block_1.timestamp
        })
        
        # Record MEV attacks
        if mev_attacks:
            for attack in mev_attacks:
                self.results["mev_attacks"].append({
                    "block_number": block_1.block_number,
                    "proposer_id": proposer.proposer_id,
                    "attack_type": "front_run" if "front_run" in attack.recipient else "back_run",
                    "mev_potential": attack.mev_potential,
                    "gas_price": attack.gas_price,
                    "timestamp": attack.created_at
                })
        
        # Record proposer stats
        self.results["proposer_stats"].append(proposer.get_stats())
    
    def _record_periodic_stats(self):
        """Record periodic chain and user statistics"""
        # Chain stats
        chain_stats = self.chain.get_chain_stats()
        self.results["chain_stats"].append(chain_stats)
        
        # User stats
        for user in self.chain.users:
            user_stats = user.get_transaction_stats()
            user_stats["user_id"] = user.user_id
            user_stats["balance"] = user.balance
            self.results["user_stats"].append(user_stats)
    
    def analyze_results(self):
        """Analyze simulation results"""
        print("\n=== P2S Simulation Analysis ===")
        
        # Convert results to DataFrames
        blocks_df = pd.DataFrame(self.results["blocks"])
        mev_attacks_df = pd.DataFrame(self.results["mev_attacks"]) if self.results["mev_attacks"] else pd.DataFrame()
        proposer_stats_df = pd.DataFrame(self.results["proposer_stats"])
        chain_stats_df = pd.DataFrame(self.results["chain_stats"])
        
        # Basic statistics
        print(f"\n1. Block Statistics:")
        print(f"   - Total blocks created: {len(blocks_df)}")
        print(f"   - Average transactions per block: {blocks_df['block_2_transactions'].mean():.2f}")
        print(f"   - Average gas fees per block: {blocks_df['block_2_gas_fees'].mean():.2f}")
        
        print(f"\n2. MEV Attack Analysis:")
        if not mev_attacks_df.empty:
            print(f"   - Total MEV attacks: {len(mev_attacks_df)}")
            print(f"   - Average MEV potential per attack: {mev_attacks_df['mev_potential'].mean():.2f}")
            print(f"   - MEV attack success rate: {len(mev_attacks_df) / len(blocks_df) * 100:.2f}%")
        else:
            print(f"   - No MEV attacks detected")
        
        print(f"\n3. Proposer Performance:")
        print(f"   - Average rewards per proposer: {proposer_stats_df['total_rewards'].mean():.2f}")
        print(f"   - Total MEV extracted: {proposer_stats_df['mev_extracted'].sum()}")
        print(f"   - Average MEV aggressiveness: {proposer_stats_df['mev_aggressiveness'].mean():.3f}")
        
        print(f"\n4. Chain Performance:")
        print(f"   - Total transactions processed: {chain_stats_df['total_transactions'].iloc[-1]}")
        print(f"   - Total gas fees collected: {chain_stats_df['total_gas_fees'].iloc[-1]}")
        print(f"   - Total MEV potential: {chain_stats_df['total_mev_potential'].iloc[-1]}")
        
        return {
            "blocks_df": blocks_df,
            "mev_attacks_df": mev_attacks_df,
            "proposer_stats_df": proposer_stats_df,
            "chain_stats_df": chain_stats_df
        }
    
    def plot_results(self, analysis_results: Dict):
        """Plot simulation results"""
        blocks_df = analysis_results["blocks_df"]
        mev_attacks_df = analysis_results["mev_attacks_df"]
        proposer_stats_df = analysis_results["proposer_stats_df"]
        
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('P2S Simulation Results', fontsize=16)
        
        # Plot 1: Transactions per block over time
        axes[0, 0].plot(blocks_df['timestamp'], blocks_df['block_2_transactions'], 'b-', alpha=0.7)
        axes[0, 0].set_title('Transactions per Block Over Time')
        axes[0, 0].set_xlabel('Time (seconds)')
        axes[0, 0].set_ylabel('Transactions')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Gas fees per block
        axes[0, 1].plot(blocks_df['timestamp'], blocks_df['block_2_gas_fees'], 'g-', alpha=0.7)
        axes[0, 1].set_title('Gas Fees per Block Over Time')
        axes[0, 1].set_xlabel('Time (seconds)')
        axes[0, 1].set_ylabel('Gas Fees')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: MEV potential per block
        axes[0, 2].plot(blocks_df['timestamp'], blocks_df['block_2_mev_potential'], 'r-', alpha=0.7)
        axes[0, 2].set_title('MEV Potential per Block Over Time')
        axes[0, 2].set_xlabel('Time (seconds)')
        axes[0, 2].set_ylabel('MEV Potential')
        axes[0, 2].grid(True, alpha=0.3)
        
        # Plot 4: Proposer rewards distribution
        axes[1, 0].hist(proposer_stats_df['total_rewards'], bins=10, alpha=0.7, color='purple')
        axes[1, 0].set_title('Proposer Rewards Distribution')
        axes[1, 0].set_xlabel('Total Rewards')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 5: MEV attacks over time
        if not mev_attacks_df.empty:
            mev_attacks_df['timestamp'].hist(bins=20, alpha=0.7, color='orange', ax=axes[1, 1])
            axes[1, 1].set_title('MEV Attacks Distribution Over Time')
            axes[1, 1].set_xlabel('Time (seconds)')
            axes[1, 1].set_ylabel('Number of Attacks')
            axes[1, 1].grid(True, alpha=0.3)
        else:
            axes[1, 1].text(0.5, 0.5, 'No MEV Attacks', ha='center', va='center', transform=axes[1, 1].transAxes)
            axes[1, 1].set_title('MEV Attacks Distribution')
        
        # Plot 6: Proposer MEV aggressiveness vs rewards
        axes[1, 2].scatter(proposer_stats_df['mev_aggressiveness'], 
                          proposer_stats_df['total_rewards'], alpha=0.7, color='red')
        axes[1, 2].set_title('MEV Aggressiveness vs Total Rewards')
        axes[1, 2].set_xlabel('MEV Aggressiveness')
        axes[1, 2].set_ylabel('Total Rewards')
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../plots/p2s_simulation_results.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    """Main simulation function"""
    print("P2S (Partial to Full) Agent-Based Simulation")
    print("=" * 50)
    
    # Simulation parameters
    params = {
        "num_users": 50,
        "num_proposers": 10,
        "num_validators": 20,
        "simulation_duration": 3600,  # 1 hour
        "slot_time": 12,
        "block_time": 12,
        "max_block_size": 100,
        "mev_attack_probability": 0.3,
        "transaction_frequency": 5.0
    }
    
    print("Simulation Parameters:")
    for key, value in params.items():
        print(f"  {key}: {value}")
    
    # Create and run simulation
    simulation = P2SSimulation(**params)
    simulation.run_simulation()
    
    # Analyze and plot results
    analysis_results = simulation.analyze_results()
    simulation.plot_results(analysis_results)
    
    print("\nSimulation completed successfully!")
    print("Results saved to ../plots/p2s_simulation_results.png")

if __name__ == "__main__":
    main() 