# Consensus Design Details

## P2S Consensus Architecture

The P2S consensus mechanism extends Ethereum's existing consensus with a two-step block proposal process designed to mitigate MEV attacks.

## Core Components

### 1. P2S Consensus Engine (`consensus/p2s/p2s.go`)

```go
type P2SConsensus struct {
    // Ethereum consensus engine
    ethConsensus consensus.Engine
    
    // P2S-specific components
    phtManager   *PHTManager
    mtManager    *MTManager
    validatorMgr *ValidatorManager
    mevDetector  *MEVDetector
}

func (p *P2SConsensus) Prepare(chain consensus.ChainReader, header *types.Header) error {
    // Prepare B1 block with PHTs
    return p.prepareB1Block(chain, header)
}

func (p *P2SConsensus) Finalize(chain consensus.ChainReader, header *types.Header, state *state.StateDB, txs []*types.Transaction, receipts []*types.Receipt) error {
    // Finalize B2 block with MTs
    return p.finalizeB2Block(chain, header, state, txs, receipts)
}
```

### 2. PHT Manager (`consensus/p2s/pht.go`)

```go
type PHTManager struct {
    commitmentScheme CommitmentScheme
    antiMEVNonce     *AntiMEVNonce
}

type PHTTransaction struct {
    // Visible fields
    Sender     common.Address `json:"sender"`
    GasPrice   *big.Int      `json:"gasPrice"`
    Commitment []byte        `json:"commitment"`
    Nonce      []byte        `json:"nonce"`
    
    // Hidden fields (committed)
    Recipient common.Address `json:"recipient"`
    Value     *big.Int      `json:"value"`
    CallData  []byte        `json:"callData"`
    TxType    uint8         `json:"txType"`
}

func (p *PHTManager) CreatePHT(tx *types.Transaction) (*PHTTransaction, error) {
    // Create commitment for hidden fields
    commitment, err := p.commitmentScheme.Commit(tx.Recipient(), tx.Value(), tx.Data())
    if err != nil {
        return nil, err
    }
    
    // Generate anti-MEV nonce
    nonce := p.antiMEVNonce.Generate()
    
    return &PHTTransaction{
        Sender:     tx.From(),
        GasPrice:   tx.GasPrice(),
        Commitment: commitment,
        Nonce:      nonce,
        Recipient:  tx.Recipient(),
        Value:      tx.Value(),
        CallData:   tx.Data(),
        TxType:     tx.Type(),
    }, nil
}
```

### 3. MT Manager (`consensus/p2s/mt.go`)

```go
type MTManager struct {
    commitmentScheme CommitmentScheme
    proofSystem      ProofSystem
}

type MTTransaction struct {
    // Revealed fields
    Recipient common.Address `json:"recipient"`
    Value     *big.Int      `json:"value"`
    CallData  []byte        `json:"callData"`
    TxType    uint8         `json:"txType"`
    
    // Proof fields
    PHTHash   common.Hash `json:"phtHash"`
    Proof     []byte      `json:"proof"`
    Timestamp uint64      `json:"timestamp"`
}

func (m *MTManager) CreateMT(pht *PHTTransaction) (*MTTransaction, error) {
    // Generate proof that MT matches PHT
    proof, err := m.proofSystem.Prove(pht.Commitment, pht.Recipient, pht.Value, pht.CallData)
    if err != nil {
        return nil, err
    }
    
    return &MTTransaction{
        Recipient: pht.Recipient,
        Value:     pht.Value,
        CallData:  pht.CallData,
        TxType:    pht.TxType,
        PHTHash:   pht.Hash(),
        Proof:     proof,
        Timestamp: uint64(time.Now().Unix()),
    }, nil
}

func (m *MTManager) VerifyMT(mt *MTTransaction, pht *PHTTransaction) error {
    // Verify proof matches commitment
    return m.proofSystem.Verify(mt.Proof, pht.Commitment, mt.Recipient, mt.Value, mt.CallData)
}
```

### 4. Validator Manager (`consensus/p2s/validator.go`)

```go
type ValidatorManager struct {
    validators map[common.Address]*Validator
    selection  ValidatorSelection
}

type Validator struct {
    Address    common.Address `json:"address"`
    Stake      *big.Int      `json:"stake"`
    Reputation int64         `json:"reputation"`
    IsActive   bool          `json:"isActive"`
    LastBlock  uint64        `json:"lastBlock"`
}

func (v *ValidatorManager) SelectProposer(blockNumber uint64) (common.Address, error) {
    // Weighted selection based on stake and reputation
    return v.selection.SelectProposer(v.validators, blockNumber)
}

func (v *ValidatorManager) UpdateReputation(validator common.Address, score int64) {
    if val, exists := v.validators[validator]; exists {
        val.Reputation += score
        // Cap reputation to prevent gaming
        if val.Reputation > MaxReputation {
            val.Reputation = MaxReputation
        }
    }
}
```

## Block Structure Modifications

### B1 Block Structure

```go
type B1Block struct {
    Header       *types.Header      `json:"header"`
    PHTs         []*PHTTransaction `json:"phts"`
    BlockType    uint8             `json:"blockType"`    // 1 for B1
    MEVScore     float64           `json:"mevScore"`     // MEV protection score
    ValidatorSig []byte            `json:"validatorSig"` // Validator signature
}

func (b *B1Block) Validate() error {
    // Validate PHT commitments
    for _, pht := range b.PHTs {
        if err := b.validatePHT(pht); err != nil {
            return err
        }
    }
    
    // Validate MEV protection score
    if b.MEVScore < MinMEVScore {
        return errors.New("insufficient MEV protection")
    }
    
    return nil
}
```

