#!/usr/bin/env python3
"""
Batch P2S Simulation Runner

This script runs multiple P2S simulations with different configurations
and compares the results to analyze the effectiveness of the protocol
under various conditions.
"""

import sys
import os
import time
import json
from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from p2s_simulation import P2SSimulation
from simulation_configs import ALL_CONFIGS, list_configs

class BatchSimulationRunner:
    def __init__(self):
        self.results = {}
        self.comparison_data = []
        
    def run_all_configurations(self, save_results: bool = True):
        """Run simulations for all configurations"""
        print("Starting batch P2S simulation...")
        print(f"Testing {len(ALL_CONFIGS)} configurations")
        
        for config_name, config in ALL_CONFIGS.items():
            print(f"\n{'='*50}")
            print(f"Running simulation: {config_name}")
            print(f"{'='*50}")
            
            try:
                # Run simulation
                start_time = time.time()
                simulation = P2SSimulation(**config)
                simulation.run_simulation()
                analysis_results = simulation.analyze_results()
                end_time = time.time()
                
                # Store results
                self.results[config_name] = {
                    "config": config,
                    "analysis_results": analysis_results,
                    "simulation_time": end_time - start_time
                }
                
                print(f"✓ {config_name} completed in {end_time - start_time:.2f} seconds")
                
            except Exception as e:
                print(f"✗ {config_name} failed: {str(e)}")
                continue
        
        if save_results:
            self.save_results()
        
        return self.results
    
    def run_specific_configurations(self, config_names: List[str], save_results: bool = True):
        """Run simulations for specific configurations"""
        print(f"Running simulations for: {config_names}")
        
        for config_name in config_names:
            if config_name not in ALL_CONFIGS:
                print(f"Warning: Configuration '{config_name}' not found, skipping...")
                continue
                
            config = ALL_CONFIGS[config_name]
            print(f"\n{'='*50}")
            print(f"Running simulation: {config_name}")
            print(f"{'='*50}")
            
            try:
                start_time = time.time()
                simulation = P2SSimulation(**config)
                simulation.run_simulation()
                analysis_results = simulation.analyze_results()
                end_time = time.time()
                
                self.results[config_name] = {
                    "config": config,
                    "analysis_results": analysis_results,
                    "simulation_time": end_time - start_time
                }
                
                print(f"✓ {config_name} completed in {end_time - start_time:.2f} seconds")
                
            except Exception as e:
                print(f"✗ {config_name} failed: {str(e)}")
                continue
        
        if save_results:
            self.save_results()
        
        return self.results
    
    def save_results(self):
        """Save simulation results to files"""
        # Create results directory
        os.makedirs("../plots", exist_ok=True)
        
        # Save summary data
        summary_data = []
        for config_name, result in self.results.items():
            config = result["config"]
            analysis = result["analysis_results"]
            
            # Extract key metrics
            blocks_df = analysis["blocks_df"]
            mev_attacks_df = analysis["mev_attacks_df"]
            proposer_stats_df = analysis["proposer_stats_df"]
            chain_stats_df = analysis["chain_stats_df"]
            
            summary = {
                "config_name": config_name,
                "num_users": config["num_users"],
                "num_proposers": config["num_proposers"],
                "num_validators": config["num_validators"],
                "mev_attack_probability": config["mev_attack_probability"],
                "transaction_frequency": config["transaction_frequency"],
                "total_blocks": len(blocks_df),
                "total_transactions": blocks_df["block_2_transactions"].sum(),
                "avg_transactions_per_block": blocks_df["block_2_transactions"].mean(),
                "total_gas_fees": blocks_df["block_2_gas_fees"].sum(),
                "avg_gas_fees_per_block": blocks_df["block_2_gas_fees"].mean(),
                "total_mev_potential": blocks_df["block_2_mev_potential"].sum(),
                "total_mev_attacks": len(mev_attacks_df),
                "mev_attack_success_rate": len(mev_attacks_df) / max(1, len(blocks_df)) * 100,
                "avg_proposer_rewards": proposer_stats_df["total_rewards"].mean(),
                "total_mev_extracted": proposer_stats_df["mev_extracted"].sum(),
                "simulation_time": result["simulation_time"]
            }
            
            summary_data.append(summary)
        
        # Save summary to CSV
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv("../plots/batch_simulation_summary.csv", index=False)
        
        # Save detailed results
        with open("../plots/batch_simulation_results.json", "w") as f:
            # Convert DataFrames to dict for JSON serialization
            json_results = {}
            for config_name, result in self.results.items():
                json_results[config_name] = {
                    "config": result["config"],
                    "simulation_time": result["simulation_time"],
                    "blocks_count": len(result["analysis_results"]["blocks_df"]),
                    "mev_attacks_count": len(result["analysis_results"]["mev_attacks_df"]),
                    "proposers_count": len(result["analysis_results"]["proposer_stats_df"])
                }
            json.dump(json_results, f, indent=2)
        
        print(f"\nResults saved to ../plots/")
        print(f"  - batch_simulation_summary.csv")
        print(f"  - batch_simulation_results.json")
    
    def create_comparison_plots(self):
        """Create comparison plots across all configurations"""
        if not self.results:
            print("No results to plot. Run simulations first.")
            return
        
        # Load summary data
        summary_df = pd.read_csv("../plots/batch_simulation_summary.csv")
        
        # Create comparison plots
        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle('P2S Protocol Comparison Across Configurations', fontsize=16)
        
        # Plot 1: MEV Attack Success Rate
        axes[0, 0].bar(summary_df['config_name'], summary_df['mev_attack_success_rate'], 
                      color='red', alpha=0.7)
        axes[0, 0].set_title('MEV Attack Success Rate')
        axes[0, 0].set_ylabel('Success Rate (%)')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Average Transactions per Block
        axes[0, 1].bar(summary_df['config_name'], summary_df['avg_transactions_per_block'], 
                      color='blue', alpha=0.7)
        axes[0, 1].set_title('Average Transactions per Block')
        axes[0, 1].set_ylabel('Transactions')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Total MEV Potential vs Extracted
        x = range(len(summary_df))
        width = 0.35
        axes[0, 2].bar([i - width/2 for i in x], summary_df['total_mev_potential'], 
                      width, label='MEV Potential', color='orange', alpha=0.7)
        axes[0, 2].bar([i + width/2 for i in x], summary_df['total_mev_extracted'], 
                      width, label='MEV Extracted', color='red', alpha=0.7)
        axes[0, 2].set_title('MEV Potential vs Extracted')
        axes[0, 2].set_ylabel('MEV Value')
        axes[0, 2].set_xticks(x)
        axes[0, 2].set_xticklabels(summary_df['config_name'], rotation=45)
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)
        
        # Plot 4: Average Proposer Rewards
        axes[1, 0].bar(summary_df['config_name'], summary_df['avg_proposer_rewards'], 
                      color='green', alpha=0.7)
        axes[1, 0].set_title('Average Proposer Rewards')
        axes[1, 0].set_ylabel('Rewards')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 5: MEV Attack Probability vs Success Rate
        axes[1, 1].scatter(summary_df['mev_attack_probability'], 
                          summary_df['mev_attack_success_rate'], 
                          s=100, alpha=0.7, color='purple')
        axes[1, 1].set_title('MEV Attack Probability vs Success Rate')
        axes[1, 1].set_xlabel('MEV Attack Probability')
        axes[1, 1].set_ylabel('Success Rate (%)')
        axes[1, 1].grid(True, alpha=0.3)
        
        # Plot 6: Simulation Performance
        axes[1, 2].bar(summary_df['config_name'], summary_df['simulation_time'], 
                      color='gray', alpha=0.7)
        axes[1, 2].set_title('Simulation Execution Time')
        axes[1, 2].set_ylabel('Time (seconds)')
        axes[1, 2].tick_params(axis='x', rotation=45)
        axes[1, 2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('../plots/batch_simulation_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        # Create correlation heatmap
        self._create_correlation_heatmap(summary_df)
    
    def _create_correlation_heatmap(self, summary_df: pd.DataFrame):
        """Create correlation heatmap of key metrics"""
        # Select numeric columns for correlation
        numeric_cols = summary_df.select_dtypes(include=[np.number]).columns
        correlation_matrix = summary_df[numeric_cols].corr()
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5)
        plt.title('Correlation Matrix of P2S Metrics')
        plt.tight_layout()
        plt.savefig('../plots/correlation_heatmap.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self):
        """Generate a comprehensive analysis report"""
        if not self.results:
            print("No results to analyze. Run simulations first.")
            return
        
        summary_df = pd.read_csv("../plots/batch_simulation_summary.csv")
        
        print("\n" + "="*60)
        print("P2S BATCH SIMULATION ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n1. OVERVIEW:")
        print(f"   - Total configurations tested: {len(summary_df)}")
        print(f"   - Total simulation time: {summary_df['simulation_time'].sum():.2f} seconds")
        print(f"   - Average simulation time: {summary_df['simulation_time'].mean():.2f} seconds")
        
        print(f"\n2. MEV PROTECTION EFFECTIVENESS:")
        avg_mev_success = summary_df['mev_attack_success_rate'].mean()
        print(f"   - Average MEV attack success rate: {avg_mev_success:.2f}%")
        print(f"   - Best MEV protection: {summary_df.loc[summary_df['mev_attack_success_rate'].idxmin(), 'config_name']}")
        print(f"   - Worst MEV protection: {summary_df.loc[summary_df['mev_attack_success_rate'].idxmax(), 'config_name']}")
        
        print(f"\n3. THROUGHPUT ANALYSIS:")
        print(f"   - Average transactions per block: {summary_df['avg_transactions_per_block'].mean():.2f}")
        print(f"   - Highest throughput: {summary_df.loc[summary_df['avg_transactions_per_block'].idxmax(), 'config_name']}")
        print(f"   - Lowest throughput: {summary_df.loc[summary_df['avg_transactions_per_block'].idxmin(), 'config_name']}")
        
        print(f"\n4. PROPOSER INCENTIVES:")
        print(f"   - Average proposer rewards: {summary_df['avg_proposer_rewards'].mean():.2f}")
        print(f"   - Total MEV extracted: {summary_df['total_mev_extracted'].sum()}")
        print(f"   - MEV extraction efficiency: {summary_df['total_mev_extracted'].sum() / summary_df['total_mev_potential'].sum() * 100:.2f}%")
        
        print(f"\n5. KEY INSIGHTS:")
        
        # Find configurations with best MEV protection
        best_mev_protection = summary_df.loc[summary_df['mev_attack_success_rate'].idxmin()]
        print(f"   - Best MEV protection achieved with: {best_mev_protection['config_name']}")
        print(f"     (MEV attack probability: {best_mev_protection['mev_attack_probability']}, Success rate: {best_mev_protection['mev_attack_success_rate']:.2f}%)")
        
        # Find configurations with highest throughput
        best_throughput = summary_df.loc[summary_df['avg_transactions_per_block'].idxmax()]
        print(f"   - Highest throughput achieved with: {best_throughput['config_name']}")
        print(f"     (Transactions per block: {best_throughput['avg_transactions_per_block']:.2f})")
        
        # Correlation analysis
        mev_correlation = summary_df['mev_attack_probability'].corr(summary_df['mev_attack_success_rate'])
        print(f"   - MEV attack probability vs success rate correlation: {mev_correlation:.3f}")
        
        print(f"\n6. RECOMMENDATIONS:")
        if avg_mev_success < 10:
            print(f"   - P2S protocol shows strong MEV protection (avg success rate: {avg_mev_success:.2f}%)")
        else:
            print(f"   - P2S protocol needs improvement for MEV protection (avg success rate: {avg_mev_success:.2f}%)")
        
        print(f"   - Consider adjusting block confirmation time for better MEV protection")
        print(f"   - Monitor proposer incentives to ensure honest behavior")

def main():
    """Main function for batch simulation"""
    print("P2S Batch Simulation Runner")
    print("=" * 40)
    
    # List available configurations
    configs = list_configs()
    print(f"Available configurations: {configs}")
    
    # Create runner
    runner = BatchSimulationRunner()
    
    # Run all configurations
    print("\nRunning all configurations...")
    results = runner.run_all_configurations()
    
    # Create comparison plots
    print("\nCreating comparison plots...")
    runner.create_comparison_plots()
    
    # Generate report
    print("\nGenerating analysis report...")
    runner.generate_report()
    
    print("\nBatch simulation completed!")

if __name__ == "__main__":
    main() 