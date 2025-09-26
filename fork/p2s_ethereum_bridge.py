#!/usr/bin/env python3
"""
P2S Ethereum Bridge
Connects your existing P2S simulation with the modified Ethereum client
"""

import json
import time
import requests
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify
import threading
import queue

# Import your existing P2S modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from env.node import Node, build_network
from env.propsoer import Proposer
from env.transaction import Transaction

class P2SEthereumBridge:
    """Bridge between P2S simulation and Ethereum client"""
    
    def __init__(self, ethereum_rpc_url: str = "http://localhost:8545"):
        self.ethereum_rpc_url = ethereum_rpc_url
        self.simulation_network = None
        self.proposers = []
        self.users = []
        self.current_round = 0
        self.merkle_trees = {}  # Store merkle trees for each round
        
    def setup_simulation_network(self, num_users: int = 10, num_proposers: int = 5):
        """Set up the P2S simulation network"""
        print(f"Setting up P2S simulation network with {num_users} users and {num_proposers} proposers...")
        
        # Create users and proposers
        self.users = [Node(f"user_{i}") for i in range(num_users)]
        self.proposers = [Proposer(f"proposer_{i}") for i in range(num_proposers)]
        
        # Build network
        self.simulation_network = build_network(self.users, self.proposers)
        
        print(f"Network created with {self.simulation_network.number_of_nodes()} nodes")
        return self.simulation_network
    
    def step1_reveal_merkle_tree(self, user_id: str, merkle_proof: List[str]) -> Dict[str, Any]:
        """
        Step 1 of P2S: User reveals Merkle Tree for PHT
        This integrates with your existing P2S workflow
        """
        print(f"Step 1: User {user_id} revealing Merkle Tree for round {self.current_round}")
        
        # Store merkle tree for this round
        self.merkle_trees[self.current_round] = {
            "user_id": user_id,
            "merkle_proof": merkle_proof,
            "timestamp": time.time()
        }
        
        # Verify merkle proof (simplified implementation)
        proof_valid = len(merkle_proof) > 0 and all(isinstance(p, str) for p in merkle_proof)
        
        if not proof_valid:
            return {
                "status": "error",
                "round": self.current_round,
                "user_id": user_id,
                "message": "Invalid merkle proof"
            }
        
        return {
            "status": "success",
            "round": self.current_round,
            "user_id": user_id,
            "message": "Merkle tree revealed successfully",
            "proof_length": len(merkle_proof)
        }
    
    def step0_proposer_selection(self, slot: int) -> tuple:
        """
        Step 0: Select P1 and P2 via RANDAO
        Select P1 for B1, and P2 as backup for B2 if P1 goes offline
        """
        import random
        
        # RANDAO selection for P1 (two slots ahead)
        random.seed(slot + 42)  # Deterministic for testing
        p1 = random.choice(self.proposers)
        
        # RANDAO selection for P2 (backup proposer)
        random.seed(slot + 43)  # Different seed for P2
        p2 = random.choice([p for p in self.proposers if p != p1])
        
        print(f"RANDAO Selection for slot {slot}:")
        print(f"  P1 (primary): {p1.id}")
        print(f"  P2 (backup):  {p2.id}")
        return p1, p2
    
    def check_proposer_availability(self, proposer, step: str) -> bool:
        """Check if proposer is available (simulate offline scenarios)"""
        import random
        
        # Simulate proposer going offline between steps
        if step == "step2" and random.random() < 0.1:  # 10% chance P1 goes offline before B2
            proposer.available = False
            print(f"  {proposer.id} went offline before {step}")
            return False
        return proposer.available
    
    def step2_select_proposer(self, block_number: int) -> Dict[str, Any]:
        """
        Step 2 of P2S: Select proposer based on P1/P2 availability
        This implements the correct P2S proposer selection logic
        """
        print(f"Step 2: Selecting proposer for block {block_number}")
        
        # Step 0: Select P1 and P2 via RANDAO
        p1, p2 = self.step0_proposer_selection(block_number)
        
        # Check if P1 is still available for B_2
        if self.check_proposer_availability(p1, "step2"):
            # P1 builds both B_1 and B_2
            selected_proposer = p1
            print(f"P1={p1.id} is available, building B_2")
        else:
            # P1 went offline, P2 takes over for B_2
            selected_proposer = p2
            print(f"P1={p1.id} went offline, P2={p2.id} building B_2")
        
        return {
            "proposer_id": selected_proposer.id,
            "address": f"0x{hash(selected_proposer.id) % (2**160):040x}",  # Generate address
            "available": selected_proposer.available,
            "stake": 1000,  # Mock stake
            "round": self.current_round,
            "block_number": block_number,
            "p1_id": p1.id,
            "p2_id": p2.id,
            "same_proposer": selected_proposer.id == p1.id
        }
    
    
    def get_ethereum_block_number(self) -> int:
        """Get current block number from Ethereum node"""
        try:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1
            }
            response = requests.post(self.ethereum_rpc_url, json=payload)
            result = response.json()
            return int(result['result'], 16)
        except Exception as e:
            print(f"Error getting block number: {e}")
            return 0
    
    def sync_with_ethereum(self):
        """Sync P2S simulation with Ethereum blockchain"""
        block_number = self.get_ethereum_block_number()
        if block_number > self.current_round:
            self.current_round = block_number
            print(f"Synced to round {self.current_round}")

