#!/usr/bin/env python3
"""
P2S Performance Test
Runs multiple blocks and shows performance metrics
"""

import time
import random
import statistics
from typing import List, Dict, Any
from p2s_simple import P2SProtocol, create_pht_transaction, create_mt_transaction

def run_performance_test(num_blocks: int = 5, tx_per_block: int = 10):
    """Run P2S performance test with multiple blocks"""
    print(f"P2S Performance Test - {num_blocks} blocks, {tx_per_block} tx/block")
    print("=" * 60)
    
    # Initialize protocol
    validators = [f"validator_{i}" for i in range(10)]
    protocol = P2SProtocol(validators)
    
    # Performance metrics
    block_times = []
    pht_submission_times = []
    mt_submission_times = []
    total_transactions = 0
    successful_matches = 0
    
    for block_num in range(100, 100 + num_blocks):
        print(f"\nBlock {block_num}")
        print("-" * 30)
        
        block_start_time = time.time()
        
        # Step 0: Select proposer
        proposer = protocol.step0_proposer_selection(block_num)
        print(f"Proposer: {proposer}")
        
        # Step 1: Submit PHTs
        phts = []
        pht_start_time = time.time()
        
        for i in range(tx_per_block):
            user = f"user_{block_num}_{i}"
            pht = create_pht_transaction(
                sender=user,
                recipient=f"recipient_{i}",
                value=random.randint(100, 1000),
                gas_limit=21000,
                gas_price=random.randint(20, 50)
            )
            protocol.submit_pht(user, pht)
            phts.append(pht)
        
        pht_time = time.time() - pht_start_time
        pht_submission_times.append(pht_time)
        print(f"PHTs submitted: {len(phts)} in {pht_time:.3f}s")
        
        # Create B₁
        b1_start_time = time.time()
        b1 = protocol.step1_partial_commitment(proposer, block_num)
        b1_time = time.time() - b1_start_time
        print(f"B₁ created in {b1_time:.3f}s")
        
        # Step 2: Submit MTs
        mts = []
        mt_start_time = time.time()
        
        for pht in phts:
            mt = create_mt_transaction(
                pht,
                f"recipient_{random.randint(0, tx_per_block-1)}",
                random.randint(100, 1000),
                f"0x{random.randint(1000, 9999):x}"
            )
            protocol.submit_mt(pht.sender, mt)
            mts.append(mt)
        
        mt_time = time.time() - mt_start_time
        mt_submission_times.append(mt_time)
        print(f"MTs submitted: {len(mts)} in {mt_time:.3f}s")
        
        # Create B₂
        b2_start_time = time.time()
        b2 = protocol.step2_full_execution(proposer, block_num)
        b2_time = time.time() - b2_start_time
        print(f"B₂ created in {b2_time:.3f}s")
        
        # Calculate block time
        block_time = time.time() - block_start_time
        block_times.append(block_time)
        
        # Count successful matches
        matches = 0
        for tx in b2["transactions"]:
            if hasattr(tx, 'recipient') and tx.recipient is not None:
                matches += 1
        
        successful_matches += matches
        total_transactions += len(phts)
        
        print(f"Total block time: {block_time:.3f}s")
        print(f"Successful matches: {matches}/{len(phts)}")
        print(f"Match rate: {matches/len(phts)*100:.1f}%")
    
    # Performance summary
    print(f"\nPerformance Summary")
    print("=" * 40)
    
    print(f"Blocks processed: {num_blocks}")
    print(f"Total transactions: {total_transactions}")
    print(f"Successful matches: {successful_matches}")
    print(f"Overall match rate: {successful_matches/total_transactions*100:.1f}%")
    
    print(f"\nTiming Statistics:")
    print(f"  Average block time: {statistics.mean(block_times):.3f}s")
    print(f"  Min block time: {min(block_times):.3f}s")
    print(f"  Max block time: {max(block_times):.3f}s")
    print(f"  Block time std dev: {statistics.stdev(block_times):.3f}s")
    
    print(f"\nPHT Submission:")
    print(f"  Average time: {statistics.mean(pht_submission_times):.3f}s")
    print(f"  Rate: {tx_per_block/statistics.mean(pht_submission_times):.1f} tx/s")
    
    print(f"\nMT Submission:")
    print(f"  Average time: {statistics.mean(mt_submission_times):.3f}s")
    print(f"  Rate: {tx_per_block/statistics.mean(mt_submission_times):.1f} tx/s")
    
    # Calculate throughput
    total_time = sum(block_times)
    throughput = total_transactions / total_time
    print(f"\nOverall Performance:")
    print(f"  Total time: {total_time:.3f}s")
    print(f"  Throughput: {throughput:.1f} tx/s")
    print(f"  Blocks per second: {num_blocks/total_time:.2f}")
    
    return {
        "blocks": num_blocks,
        "transactions": total_transactions,
        "successful_matches": successful_matches,
        "match_rate": successful_matches/total_transactions*100,
        "avg_block_time": statistics.mean(block_times),
        "throughput": throughput,
        "block_times": block_times
    }

