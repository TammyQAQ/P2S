"""
P2S Etherscan-style Block Explorer Test
Shows transactions in blocks like Etherscan for 10 blocks
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

class P2SBlockExplorer:
    """P2S Block Explorer - Etherscan-style display"""
    
    def __init__(self, validators: List[str]):
        self.validators = validators
        self.blocks: Dict[int, Any] = {}
        self.mempool: Dict[str, PHTTransaction] = {}
        self.exposure_pool: set = set()
        self.proposer_availability: Dict[str, bool] = {v: True for v in validators}
        self.block_number = 0
        
    def step0_proposer_selection(self, slot: int) -> Tuple[str, str]:
        """Step 0: Select P1 and P2 via RANDAO"""
        random.seed(slot + 42)
        p1 = random.choice(self.validators)
        random.seed(slot + 43)
        p2 = random.choice([v for v in self.validators if v != p1])
        return p1, p2
    
    def check_proposer_availability(self, proposer: str) -> bool:
        """Check if proposer is available"""
        if random.random() < 0.15:  # 15% chance of going offline
            self.proposer_availability[proposer] = False
            return False
        return self.proposer_availability.get(proposer, True)
    
    def step1_partial_commitment(self, p1: str, slot: int) -> Dict[str, Any]:
        """Step 1: Create B₁ with PHTs"""
        if not self.check_proposer_availability(p1):
            raise Exception(f"P1 {p1} is offline, cannot create B_1")
        
        selected_phts = list(self.mempool.values())[:8]  # Limit block size
        
        b1 = {
            "block_number": slot,
            "proposer": p1,
            "transactions": selected_phts,
            "block_type": "B_1",
            "timestamp": time.time(),
            "gas_used": sum(tx.gas_limit for tx in selected_phts),
            "gas_limit": 30000000,  # Ethereum-like gas limit
            "base_fee": 20,  # Base fee per gas
            "size": len(str(selected_phts))  # Approximate block size
        }
        
        self.blocks[slot] = b1
        return b1
    
    def step2_full_execution(self, p1: str, p2: str, slot: int) -> Dict[str, Any]:
        """Step 2: Create B₂ with MTs"""
        if self.check_proposer_availability(p1):
            proposer_for_b2 = p1
        else:
            proposer_for_b2 = p2
        
        b1 = self.blocks[slot]
        
        # Replace PHTs with MTs
        final_transactions = []
        for pht in b1["transactions"]:
            matching_mt = None
            for mt in self.exposure_pool:
                if mt.pht_hash == pht.hash:
                    matching_mt = mt
                    break
            
            if matching_mt:
                final_transactions.append(matching_mt)
            else:
                final_transactions.append(pht)
        
        b2 = {
            "block_number": slot,
            "proposer": proposer_for_b2,
            "transactions": final_transactions,
            "block_type": "B_2",
            "timestamp": time.time(),
            "gas_used": sum(tx.gas_limit for tx in final_transactions),
            "gas_limit": 30000000,
            "base_fee": 20,
            "size": len(str(final_transactions))
        }
        
        self.blocks[slot] = b2
        return b2
    
    def submit_pht(self, user: str, pht: PHTTransaction) -> bool:
        """Submit PHT to mempool"""
        self.mempool[pht.hash] = pht
        return True
    
    def submit_mt(self, user: str, mt: MTTransaction) -> bool:
        """Submit MT to exposure pool"""
        self.exposure_pool.add(mt)
        return True
    
    def display_block(self, block: Dict[str, Any], block_num: int):
        """Display block information like Etherscan"""
        print(f"\n{'='*80}")
        print(f"BLOCK #{block_num} - {block['block_type']}")
        print(f"{'='*80}")
        
        print(f"Block Hash:     0x{hash(str(block)) % (2**256):064x}")
        print(f"Parent Hash:    0x{hash(str(block_num-1)) % (2**256):064x}")
        print(f"Proposer:       {block['proposer']}")
        print(f"Timestamp:      {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block['timestamp']))}")
        print(f"Gas Used:       {block['gas_used']:,}")
        print(f"Gas Limit:      {block['gas_limit']:,}")
        print(f"Base Fee:       {block['base_fee']} Gwei")
        print(f"Block Size:     {block['size']:,} bytes")
        print(f"Transaction Count: {len(block['transactions'])}")
        
        print(f"\n{'TRANSACTIONS':^80}")
        print(f"{'='*80}")
        
        for i, tx in enumerate(block['transactions']):
            print(f"\nTransaction #{i+1}")
            print(f"{'─'*40}")
            print(f"Hash:          0x{tx.hash}")
            print(f"From:          {tx.sender}")
            
            if hasattr(tx, 'recipient') and tx.recipient:
                print(f"To:            {tx.recipient}")
            else:
                print(f"To:            [HIDDEN]")
            
            if hasattr(tx, 'value') and tx.value:
                print(f"Value:         {tx.value:,} ETH")
            else:
                print(f"Value:         [HIDDEN]")
            
            print(f"Nonce:         {tx.nonce}")
            print(f"Gas Limit:     {tx.gas_limit:,}")
            print(f"Gas Price:     {tx.gas_price} Gwei")
            
            if hasattr(tx, 'call_data') and tx.call_data:
                print(f"Call Data:     {tx.call_data}")
            else:
                print(f"Call Data:     [HIDDEN]")
            
            print(f"Signature:     {tx.signature}")
            
            if hasattr(tx, 'pht_hash'):
                print(f"PHT Hash:      {tx.pht_hash}")
                print(f"Proof:         {tx.proof}")

def create_pht_transaction(sender: str, recipient: str, value: int, 
                          gas_limit: int, gas_price: int) -> PHTTransaction:
    """Create a PHT transaction"""
    tx_data = f"{sender}{recipient}{value}{gas_limit}{gas_price}{time.time()}"
    tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
    
    return PHTTransaction(
        sender=sender,
        nonce=random.randint(1, 100),
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

def run_etherscan_test():
    """Run P2S test with Etherscan-style display for 10 blocks"""
    print("P2S Block Explorer Test - 10 Blocks")
    print("="*80)
    
    # Initialize protocol
    validators = ["validator_1", "validator_2", "validator_3", "validator_4"]
    explorer = P2SBlockExplorer(validators)
    
    # Create some users and transactions
    users = ["user_1", "user_2", "user_3", "user_4", "user_5"]
    recipients = ["contract_A", "contract_B", "contract_C", "wallet_X", "wallet_Y"]
    
    print(f"Initializing with {len(validators)} validators and {len(users)} users")
    print(f"Running 10 blocks with P2S protocol...")
    
    for block_num in range(1, 11):
        print(f"\n{'='*20} BLOCK {block_num} {'='*20}")
        
        # Step 0: Select P1 and P2
        p1, p2 = explorer.step0_proposer_selection(block_num)
        print(f"RANDAO Selection: P1={p1}, P2={p2}")
        
        # Create some PHTs for this block
        phts = []
        for i in range(random.randint(3, 6)):  # 3-6 transactions per block
            user = random.choice(users)
            recipient = random.choice(recipients)
            value = random.randint(100, 10000)
            gas_limit = random.randint(21000, 100000)
            gas_price = random.randint(20, 100)
            
            pht = create_pht_transaction(user, recipient, value, gas_limit, gas_price)
            explorer.submit_pht(user, pht)
            phts.append(pht)
        
        print(f"Created {len(phts)} PHTs for this block")
        
        # Step 1: Create B₁
        try:
            b1 = explorer.step1_partial_commitment(p1, block_num)
            explorer.display_block(b1, block_num)
        except Exception as e:
            print(f"Error creating B₁: {e}")
            continue
        
        # Users submit MTs
        mts = []
        for pht in phts:
            if random.random() < 0.9:  # 90% chance to submit MT
                mt = create_mt_transaction(
                    pht, 
                    random.choice(recipients), 
                    random.randint(100, 10000),
                    f"0x{random.randint(1000, 9999):04x}"
                )
                explorer.submit_mt(pht.sender, mt)
                mts.append(mt)
        
        print(f"Users submitted {len(mts)} MTs")
        
        # Step 2: Create B₂
        b2 = explorer.step2_full_execution(p1, p2, block_num)
        explorer.display_block(b2, block_num)
        
        # Summary
        print(f"\nBlock {block_num} Summary:")
        print(f"  B₁ proposer: {b1['proposer']}")
        print(f"  B₂ proposer: {b2['proposer']}")
        print(f"  Same proposer: {'Yes' if b1['proposer'] == b2['proposer'] else 'No'}")
        print(f"  PHTs: {len(b1['transactions'])}")
        print(f"  MTs revealed: {len([tx for tx in b2['transactions'] if hasattr(tx, 'recipient') and tx.recipient])}")
        print(f"  MEV Protection: Active")

if __name__ == "__main__":
    run_etherscan_test()
