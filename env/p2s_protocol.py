"""
P2S (Proposer in 2 Steps) Protocol Implementation
Based on the formal specification for MEV mitigation
"""

import hashlib
import json
import time
import random
from typing import Dict, List, Set, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

class TransactionType(Enum):
    PHT = "PHT"  # Partially Hidden Transaction
    MT = "MT"    # Matching Transaction

@dataclass
class PHTTransaction:
    """Partially Hidden Transaction (t_PHT) - Step 1"""
    sender: str
    nonce: int
    gas_limit: int
    gas_price: int
    hash: str
    signature: str
    # Hidden fields (revealed in MT)
    recipient: Optional[str] = None
    value: Optional[int] = None
    call_data: Optional[str] = None
    # P2S specific fields
    commitment: Optional[str] = None  # Commitment to hidden fields
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "PHT",
            "sender": self.sender,
            "nonce": self.nonce,
            "gas_limit": self.gas_limit,
            "gas_price": self.gas_price,
            "hash": self.hash,
            "signature": self.signature,
            "commitment": self.commitment,
            "timestamp": self.timestamp
        }

@dataclass
class MTTransaction:
    """Matching Transaction (t_MT) - Step 2"""
    # Revealed fields from PHT
    sender: str
    nonce: int
    gas_limit: int
    gas_price: int
    hash: str
    signature: str
    # Now revealed fields
    recipient: str
    value: int
    call_data: str
    # P2S specific fields
    pht_hash: str  # Reference to corresponding PHT
    proof: str     # Proof of matching
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "MT",
            "sender": self.sender,
            "nonce": self.nonce,
            "gas_limit": self.gas_limit,
            "gas_price": self.gas_price,
            "hash": self.hash,
            "signature": self.signature,
            "recipient": self.recipient,
            "value": self.value,
            "call_data": self.call_data,
            "pht_hash": self.pht_hash,
            "proof": self.proof,
            "timestamp": self.timestamp
        }

@dataclass
class Block:
    """Block structure for P2S protocol"""
    block_number: int
    proposer: str
    transactions: List[Any]  # PHT or MT transactions
    parent_hash: str
    timestamp: float
    block_type: str  # "B0", "B1", or "B2"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "block_number": self.block_number,
            "proposer": self.proposer,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "parent_hash": self.parent_hash,
            "timestamp": self.timestamp,
            "block_type": self.block_type
        }

