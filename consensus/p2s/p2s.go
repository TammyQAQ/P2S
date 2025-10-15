package p2s

import (
	"errors"
	"math/big"
	"sync"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/consensus"
	"github.com/ethereum/go-ethereum/core/state"
	"github.com/ethereum/go-ethereum/core/types"
)

// P2SConsensus implements the P2S (Proposer in 2 Steps) consensus mechanism
type P2SConsensus struct {
	// Ethereum consensus engine
	ethConsensus consensus.Engine
	
	// P2S-specific components
	phtManager   *PHTManager
	mtManager    *MTManager
	validatorMgr *ValidatorManager
	mevDetector  *MEVDetector
	
	// Configuration
	config *P2SConfig
	
	// Caching
	cache *P2SCache
	
	// Thread safety
	mu sync.RWMutex
}

// P2SConfig contains P2S-specific configuration
type P2SConfig struct {
	// Block time configuration
	B1BlockTime time.Duration
	B2BlockTime time.Duration
	
	// MEV protection thresholds
	MinMEVScore float64
	MaxMEVScore float64
	
	// Validator configuration
	MinStake      *big.Int
	MaxValidators int
	
	// Cryptographic parameters
	CommitmentScheme string
	ProofSystem      string
}

// DefaultP2SConfig returns default P2S configuration
func DefaultP2SConfig() *P2SConfig {
	return &P2SConfig{
		B1BlockTime:      6 * time.Second,  // 6 seconds for B1 block
		B2BlockTime:      6 * time.Second,  // 6 seconds for B2 block
		MinMEVScore:      0.7,
		MaxMEVScore:      1.0,
		MinStake:         big.NewInt(1000000000000000000), // 1 ETH
		MaxValidators:    100,
		CommitmentScheme: "pedersen",
		ProofSystem:      "merkle",
	}
}

// NewP2SConsensus creates a new P2S consensus engine
func NewP2SConsensus(ethConsensus consensus.Engine, config *P2SConfig) *P2SConsensus {
	if config == nil {
		config = DefaultP2SConfig()
	}
	
	return &P2SConsensus{
		ethConsensus: ethConsensus,
		phtManager:   NewPHTManager(config),
		mtManager:    NewMTManager(config),
		validatorMgr: NewValidatorManager(config),
		mevDetector:  NewMEVDetector(config),
		config:       config,
		cache:       NewP2SCache(),
	}
}

// Prepare implements consensus.Engine.Prepare for B1 block preparation
func (p *P2SConsensus) Prepare(chain consensus.ChainReader, header *types.Header) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	// Set block type to B1
	header.Extra = append(header.Extra, byte(1)) // B1 block type
	
	// Prepare B1 block with PHTs
	return p.prepareB1Block(chain, header)
}

// Finalize implements consensus.Engine.Finalize for B2 block finalization
func (p *P2SConsensus) Finalize(chain consensus.ChainReader, header *types.Header, state *state.StateDB, txs []*types.Transaction, receipts []*types.Receipt) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	// Set block type to B2
	header.Extra = append(header.Extra, byte(2)) // B2 block type
	
	// Finalize B2 block with MTs
	return p.finalizeB2Block(chain, header, state, txs, receipts)
}

// prepareB1Block prepares a B1 block containing PHTs
func (p *P2SConsensus) prepareB1Block(chain consensus.ChainReader, header *types.Header) error {
	// Get pending transactions from mempool
	pendingTxs := p.getPendingTransactions()
	
	// Convert transactions to PHTs
	phts, err := p.convertToPHTs(pendingTxs)
	if err != nil {
		return err
	}
	
	// Detect MEV attacks
	mevScore, attacks := p.mevDetector.DetectMEV(phts)
	
	// Check MEV protection threshold
	if mevScore < p.config.MinMEVScore {
		return errors.New("insufficient MEV protection")
	}
	
	// Create B1 block
	b1Block := &B1Block{
		Header:       header,
		PHTs:         phts,
		BlockType:    1,
		MEVScore:     mevScore,
		DetectedAttacks: attacks,
		Timestamp:    uint64(time.Now().Unix()),
	}
	
	// Validate B1 block
	if err := b1Block.Validate(); err != nil {
		return err
	}
	
	// Cache B1 block
	p.cache.SetB1Block(header.Hash(), b1Block)
	
	return nil
}

// finalizeB2Block finalizes a B2 block containing MTs
func (p *P2SConsensus) finalizeB2Block(chain consensus.ChainReader, header *types.Header, state *state.StateDB, txs []*types.Transaction, receipts []*types.Receipt) error {
	// Get corresponding B1 block
	b1Block, exists := p.cache.GetB1Block(header.ParentHash)
	if !exists {
		return errors.New("B1 block not found")
	}
	
	// Convert PHTs to MTs
	mts, err := p.convertPHTsToMTs(b1Block.PHTs)
	if err != nil {
		return err
	}
	
	// Create B2 block
	b2Block := &B2Block{
		Header:       header,
		MTs:          mts,
		BlockType:    2,
		B1BlockHash:  b1Block.Header.Hash(),
		Timestamp:    uint64(time.Now().Unix()),
	}
	
	// Validate B2 block against B1 block
	if err := b2Block.Validate(b1Block); err != nil {
		return err
	}
	
	// Cache B2 block
	p.cache.SetB2Block(header.Hash(), b2Block)
	
	return nil
}

