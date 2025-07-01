import random
import numpy as np
from typing import List, Optional
from .transaction import Transaction, TransactionType

class User:
    def __init__(self, user_id: str, balance: int = 10000):
        self.user_id = user_id
        self.balance = balance
        self.nonce = 0
        self.transactions: List[Transaction] = []
        self.pending_transactions: List[Transaction] = []
        
        # User behavior parameters
        self.transaction_frequency = np.random.exponential(5.0)  # Average time between transactions
        self.max_gas_price = random.randint(20, 100)  # Gwei
        self.preferred_gas_limit = random.randint(21000, 100000)
        self.mev_sensitivity = random.random()  # How much they care about MEV protection
        
    def create_transaction(self, 
                          recipient: str, 
                          value: int, 
                          current_time: int,
                          mev_potential: int = 0) -> Transaction:
        """Create a new transaction"""
        gas_price = min(self.max_gas_price, 
                       int(self.max_gas_price * (1 + mev_potential / 1000)))
        
        tx = Transaction(
            sender=self.user_id,
            recipient=recipient,
            value=value,
            gas_price=gas_price,
            gas_limit=self.preferred_gas_limit,
            nonce=self.nonce,
            mev_potential=mev_potential,
            created_at=current_time
        )
        
        self.nonce += 1
        self.transactions.append(tx)
        self.pending_transactions.append(tx)
        return tx
    
    def create_partial_hidden_transaction(self, tx: Transaction) -> Transaction:
        """Create a partial hidden version of a transaction"""
        pht = tx.create_partial_hidden_version()
        return pht
    
    def create_matching_transaction(self, tx: Transaction) -> Transaction:
        """Create a matching transaction for a partial hidden transaction"""
        mt = tx.create_matching_transaction()
        return mt
    
    def should_submit_transaction(self, current_time: int) -> bool:
        """Determine if user should submit a transaction based on frequency"""
        if not self.pending_transactions:
            return False
        
        last_tx_time = max([tx.created_at for tx in self.pending_transactions], default=0)
        time_since_last = current_time - last_tx_time
        
        return time_since_last >= self.transaction_frequency
    
    def get_random_recipient(self, other_users: List['User']) -> str:
        """Get a random recipient from other users"""
        if not other_users:
            return f"contract_{random.randint(1, 100)}"
        
        other_user = random.choice(other_users)
        return other_user.user_id
    
    def update_balance(self, amount: int):
        """Update user balance"""
        self.balance += amount
    
    def get_transaction_stats(self) -> dict:
        """Get statistics about user's transactions"""
        if not self.transactions:
            return {
                "total_transactions": 0,
                "total_value": 0,
                "avg_gas_price": 0,
                "total_mev_potential": 0
            }
        
        return {
            "total_transactions": len(self.transactions),
            "total_value": sum(tx.value for tx in self.transactions),
            "avg_gas_price": np.mean([tx.gas_price for tx in self.transactions]),
            "total_mev_potential": sum(tx.mev_potential for tx in self.transactions)
        }