class P2SProtocol:
    """Main P2S Protocol Implementation"""
    
    def __init__(self, validator_set: List[str], delta: float = 1.0):
        self.validator_set = validator_set
        self.delta = delta  # Bounded message delay
        self.current_slot = 0
        self.blocks: Dict[int, Block] = {}
        self.mempool: Dict[str, PHTTransaction] = {}
        self.exposure_pool: Set[MTTransaction] = set()
        self.utility_functions = UtilityFunctions()
        
    def step0_proposer_selection(self, slot: int) -> str:
        """
        Step 0: Proposer Selection
        Randomly select validator P_i via RANDAO two slots ahead
        """
        # Simulate RANDAO selection (in practice, this would use actual RANDAO)
        random.seed(slot + 42)  # Deterministic for testing
        proposer = random.choice(self.validator_set)
        print(f"🎯 Step 0: Selected proposer {proposer} for slot {slot}")
        return proposer
    
    def step1_partial_commitment(self, proposer: str, slot: int) -> Block:
        """
        Step 1: Partial Transaction Commitment
        Proposer constructs B_1 with PHTs
        """
        print(f"🔒 Step 1: Proposer {proposer} creating B_1 with PHTs")
        
        # Select PHTs from mempool
        selected_phts = self._select_phts_for_block()
        
        # Create B_1 block
        b1 = Block(
            block_number=slot,
            proposer=proposer,
            transactions=selected_phts,
            parent_hash=self._get_last_block_hash(),
            timestamp=time.time(),
            block_type="B_1"
        )
        
        # Store block
        self.blocks[slot] = b1
        
        print(f"✅ B_1 created with {len(selected_phts)} PHTs")
        return b1
    
    def step2_full_execution(self, proposer: str, slot: int) -> Block:
        """
        Step 2: Full Transaction Execution
        Process MTs and create final B_2 block
        """
        print(f"🔓 Step 2: Processing MTs for B_2")
        
        # Get B_1 for reference
        b1 = self.blocks.get(slot)
        if not b1:
            raise ValueError(f"B_1 not found for slot {slot}")
        
        # Byzantine set-union consensus for MTs
        verified_mts = self._byzantine_set_union_consensus()
        
        # Create B_2 by replacing PHTs with corresponding MTs
        b2_transactions = self._replace_phts_with_mts(b1.transactions, verified_mts)
        
        # Create B_2 block
        b2 = Block(
            block_number=slot,
            proposer=proposer,
            transactions=b2_transactions,
            parent_hash=b1.parent_hash,
            timestamp=time.time(),
            block_type="B_2"
        )
        
        # Replace B_1 with B_2
        self.blocks[slot] = b2
        
        print(f"✅ B_2 created with {len(b2_transactions)} transactions")
        return b2
    
    def submit_pht(self, user: str, pht: PHTTransaction) -> bool:
        """Submit a PHT to the mempool"""
        if self._validate_pht(pht):
            self.mempool[pht.hash] = pht
            print(f"📝 PHT submitted by {user}: {pht.hash[:8]}...")
            return True
        return False
    
    def submit_mt(self, user: str, mt: MTTransaction) -> bool:
        """Submit an MT to the exposure pool"""
        if self._validate_mt(mt):
            self.exposure_pool.add(mt)
            print(f"🔓 MT submitted by {user}: {mt.hash[:8]}...")
            return True
        return False
    
    def _select_phts_for_block(self) -> List[PHTTransaction]:
        """Select PHTs from mempool for inclusion in B_1"""
        # Simple selection strategy (can be enhanced)
        phts = list(self.mempool.values())
        # Sort by gas price (descending) for MEV resistance
        phts.sort(key=lambda x: x.gas_price, reverse=True)
        return phts[:10]  # Limit block size
    
    def _byzantine_set_union_consensus(self) -> Set[MTTransaction]:
        """
        Byzantine set-union consensus for MTs
        Simplified implementation - in practice would use BFT consensus
        """
        print("🛡️ Running Byzantine set-union consensus for MTs")
        
        # For now, return all MTs (simplified)
        # In practice, this would involve validator voting
        verified_mts = set()
        
        for mt in self.exposure_pool:
            if self._verify_mt_proof(mt):
                verified_mts.add(mt)
        
        print(f"✅ Consensus reached on {len(verified_mts)} MTs")
        return verified_mts
    
    def _replace_phts_with_mts(self, phts: List[PHTTransaction], mts: Set[MTTransaction]) -> List[Any]:
        """Replace PHTs with corresponding MTs in B_2"""
        mt_dict = {mt.pht_hash: mt for mt in mts}
        final_transactions = []
        
        for pht in phts:
            if pht.hash in mt_dict:
                # Replace with MT
                final_transactions.append(mt_dict[pht.hash])
            else:
                # Keep PHT if no matching MT
                final_transactions.append(pht)
        
        return final_transactions
    
    def _validate_pht(self, pht: PHTTransaction) -> bool:
        """Validate PHT structure and signature"""
        # Check required fields
        if not all([pht.sender, pht.nonce, pht.gas_limit, pht.gas_price, pht.hash, pht.signature]):
            return False
        
        # Validate signature (simplified)
        return self._verify_signature(pht.sender, pht.hash, pht.signature)
    
    def _validate_mt(self, mt: MTTransaction) -> bool:
        """Validate MT structure and proof"""
        # Check required fields
        if not all([mt.sender, mt.nonce, mt.recipient, mt.value, mt.pht_hash, mt.proof]):
            return False
        
        # Validate proof of matching
        return self._verify_mt_proof(mt)
    
    def _verify_mt_proof(self, mt: MTTransaction) -> bool:
        """Verify that MT matches its corresponding PHT"""
        # Check if PHT exists
        if mt.pht_hash not in self.mempool:
            return False
        
        pht = self.mempool[mt.pht_hash]
        
        # Verify matching fields
        return (mt.sender == pht.sender and 
                mt.nonce == pht.nonce and
                mt.gas_limit == pht.gas_limit and
                mt.gas_price == pht.gas_price)
    
    def _verify_signature(self, sender: str, message: str, signature: str) -> bool:
        """Verify transaction signature (simplified)"""
        # In practice, this would use proper cryptographic verification
        return len(signature) > 0
    
    def _get_last_block_hash(self) -> str:
        """Get hash of the last confirmed block"""
        if not self.blocks:
            return "0x0"
        last_block = max(self.blocks.values(), key=lambda b: b.block_number)
        return hashlib.sha256(str(last_block.block_number).encode()).hexdigest()
    
    def calculate_user_utility(self, user: str, strategy: str) -> float:
        """Calculate user utility based on strategy"""
        return self.utility_functions.user_utility(user, strategy, self)
    
    def calculate_proposer_utility(self, proposer: str, b1: Block, b2: Block) -> float:
        """Calculate proposer utility for B_1 and B_2"""
        return self.utility_functions.proposer_utility(proposer, b1, b2, self)

