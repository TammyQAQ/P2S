"""
P2S Realistic Network Simulation
Large-scale simulation with many validators, users, and malicious participants
"""

import hashlib
import time
import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class ParticipantType(Enum):
    HONEST_USER = "honest_user"
    MEV_ATTACKER = "mev_attacker"
    FRONT_RUNNER = "front_runner"
    SANDWICH_ATTACKER = "sandwich_attacker"
    ARBITRAGEUR = "arbitrageur"

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
    participant_type: ParticipantType = ParticipantType.HONEST_USER

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
    participant_type: ParticipantType = ParticipantType.HONEST_USER

class RealisticP2SNetwork:
    """Realistic P2S Network with Large Scale and Malicious Participants"""
    
    def __init__(self, num_validators: int = 100, num_users: int = 1000):
        self.num_validators = num_validators
        self.num_users = num_users
        
        # Create realistic validator set (like Ethereum 2.0)
        self.validators = [f"validator_{i:04d}" for i in range(num_validators)]
        
        # Create diverse user base with different participant types
        self.users = self._create_realistic_users()
        
        # Network state
        self.blocks: Dict[int, Any] = {}
        self.mempool: Dict[str, PHTTransaction] = {}
        self.exposure_pool: set = set()
        self.proposer_availability: Dict[str, bool] = {v: True for v in self.validators}
        
        # Attack statistics
        self.attack_stats = {
            "front_running_attempts": 0,
            "sandwich_attempts": 0,
            "arbitrage_attempts": 0,
            "successful_attacks": 0,
            "blocked_attacks": 0
        }
        
        print(f"Network initialized:")
        print(f"  Validators: {num_validators}")
        print(f"  Users: {num_users}")
        print(f"  Honest users: {len([u for u in self.users if u['type'] == ParticipantType.HONEST_USER])}")
        print(f"  MEV attackers: {len([u for u in self.users if u['type'] == ParticipantType.MEV_ATTACKER])}")
        print(f"  Front runners: {len([u for u in self.users if u['type'] == ParticipantType.FRONT_RUNNER])}")
        print(f"  Sandwich attackers: {len([u for u in self.users if u['type'] == ParticipantType.SANDWICH_ATTACKER])}")
        print(f"  Arbitrageurs: {len([u for u in self.users if u['type'] == ParticipantType.ARBITRAGEUR])}")
    
    def _create_realistic_users(self) -> List[Dict[str, Any]]:
        """Create realistic user distribution"""
        users = []
        
        # 70% honest users
        honest_count = int(self.num_users * 0.70)
        for i in range(honest_count):
            users.append({
                "id": f"honest_user_{i:04d}",
                "type": ParticipantType.HONEST_USER,
                "stake": random.randint(1, 100),  # Small to medium stakes
                "activity_level": random.uniform(0.1, 0.8)  # How often they transact
            })
        
        # 10% MEV attackers
        mev_count = int(self.num_users * 0.10)
        for i in range(mev_count):
            users.append({
                "id": f"mev_attacker_{i:03d}",
                "type": ParticipantType.MEV_ATTACKER,
                "stake": random.randint(50, 500),  # Higher stakes
                "activity_level": random.uniform(0.7, 1.0),  # Very active
                "attack_success_rate": random.uniform(0.1, 0.3)  # Success rate
            })
        
        # 8% Front runners
        frontrun_count = int(self.num_users * 0.08)
        for i in range(frontrun_count):
            users.append({
                "id": f"frontrunner_{i:03d}",
                "type": ParticipantType.FRONT_RUNNER,
                "stake": random.randint(30, 200),
                "activity_level": random.uniform(0.8, 1.0),
                "attack_success_rate": random.uniform(0.2, 0.4)
            })
        
        # 7% Sandwich attackers
        sandwich_count = int(self.num_users * 0.07)
        for i in range(sandwich_count):
            users.append({
                "id": f"sandwich_{i:03d}",
                "type": ParticipantType.SANDWICH_ATTACKER,
                "stake": random.randint(100, 1000),  # High stakes needed
                "activity_level": random.uniform(0.6, 0.9),
                "attack_success_rate": random.uniform(0.15, 0.35)
            })
        
        # 5% Arbitrageurs
        arbitrage_count = int(self.num_users * 0.05)
        for i in range(arbitrage_count):
            users.append({
                "id": f"arbitrageur_{i:03d}",
                "type": ParticipantType.ARBITRAGEUR,
                "stake": random.randint(20, 300),
                "activity_level": random.uniform(0.5, 0.8),
                "attack_success_rate": random.uniform(0.3, 0.6)  # Higher success rate
            })
        
        return users
    
    def step0_proposer_selection(self, slot: int) -> Tuple[str, str]:
        """Step 0: Select P1 and P2 via RANDAO"""
        random.seed(slot + 42)
        p1 = random.choice(self.validators)
        random.seed(slot + 43)
        p2 = random.choice([v for v in self.validators if v != p1])
        return p1, p2
    
    def check_proposer_availability(self, proposer: str) -> bool:
        """Check if proposer is available (realistic offline rate)"""
        # Realistic offline rate: 1-2% chance
        if random.random() < 0.015:
            self.proposer_availability[proposer] = False
            return False
        return self.proposer_availability.get(proposer, True)
    
    def create_realistic_transactions(self, block_num: int) -> List[PHTTransaction]:
        """Create realistic transaction mix for a block"""
        transactions = []
        
        # Determine how many transactions this block will have (realistic range)
        tx_count = random.randint(50, 200)  # Realistic block size
        
        for i in range(tx_count):
            # Select user based on activity level
            active_users = [u for u in self.users if random.random() < u['activity_level']]
            if not active_users:
                continue
                
            user = random.choice(active_users)
            
            # Create transaction based on user type
            if user['type'] == ParticipantType.HONEST_USER:
                tx = self._create_honest_transaction(user, i)
            elif user['type'] == ParticipantType.MEV_ATTACKER:
                tx = self._create_mev_attack_transaction(user, i)
            elif user['type'] == ParticipantType.FRONT_RUNNER:
                tx = self._create_frontrun_transaction(user, i)
            elif user['type'] == ParticipantType.SANDWICH_ATTACKER:
                tx = self._create_sandwich_transaction(user, i)
            elif user['type'] == ParticipantType.ARBITRAGEUR:
                tx = self._create_arbitrage_transaction(user, i)
            
            if tx:
                transactions.append(tx)
                self.mempool[tx.hash] = tx
        
        return transactions
    
    def _create_honest_transaction(self, user: Dict, tx_id: int) -> PHTTransaction:
        """Create honest user transaction"""
        tx_data = f"{user['id']}{tx_id}{time.time()}{random.random()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        return PHTTransaction(
            sender=user['id'],
            nonce=random.randint(1, 1000),
            gas_limit=random.randint(21000, 100000),
            gas_price=random.randint(20, 50),  # Normal gas prices
            hash=tx_hash,
            signature=f"sig_{tx_hash[:8]}",
            participant_type=ParticipantType.HONEST_USER
        )
    
    def _create_mev_attack_transaction(self, user: Dict, tx_id: int) -> PHTTransaction:
        """Create MEV attack transaction"""
        self.attack_stats["front_running_attempts"] += 1
        
        tx_data = f"{user['id']}{tx_id}{time.time()}{random.random()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        return PHTTransaction(
            sender=user['id'],
            nonce=random.randint(1, 1000),
            gas_limit=random.randint(50000, 200000),  # Higher gas limit
            gas_price=random.randint(100, 500),  # Much higher gas price
            hash=tx_hash,
            signature=f"sig_{tx_hash[:8]}",
            participant_type=ParticipantType.MEV_ATTACKER
        )
    
    def _create_frontrun_transaction(self, user: Dict, tx_id: int) -> PHTTransaction:
        """Create front-running transaction"""
        self.attack_stats["front_running_attempts"] += 1
        
        tx_data = f"{user['id']}{tx_id}{time.time()}{random.random()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        return PHTTransaction(
            sender=user['id'],
            nonce=random.randint(1, 1000),
            gas_limit=random.randint(30000, 150000),
            gas_price=random.randint(80, 300),  # High gas price for front-running
            hash=tx_hash,
            signature=f"sig_{tx_hash[:8]}",
            participant_type=ParticipantType.FRONT_RUNNER
        )
    
    def _create_sandwich_transaction(self, user: Dict, tx_id: int) -> PHTTransaction:
        """Create sandwich attack transaction"""
        self.attack_stats["sandwich_attempts"] += 1
        
        tx_data = f"{user['id']}{tx_id}{time.time()}{random.random()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        return PHTTransaction(
            sender=user['id'],
            nonce=random.randint(1, 1000),
            gas_limit=random.randint(100000, 500000),  # Very high gas limit
            gas_price=random.randint(200, 1000),  # Very high gas price
            hash=tx_hash,
            signature=f"sig_{tx_hash[:8]}",
            participant_type=ParticipantType.SANDWICH_ATTACKER
        )
    
    def _create_arbitrage_transaction(self, user: Dict, tx_id: int) -> PHTTransaction:
        """Create arbitrage transaction"""
        self.attack_stats["arbitrage_attempts"] += 1
        
        tx_data = f"{user['id']}{tx_id}{time.time()}{random.random()}"
        tx_hash = hashlib.sha256(tx_data.encode()).hexdigest()
        
        return PHTTransaction(
            sender=user['id'],
            nonce=random.randint(1, 1000),
            gas_limit=random.randint(50000, 300000),
            gas_price=random.randint(50, 200),  # Moderate-high gas price
            hash=tx_hash,
            signature=f"sig_{tx_hash[:8]}",
            participant_type=ParticipantType.ARBITRAGEUR
        )
    
    def step1_partial_commitment(self, p1: str, slot: int) -> Dict[str, Any]:
        """Step 1: Create B₁ with PHTs"""
        if not self.check_proposer_availability(p1):
            raise Exception(f"P1 {p1} is offline, cannot create B_1")
        
        # Create realistic transaction mix
        transactions = self.create_realistic_transactions(slot)
        
        # Select transactions for block (prioritize by gas price)
        transactions.sort(key=lambda x: x.gas_price, reverse=True)
        selected_phts = transactions[:min(len(transactions), 150)]  # Realistic block size
        
        b1 = {
            "block_number": slot,
            "proposer": p1,
            "transactions": selected_phts,
            "block_type": "B_1",
            "timestamp": time.time(),
            "gas_used": sum(tx.gas_limit for tx in selected_phts),
            "gas_limit": 30000000,
            "base_fee": 20,
            "size": len(str(selected_phts))
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
    
    def submit_mt(self, user_id: str, mt: MTTransaction) -> bool:
        """Submit MT to exposure pool"""
        self.exposure_pool.add(mt)
        return True
    
    def analyze_mev_protection(self, b1: Dict, b2: Dict) -> Dict[str, Any]:
        """Analyze MEV protection effectiveness"""
        analysis = {
            "total_transactions": len(b1["transactions"]),
            "honest_transactions": 0,
            "attack_transactions": 0,
            "hidden_transactions": 0,
            "revealed_transactions": 0,
            "mev_protection_rate": 0.0,
            "attack_types": {
                "mev_attacker": 0,
                "front_runner": 0,
                "sandwich": 0,
                "arbitrage": 0
            }
        }
        
        # Analyze B₁ (PHTs)
        for tx in b1["transactions"]:
            if tx.participant_type == ParticipantType.HONEST_USER:
                analysis["honest_transactions"] += 1
            else:
                analysis["attack_transactions"] += 1
                attack_type_key = tx.participant_type.value.replace("_attacker", "")
                if attack_type_key in analysis["attack_types"]:
                    analysis["attack_types"][attack_type_key] += 1
            
            if tx.recipient is None:  # Hidden
                analysis["hidden_transactions"] += 1
        
        # Analyze B₂ (MTs)
        for tx in b2["transactions"]:
            if hasattr(tx, 'recipient') and tx.recipient:
                analysis["revealed_transactions"] += 1
        
        # Calculate MEV protection rate
        if analysis["total_transactions"] > 0:
            analysis["mev_protection_rate"] = analysis["hidden_transactions"] / analysis["total_transactions"]
        
        return analysis
    
    def display_network_stats(self):
        """Display comprehensive network statistics"""
        print(f"\n{'='*80}")
        print(f"REALISTIC P2S NETWORK STATISTICS")
        print(f"{'='*80}")
        
        print(f"Network Scale:")
        print(f"  Validators: {self.num_validators:,}")
        print(f"  Total Users: {self.num_users:,}")
        
        print(f"\nUser Distribution:")
        for user_type in ParticipantType:
            count = len([u for u in self.users if u['type'] == user_type])
            percentage = (count / self.num_users) * 100
            print(f"  {user_type.value}: {count:,} ({percentage:.1f}%)")
        
        print(f"\nAttack Statistics:")
        print(f"  Front-running attempts: {self.attack_stats['front_running_attempts']:,}")
        print(f"  Sandwich attempts: {self.attack_stats['sandwich_attempts']:,}")
        print(f"  Arbitrage attempts: {self.attack_stats['arbitrage_attempts']:,}")
        print(f"  Total attack attempts: {sum(self.attack_stats.values()):,}")

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
        proof=proof,
        participant_type=pht.participant_type
    )

