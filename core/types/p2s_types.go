package types

import (
	"math/big"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
)

// P2STransaction represents a P2S transaction that can be either PHT or MT
type P2STransaction interface {
	GetSender() common.Address
	GetGasPrice() *big.Int
	GetHash() common.Hash
	GetType() uint8
	IsPHT() bool
	IsMT() bool
}

// PHTTransaction represents a Partially Hidden Transaction
type PHTTransaction struct {
	// Visible fields (included in B1 block)
	Sender     common.Address `json:"sender"`
	GasPrice   *big.Int      `json:"gasPrice"`
	Commitment []byte        `json:"commitment"`
	Nonce      []byte        `json:"nonce"`
	Timestamp  uint64        `json:"timestamp"`
	
	// Hidden fields (committed but not revealed until B2)
	Recipient common.Address `json:"recipient"`
	Value     *big.Int      `json:"value"`
	CallData  []byte        `json:"callData"`
	TxType    uint8         `json:"txType"`
	GasLimit  uint64        `json:"gasLimit"`
	
	// Transaction hash
	TxHash common.Hash `json:"txHash"`
}

// MTTransaction represents a Matching Transaction
type MTTransaction struct {
	// Revealed fields (included in B2 block)
	Recipient common.Address `json:"recipient"`
	Value     *big.Int      `json:"value"`
	CallData  []byte        `json:"callData"`
	TxType    uint8         `json:"txType"`
	GasLimit  uint64        `json:"gasLimit"`
	
	// Proof fields
	PHTHash   common.Hash `json:"phtHash"`
	Proof     []byte      `json:"proof"`
	Timestamp uint64      `json:"timestamp"`
	
	// Transaction hash
	TxHash common.Hash `json:"txHash"`
}

// P2SBlock represents a P2S block that can be either B1 or B2
type P2SBlock interface {
	GetBlockType() uint8
	GetHeader() *types.Header
	GetTransactionCount() int
	GetTimestamp() uint64
	GetBlockHash() common.Hash
	IsB1Block() bool
	IsB2Block() bool
}

// B1Block represents a B1 block containing PHTs
type B1Block struct {
	Header          *types.Header      `json:"header"`
	PHTs            []*PHTTransaction  `json:"phts"`
	BlockType       uint8              `json:"blockType"`       // 1 for B1
	MEVScore        float64            `json:"mevScore"`        // MEV protection score
	DetectedAttacks []string           `json:"detectedAttacks"` // Detected MEV attacks
	ValidatorSig    []byte             `json:"validatorSig"`    // Validator signature
	Timestamp       uint64             `json:"timestamp"`
	BlockHash       common.Hash        `json:"blockHash"`
}

// B2Block represents a B2 block containing MTs
type B2Block struct {
	Header          *types.Header      `json:"header"`
	MTs             []*MTTransaction   `json:"mts"`
	BlockType       uint8              `json:"blockType"`       // 2 for B2
	B1BlockHash     common.Hash        `json:"b1BlockHash"`     // Reference to B1 block
	ValidatorSig    []byte             `json:"validatorSig"`    // Validator signature
	Timestamp       uint64             `json:"timestamp"`
	BlockHash       common.Hash        `json:"blockHash"`
}

// P2SBlockHeader extends Ethereum's block header with P2S-specific fields
type P2SBlockHeader struct {
	*types.Header
	BlockType    uint8   `json:"blockType"`    // 1 for B1, 2 for B2
	MEVScore     float64 `json:"mevScore"`     // MEV protection score
	B1BlockHash  common.Hash `json:"b1BlockHash"` // Reference to B1 block (for B2 blocks)
	ValidatorSig []byte  `json:"validatorSig"` // Validator signature
}

// P2SConfig contains P2S-specific configuration
type P2SConfig struct {
	// Block time configuration
	B1BlockTime int64 // B1 block time in seconds
	B2BlockTime int64 // B2 block time in seconds
	
	// MEV protection thresholds
	MinMEVScore float64
	MaxMEVScore float64
	
	// Validator configuration
	MinStake      *big.Int
	MaxValidators int
	
	// Cryptographic parameters
	CommitmentScheme string
	ProofSystem      string
	
	// Network parameters
	MaxBlockSize     int
	MaxTransactions  int
	MaxPHTsPerBlock  int
	MaxMTsPerBlock   int
}

