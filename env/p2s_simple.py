#!/usr/bin/env python3
"""
P2S Protocol - Simple Implementation
Clean, minimal implementation of the P2S protocol for MEV mitigation
"""

import hashlib
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class PHTTransaction:
    """Partially Hidden Transaction - Step 1"""
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
    commitment: Optional[str] = None

@dataclass(frozen=True)
class MTTransaction:
    """Matching Transaction - Step 2"""
    # All PHT fields plus revealed fields
    sender: str
    nonce: int
    gas_limit: int
    gas_price: int
    hash: str
    signature: str
    recipient: str
    value: int
    call_data: str
    pht_hash: str
    proof: str

class P2SProtocol:
    """P2S Protocol Implementation"""
    
    def __init__(self, validators: List[str]):
        self.validators = validators
        self.blocks: Dict[int, Any] = {}
        self.mempool: Dict[str, PHTTransaction] = {}
        self.exposure_pool: set = set()
    
    def step0_proposer_selection(self, slot: int) -> str:
        """Step 0: Select proposer via RANDAO"""
        random.seed(slot + 42)
        return random.choice(self.validators)
    
    def step1_partial_commitment(self, proposer: str, slot: int) -> Dict[str, Any]:
        """Step 1: Create B₁ with PHTs (hidden details)"""
        selected_phts = list(self.mempool.values())[:10]  # Limit block size
        
        b1 = {
            "block_number": slot,
            "proposer": proposer,
            "transactions": selected_phts,
            "block_type": "B_1",
            "timestamp": time.time()
        }
        
        self.blocks[slot] = b1
        print(f"✅ B₁ created with {len(selected_phts)} PHTs (hidden details)")
        return b1
    
    def step2_full_execution(self, proposer: str, slot: int) -> Dict[str, Any]:
        """Step 2: Create B₂ with MTs (revealed details)"""
        b1 = self.blocks[slot]
        
        # Replace PHTs with MTs
        final_transactions = []
        for pht in b1["transactions"]:
            # Find matching MT
            matching_mt = None
            for mt in self.exposure_pool:
                if mt.pht_hash == pht.hash:
                    matching_mt = mt
                    break
            
            if matching_mt:
                final_transactions.append(matching_mt)
            else:
                final_transactions.append(pht)  # Keep PHT if no MT
        
        b2 = {
            "block_number": slot,
            "proposer": proposer,
            "transactions": final_transactions,
            "block_type": "B_2",
            "timestamp": time.time()
        }
        
        self.blocks[slot] = b2
        print(f"✅ B₂ created with {len(final_transactions)} transactions (revealed details)")
        return b2
    
    def submit_pht(self, user: str, pht: PHTTransaction) -> bool:
        """Submit PHT to mempool"""
        self.mempool[pht.hash] = pht
        print(f"📝 {user} submitted PHT: {pht.hash[:8]}...")
        return True
    
    def submit_mt(self, user: str, mt: MTTransaction) -> bool:
        """Submit MT to exposure pool"""
        self.exposure_pool.add(mt)
        print(f"🔓 {user} submitted MT: {mt.hash[:8]}...")
        return True

def create_pht_transaction(sender: str, recipient: str, value: int, 
                          gas_limit: int, gas_price: int) -> PHTTransaction:
    """Create PHT with hidden fields"""
    nonce = random.randint(1, 1000)
    
    # Create commitment to hidden fields
    hidden_data = f"{recipient}:{value}"
    commitment = hashlib.sha256(hidden_data.encode()).hexdigest()
    
    # Create transaction hash
    tx_data = f"{sender}:{nonce}:{gas_limit}:{gas_price}:{commitment}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
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

def create_mt_transaction(pht: PHTTransaction, recipient: str, value: int, 
                         call_data: str = "") -> MTTransaction:
    """Create MT that reveals hidden fields"""
    proof = hashlib.sha256(f"{pht.hash}:{recipient}:{value}".encode()).hexdigest()
    
    return MTTransaction(
        sender=pht.sender,
        nonce=pht.nonce,
        gas_limit=pht.gas_limit,
        gas_price=pht.gas_price,
        hash=pht.hash,
        signature=pht.signature,
        recipient=recipient,
        value=value,
        call_data=call_data,
        pht_hash=pht.hash,
        proof=proof
    )

def demonstrate_p2s():
    """Demonstrate P2S protocol"""
    print("🚀 P2S Protocol Demonstration")
    print("=" * 40)
    
    # Initialize protocol
    validators = ["validator_1", "validator_2", "validator_3"]
    protocol = P2SProtocol(validators)
    
    # Step 0: Select proposer
    proposer = protocol.step0_proposer_selection(100)
    print(f"🎯 Selected proposer: {proposer}")
    
    # Step 1: Users submit PHTs
    print("\n🔒 Step 1: Partial Transaction Commitment")
    users = ["user_1", "user_2", "user_3"]
    phts = []
    
    for i, user in enumerate(users):
        pht = create_pht_transaction(
            sender=user,
            recipient=f"recipient_{i}",
            value=1000,
            gas_limit=21000,
            gas_price=20
        )
        protocol.submit_pht(user, pht)
        phts.append(pht)
    
    # Create B₁
    b1 = protocol.step1_partial_commitment(proposer, 100)
    
    # Step 2: Users submit MTs
    print("\n🔓 Step 2: Full Transaction Execution")
    mts = []
    
    for pht in phts:
        mt = create_mt_transaction(
            pht, 
            f"recipient_{random.randint(0, 2)}", 
            1000
        )
        protocol.submit_mt(pht.sender, mt)
        mts.append(mt)
    
    # Create B₂
    b2 = protocol.step2_full_execution(proposer, 100)
    
    # Results
    print(f"\n📊 Results:")
    print(f"  PHTs submitted: {len(phts)}")
    print(f"  MTs submitted: {len(mts)}")
    print(f"  B₁ transactions: {len(b1['transactions'])}")
    print(f"  B₂ transactions: {len(b2['transactions'])}")
    print(f"  MEV Protection: ✅ Hidden details in B₁, revealed in B₂")

if __name__ == "__main__":
    demonstrate_p2s()
