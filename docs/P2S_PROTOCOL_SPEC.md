# P2S Protocol Specification

## Overview

The P2S (Proposer in 2 Steps) protocol is a novel consensus mechanism designed to mitigate MEV (Maximal Extractable Value) attacks through a two-step block proposal process.

## Core Concepts

### 1. Partially Hidden Transactions (PHTs)
PHTs contain transaction metadata but hide sensitive fields:
- **Visible**: Sender, gas price, commitment hash, anti-MEV nonce
- **Hidden**: Recipient, value, call data, transaction type

### 2. Matching Transactions (MTs)
MTs reveal the hidden details after B1 block confirmation:
- **Contains**: Full transaction details with cryptographic proof
- **Proves**: That MT matches the original PHT commitment

### 3. Two-Step Block Proposal
- **B1 Block**: Contains only PHTs (details hidden)
- **B2 Block**: Contains MTs (details revealed, replaces B1)

## Protocol Flow

```
1. User submits PHT with hidden details
2. Proposer creates B1 block with PHTs
3. B1 block confirmed on-chain
4. Users reveal MTs with full details
5. Proposer creates B2 block with MTs
6. B2 block replaces B1 block
```

## MEV Protection Mechanisms

### Information Asymmetry
- Attackers cannot see transaction details in PHTs
- No front-running opportunities during B1 phase
- Details only revealed after block commitment

### Cryptographic Commitments
- Pedersen commitments for transaction hiding
- Merkle tree proofs for batch verification
- Zero-knowledge proofs for transaction validation

### Timing Protection
- B1 confirmation prevents transaction modification
- MT revelation happens after commitment
- No opportunity for sandwich attacks

## Consensus Integration

### Validator Selection
- Modified validator selection algorithm
- Stake-weighted proposal rights
- Anti-MEV validator incentives

### Block Validation
- B1 blocks validated for PHT commitments
- B2 blocks validated for MT proofs
- Cross-validation between B1 and B2

### Network Protocol
- Modified P2P messages for P2S
- Gossip protocol for B1/B2 propagation
- RPC API extensions for P2S operations

## Security Properties

### Commitment Binding
- Cryptographic commitments prevent modification
- Hash-based binding ensures integrity
- Nonce-based anti-MEV protection

### Transaction Privacy
- Sensitive details hidden until B2
- No pattern recognition possible
- MEV attack vectors eliminated

### Consensus Security
- Maintains Ethereum's security properties
- Validator selection prevents collusion
- B1/B2 separation ensures ordering

## Performance Considerations

### Block Time
- Target: 12 seconds (same as Ethereum)
- B1 + B2 total time: ~24 seconds
- Parallel processing where possible

### Throughput
- PHTs reduce transaction size
- Batch commitment verification
- Optimized MT revelation

### Network Overhead
- Additional B2 block propagation
- Modified P2P protocol messages
- Increased bandwidth requirements

## Implementation Requirements

### Cryptographic Primitives
- Pedersen commitments
- Merkle tree construction
- Zero-knowledge proof systems
- BLS signature aggregation

### Consensus Modifications
- Modified block structure
- P2S-specific validation rules
- Validator selection algorithm
- MEV protection mechanisms

### Network Layer
- P2P protocol extensions
- RPC API modifications
- Gossip protocol updates
- Message serialization

## Testing Strategy

### Unit Tests
- PHT/MT transaction handling
- Cryptographic commitment verification
- Consensus rule validation
- MEV protection mechanisms

### Integration Tests
- End-to-end transaction flow
- B1/B2 block proposal process
- Network protocol compatibility
- Validator selection and rotation

### Performance Tests
- Throughput benchmarking
- Latency measurements
- Resource usage analysis
- MEV attack resistance

### Attack Simulation
- Sandwich attack attempts
- Front-running simulations
- Validator collusion scenarios
- Network partition attacks

## Future Enhancements

### Advanced MEV Protection
- Dynamic commitment schemes
- Adaptive anti-MEV mechanisms
- Machine learning attack detection

### Scalability Improvements
- Sharding integration
- Layer 2 compatibility
- Cross-chain MEV protection

### Privacy Enhancements
- Zero-knowledge transaction proofs
- Homomorphic encryption
- Multi-party computation