// DefaultP2SConfig returns default P2S configuration
func DefaultP2SConfig() *P2SConfig {
	return &P2SConfig{
		B1BlockTime:       6,  // 6 seconds for B1 block
		B2BlockTime:       6,  // 6 seconds for B2 block
		MinMEVScore:       0.7,
		MaxMEVScore:       1.0,
		MinStake:          big.NewInt(1000000000000000000), // 1 ETH
		MaxValidators:     100,
		CommitmentScheme:  "pedersen",
		ProofSystem:       "merkle",
		MaxBlockSize:      1024 * 1024, // 1MB
		MaxTransactions:   1000,
		MaxPHTsPerBlock:   100,
		MaxMTsPerBlock:    100,
	}
}

// P2STransactionPool represents a pool of P2S transactions
type P2STransactionPool struct {
	phts map[common.Hash]*PHTTransaction
	mts  map[common.Hash]*MTTransaction
}

// NewP2STransactionPool creates a new P2S transaction pool
func NewP2STransactionPool() *P2STransactionPool {
	return &P2STransactionPool{
		phts: make(map[common.Hash]*PHTTransaction),
		mts:  make(map[common.Hash]*MTTransaction),
	}
}

// AddPHT adds a PHT to the pool
func (p *P2STransactionPool) AddPHT(pht *PHTTransaction) {
	p.phts[pht.TxHash] = pht
}

// AddMT adds an MT to the pool
func (p *P2STransactionPool) AddMT(mt *MTTransaction) {
	p.mts[mt.TxHash] = mt
}

// GetPHT retrieves a PHT from the pool
func (p *P2STransactionPool) GetPHT(hash common.Hash) (*PHTTransaction, bool) {
	pht, exists := p.phts[hash]
	return pht, exists
}

// GetMT retrieves an MT from the pool
func (p *P2STransactionPool) GetMT(hash common.Hash) (*MTTransaction, bool) {
	mt, exists := p.mts[hash]
	return mt, exists
}

// RemovePHT removes a PHT from the pool
func (p *P2STransactionPool) RemovePHT(hash common.Hash) {
	delete(p.phts, hash)
}

// RemoveMT removes an MT from the pool
func (p *P2STransactionPool) RemoveMT(hash common.Hash) {
	delete(p.mts, hash)
}

// GetPHTCount returns the number of PHTs in the pool
func (p *P2STransactionPool) GetPHTCount() int {
	return len(p.phts)
}

// GetMTCount returns the number of MTs in the pool
func (p *P2STransactionPool) GetMTCount() int {
	return len(p.mts)
}

// GetAllPHTs returns all PHTs in the pool
func (p *P2STransactionPool) GetAllPHTs() []*PHTTransaction {
	phts := make([]*PHTTransaction, 0, len(p.phts))
	for _, pht := range p.phts {
		phts = append(phts, pht)
	}
	return phts
}

// GetAllMTs returns all MTs in the pool
func (p *P2STransactionPool) GetAllMTs() []*MTTransaction {
	mts := make([]*MTTransaction, 0, len(p.mts))
	for _, mt := range p.mts {
		mts = append(mts, mt)
	}
	return mts
}

// Clear clears the transaction pool
func (p *P2STransactionPool) Clear() {
	p.phts = make(map[common.Hash]*PHTTransaction)
	p.mts = make(map[common.Hash]*MTTransaction)
}

// P2SBlockChain represents a blockchain with P2S blocks
type P2SBlockChain struct {
	b1Blocks map[common.Hash]*B1Block
	b2Blocks map[common.Hash]*B2Block
}

// NewP2SBlockChain creates a new P2S blockchain
func NewP2SBlockChain() *P2SBlockChain {
	return &P2SBlockChain{
		b1Blocks: make(map[common.Hash]*B1Block),
		b2Blocks: make(map[common.Hash]*B2Block),
	}
}

// AddB1Block adds a B1 block to the blockchain
func (bc *P2SBlockChain) AddB1Block(block *B1Block) {
	bc.b1Blocks[block.BlockHash] = block
}

