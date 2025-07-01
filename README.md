# P2S (Partial to Full) Agent-Based Simulation

This repository contains a comprehensive agent-based simulation of the P2S (Partial to Full) protocol, which is designed to reduce MEV (Maximal Extractable Value) opportunities in blockchain systems by splitting block proposal into two coordinated steps.

## Overview

The P2S protocol addresses MEV attacks by implementing a two-step block proposal process:

1. **Step 1: Partial Transaction Commitment (B1)**
   - Proposer constructs block B1 with partially hidden transactions
   - Only sender, nonce, gas parameters, hash, and signature are revealed
   - Recipient address, value, and call data are hidden
   - Block B1 is added to chain without rewards or fees

2. **Step 2: Full Transaction Execution (B2)**
   - Transaction owners release matching transactions with full details
   - Validator committee reaches Byzantine consensus on matching transactions
   - Proposer finalizes block B2, replacing partial hidden transactions
   - Full rewards and fees are distributed

## Key Features

- **Realistic MEV Attack Simulation**: Proposers can attempt front-running and back-running attacks based on partial information
- **Byzantine Consensus**: Validator committee with configurable honest/byzantine ratio
- **Dynamic Transaction Generation**: Users create transactions with varying MEV potential
- **Configurable Parameters**: Multiple simulation scenarios for different network conditions
- **Comprehensive Analysis**: Detailed metrics and visualization of results

## System Architecture

### Core Components

- **Transaction**: Supports partial hidden and matching transaction types
- **User**: Generates transactions with realistic behavior patterns
- **Proposer**: Implements P2S protocol with MEV attack capabilities
- **Chain**: Manages blockchain state and consensus
- **ValidatorCommittee**: Handles Byzantine consensus for matching transactions

### Key Parameters

| Parameter | Description | Default Value |
|-----------|-------------|---------------|
| `num_users` | Number of transaction creators | 50 |
| `num_proposers` | Number of validators/proposers | 10 |
| `num_validators` | Size of validator committee | 20 |
| `mev_attack_probability` | Probability of MEV attacks | 0.3 |
| `transaction_frequency` | Average time between transactions | 5.0 seconds |
| `slot_time` | Time per slot | 12 seconds |
| `block_time` | Time per block | 12 seconds |
| `max_block_size` | Maximum transactions per block | 100 |

## Installation and Setup

1. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

## Usage

### Single Simulation

Run a basic P2S simulation:

```bash
cd playground
python p2s_simulation.py
```

### Batch Simulations

Run multiple configurations and compare results:

```bash
cd playground
python batch_simulation.py
```

### Custom Configuration

Create custom simulation parameters:

```python
from simulation_configs import get_config
from p2s_simulation import P2SSimulation

# Get specific configuration
config = get_config("high_mev")

# Run simulation
simulation = P2SSimulation(**config)
simulation.run_simulation()
results = simulation.analyze_results()
simulation.plot_results(results)
```

## Simulation Scenarios

The simulation includes several pre-configured scenarios:

- **Base**: Standard P2S configuration
- **High MEV**: Aggressive proposers with high MEV attack probability
- **Low MEV**: Honest proposers with low MEV attack probability
- **High Volume**: High transaction throughput scenario
- **Low Volume**: Low transaction throughput scenario
- **Large Validator**: Large validator committee
- **Small Validator**: Small validator committee
- **Fast Blocks**: Fast block time (like Solana)
- **Slow Blocks**: Slow block time (like Bitcoin)

## Output and Analysis

### Generated Files

- `plots/p2s_simulation_results.png`: Individual simulation results
- `plots/batch_simulation_comparison.png`: Comparison across configurations
- `plots/correlation_heatmap.png`: Correlation analysis of metrics
- `plots/batch_simulation_summary.csv`: Summary statistics
- `plots/batch_simulation_results.json`: Detailed results

### Key Metrics

- **MEV Attack Success Rate**: Percentage of successful MEV attacks
- **Transaction Throughput**: Average transactions per block
- **Proposer Rewards**: Total and average rewards per proposer
- **MEV Extraction Efficiency**: Ratio of extracted vs potential MEV
- **Block Confirmation Time**: Time for B1 confirmation

## MEV Attack Simulation

The simulation realistically models MEV attacks:

1. **Front-running**: Proposer creates transaction with higher gas price before target transaction
2. **Back-running**: Proposer creates transaction after target transaction to capture arbitrage
3. **Partial Information Analysis**: Proposer analyzes gas prices, transaction patterns from partial hidden transactions
4. **Attack Success**: Based on proposer aggressiveness and available MEV potential

## Consensus Mechanism

The validator committee implements Byzantine consensus:

- **Honest Validators**: 80% of validators vote honestly
- **Byzantine Validators**: 20% may vote maliciously
- **Consensus Threshold**: Transaction accepted if honest votes > byzantine votes
- **Fault Tolerance**: 1/3 Byzantine tolerance

## Results Interpretation

### MEV Protection Effectiveness

- **Success Rate < 10%**: Strong MEV protection
- **Success Rate 10-30%**: Moderate MEV protection
- **Success Rate > 30%**: Weak MEV protection

### Key Insights

1. **Partial Information Limitation**: Hiding recipient, value, and call data significantly reduces MEV opportunities
2. **Confirmation Delay**: B1 confirmation time affects MEV attack success
3. **Proposer Incentives**: Honest proposers vs MEV-extracting proposers
4. **Network Effects**: Transaction volume and proposer count impact MEV dynamics

## Customization

### Adding New Scenarios

```python
# In simulation_configs.py
CUSTOM_CONFIG = {
    **BASE_CONFIG,
    "num_users": 75,
    "mev_attack_probability": 0.5,
    "simulation_duration": 5400,
}
```

### Modifying Agent Behavior

```python
# Custom user behavior
class CustomUser(User):
    def should_submit_transaction(self, current_time: int) -> bool:
        # Custom transaction frequency logic
        return super().should_submit_transaction(current_time)

# Custom proposer behavior
class CustomProposer(Proposer):
    def attempt_mev_attack(self, partial_hidden_txs, current_time):
        # Custom MEV attack strategy
        return super().attempt_mev_attack(partial_hidden_txs, current_time)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## References

- P2S Protocol Paper: [Link to paper]
- MEV Research: [Link to MEV research]
- Byzantine Consensus: [Link to consensus research]