def run_realistic_network_test():
    """Run realistic P2S network simulation"""
    print("P2S Realistic Network Simulation")
    print("="*80)
    
    # Initialize realistic network
    network = RealisticP2SNetwork(num_validators=100, num_users=1000)
    network.display_network_stats()
    
    print(f"\nRunning 5 blocks with realistic transaction patterns...")
    
    for block_num in range(1, 6):
        print(f"\n{'='*20} BLOCK {block_num} {'='*20}")
        
        # Step 0: Select P1 and P2
        p1, p2 = network.step0_proposer_selection(block_num)
        print(f"RANDAO Selection: P1={p1}, P2={p2}")
        
        # Step 1: Create B₁
        try:
            b1 = network.step1_partial_commitment(p1, block_num)
            print(f"B₁ created with {len(b1['transactions'])} transactions")
        except Exception as e:
            print(f"Error creating B₁: {e}")
            continue
        
        # Users submit MTs (simulate realistic MT submission rate)
        mts_submitted = 0
        for tx in b1["transactions"]:
            if random.random() < 0.85:  # 85% MT submission rate
                mt = create_mt_transaction(
                    tx,
                    f"recipient_{random.randint(1, 100)}",
                    random.randint(100, 10000),
                    f"0x{random.randint(1000, 9999):04x}"
                )
                network.submit_mt(tx.sender, mt)
                mts_submitted += 1
        
        print(f"Users submitted {mts_submitted} MTs")
        
        # Step 2: Create B₂
        b2 = network.step2_full_execution(p1, p2, block_num)
        
        # Analyze MEV protection
        analysis = network.analyze_mev_protection(b1, b2)
        
        print(f"\nBlock {block_num} Analysis:")
        print(f"  Total transactions: {analysis['total_transactions']}")
        print(f"  Honest transactions: {analysis['honest_transactions']}")
        print(f"  Attack transactions: {analysis['attack_transactions']}")
        print(f"  MEV Protection Rate: {analysis['mev_protection_rate']*100:.1f}%")
        print(f"  Attack breakdown:")
        for attack_type, count in analysis['attack_types'].items():
            if count > 0:
                print(f"    {attack_type}: {count}")
        
        print(f"  B₁ proposer: {b1['proposer']}")
        print(f"  B₂ proposer: {b2['proposer']}")
        print(f"  Same proposer: {'Yes' if b1['proposer'] == b2['proposer'] else 'No'}")

if __name__ == "__main__":
    run_realistic_network_test()