// convertToPHTs converts regular transactions to PHTs
func (p *P2SConsensus) convertToPHTs(txs []*types.Transaction) ([]*PHTTransaction, error) {
	phts := make([]*PHTTransaction, 0, len(txs))
	
	for _, tx := range txs {
		pht, err := p.phtManager.CreatePHT(tx)
		if err != nil {
			return nil, err
		}
		phts = append(phts, pht)
	}
	
	return phts, nil
}

// convertPHTsToMTs converts PHTs to MTs
func (p *P2SConsensus) convertPHTsToMTs(phts []*PHTTransaction) ([]*MTTransaction, error) {
	mts := make([]*MTTransaction, 0, len(phts))
	
	for _, pht := range phts {
		mt, err := p.mtManager.CreateMT(pht)
		if err != nil {
			return nil, err
		}
		mts = append(mts, mt)
	}
	
	return mts, nil
}

// getPendingTransactions retrieves pending transactions from mempool
func (p *P2SConsensus) getPendingTransactions() []*types.Transaction {
	// This would typically interface with the mempool
	// For now, return empty slice
	return []*types.Transaction{}
}

// ValidateBlock validates a P2S block
func (p *P2SConsensus) ValidateBlock(chain consensus.ChainReader, block *types.Block) error {
	p.mu.RLock()
	defer p.mu.RUnlock()
	
	// Check block type
	blockType := p.getBlockType(block.Header())
	
	switch blockType {
	case 1: // B1 block
		return p.validateB1Block(chain, block)
	case 2: // B2 block
		return p.validateB2Block(chain, block)
	default:
		return errors.New("invalid block type")
	}
}

// validateB1Block validates a B1 block
func (p *P2SConsensus) validateB1Block(chain consensus.ChainReader, block *types.Block) error {
	// Get B1 block from cache
	b1Block, exists := p.cache.GetB1Block(block.Hash())
	if !exists {
		return errors.New("B1 block not found in cache")
	}
	
	// Validate PHTs
	for _, pht := range b1Block.PHTs {
		if err := p.phtManager.ValidatePHT(pht); err != nil {
			return err
		}
	}
	
	// Validate MEV score
	if b1Block.MEVScore < p.config.MinMEVScore {
		return errors.New("insufficient MEV protection")
	}
	
	return nil
}

// validateB2Block validates a B2 block
func (p *P2SConsensus) validateB2Block(chain consensus.ChainReader, block *types.Block) error {
	// Get B2 block from cache
	b2Block, exists := p.cache.GetB2Block(block.Hash())
	if !exists {
		return errors.New("B2 block not found in cache")
	}
	
	// Get corresponding B1 block
	b1Block, exists := p.cache.GetB1Block(b2Block.B1BlockHash)
	if !exists {
		return errors.New("corresponding B1 block not found")
	}
	
	// Validate MTs against PHTs
	for i, mt := range b2Block.MTs {
		if i >= len(b1Block.PHTs) {
			return errors.New("MT count exceeds PHT count")
		}
		
		pht := b1Block.PHTs[i]
		if err := p.mtManager.VerifyMT(mt, pht); err != nil {
			return err
		}
	}
	
	return nil
}

// getBlockType extracts block type from header
func (p *P2SConsensus) getBlockType(header *types.Header) uint8 {
	if len(header.Extra) > 0 {
		return header.Extra[len(header.Extra)-1]
	}
	return 0
}

// GetMEVScore returns the MEV protection score for a block
func (p *P2SConsensus) GetMEVScore(block *types.Block) float64 {
	p.mu.RLock()
	defer p.mu.RUnlock()
	
	blockType := p.getBlockType(block.Header())
	
	switch blockType {
	case 1: // B1 block
		if b1Block, exists := p.cache.GetB1Block(block.Hash()); exists {
			return b1Block.MEVScore
		}
	case 2: // B2 block
		if b2Block, exists := p.cache.GetB2Block(block.Hash()); exists {
			if b1Block, exists := p.cache.GetB1Block(b2Block.B1BlockHash); exists {
				return b1Block.MEVScore
			}
		}
	}
	
	return 0.0
}

// GetDetectedAttacks returns detected MEV attacks for a block
func (p *P2SConsensus) GetDetectedAttacks(block *types.Block) []string {
	p.mu.RLock()
	defer p.mu.RUnlock()
	
	blockType := p.getBlockType(block.Header())
	
	switch blockType {
	case 1: // B1 block
		if b1Block, exists := p.cache.GetB1Block(block.Hash()); exists {
			return b1Block.DetectedAttacks
		}
	case 2: // B2 block
		if b2Block, exists := p.cache.GetB2Block(block.Hash()); exists {
			if b1Block, exists := p.cache.GetB1Block(b2Block.B1BlockHash); exists {
				return b1Block.DetectedAttacks
			}
		}
	}
	
	return []string{}
}

// UpdateValidatorReputation updates validator reputation based on performance
func (p *P2SConsensus) UpdateValidatorReputation(validator common.Address, score int64) {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	p.validatorMgr.UpdateReputation(validator, score)
}

// GetValidatorInfo returns validator information
func (p *P2SConsensus) GetValidatorInfo(validator common.Address) *Validator {
	p.mu.RLock()
	defer p.mu.RUnlock()
	
	return p.validatorMgr.GetValidator(validator)
}

// GetConfig returns P2S configuration
func (p *P2SConsensus) GetConfig() *P2SConfig {
	return p.config
}

// SetConfig updates P2S configuration
func (p *P2SConsensus) SetConfig(config *P2SConfig) {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	p.config = config
}
