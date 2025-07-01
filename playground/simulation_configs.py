"""
P2S Simulation Configuration Scenarios

This file contains different simulation configurations to test various aspects
of the P2S protocol under different conditions.
"""

# Base configuration
BASE_CONFIG = {
    "num_users": 50,
    "num_proposers": 10,
    "num_validators": 20,
    "simulation_duration": 3600,  # 1 hour
    "slot_time": 12,
    "block_time": 12,
    "max_block_size": 100,
    "mev_attack_probability": 0.3,
    "transaction_frequency": 5.0
}

# High MEV environment - more aggressive proposers
HIGH_MEV_CONFIG = {
    **BASE_CONFIG,
    "mev_attack_probability": 0.7,
    "num_proposers": 15,  # More proposers competing
    "simulation_duration": 7200,  # 2 hours for more data
}

# Low MEV environment - honest proposers
LOW_MEV_CONFIG = {
    **BASE_CONFIG,
    "mev_attack_probability": 0.1,
    "num_proposers": 5,
    "simulation_duration": 3600,
}

# High transaction volume
HIGH_VOLUME_CONFIG = {
    **BASE_CONFIG,
    "num_users": 100,
    "max_block_size": 200,
    "transaction_frequency": 2.0,  # More frequent transactions
    "simulation_duration": 7200,
}

# Low transaction volume
LOW_VOLUME_CONFIG = {
    **BASE_CONFIG,
    "num_users": 20,
    "max_block_size": 50,
    "transaction_frequency": 10.0,  # Less frequent transactions
    "simulation_duration": 3600,
}

# Large validator set
LARGE_VALIDATOR_CONFIG = {
    **BASE_CONFIG,
    "num_validators": 50,
    "num_proposers": 20,
    "simulation_duration": 7200,
}

# Small validator set
SMALL_VALIDATOR_CONFIG = {
    **BASE_CONFIG,
    "num_validators": 10,
    "num_proposers": 5,
    "simulation_duration": 3600,
}

# Fast block time (like Solana)
FAST_BLOCKS_CONFIG = {
    **BASE_CONFIG,
    "slot_time": 0.4,  # 400ms slots
    "block_time": 0.4,  # 400ms blocks
    "simulation_duration": 3600,
}

# Slow block time (like Bitcoin)
SLOW_BLOCKS_CONFIG = {
    **BASE_CONFIG,
    "slot_time": 600,  # 10 minutes
    "block_time": 600,  # 10 minutes
    "simulation_duration": 7200,
}

# All configurations for batch testing
ALL_CONFIGS = {
    "base": BASE_CONFIG,
    "high_mev": HIGH_MEV_CONFIG,
    "low_mev": LOW_MEV_CONFIG,
    "high_volume": HIGH_VOLUME_CONFIG,
    "low_volume": LOW_VOLUME_CONFIG,
    "large_validator": LARGE_VALIDATOR_CONFIG,
    "small_validator": SMALL_VALIDATOR_CONFIG,
    "fast_blocks": FAST_BLOCKS_CONFIG,
    "slow_blocks": SLOW_BLOCKS_CONFIG,
}

def get_config(config_name: str):
    """Get a specific configuration by name"""
    return ALL_CONFIGS.get(config_name, BASE_CONFIG)

def list_configs():
    """List all available configurations"""
    return list(ALL_CONFIGS.keys()) 