### B2 Block Structure

```go
type B2Block struct {
    Header       *types.Header      `json:"header"`
    MTs          []*MTTransaction   `json:"mts"`
    BlockType    uint8             `json:"blockType"`    // 2 for B2
    B1BlockHash  common.Hash       `json:"b1BlockHash"` // Reference to B1
    ValidatorSig []byte            `json:"validatorSig"` // Validator signature
}

func (b *B2Block) Validate(b1Block *B1Block) error {
    // Validate MT proofs against B1 PHTs
    if len(b.MTs) != len(b1Block.PHTs) {
        return errors.New("MT count mismatch with B1 PHTs")
    }
    
    for i, mt := range b.MTs {
        pht := b1Block.PHTs[i]
        if err := b.validateMT(mt, pht); err != nil {
            return err
        }
    }
    
    return nil
}
```

## MEV Protection Mechanisms

### MEV Detector (`consensus/p2s/mev_detector.go`)

```go
type MEVDetector struct {
    attackPatterns map[string]AttackPattern
    threshold      float64
}

type AttackPattern struct {
    Name        string  `json:"name"`
    Threshold   float64 `json:"threshold"`
    Description string  `json:"description"`
}

func (m *MEVDetector) DetectMEV(phts []*PHTTransaction) (float64, []string) {
    var mevScore float64
    var detectedAttacks []string
    
    for _, pht := range phts {
        // Analyze transaction patterns
        score, attacks := m.analyzeTransaction(pht)
        mevScore += score
        detectedAttacks = append(detectedAttacks, attacks...)
    }
    
    // Normalize score
    mevScore = mevScore / float64(len(phts))
    
    return mevScore, detectedAttacks
}

func (m *MEVDetector) analyzeTransaction(pht *PHTTransaction) (float64, []string) {
    var score float64
    var attacks []string
    
    // Check for sandwich attack patterns
    if m.isSandwichPattern(pht) {
        score += 0.8
        attacks = append(attacks, "sandwich_attack")
    }
    
    // Check for front-running patterns
    if m.isFrontRunPattern(pht) {
        score += 0.6
        attacks = append(attacks, "front_running")
    }
    
    // Check for arbitrage patterns
    if m.isArbitragePattern(pht) {
        score += 0.3
        attacks = append(attacks, "arbitrage")
    }
    
    return score, attacks
}
```

## Network Protocol Extensions

### P2P Message Types

```go
const (
    PHTMessageType = 0x10
    MTMessageType  = 0x11
    B1BlockType    = 0x12
    B2BlockType    = 0x13
)

type PHTMessage struct {
    PHT *PHTTransaction `json:"pht"`
}

type MTMessage struct {
    MT *MTTransaction `json:"mt"`
}

type B1BlockMessage struct {
    Block *B1Block `json:"block"`
}

type B2BlockMessage struct {
    Block *B2Block `json:"block"`
}
```

### Gossip Protocol Modifications

```go
func (p *P2SProtocol) BroadcastPHT(pht *PHTTransaction) error {
    msg := &PHTMessage{PHT: pht}
    return p.broadcastMessage(PHTMessageType, msg)
}

func (p *P2SProtocol) BroadcastMT(mt *MTTransaction) error {
    msg := &MTMessage{MT: mt}
    return p.broadcastMessage(MTMessageType, msg)
}

func (p *P2SProtocol) BroadcastB1Block(block *B1Block) error {
    msg := &B1BlockMessage{Block: block}
    return p.broadcastMessage(B1BlockType, msg)
}

func (p *P2SProtocol) BroadcastB2Block(block *B2Block) error {
    msg := &B2BlockMessage{Block: block}
    return p.broadcastMessage(B2BlockType, msg)
}
```

## Performance Optimizations

### Batch Processing

```go
func (p *P2SConsensus) ProcessBatch(phts []*PHTTransaction) ([]*MTTransaction, error) {
    // Process PHTs in parallel
    var wg sync.WaitGroup
    mts := make([]*MTTransaction, len(phts))
    errors := make([]error, len(phts))
    
    for i, pht := range phts {
        wg.Add(1)
        go func(index int, pht *PHTTransaction) {
            defer wg.Done()
            mt, err := p.mtManager.CreateMT(pht)
            mts[index] = mt
            errors[index] = err
        }(i, pht)
    }
    
    wg.Wait()
    
    // Check for errors
    for _, err := range errors {
        if err != nil {
            return nil, err
        }
    }
    
    return mts, nil
}
```

### Caching Mechanisms

```go
type P2SCache struct {
    phtCache    map[common.Hash]*PHTTransaction
    mtCache     map[common.Hash]*MTTransaction
    commitmentCache map[string][]byte
}

func (c *P2SCache) GetPHT(hash common.Hash) (*PHTTransaction, bool) {
    pht, exists := c.phtCache[hash]
    return pht, exists
}

func (c *P2SCache) SetPHT(hash common.Hash, pht *PHTTransaction) {
    c.phtCache[hash] = pht
}
```

This consensus design provides a solid foundation for implementing the P2S protocol with proper MEV protection mechanisms while maintaining compatibility with Ethereum's existing consensus infrastructure.
