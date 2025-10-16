#!/usr/bin/env python3
"""
Network Simulation Test
Simulates network behavior without requiring Go installation
"""

import time
import random
import hashlib
from typing import Dict, List, Set, Optional

class NetworkSimulator:
    """Simulates P2S network behavior"""
    
    def __init__(self):
        self.nodes = {}
        self.blocks = {}
        self.transactions = {}
        self.mev_attacks = []
        self.current_slot = 0
        
    def create_node(self, node_id: str, node_type: str, stake: int = 1000):
        """Create a network node"""
        self.nodes[node_id] = {
            'id': node_id,
            'type': node_type,
            'stake': stake,
            'reputation': 100,
            'is_active': True,
            'transactions_submitted': 0,
            'blocks_proposed': 0,
            'mev_profit': 0.0
        }
        print(f"[NODE] Created {node_type} node {node_id} with stake {stake}")
    
    def create_pht_transaction(self, sender: str, value: int = 1000):
        """Create a Partially Hidden Transaction"""
        tx_hash = hashlib.sha256(f"pht_{sender}_{time.time()}".encode()).hexdigest()
        commitment = hashlib.sha256(f"commitment_{tx_hash}_{value}".encode()).hexdigest()
        
        pht = {
            'tx_hash': tx_hash,
            'sender': sender,
            'gas_price': random.randint(20, 100),
            'commitment': commitment,
            'timestamp': time.time(),
            'hidden_value': value,
            'hidden_recipient': f"contract_{random.randint(1, 10)}"
        }
        
        self.transactions[tx_hash] = pht
        self.nodes[sender]['transactions_submitted'] += 1
        
        print(f"[PHT] {sender} submitted PHT: {tx_hash[:8]}... (value: {value})")
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
            'proof': hashlib.sha256(f"proof_{pht_hash}".encode()).hexdigest(),
            'timestamp': time.time()
        }
        
        self.transactions[mt_hash] = mt
        print(f"[MT] {pht['sender']} revealed MT: {mt_hash[:8]}... (recipient: {mt['recipient']}, value: {mt['value']})")
        return mt
    
    def detect_mev_attack(self, pht: Dict) -> Optional[str]:
        """Detect potential MEV attacks"""
        # High gas price indicates potential MEV
        if pht['gas_price'] > 80:
            return "high_gas_price"
        
        # Large value transactions are more susceptible
        if pht['hidden_value'] > 5000:
            return "large_value"
        
        # Contract interactions are more susceptible
        if "contract" in pht['hidden_recipient']:
            return "contract_interaction"
        
        return None
    
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
            attack = self.detect_mev_attack(pht)
            if attack:
                mev_score -= 0.2
                detected_attacks.append(attack)
        
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
        print(f"[B1] MEV Score: {mev_score:.2f}, Attacks: {len(detected_attacks)}")
        
        return b1_block
    
    def propose_b2_block(self, proposer_id: str, b1_block: Dict) -> Dict:
        """Propose a B2 block with MTs"""
        if proposer_id not in self.nodes:
            return None
        
        # Convert PHTs to MTs
        mts = []
        for pht in b1_block['phts']:
            mt = self.create_mt_transaction(pht['tx_hash'])
            if mt:
                mts.append(mt)
        
        b2_block = {
            'block_number': b1_block['block_number'],
            'proposer': proposer_id,
            'mts': mts,
            'block_type': 'B2',
            'b1_block_hash': b1_block['block_number'],
            'timestamp': time.time()
        }
        
        self.blocks[f"B2_{b2_block['block_number']}"] = b2_block
        
        print(f"[B2] Block {b2_block['block_number']} proposed by {proposer_id}")
        print(f"[B2] MTs revealed: {len(mts)}")
        
        return b2_block
    
    def simulate_mev_attack(self, attacker_id: str, target_tx_hash: str) -> bool:
        """Simulate an MEV attack"""
        if target_tx_hash not in self.transactions:
            return False
        
        target_tx = self.transactions[target_tx_hash]
        
        # Calculate potential profit
        profit = target_tx['hidden_value'] * 0.05  # 5% of transaction value
        
        attack = {
            'attacker': attacker_id,
            'target_tx': target_tx_hash,
            'attack_type': 'sandwich',
            'profit': profit,
            'timestamp': time.time(),
            'success': random.random() < 0.3  # 30% success rate
        }
        
        self.mev_attacks.append(attack)
        
        if attack['success']:
            self.nodes[attacker_id]['mev_profit'] += profit
            print(f"[MEV] {attacker_id} successful attack: ${profit:.2f} profit")
        else:
            print(f"[MEV] {attacker_id} attack blocked")
        
        return attack['success']
    
    def run_simulation(self, duration: int = 30):
        """Run P2S network simulation"""
        print(f"[SIM] Starting P2S network simulation for {duration} seconds")
        print("=" * 60)
        
        start_time = time.time()
        end_time = start_time + duration
        
        # Create network nodes
        self.create_node("proposer_1", "proposer", 5000)
        self.create_node("proposer_2", "proposer", 3000)
        self.create_node("user_1", "user", 1000)
        self.create_node("user_2", "user", 1500)
        self.create_node("attacker_1", "attacker", 2000)
        
        block_count = 0
        
        while time.time() < end_time:
            # Simulate transaction submission
            if random.random() < 0.3:  # 30% chance
                user = random.choice(["user_1", "user_2"])
                value = random.randint(100, 10000)
                pht = self.create_pht_transaction(user, value)
                
                # Simulate MEV attack attempt
                if random.random() < 0.2:  # 20% chance
                    self.simulate_mev_attack("attacker_1", pht['tx_hash'])
            
            # Simulate block proposal
            if random.random() < 0.1:  # 10% chance
                proposer = random.choice(["proposer_1", "proposer_2"])
                b1_block = self.propose_b1_block(proposer)
                
                if b1_block:
                    # Wait a bit, then propose B2
                    time.sleep(0.1)
                    b2_block = self.propose_b2_block(proposer, b1_block)
                    block_count += 1
            
            time.sleep(0.1)
        
        print(f"\n[SIM] Simulation completed!")
        self.print_statistics()
    
    def print_statistics(self):
        """Print simulation statistics"""
        print("\n[STATS] P2S Network Simulation Results")
        print("=" * 50)
        
        # Node statistics
        print(f"[STATS] Total Nodes: {len(self.nodes)}")
        print(f"[STATS] Total Blocks: {len(self.blocks)}")
        print(f"[STATS] Total Transactions: {len(self.transactions)}")
        print(f"[STATS] MEV Attacks: {len(self.mev_attacks)}")
        
        # MEV statistics
        successful_attacks = [a for a in self.mev_attacks if a['success']]
        total_profit = sum(a['profit'] for a in successful_attacks)
        
        print(f"[STATS] Successful MEV Attacks: {len(successful_attacks)}")
        print(f"[STATS] Total MEV Profit: ${total_profit:.2f}")
        
        if len(self.mev_attacks) > 0:
            success_rate = len(successful_attacks) / len(self.mev_attacks) * 100
            print(f"[STATS] MEV Success Rate: {success_rate:.1f}%")
        
        # Node performance
        print(f"\n[STATS] Node Performance:")
        for node_id, node in self.nodes.items():
            print(f"[STATS] {node_id}: {node['blocks_proposed']} blocks, ${node['mev_profit']:.2f} profit")
        
        # Block statistics
        b1_blocks = [b for b in self.blocks.values() if b['block_type'] == 'B1']
        b2_blocks = [b for b in self.blocks.values() if b['block_type'] == 'B2']
        
        print(f"\n[STATS] Block Statistics:")
        print(f"[STATS] B1 Blocks: {len(b1_blocks)}")
        print(f"[STATS] B2 Blocks: {len(b2_blocks)}")
        
        if b1_blocks:
            avg_mev_score = sum(b['mev_score'] for b in b1_blocks) / len(b1_blocks)
            print(f"[STATS] Average MEV Score: {avg_mev_score:.2f}")

def main():
    """Main function"""
    print("[START] Network Simulation Test")
    print("=" * 50)
    
    simulator = NetworkSimulator()
    simulator.run_simulation(duration=20)  # 20 second simulation
    
    print(f"\n[COMPLETE] Network test completed successfully!")

if __name__ == "__main__":
    main()