def run_scalability_test():
    """Test P2S performance with increasing transaction loads"""
    print(f"\nScalability Test")
    print("=" * 30)
    
    transaction_loads = [5, 10, 20, 50]
    results = []
    
    for tx_count in transaction_loads:
        print(f"\nTesting with {tx_count} transactions per block...")
        
        start_time = time.time()
        result = run_performance_test(num_blocks=3, tx_per_block=tx_count)
        end_time = time.time()
        
        result["tx_per_block"] = tx_count
        result["test_time"] = end_time - start_time
        results.append(result)
        
        print(f"Completed in {result['test_time']:.3f}s")
    
    # Scalability analysis
    print(f"\nScalability Analysis:")
    print("=" * 40)
    
    for result in results:
        print(f"  {result['tx_per_block']:2d} tx/block: {result['throughput']:5.1f} tx/s, "
              f"{result['avg_block_time']:.3f}s/block, {result['match_rate']:5.1f}% match rate")

def run_mev_protection_test():
    """Test MEV protection effectiveness"""
    print(f"\nMEV Protection Test")
    print("=" * 30)
    
    # Initialize protocol
    validators = [f"validator_{i}" for i in range(10)]
    protocol = P2SProtocol(validators)
    
    # Create high-value transaction (MEV target)
    high_value_pht = create_pht_transaction(
        sender="victim_user",
        recipient="target_contract",
        value=10000,  # High value
        gas_limit=100000,
        gas_price=100  # High gas price
    )
    
    protocol.submit_pht("victim_user", high_value_pht)
    
    # Run P2S protocol
    proposer = protocol.step0_proposer_selection(200)
    b1 = protocol.step1_partial_commitment(proposer, 200)
    
    # Check MEV protection
    mev_protection_score = 0
    for tx in b1["transactions"]:
        if hasattr(tx, 'recipient') and tx.recipient is None:
            mev_protection_score += 1
    
    mev_protection_rate = mev_protection_score / len(b1["transactions"]) * 100
    
    print(f"MEV Protection Analysis:")
    print(f"  High-value transactions: 1")
    print(f"  Hidden details in B₁: {mev_protection_score}/{len(b1['transactions'])}")
    print(f"  MEV protection rate: {mev_protection_rate:.1f}%")
    
    if mev_protection_rate > 80:
        print(f"  Status: Excellent MEV protection")
    elif mev_protection_rate > 60:
        print(f"  Status: Good MEV protection")
    else:
        print(f"  Status: Limited MEV protection")

if __name__ == "__main__":
    # Run comprehensive performance test
    print("P2S Comprehensive Performance Test")
    print("=" * 50)
    
    # Basic performance test
    basic_results = run_performance_test(num_blocks=5, tx_per_block=10)
    
    # Scalability test
    run_scalability_test()
    
    # MEV protection test
    run_mev_protection_test()
    
    print(f"\nPerformance Test Complete!")
    print("=" * 50)
    print(f"Key Metrics:")
    print(f"  Throughput: {basic_results['throughput']:.1f} tx/s")
    print(f"  Match Rate: {basic_results['match_rate']:.1f}%")
    print(f"  Avg Block Time: {basic_results['avg_block_time']:.3f}s")
    print(f"  MEV Protection: Active")