# Flask API server for Ethereum client integration
app = Flask(__name__)
bridge = P2SEthereumBridge()

@app.route('/get_proposer', methods=['GET'])
def get_proposer():
    """Get proposer for a specific round (called by Ethereum client)"""
    round_num = int(request.args.get('round', 0))
    block_number = int(request.args.get('block', round_num))
    
    # Sync with Ethereum
    bridge.current_round = round_num
    
    # Execute P2S steps
    proposer_data = bridge.step2_select_proposer(block_number)
    
    return jsonify(proposer_data)

@app.route('/reveal_merkle_tree', methods=['POST'])
def reveal_merkle_tree():
    """Handle merkle tree revelation (Step 1 of P2S)"""
    data = request.get_json()
    user_id = data.get('user_id')
    merkle_proof = data.get('merkle_proof', [])
    
    result = bridge.step1_reveal_merkle_tree(user_id, merkle_proof)
    return jsonify(result)

@app.route('/update_proposer', methods=['POST'])
def update_proposer():
    """Update proposer availability"""
    data = request.get_json()
    proposer_id = data.get('proposer_id')
    available = data.get('available', True)
    
    # Find and update proposer
    for proposer in bridge.proposers:
        if proposer.id == proposer_id:
            proposer.available = available
            return jsonify({"status": "success", "proposer_id": proposer_id})
    
    return jsonify({"error": "Proposer not found"}), 404

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "proposers": len(bridge.proposers),
        "users": len(bridge.users),
        "current_round": bridge.current_round,
        "ethereum_rpc": bridge.ethereum_rpc_url
    })

@app.route('/simulation_status', methods=['GET'])
def simulation_status():
    """Get detailed simulation status"""
    return jsonify({
        "network_nodes": bridge.simulation_network.number_of_nodes() if bridge.simulation_network else 0,
        "network_edges": bridge.simulation_network.number_of_edges() if bridge.simulation_network else 0,
        "proposers": [{"id": p.id, "available": getattr(p, 'available', True)} for p in bridge.proposers],
        "merkle_trees": len(bridge.merkle_trees),
        "current_round": bridge.current_round
    })

def start_bridge_server(host='0.0.0.0', port=8000, debug=True):
    """Start the P2S bridge server"""
    print("Starting P2S Ethereum Bridge Server...")
    print(f"Server will be available at: http://{host}:{port}")
    print("Available endpoints:")
    print("   GET  /get_proposer?round=<round>&block=<block>")
    print("   POST /reveal_merkle_tree")
    print("   POST /update_proposer")
    print("   GET  /health")
    print("   GET  /simulation_status")
    
    # Initialize simulation network
    bridge.setup_simulation_network()
    
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    # You can customize the network size here
    start_bridge_server()
