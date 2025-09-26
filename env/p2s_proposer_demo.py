"""
P2S Proposer Selection Demonstration
Shows P1/P2 selection via RANDAO and P2 takeover when P1 goes offline
"""

import hashlib
import time
import random
from typing import Dict, List, Optional, Any, Tuple
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
    # Hidden fields
    recipient: Optional[str] = None
    value: Optional[int] = None
    call_data: Optional[str] = None

@dataclass(frozen=True)
class MTTransaction:
    """Matching Transaction - Step 2"""
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
    """P2S Protocol with Correct P1/P2 Selection"""
    
    def __init__(self, validators: List[str]):
        self.validators = validators
        self.blocks: Dict[int, Any] = {}
        self.mempool: Dict[str, PHTTransaction] = {}
        self.exposure_pool: set = set()
        self.proposer_availability: Dict[str, bool] = {v: True for v in validators}
    
    def step0_proposer_selection(self, slot: int) -> Tuple[str, str]:
        """Step 0: Select P1 and P2 via RANDAO"""
        # RANDAO selection for P1 (two slots ahead)
        random.seed(slot + 42)
        p1 = random.choice(self.validators)
        
        # RANDAO selection for P2 (backup proposer)
        random.seed(slot + 43)
        p2 = random.choice([v for v in self.validators if v != p1])
        
        print(f"RANDAO Selection for slot {slot}:")
        print(f"  P1 (primary): {p1}")
        print(f"  P2 (backup):  {p2}")
        return p1, p2
    
    def check_proposer_availability(self, proposer: str, step: str) -> bool:
        """Check if proposer is available (simulate offline scenarios)"""
        # Simulate proposer going offline between steps
        if step == "step2" and random.random() < 0.3:  # 30% chance P1 goes offline before B2
            self.proposer_availability[proposer] = False
            print(f"  {proposer} went offline before {step}")
            return False
        return self.proposer_availability.get(proposer, True)
    
    def step1_partial_commitment(self, p1: str, slot: int) -> Dict[str, Any]:
        """Step 1: P1 creates B₁ with PHTs"""
        print(f"\nStep 1: P1={p1} creating B₁")
        
        selected_phts = list(self.mempool.values())[:5]  # Limit block size
        
        b1 = {
            "block_number": slot,
            "proposer": p1,
            "transactions": selected_phts,
            "block_type": "B_1",
            "timestamp": time.time()
        }
        
        self.blocks[slot] = b1
        print(f"  B₁ created with {len(selected_phts)} PHTs (hidden details)")
        return b1
    
    def step2_full_execution(self, p1: str, p2: str, slot: int) -> Dict[str, Any]:
        """Step 2: P1 builds B₂ if available, otherwise P2 takes over"""
        print(f"\nStep 2: Checking proposer availability for B₂")
        
        # Check if P1 is still available for B_2
        if self.check_proposer_availability(p1, "step2"):
            # P1 builds both B_1 and B_2
            proposer_for_b2 = p1
            print(f"  P1={p1} is available, building B_2")
        else:
            # P1 went offline, P2 takes over for B_2
            proposer_for_b2 = p2
            print(f"  P1={p1} went offline, P2={p2} building B_2")
        
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
            "proposer": proposer_for_b2,
            "transactions": final_transactions,
            "block_type": "B_2",
            "timestamp": time.time()
        }
        
        self.blocks[slot] = b2
        print(f"  B₂ created with {len(final_transactions)} transactions by {proposer_for_b2}")
        return b2
    
    def submit_pht(self, user: str, pht: PHTTransaction) -> bool:
        """Submit PHT to mempool"""
        self.mempool[pht.hash] = pht
        print(f"  {user} submitted PHT: {pht.hash[:8]}...")
        return True
    
    def submit_mt(self, user: str, mt: MTTransaction) -> bool:
        """Submit MT to exposure pool"""
        self.exposure_pool.add(mt)
        print(f"  {user} submitted MT: {mt.pht_hash[:8]}...")
        return True

def create_pht_transaction(sender: str, recipient: str, value: int, 
                          gas_limit: int, gas_price: int) -> PHTTransaction:
    """Create a PHT transaction"""
    tx_data = f"{sender}{recipient}{value}{gas_limit}{gas_price}{time.time()}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
    
    return PHTTransaction(
        sender=sender,
        nonce=1,
        gas_limit=gas_limit,
        gas_price=gas_price,
        hash=tx_hash,
        signature=f"sig_{tx_hash[:8]}"
    )

def create_mt_transaction(pht: PHTTransaction, recipient: str, value: int, 
                         call_data: str = "") -> MTTransaction:
    """Create an MT transaction from PHT"""
    proof = f"proof_{pht.hash[:8]}"
    
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

def demonstrate_p1_p2_selection():
    """Demonstrate P1/P2 selection and P2 takeover scenarios"""
    print("P2S Proposer Selection Demonstration")
    print("=" * 50)
    
    # Initialize protocol
    validators = ["validator_1", "validator_2", "validator_3", "validator_4"]
    protocol = P2SProtocol(validators)
    
    # Create some transactions
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
    
    # Run multiple scenarios
    for scenario in range(1, 4):
        print(f"\n{'='*20} Scenario {scenario} {'='*20}")
        
        # Step 0: Select P1 and P2 via RANDAO
        p1, p2 = protocol.step0_proposer_selection(100 + scenario)
        
        # Step 1: P1 creates B₁
        b1 = protocol.step1_partial_commitment(p1, 100 + scenario)
        
        # Users submit MTs
        print(f"\nUsers submitting MTs:")
        for pht in phts:
            mt = create_mt_transaction(
                pht, 
                f"recipient_{random.randint(0, 2)}", 
                1000
            )
            protocol.submit_mt(pht.sender, mt)
        
        # Step 2: Create B₂ (P1 or P2)
        b2 = protocol.step2_full_execution(p1, p2, 100 + scenario)
        
        # Results
        print(f"\nResults:")
        print(f"  B₁ proposer: {b1['proposer']}")
        print(f"  B₂ proposer: {b2['proposer']}")
        print(f"  Same proposer: {'Yes' if b1['proposer'] == b2['proposer'] else 'No'}")
        print(f"  MEV Protection: Active")

if __name__ == "__main__":
    demonstrate_p1_p2_selection()
