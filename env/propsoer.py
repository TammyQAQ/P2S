'''Define the proposer actions here'''

import random
import numpy as np
from typing import List, Dict, Optional, Tuple
from .transaction import Transaction, TransactionType
from .node import Node

class Proposer(Node):
    def __init__(self, proposer_id: str, stake: int = 1000):
        super().__init__(proposer_id)
        self.proposer_id = proposer_id
        self.stake = stake
        self.total_rewards = 0
        self.mev_extracted = 0
        self.blocks_proposed = 0
        
        # Proposer behavior parameters
        self.mev_aggressiveness = random.random()  # How aggressive they are with MEV
        self.honest_probability = random.uniform(0.7, 1.0)  # Probability of honest behavior
        self.gas_price_premium = random.uniform(1.0, 2.0)  # Premium for front-running
        
        # P2S specific state
        self.partial_hidden_transactions: List[Transaction] = []
        self.matching_transactions: List[Transaction] = []
        self.pending_block_1: Optional['Block'] = None
        self.pending_block_2: Optional['Block'] = None
        
    def select_transactions_for_block_1(self, 
                                      available_transactions: List[Transaction],
                                      max_block_size: int = 100) -> List[Transaction]:
        """Select transactions for the first block (partial hidden)"""
        # Sort by gas price (descending) to maximize fees
        sorted_txs = sorted(available_transactions, 
                           key=lambda tx: tx.gas_price, reverse=True)
        
        selected_txs = []
        for tx in sorted_txs[:max_block_size]:
            # Create partial hidden version
            pht = tx.create_partial_hidden_version()
            selected_txs.append(pht)
            self.partial_hidden_transactions.append(pht)
        
        return selected_txs
    
    def attempt_mev_attack(self, 
                          partial_hidden_txs: List[Transaction],
                          current_time: int) -> List[Transaction]:
        """Attempt MEV attack based on partial information"""
        if random.random() > self.mev_aggressiveness:
            return []  # Honest proposer, no attack
        
        mev_attacks = []
        
        for pht in partial_hidden_txs:
            # Analyze partial information for MEV opportunities
            mev_opportunity = self._analyze_mev_potential(pht)
            
            if mev_opportunity > 0:
                # Create front-running transaction
                front_run_tx = self._create_front_run_transaction(pht, mev_opportunity, current_time)
                mev_attacks.append(front_run_tx)
                
                # Create back-running transaction
                back_run_tx = self._create_back_run_transaction(pht, mev_opportunity, current_time)
                mev_attacks.append(back_run_tx)
        
        return mev_attacks
    
    def _analyze_mev_potential(self, pht: Transaction) -> int:
        """Analyze MEV potential from partial hidden transaction"""
        # In real scenario, this would analyze patterns, gas prices, etc.
        # For simulation, we use the original transaction's MEV potential
        if hasattr(pht, 'partial_hidden_tx') and pht.partial_hidden_tx:
            return pht.partial_hidden_tx.mev_potential
        return 0
    
    def _create_front_run_transaction(self, 
                                    target_tx: Transaction, 
                                    mev_potential: int,
                                    current_time: int) -> Transaction:
        """Create a front-running transaction"""
        # Front-run with higher gas price
        gas_price = int(target_tx.gas_price * self.gas_price_premium)
        
        front_run = Transaction(
            sender=self.proposer_id,
            recipient=f"front_run_target_{target_tx.hash[:8]}",
            value=mev_potential // 2,  # Extract half the MEV
            gas_price=gas_price,
            gas_limit=21000,
            nonce=0,
            mev_potential=mev_potential // 2,
            created_at=current_time,
            tx_type=TransactionType.REGULAR
        )
        
        return front_run
    
    def _create_back_run_transaction(self, 
                                   target_tx: Transaction, 
                                   mev_potential: int,
                                   current_time: int) -> Transaction:
        """Create a back-running transaction"""
        # Back-run with lower gas price but still profitable
        gas_price = int(target_tx.gas_price * 0.8)
        
        back_run = Transaction(
            sender=self.proposer_id,
            recipient=f"back_run_target_{target_tx.hash[:8]}",
            value=mev_potential // 2,  # Extract half the MEV
            gas_price=gas_price,
            gas_limit=21000,
            nonce=1,
            mev_potential=mev_potential // 2,
            created_at=current_time,
            tx_type=TransactionType.REGULAR
        )
        
        return back_run
    
    def process_matching_transactions(self, 
                                    matching_txs: List[Transaction]) -> List[Transaction]:
        """Process matching transactions and replace partial hidden ones"""
        processed_txs = []
        
        for mt in matching_txs:
            # Find corresponding partial hidden transaction
            corresponding_pht = None
            for pht in self.partial_hidden_transactions:
                if pht.hash == mt.hash:
                    corresponding_pht = pht
                    break
            
            if corresponding_pht:
                # Replace partial hidden with matching transaction
                processed_txs.append(mt)
                self.matching_transactions.append(mt)
            else:
                # New transaction, add to block
                processed_txs.append(mt)
        
        return processed_txs
    
    def calculate_block_rewards(self, block_transactions: List[Transaction]) -> int:
        """Calculate total rewards from block"""
        base_reward = 2  # ETH base reward
        gas_fees = sum(tx.gas_price * tx.gas_limit for tx in block_transactions)
        mev_extracted = sum(tx.mev_potential for tx in block_transactions 
                           if tx.sender == self.proposer_id)
        
        return base_reward + gas_fees + mev_extracted
    
    def update_stats(self, block_rewards: int, mev_extracted: int):
        """Update proposer statistics"""
        self.total_rewards += block_rewards
        self.mev_extracted += mev_extracted
        self.blocks_proposed += 1
    
    def get_stats(self) -> Dict:
        """Get proposer statistics"""
        return {
            "proposer_id": self.proposer_id,
            "stake": self.stake,
            "total_rewards": self.total_rewards,
            "mev_extracted": self.mev_extracted,
            "blocks_proposed": self.blocks_proposed,
            "avg_reward_per_block": self.total_rewards / max(1, self.blocks_proposed),
            "mev_aggressiveness": self.mev_aggressiveness,
            "honest_probability": self.honest_probability
        }