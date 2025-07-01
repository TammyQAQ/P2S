import random
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

random.seed(16)

tx_counter = 0

class TransactionType(Enum):
    PARTIAL_HIDDEN = "partial_hidden"
    MATCHING = "matching"
    REGULAR = "regular"

@dataclass
class TransactionData:
    """Complete transaction data structure"""
    sender: str
    recipient: str
    value: int
    gas_price: int
    gas_limit: int
    nonce: int
    call_data: bytes
    signature: bytes

class Transaction:
    def __init__(self, 
                 sender: str,
                 recipient: str,
                 value: int,
                 gas_price: int,
                 gas_limit: int,
                 nonce: int,
                 call_data: bytes = b"",
                 mev_potential: int = 0,
                 created_at: int = 0,
                 tx_type: TransactionType = TransactionType.REGULAR):
        global tx_counter
        self.id = tx_counter
        tx_counter += 1
        
        # Core transaction data
        self.sender = sender
        self.recipient = recipient
        self.value = value
        self.gas_price = gas_price
        self.gas_limit = gas_limit
        self.nonce = nonce
        self.call_data = call_data
        self.signature = self._generate_signature()
        
        # P2S specific fields
        self.tx_type = tx_type
        self.mev_potential = mev_potential
        self.created_at = created_at
        self.included_at = None
        self.position = None
        
        # P2S linking
        self.partial_hidden_tx: Optional['Transaction'] = None
        self.matching_tx: Optional['Transaction'] = None
        self.hash = self._compute_hash()
        
    def _generate_signature(self) -> bytes:
        """Generate a mock signature for the transaction"""
        content = f"{self.sender}{self.recipient}{self.value}{self.gas_price}{self.nonce}".encode()
        return hashlib.sha256(content).digest()
    
    def _compute_hash(self) -> str:
        """Compute transaction hash"""
        content = f"{self.sender}{self.recipient}{self.value}{self.gas_price}{self.gas_limit}{self.nonce}{self.call_data.hex()}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def create_partial_hidden_version(self) -> 'Transaction':
        """Create a partial hidden transaction that reveals only sender, nonce, gas params, hash, and signature"""
        pht = Transaction(
            sender=self.sender,
            recipient="",  # Hidden
            value=0,       # Hidden
            gas_price=self.gas_price,
            gas_limit=self.gas_limit,
            nonce=self.nonce,
            call_data=b"", # Hidden
            mev_potential=self.mev_potential,
            created_at=self.created_at,
            tx_type=TransactionType.PARTIAL_HIDDEN
        )
        pht.hash = self.hash  # Same hash as original
        pht.signature = self.signature
        pht.partial_hidden_tx = self
        self.matching_tx = pht
        return pht
    
    def create_matching_transaction(self) -> 'Transaction':
        """Create a matching transaction that reveals the full details"""
        mt = Transaction(
            sender=self.sender,
            recipient=self.recipient,
            value=self.value,
            gas_price=self.gas_price,
            gas_limit=self.gas_limit,
            nonce=self.nonce,
            call_data=self.call_data,
            mev_potential=self.mev_potential,
            created_at=self.created_at,
            tx_type=TransactionType.MATCHING
        )
        mt.hash = self.hash  # Same hash as original
        mt.signature = self.signature
        mt.matching_tx = self
        self.partial_hidden_tx = mt
        return mt
    
    def get_visible_data(self) -> Dict[str, Any]:
        """Get data visible to proposer based on transaction type"""
        if self.tx_type == TransactionType.PARTIAL_HIDDEN:
            return {
                "sender": self.sender,
                "nonce": self.nonce,
                "gas_price": self.gas_price,
                "gas_limit": self.gas_limit,
                "hash": self.hash,
                "signature": self.signature.hex(),
                "tx_type": self.tx_type.value
            }
        else:
            return {
                "sender": self.sender,
                "recipient": self.recipient,
                "value": self.value,
                "gas_price": self.gas_price,
                "gas_limit": self.gas_limit,
                "nonce": self.nonce,
                "call_data": self.call_data.hex(),
                "signature": self.signature.hex(),
                "hash": self.hash,
                "tx_type": self.tx_type.value
            }

    def to_dict(self):
        return {
            "id": self.id,
            "position": self.position,
            "sender": self.sender,
            "recipient": self.recipient,
            "value": self.value,
            "gas_price": self.gas_price,
            "gas_limit": self.gas_limit,
            "nonce": self.nonce,
            "mev_potential": self.mev_potential,
            "created_at": self.created_at,
            "included_at": self.included_at,
            "hash": self.hash,
            "tx_type": self.tx_type.value
        }