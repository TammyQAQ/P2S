'''All agents imported to the chain and p2s happens here'''

import random
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from .transaction import Transaction, TransactionType
from .propsoer import Proposer
from .user import User

@dataclass
class Block:
    """Represents a block in the P2S system"""
    block_number: int
    proposer_id: str
    transactions: List[Transaction]
    timestamp: int
    parent_hash: str
    block_hash: str
    is_partial_hidden: bool = False
    confirmed: bool = False
    
    def __post_init__(self):
        if not hasattr(self, 'block_hash') or not self.block_hash:
            self.block_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute block hash"""
        import hashlib
        content = f"{self.block_number}{self.proposer_id}{self.timestamp}{self.parent_hash}"
        for tx in self.transactions:
            content += tx.hash
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get_total_gas_fees(self) -> int:
        """Calculate total gas fees in the block"""
        return sum(tx.gas_price * tx.gas_limit for tx in self.transactions)
    
    def get_total_mev_potential(self) -> int:
        """Calculate total MEV potential in the block"""
        return sum(tx.mev_potential for tx in self.transactions)

class ValidatorCommittee:
    """Represents the validator committee for consensus"""
    def __init__(self, validators: List[str]):
        self.validators = validators
        self.byzantine_threshold = len(validators) // 3  # 1/3 Byzantine tolerance
        
    def reach_consensus(self, matching_transactions: List[Transaction]) -> List[Transaction]:
        """Reach Byzantine consensus on matching transactions"""
        # Simulate consensus process
        consensus_txs = []
        
        for tx in matching_transactions:
            # Simulate voting process
            honest_votes = 0
            byzantine_votes = 0
            
            for validator in self.validators:
                if random.random() < 0.8:  # 80% honest validators
                    honest_votes += 1
                else:
                    byzantine_votes += 1
            
            # Transaction is accepted if honest votes > byzantine votes
            if honest_votes > byzantine_votes:
                consensus_txs.append(tx)
        
        return consensus_txs

class Chain:
    """Main blockchain implementation with P2S protocol"""
    def __init__(self, 
                 slot_time: int = 12,  # seconds per slot
                 block_time: int = 12,  # seconds per block
                 max_block_size: int = 100):
        self.slot_time = slot_time
        self.block_time = block_time
        self.max_block_size = max_block_size
        
        # Chain state
        self.blocks: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.partial_hidden_blocks: List[Block] = []
        self.current_slot = 0
        self.current_time = 0
        
        # Network participants
        self.users: List[User] = []
        self.proposers: List[Proposer] = []
        self.validator_committee: Optional[ValidatorCommittee] = None
        
        # P2S specific state
        self.pending_matching_transactions: List[Transaction] = []
        self.block_1_confirmation_slots = 2  # Slots to wait for B1 confirmation
        
    def add_user(self, user: User):
        """Add a user to the network"""
        self.users.append(user)
    
    def add_proposer(self, proposer: Proposer):
        """Add a proposer to the network"""
        self.proposers.append(proposer)
    
    def set_validator_committee(self, validators: List[str]):
        """Set the validator committee"""
        self.validator_committee = ValidatorCommittee(validators)
    
    def select_proposer(self) -> Proposer:
        """Select proposer using RANDAO-like mechanism"""
        # Simulate RANDAO selection
        total_stake = sum(p.stake for p in self.proposers)
        selection_point = random.uniform(0, total_stake)
        
        current_stake = 0
        for proposer in self.proposers:
            current_stake += proposer.stake
            if current_stake >= selection_point:
                return proposer
        
        return self.proposers[0]  # Fallback
    
    def generate_transactions(self, current_time: int):
        """Generate new transactions from users"""
        for user in self.users:
            if user.should_submit_transaction(current_time):
                # Create transaction with random recipient
                other_users = [u for u in self.users if u != user]
                recipient = user.get_random_recipient(other_users)
                value = random.randint(1, 100)
                mev_potential = random.randint(0, 50)  # Some transactions have MEV potential
                
                tx = user.create_transaction(recipient, value, current_time, mev_potential)
                self.pending_transactions.append(tx)
    
    def step_1_partial_commitment(self, proposer: Proposer) -> Block:
        """Step 1: Create block B1 with partial hidden transactions"""
        # Select transactions for block
        selected_txs = proposer.select_transactions_for_block_1(
            self.pending_transactions, self.max_block_size
        )
        
        # Remove selected transactions from pending
        for tx in selected_txs:
            if hasattr(tx, 'partial_hidden_tx') and tx.partial_hidden_tx:
                if tx.partial_hidden_tx in self.pending_transactions:
                    self.pending_transactions.remove(tx.partial_hidden_tx)
        
        # Create block B1
        parent_hash = self.blocks[-1].block_hash if self.blocks else "0" * 64
        block_1 = Block(
            block_number=len(self.blocks),
            proposer_id=proposer.proposer_id,
            transactions=selected_txs,
            timestamp=self.current_time,
            parent_hash=parent_hash,
            block_hash="",
            is_partial_hidden=True
        )
        
        # Add to chain (no rewards yet)
        self.blocks.append(block_1)
        self.partial_hidden_blocks.append(block_1)
        
        return block_1
    
    def step_2_full_execution(self, proposer: Proposer, block_1: Block) -> Block:
        """Step 2: Create block B2 with full transactions"""
        # Simulate users releasing matching transactions
        matching_txs = []
        for pht in block_1.transactions:
            if hasattr(pht, 'partial_hidden_tx') and pht.partial_hidden_tx:
                # Create matching transaction
                mt = pht.partial_hidden_tx.create_matching_transaction()
                matching_txs.append(mt)
        
        # Validator committee consensus
        if self.validator_committee:
            consensus_txs = self.validator_committee.reach_consensus(matching_txs)
        else:
            consensus_txs = matching_txs
        
        # Proposer processes matching transactions
        final_txs = proposer.process_matching_transactions(consensus_txs)
        
        # Add any new pending transactions
        final_txs.extend(self.pending_transactions[:self.max_block_size - len(final_txs)])
        
        # Create block B2
        block_2 = Block(
            block_number=len(self.blocks),
            proposer_id=proposer.proposer_id,
            transactions=final_txs,
            timestamp=self.current_time,
            parent_hash=block_1.block_hash,
            block_hash="",
            is_partial_hidden=False
        )
        
        # Replace B1 with B2
        self.blocks[-1] = block_2
        
        # Calculate and distribute rewards
        block_rewards = proposer.calculate_block_rewards(final_txs)
        mev_extracted = sum(tx.mev_potential for tx in final_txs 
                           if tx.sender == proposer.proposer_id)
        
        proposer.update_stats(block_rewards, mev_extracted)
        
        return block_2
    
    def simulate_mev_attack(self, proposer: Proposer, block_1: Block) -> List[Transaction]:
        """Simulate MEV attack attempts"""
        mev_attacks = proposer.attempt_mev_attack(block_1.transactions, self.current_time)
        
        # Add MEV attack transactions to pending
        for attack_tx in mev_attacks:
            self.pending_transactions.append(attack_tx)
        
        return mev_attacks
    
    def advance_time(self, time_delta: int = 1):
        """Advance simulation time"""
        self.current_time += time_delta
        self.current_slot = self.current_time // self.slot_time
    
    def run_simulation_step(self):
        """Run one simulation step"""
        # Generate new transactions
        self.generate_transactions(self.current_time)
        
        # Check if it's time for a new block
        if self.current_time % self.block_time == 0:
            # Select proposer
            proposer = self.select_proposer()
            
            # Step 1: Partial commitment
            block_1 = self.step_1_partial_commitment(proposer)
            
            # Simulate MEV attack attempts
            mev_attacks = self.simulate_mev_attack(proposer, block_1)
            
            # Wait for B1 confirmation
            self.advance_time(self.block_time * self.block_1_confirmation_slots)
            
            # Step 2: Full execution
            block_2 = self.step_2_full_execution(proposer, block_1)
            
            return {
                "block_1": block_1,
                "block_2": block_2,
                "mev_attacks": mev_attacks,
                "proposer": proposer
            }
        
        self.advance_time()
        return None
    
    def get_chain_stats(self) -> Dict:
        """Get chain statistics"""
        total_blocks = len(self.blocks)
        total_transactions = sum(len(block.transactions) for block in self.blocks)
        total_gas_fees = sum(block.get_total_gas_fees() for block in self.blocks)
        total_mev_potential = sum(block.get_total_mev_potential() for block in self.blocks)
        
        return {
            "total_blocks": total_blocks,
            "total_transactions": total_transactions,
            "total_gas_fees": total_gas_fees,
            "total_mev_potential": total_mev_potential,
            "avg_transactions_per_block": total_transactions / max(1, total_blocks),
            "current_time": self.current_time,
            "current_slot": self.current_slot
        }