class UtilityFunctions:
    """Utility functions for P2S protocol analysis"""
    
    def user_utility(self, user: str, strategy: str, protocol: P2SProtocol) -> float:
        """
        Calculate user utility based on strategy
        U_user = f(transaction_success, gas_costs, mev_protection)
        """
        # Base utility from successful transaction
        base_utility = 1.0
        
        # Gas cost penalty
        gas_penalty = 0.1  # Simplified
        
        # MEV protection bonus
        mev_protection_bonus = 0.2
        
        return base_utility - gas_penalty + mev_protection_bonus
    
    def proposer_utility(self, proposer: str, b1: Block, b2: Block, protocol: P2SProtocol) -> float:
        """
        Calculate proposer utility for B_1 and B_2
        U_proposer = f(block_rewards, transaction_fees, mev_opportunities)
        """
        # Block reward (only for B_2)
        block_reward = 2.0 if b2.block_type == "B_2" else 0.0
        
        # Transaction fees from B_2
        transaction_fees = sum(tx.gas_price * tx.gas_limit for tx in b2.transactions if hasattr(tx, 'gas_price'))
        fee_utility = transaction_fees * 0.001  # Convert to utility units
        
        # MEV opportunity reduction (penalty for proposer)
        mev_penalty = 0.1  # P2S reduces MEV opportunities
        
        return block_reward + fee_utility - mev_penalty

def create_pht_transaction(sender: str, recipient: str, value: int, 
                          gas_limit: int, gas_price: int, call_data: str = "") -> PHTTransaction:
    """Create a PHT transaction with hidden fields"""
    nonce = random.randint(1, 1000)
    
    # Create commitment to hidden fields
    hidden_data = f"{recipient}:{value}:{call_data}"
    commitment = hashlib.sha256(hidden_data.encode()).hexdigest()
    
    # Create transaction hash
    tx_data = f"{sender}:{nonce}:{gas_limit}:{gas_price}:{commitment}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
    
    # Create signature (simplified)
    signature = hashlib.sha256(f"{tx_hash}:{sender}".encode()).hexdigest()
    
    return PHTTransaction(
        sender=sender,
        nonce=nonce,
        gas_limit=gas_limit,
        gas_price=gas_price,
        hash=tx_hash,
        signature=signature,
        commitment=commitment
    )

def create_mt_transaction(pht: PHTTransaction, recipient: str, value: int, call_data: str = "") -> MTTransaction:
    """Create an MT transaction that reveals hidden fields from PHT"""
    # Create proof of matching
    proof = hashlib.sha256(f"{pht.hash}:{recipient}:{value}:{call_data}".encode()).hexdigest()
    
    return MTTransaction(
        sender=pht.sender,
        nonce=pht.nonce,
        gas_limit=pht.gas_limit,
        gas_price=pht.gas_price,
        hash=pht.hash,  # Same hash as PHT
        signature=pht.signature,
        recipient=recipient,
        value=value,
        call_data=call_data,
        pht_hash=pht.hash,
        proof=proof
    )