// AddB2Block adds a B2 block to the blockchain
func (bc *P2SBlockChain) AddB2Block(block *B2Block) {
	bc.b2Blocks[block.BlockHash] = block
}

// GetB1Block retrieves a B1 block from the blockchain
func (bc *P2SBlockChain) GetB1Block(hash common.Hash) (*B1Block, bool) {
	block, exists := bc.b1Blocks[hash]
	return block, exists
}

// GetB2Block retrieves a B2 block from the blockchain
func (bc *P2SBlockChain) GetB2Block(hash common.Hash) (*B2Block, bool) {
	block, exists := bc.b2Blocks[hash]
	return block, exists
}

// GetB1BlockCount returns the number of B1 blocks
func (bc *P2SBlockChain) GetB1BlockCount() int {
	return len(bc.b1Blocks)
}

// GetB2BlockCount returns the number of B2 blocks
func (bc *P2SBlockChain) GetB2BlockCount() int {
	return len(bc.b2Blocks)
}

// GetAllB1Blocks returns all B1 blocks
func (bc *P2SBlockChain) GetAllB1Blocks() []*B1Block {
	blocks := make([]*B1Block, 0, len(bc.b1Blocks))
	for _, block := range bc.b1Blocks {
		blocks = append(blocks, block)
	}
	return blocks
}

// GetAllB2Blocks returns all B2 blocks
func (bc *P2SBlockChain) GetAllB2Blocks() []*B2Block {
	blocks := make([]*B2Block, 0, len(bc.b2Blocks))
	for _, block := range bc.b2Blocks {
		blocks = append(blocks, block)
	}
	return blocks
}

// Clear clears the blockchain
func (bc *P2SBlockChain) Clear() {
	bc.b1Blocks = make(map[common.Hash]*B1Block)
	bc.b2Blocks = make(map[common.Hash]*B2Block)
}

// P2SValidator represents a validator in the P2S network
type P2SValidator struct {
	Address    common.Address `json:"address"`
	Stake      *big.Int      `json:"stake"`
	Reputation int64         `json:"reputation"`
	IsActive   bool          `json:"isActive"`
	LastBlock  uint64        `json:"lastBlock"`
	CreatedAt  uint64        `json:"createdAt"`
	UpdatedAt  uint64        `json:"updatedAt"`
}

// P2SValidatorSet represents a set of validators
type P2SValidatorSet struct {
	validators map[common.Address]*P2SValidator
}

// NewP2SValidatorSet creates a new validator set
func NewP2SValidatorSet() *P2SValidatorSet {
	return &P2SValidatorSet{
		validators: make(map[common.Address]*P2SValidator),
	}
}

// AddValidator adds a validator to the set
func (vs *P2SValidatorSet) AddValidator(validator *P2SValidator) {
	vs.validators[validator.Address] = validator
}

// RemoveValidator removes a validator from the set
func (vs *P2SValidatorSet) RemoveValidator(address common.Address) {
	delete(vs.validators, address)
}

// GetValidator retrieves a validator from the set
func (vs *P2SValidatorSet) GetValidator(address common.Address) (*P2SValidator, bool) {
	validator, exists := vs.validators[address]
	return validator, exists
}

// GetValidatorCount returns the number of validators
func (vs *P2SValidatorSet) GetValidatorCount() int {
	return len(vs.validators)
}

// GetActiveValidatorCount returns the number of active validators
func (vs *P2SValidatorSet) GetActiveValidatorCount() int {
	count := 0
	for _, validator := range vs.validators {
		if validator.IsActive {
			count++
		}
	}
	return count
}

// GetAllValidators returns all validators
func (vs *P2SValidatorSet) GetAllValidators() []*P2SValidator {
	validators := make([]*P2SValidator, 0, len(vs.validators))
	for _, validator := range vs.validators {
		validators = append(validators, validator)
	}
	return validators
}

// GetActiveValidators returns only active validators
func (vs *P2SValidatorSet) GetActiveValidators() []*P2SValidator {
	validators := make([]*P2SValidator, 0)
	for _, validator := range vs.validators {
		if validator.IsActive {
			validators = append(validators, validator)
		}
	}
	return validators
}

// Clear clears the validator set
func (vs *P2SValidatorSet) Clear() {
	vs.validators = make(map[common.Address]*P2SValidator)
}
