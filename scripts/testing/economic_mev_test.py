#!/usr/bin/env python3
"""
MEV Economic Attack Simulation
Tests the economic utility of MEV attacks with gas fee pressure
"""

import time
import random
import hashlib
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class AttackType(Enum):
    SANDWICH = "sandwich"
    FRONT_RUN = "front_run"
    BACK_RUN = "back_run"
    ARBITRAGE = "arbitrage"

class UserType(Enum):
    BENIGN = "benign"
    ATTACKER = "attacker"

@dataclass
class MEVAttack:
    attacker_id: str
    target_tx_hash: str
    attack_type: AttackType
    gas_price: int
    gas_limit: int
    expected_profit: float
    success_probability: float
    revealed: bool = False
    executed: bool = False
    actual_profit: float = 0.0
    gas_cost: float = 0.0

class MEVEconomicSimulator:
    """Simulates P2S network with economic MEV attack pressure"""
    
    def __init__(self):
        self.nodes = {}
        self.blocks = {}
        self.transactions = {}
        self.mev_attacks = []
        self.current_slot = 0
        self.base_gas_price = 20
        self.gas_cost_per_unit = 0.000001  # ETH per gas unit
        
    def create_node(self, node_id: str, node_type: str, user_type: UserType, stake: int = 1000, eth_balance: float = 10.0):
        """Create a network node with economic parameters"""
        self.nodes[node_id] = {
            'id': node_id,
            'type': node_type,
            'user_type': user_type,
            'stake': stake,
            'eth_balance': eth_balance,
            'reputation': 100,
            'is_active': True,
            'transactions_submitted': 0,
            'blocks_proposed': 0,
            'total_profit': 0.0,
            'total_gas_spent': 0.0,
            'successful_attacks': 0,
            'failed_attacks': 0,
            'net_profit': 0.0
        }
        print(f"[NODE] Created {user_type.value} {node_type} {node_id} with {eth_balance} ETH")
    
    def create_pht_transaction(self, sender: str, value: int = 1000, is_mev_target: bool = False):
        """Create a Partially Hidden Transaction"""
        tx_hash = hashlib.sha256(f"pht_{sender}_{time.time()}".encode()).hexdigest()
        commitment = hashlib.sha256(f"commitment_{tx_hash}_{value}".encode()).hexdigest()
        
        # MEV targets have higher gas prices and larger values
        gas_price = self.base_gas_price
        if is_mev_target:
            gas_price = random.randint(50, 150)  # Higher gas for MEV targets
            value = random.randint(5000, 20000)  # Larger values
        
        pht = {
            'tx_hash': tx_hash,
            'sender': sender,
            'gas_price': gas_price,
            'gas_limit': random.randint(21000, 100000),
            'commitment': commitment,
            'timestamp': time.time(),
            'hidden_value': value,
            'hidden_recipient': f"contract_{random.randint(1, 10)}",
            'is_mev_target': is_mev_target,
            'mev_potential': value * 0.1 if is_mev_target else 0  # 10% of value as MEV potential
        }
        
        self.transactions[tx_hash] = pht
        self.nodes[sender]['transactions_submitted'] += 1
        
        target_indicator = " [MEV TARGET]" if is_mev_target else ""
        print(f"[PHT] {sender} submitted PHT: {tx_hash[:8]}... (value: {value}, gas: {gas_price}){target_indicator}")
        return pht
    
    def create_mt_transaction(self, pht_hash: str):
        """Create a Matching Transaction"""
        if pht_hash not in self.transactions:
            return None
        
        pht = self.transactions[pht_hash]
        mt_hash = hashlib.sha256(f"mt_{pht_hash}".encode()).hexdigest()
        
        mt = {
            'tx_hash': mt_hash,
            'pht_hash': pht_hash,
            'sender': pht['sender'],
            'recipient': pht['hidden_recipient'],
            'value': pht['hidden_value'],
            'gas_price': pht['gas_price'],
            'gas_limit': pht['gas_limit'],
            'proof': hashlib.sha256(f"proof_{pht_hash}".encode()).hexdigest(),
            'timestamp': time.time(),
            'is_mev_target': pht['is_mev_target'],
            'mev_potential': pht['mev_potential']
        }
        
        self.transactions[mt_hash] = mt
        target_indicator = " [MEV TARGET]" if mt['is_mev_target'] else ""
        print(f"[MT] {pht['sender']} revealed MT: {mt_hash[:8]}... (recipient: {mt['recipient']}, value: {mt['value']}){target_indicator}")
        return mt
    
    def calculate_attack_profitability(self, attacker_id: str, target_tx: Dict, attack_type: AttackType) -> Tuple[float, float, float]:
        """Calculate if an MEV attack is profitable considering gas costs"""
        
        # Base profit calculation
        if attack_type == AttackType.SANDWICH:
            base_profit = target_tx['mev_potential'] * 0.8  # 80% of MEV potential
            success_prob = 0.4  # 40% success rate for sandwich
        elif attack_type == AttackType.FRONT_RUN:
            base_profit = target_tx['mev_potential'] * 0.6  # 60% of MEV potential
            success_prob = 0.3  # 30% success rate for front-run
        elif attack_type == AttackType.BACK_RUN:
            base_profit = target_tx['mev_potential'] * 0.5  # 50% of MEV potential
            success_prob = 0.5  # 50% success rate for back-run
        elif attack_type == AttackType.ARBITRAGE:
            base_profit = target_tx['mev_potential'] * 0.7  # 70% of MEV potential
            success_prob = 0.6  # 60% success rate for arbitrage
        else:
            base_profit = 0
            success_prob = 0
        
        # Gas cost calculation
        attack_gas_price = target_tx['gas_price'] + random.randint(10, 50)  # Must outbid target
        attack_gas_limit = random.randint(100000, 300000)  # Higher gas limit for complex attacks
        gas_cost = attack_gas_price * attack_gas_limit * self.gas_cost_per_unit
        
        # Expected profit = (success_prob * base_profit) - gas_cost
        expected_profit = (success_prob * base_profit) - gas_cost
        
        return expected_profit, gas_cost, success_prob
    
    def create_mev_attack(self, attacker_id: str, target_tx_hash: str) -> Optional[MEVAttack]:
        """Create an MEV attack with economic considerations"""
        if target_tx_hash not in self.transactions:
            return None
        
        target_tx = self.transactions[target_tx_hash]
        
        # Only attack MEV targets
        if not target_tx['is_mev_target']:
            return None
        
        # Choose attack type
        attack_type = random.choice(list(AttackType))
        
        # Calculate profitability
        expected_profit, gas_cost, success_prob = self.calculate_attack_profitability(
            attacker_id, target_tx, attack_type
        )
        
        # Only create attack if potentially profitable
        if expected_profit <= 0:
            print(f"[MEV] {attacker_id} skipped unprofitable {attack_type.value} attack (expected: ${expected_profit:.2f})")
            return None
        
        attack = MEVAttack(
            attacker_id=attacker_id,
            target_tx_hash=target_tx_hash,
            attack_type=attack_type,
            gas_price=target_tx['gas_price'] + random.randint(10, 50),
            gas_limit=random.randint(100000, 300000),
            expected_profit=expected_profit,
            success_probability=success_prob
        )
        
        self.mev_attacks.append(attack)
        print(f"[MEV] {attacker_id} created {attack_type.value} attack targeting {target_tx_hash[:8]}... (expected: ${expected_profit:.2f}, gas: ${gas_cost:.4f})")
        
        return attack
    
    def decide_attack_revelation(self, attack: MEVAttack) -> bool:
        """Decide whether to reveal the attack MT based on economic factors"""
        
        attacker = self.nodes[attack.attacker_id]
        
        # Calculate gas cost
        gas_cost = attack.gas_price * attack.gas_limit * self.gas_cost_per_unit
        
        # Check if attacker has enough ETH
        if attacker['eth_balance'] < gas_cost:
            print(f"[MEV] {attack.attacker_id} insufficient ETH for attack (need: ${gas_cost:.4f}, have: ${attacker['eth_balance']:.4f})")
            return False
        
        # Economic decision: reveal if expected profit > gas cost
        if attack.expected_profit > gas_cost:
            print(f"[MEV] {attack.attacker_id} decided to reveal attack (profit: ${attack.expected_profit:.2f} > cost: ${gas_cost:.4f})")
            return True
        else:
            print(f"[MEV] {attack.attacker_id} decided NOT to reveal attack (profit: ${attack.expected_profit:.2f} <= cost: ${gas_cost:.4f})")
            return False
    
    def execute_attack(self, attack: MEVAttack) -> bool:
        """Execute the MEV attack and calculate actual results"""
        
        attacker = self.nodes[attack.attacker_id]
        
        # Calculate gas cost
        gas_cost = attack.gas_price * attack.gas_limit * self.gas_cost_per_unit
        
        # Deduct gas cost from attacker's balance
        attacker['eth_balance'] -= gas_cost
        attacker['total_gas_spent'] += gas_cost
        
        # Determine if attack succeeds
        attack.success = random.random() < attack.success_probability
        
        if attack.success:
            # Calculate actual profit (may differ from expected)
            actual_profit = attack.expected_profit * random.uniform(0.8, 1.2)
            attack.actual_profit = actual_profit
            attack.gas_cost = gas_cost
            
            attacker['total_profit'] += actual_profit
            attacker['successful_attacks'] += 1
            attacker['net_profit'] = attacker['total_profit'] - attacker['total_gas_spent']
            
            print(f"[MEV] {attack.attacker_id} SUCCESSFUL {attack.attack_type.value} attack: ${actual_profit:.2f} profit, ${gas_cost:.4f} gas cost")
        else:
            attack.actual_profit = 0
            attack.gas_cost = gas_cost
            
            attacker['failed_attacks'] += 1
            attacker['net_profit'] = attacker['total_profit'] - attacker['total_gas_spent']
            
            print(f"[MEV] {attack.attacker_id} FAILED {attack.attack_type.value} attack: $0 profit, ${gas_cost:.4f} gas cost")
        
        attack.executed = True
        return attack.success
    
    def propose_b1_block(self, proposer_id: str) -> Dict:
        """Propose a B1 block with PHTs"""
        if proposer_id not in self.nodes:
            return None
        
        # Get pending PHTs
        phts = [tx for tx in self.transactions.values() if 'hidden_value' in tx]
        
        if not phts:
            return None
        
        # Select top PHTs by gas price
        phts.sort(key=lambda x: x['gas_price'], reverse=True)
        selected_phts = phts[:5]  # Limit block size
        
        # Calculate MEV protection score
        mev_score = 1.0
        detected_attacks = []
        
        for pht in selected_phts:
            if pht['is_mev_target']:
                mev_score -= 0.3
                detected_attacks.append("mev_target")
        
        mev_score = max(0.0, mev_score)
        
        b1_block = {
            'block_number': len(self.blocks) + 1,
            'proposer': proposer_id,
            'phts': selected_phts,
            'block_type': 'B1',
            'mev_score': mev_score,
            'detected_attacks': detected_attacks,
            'timestamp': time.time()
        }
        
        self.blocks[b1_block['block_number']] = b1_block
        self.nodes[proposer_id]['blocks_proposed'] += 1
        
        print(f"[B1] Block {b1_block['block_number']} proposed by {proposer_id}")
        print(f"[B1] MEV Score: {mev_score:.2f}, MEV Targets: {len(detected_attacks)}")
        
        return b1_block
    
    def propose_b2_block(self, proposer_id: str, b1_block: Dict) -> Dict:
        """Propose a B2 block with MTs and handle attack revelations"""
        if proposer_id not in self.nodes:
            return None
        
        # Convert PHTs to MTs
        mts = []
        for pht in b1_block['phts']:
            mt = self.create_mt_transaction(pht['tx_hash'])
            if mt:
                mts.append(mt)
        
        # Handle MEV attack revelations
        attack_mts = []
        for attack in self.mev_attacks:
            if not attack.revealed and not attack.executed:
                # Check if target MT is in this block
                target_mt = next((mt for mt in mts if mt['pht_hash'] == attack.target_tx_hash), None)
                if target_mt:
                    # Decide whether to reveal attack
                    if self.decide_attack_revelation(attack):
                        attack.revealed = True
                        # Execute the attack
                        self.execute_attack(attack)
                        attack_mts.append(attack)
        
        b2_block = {
            'block_number': b1_block['block_number'],
            'proposer': proposer_id,
            'mts': mts,
            'attack_mts': attack_mts,
            'block_type': 'B2',
            'b1_block_hash': b1_block['block_number'],
            'timestamp': time.time()
        }
        
        self.blocks[f"B2_{b2_block['block_number']}"] = b2_block
        
        print(f"[B2] Block {b2_block['block_number']} proposed by {proposer_id}")
        print(f"[B2] MTs revealed: {len(mts)}, Attacks executed: {len(attack_mts)}")
        
        return b2_block
    
    def run_economic_simulation(self, duration: int = 30):
        """Run P2S network simulation with economic MEV pressure"""
        print(f"[SIM] Starting P2S Economic MEV Simulation for {duration} seconds")
        print("=" * 70)
        
        start_time = time.time()
        end_time = start_time + duration
        
        # Create network nodes with economic parameters
        self.create_node("proposer_1", "proposer", UserType.BENIGN, 5000, 15.0)
        self.create_node("proposer_2", "proposer", UserType.BENIGN, 3000, 12.0)
        self.create_node("user_1", "user", UserType.BENIGN, 1000, 8.0)
        self.create_node("user_2", "user", UserType.BENIGN, 1500, 10.0)
        self.create_node("attacker_1", "user", UserType.ATTACKER, 2000, 20.0)  # More ETH for attacks
        self.create_node("attacker_2", "proposer", UserType.ATTACKER, 4000, 25.0)  # Proposer attacker
        
        block_count = 0
        
        while time.time() < end_time:
            # Simulate transaction submission
            if random.random() < 0.4:  # 40% chance
                user = random.choice(["user_1", "user_2"])
                is_mev_target = random.random() < 0.3  # 30% of transactions are MEV targets
                value = random.randint(100, 5000) if not is_mev_target else random.randint(5000, 20000)
                pht = self.create_pht_transaction(user, value, is_mev_target)
                
                # Create MEV attack if target is attractive
                if is_mev_target and random.random() < 0.5:  # 50% chance to attack MEV targets
                    attacker = random.choice(["attacker_1", "attacker_2"])
                    self.create_mev_attack(attacker, pht['tx_hash'])
            
            # Simulate block proposal
            if random.random() < 0.15:  # 15% chance
                proposer = random.choice(["proposer_1", "proposer_2"])
                b1_block = self.propose_b1_block(proposer)
                
                if b1_block:
                    # Wait a bit, then propose B2
                    time.sleep(0.1)
                    b2_block = self.propose_b2_block(proposer, b1_block)
                    block_count += 1
            
            time.sleep(0.1)
        
        print(f"\n[SIM] Economic simulation completed!")
        self.print_economic_statistics()
    
    def print_economic_statistics(self):
        """Print economic simulation statistics"""
        print("\n[STATS] P2S Economic MEV Simulation Results")
        print("=" * 60)
        
        # Overall statistics
        print(f"[STATS] Total Nodes: {len(self.nodes)}")
        print(f"[STATS] Total Blocks: {len(self.blocks)}")
        print(f"[STATS] Total Transactions: {len(self.transactions)}")
        print(f"[STATS] MEV Attacks Created: {len(self.mev_attacks)}")
        
        # Attack statistics
        revealed_attacks = [a for a in self.mev_attacks if a.revealed]
        executed_attacks = [a for a in self.mev_attacks if a.executed]
        successful_attacks = [a for a in self.mev_attacks if a.executed and a.success]
        
        print(f"[STATS] Attacks Revealed: {len(revealed_attacks)}")
        print(f"[STATS] Attacks Executed: {len(executed_attacks)}")
        print(f"[STATS] Successful Attacks: {len(successful_attacks)}")
        
        if len(self.mev_attacks) > 0:
            revelation_rate = len(revealed_attacks) / len(self.mev_attacks) * 100
            execution_rate = len(executed_attacks) / len(self.mev_attacks) * 100
            success_rate = len(successful_attacks) / len(executed_attacks) * 100 if executed_attacks else 0
            
            print(f"[STATS] Attack Revelation Rate: {revelation_rate:.1f}%")
            print(f"[STATS] Attack Execution Rate: {execution_rate:.1f}%")
            print(f"[STATS] Attack Success Rate: {success_rate:.1f}%")
        
        # Economic statistics
        total_gas_spent = sum(a.gas_cost for a in executed_attacks)
        total_profit = sum(a.actual_profit for a in successful_attacks)
        net_profit = total_profit - total_gas_spent
        
        print(f"\n[STATS] Economic Results:")
        print(f"[STATS] Total Gas Spent: ${total_gas_spent:.4f}")
        print(f"[STATS] Total Profit: ${total_profit:.2f}")
        print(f"[STATS] Net Profit: ${net_profit:.2f}")
        
        if total_gas_spent > 0:
            roi = (net_profit / total_gas_spent) * 100
            print(f"[STATS] ROI: {roi:.1f}%")
        
        # Node economic performance
        print(f"\n[STATS] Node Economic Performance:")
        for node_id, node in self.nodes.items():
            if node['user_type'] == UserType.ATTACKER:
                print(f"[STATS] {node_id} ({node['user_type'].value}):")
                print(f"[STATS]   ETH Balance: ${node['eth_balance']:.4f}")
                print(f"[STATS]   Total Profit: ${node['total_profit']:.2f}")
                print(f"[STATS]   Total Gas Spent: ${node['total_gas_spent']:.4f}")
                print(f"[STATS]   Net Profit: ${node['net_profit']:.2f}")
                print(f"[STATS]   Successful Attacks: {node['successful_attacks']}")
                print(f"[STATS]   Failed Attacks: {node['failed_attacks']}")
        
        # Attack type analysis
        attack_types = {}
        for attack in executed_attacks:
            attack_type = attack.attack_type.value
            if attack_type not in attack_types:
                attack_types[attack_type] = {'count': 0, 'profit': 0, 'gas_cost': 0}
            attack_types[attack_type]['count'] += 1
            attack_types[attack_type]['profit'] += attack.actual_profit
            attack_types[attack_type]['gas_cost'] += attack.gas_cost
        
        if attack_types:
            print(f"\n[STATS] Attack Type Analysis:")
            for attack_type, stats in attack_types.items():
                net_profit = stats['profit'] - stats['gas_cost']
                print(f"[STATS] {attack_type}: {stats['count']} attacks, ${stats['profit']:.2f} profit, ${stats['gas_cost']:.4f} gas, ${net_profit:.2f} net")

def main():
    """Main function"""
    print("[START] Economic MEV Attack Simulation")
    print("=" * 60)
    
    simulator = MEVEconomicSimulator()
    simulator.run_economic_simulation(duration=25)  # 25 second simulation
    
    print(f"\n[COMPLETE] Economic MEV test completed successfully!")

if __name__ == "__main__":
    main()
