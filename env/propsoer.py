'''Define the proposer actions here'''
from env.node import Node
from typing import List, Optional, Dict, Any
import hashlib
import json

class Proposer(Node):
    def __init__(self, node_id: int, stake: int = 1000) -> None:
        super().__init__(node_id)
        self.stake = stake
        self.available = True
        self.selected_rounds = []  # Track rounds when this proposer was selected
        self.merkle_proofs = {}    # Store merkle proofs for P2S
        
    def is_available(self) -> bool:
        """Check if proposer is available for selection"""
        return self.available
    
    def set_availability(self, available: bool) -> None:
        """Set proposer availability"""
        self.available = available
    
    def add_merkle_proof(self, round_num: int, proof: List[str]) -> None:
        """Add merkle proof for a specific round (P2S Step 1)"""
        self.merkle_proofs[round_num] = proof
    
    def get_merkle_proof(self, round_num: int) -> Optional[List[str]]:
        """Get merkle proof for a specific round"""
        return self.merkle_proofs.get(round_num)
    
    def was_selected_in_round(self, round_num: int) -> bool:
        """Check if this proposer was selected in a specific round"""
        return round_num in self.selected_rounds
    
    def mark_selected(self, round_num: int) -> None:
        """Mark this proposer as selected for a round"""
        self.selected_rounds.append(round_num)
        self.available = False  # Temporarily unavailable after selection
    
    def reset_availability(self) -> None:
        """Reset proposer availability (called at end of round)"""
        self.available = True
    
    def get_proposer_info(self) -> Dict[str, Any]:
        """Get proposer information for API responses"""
        return {
            "id": self.id,
            "stake": self.stake,
            "available": self.available,
            "selected_rounds": self.selected_rounds,
            "merkle_proofs_count": len(self.merkle_proofs)
        }
    
    def generate_address(self) -> str:
        """Generate a mock Ethereum address for this proposer"""
        # Simple hash-based address generation
        hash_input = f"proposer_{self.id}_{self.stake}".encode()
        address_hash = hashlib.sha256(hash_input).hexdigest()[:40]
        return f"0x{address_hash}"