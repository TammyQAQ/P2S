package p2s

import (
	"errors"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
)

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

// P2SCache caches P2S-specific data
type P2SCache struct {
	b1Blocks    map[common.Hash]*B1Block
	b2Blocks    map[common.Hash]*B2Block
	phtCache    map[common.Hash]*PHTTransaction
	mtCache     map[common.Hash]*MTTransaction
	commitmentCache map[string][]byte
	maxSize     int
}

// NewP2SCache creates a new P2S cache
func NewP2SCache() *P2SCache {
	return &P2SCache{
		b1Blocks:        make(map[common.Hash]*B1Block),
		b2Blocks:        make(map[common.Hash]*B2Block),
		phtCache:        make(map[common.Hash]*PHTTransaction),
		mtCache:         make(map[common.Hash]*MTTransaction),
		commitmentCache: make(map[string][]byte),
		maxSize:         1000, // Maximum cache size
	}
}

// SetB1Block stores a B1 block in cache
func (c *P2SCache) SetB1Block(hash common.Hash, block *B1Block) {
	if len(c.b1Blocks) >= c.maxSize {
		c.evictOldestB1Block()
	}
	
	block.BlockHash = hash
	c.b1Blocks[hash] = block
}

// GetB1Block retrieves a B1 block from cache
func (c *P2SCache) GetB1Block(hash common.Hash) (*B1Block, bool) {
	block, exists := c.b1Blocks[hash]
	return block, exists
}

// SetB2Block stores a B2 block in cache
func (c *P2SCache) SetB2Block(hash common.Hash, block *B2Block) {
	if len(c.b2Blocks) >= c.maxSize {
		c.evictOldestB2Block()
	}
	
	block.BlockHash = hash
	c.b2Blocks[hash] = block
}

// GetB2Block retrieves a B2 block from cache
func (c *P2SCache) GetB2Block(hash common.Hash) (*B2Block, bool) {
	block, exists := c.b2Blocks[hash]
	return block, exists
}

// SetPHT stores a PHT in cache
func (c *P2SCache) SetPHT(hash common.Hash, pht *PHTTransaction) {
	if len(c.phtCache) >= c.maxSize {
		c.evictOldestPHT()
	}
	
	c.phtCache[hash] = pht
}

// GetPHT retrieves a PHT from cache
func (c *P2SCache) GetPHT(hash common.Hash) (*PHTTransaction, bool) {
	pht, exists := c.phtCache[hash]
	return pht, exists
}

// SetMT stores an MT in cache
func (c *P2SCache) SetMT(hash common.Hash, mt *MTTransaction) {
	if len(c.mtCache) >= c.maxSize {
		c.evictOldestMT()
	}
	
	c.mtCache[hash] = mt
}

// GetMT retrieves an MT from cache
func (c *P2SCache) GetMT(hash common.Hash) (*MTTransaction, bool) {
	mt, exists := c.mtCache[hash]
	return mt, exists
}

// SetCommitment stores a commitment in cache
func (c *P2SCache) SetCommitment(key string, commitment []byte) {
	if len(c.commitmentCache) >= c.maxSize {
		c.evictOldestCommitment()
	}
	
	c.commitmentCache[key] = commitment
}

// GetCommitment retrieves a commitment from cache
func (c *P2SCache) GetCommitment(key string) ([]byte, bool) {
	commitment, exists := c.commitmentCache[key]
	return commitment, exists
}

// evictOldestB1Block evicts the oldest B1 block from cache
func (c *P2SCache) evictOldestB1Block() {
	var oldestHash common.Hash
	var oldestTime uint64 = ^uint64(0) // Max uint64
	
	for hash, block := range c.b1Blocks {
		if block.Timestamp < oldestTime {
			oldestTime = block.Timestamp
			oldestHash = hash
		}
	}
	
	delete(c.b1Blocks, oldestHash)
}

// evictOldestB2Block evicts the oldest B2 block from cache
func (c *P2SCache) evictOldestB2Block() {
	var oldestHash common.Hash
	var oldestTime uint64 = ^uint64(0) // Max uint64
	
	for hash, block := range c.b2Blocks {
		if block.Timestamp < oldestTime {
			oldestTime = block.Timestamp
			oldestHash = hash
		}
	}
	
	delete(c.b2Blocks, oldestHash)
}

// evictOldestPHT evicts the oldest PHT from cache
func (c *P2SCache) evictOldestPHT() {
	var oldestHash common.Hash
	var oldestTime uint64 = ^uint64(0) // Max uint64
	
	for hash, pht := range c.phtCache {
		if pht.Timestamp < oldestTime {
			oldestTime = pht.Timestamp
			oldestHash = hash
		}
	}
	
	delete(c.phtCache, oldestHash)
}

// evictOldestMT evicts the oldest MT from cache
func (c *P2SCache) evictOldestMT() {
	var oldestHash common.Hash
	var oldestTime uint64 = ^uint64(0) // Max uint64
	
	for hash, mt := range c.mtCache {
		if mt.Timestamp < oldestTime {
			oldestTime = mt.Timestamp
			oldestHash = hash
		}
	}
	
	delete(c.mtCache, oldestHash)
}

// evictOldestCommitment evicts the oldest commitment from cache
func (c *P2SCache) evictOldestCommitment() {
	// Simple eviction - remove first key
	for key := range c.commitmentCache {
		delete(c.commitmentCache, key)
		break
	}
}

// Clear clears all caches
func (c *P2SCache) Clear() {
	c.b1Blocks = make(map[common.Hash]*B1Block)
	c.b2Blocks = make(map[common.Hash]*B2Block)
	c.phtCache = make(map[common.Hash]*PHTTransaction)
	c.mtCache = make(map[common.Hash]*MTTransaction)
	c.commitmentCache = make(map[string][]byte)
}

// GetCacheStats returns cache statistics
func (c *P2SCache) GetCacheStats() map[string]interface{} {
	stats := make(map[string]interface{})
	
	stats["b1_blocks"] = len(c.b1Blocks)
	stats["b2_blocks"] = len(c.b2Blocks)
	stats["phts"] = len(c.phtCache)
	stats["mts"] = len(c.mtCache)
	stats["commitments"] = len(c.commitmentCache)
	stats["max_size"] = c.maxSize
	
	return stats
}

// Validate validates a B1 block
func (b *B1Block) Validate() error {
	// Validate header
	if b.Header == nil {
		return errors.New("missing header")
	}
	
	// Validate block type
	if b.BlockType != 1 {
		return errors.New("invalid block type for B1 block")
	}
	
	// Validate PHTs
	if len(b.PHTs) == 0 {
		return errors.New("no PHTs in B1 block")
	}
	
	for i, pht := range b.PHTs {
		if pht == nil {
			return errors.New("nil PHT at index " + string(rune(i)))
		}
		
		// Validate PHT hash
		if pht.Hash() == (common.Hash{}) {
			return errors.New("invalid PHT hash at index " + string(rune(i)))
		}
	}
	
	// Validate MEV score
	if b.MEVScore < 0 || b.MEVScore > 1 {
		return errors.New("invalid MEV score")
	}
	
	// Validate timestamp
	if b.Timestamp == 0 {
		return errors.New("missing timestamp")
	}
	
	// Validate timestamp is not in the future
	if b.Timestamp > uint64(time.Now().Unix()+60) { // Allow 1 minute tolerance
		return errors.New("timestamp in the future")
	}
	
	return nil
}

// Validate validates a B2 block against its corresponding B1 block
func (b *B2Block) Validate(b1Block *B1Block) error {
	// Validate header
	if b.Header == nil {
		return errors.New("missing header")
	}
	
	// Validate block type
	if b.BlockType != 2 {
		return errors.New("invalid block type for B2 block")
	}
	
	// Validate B1 block reference
	if b.B1BlockHash != b1Block.BlockHash {
		return errors.New("B1 block hash mismatch")
	}
	
	// Validate MTs
	if len(b.MTs) == 0 {
		return errors.New("no MTs in B2 block")
	}
	
	// Validate MT count matches PHT count
	if len(b.MTs) != len(b1Block.PHTs) {
		return errors.New("MT count mismatch with B1 PHTs")
	}
	
	// Validate each MT against corresponding PHT
	for i, mt := range b.MTs {
		if mt == nil {
			return errors.New("nil MT at index " + string(rune(i)))
		}
		
		pht := b1Block.PHTs[i]
		if pht == nil {
			return errors.New("nil PHT at index " + string(rune(i)))
		}
		
		// Validate MT hash
		if mt.Hash() == (common.Hash{}) {
			return errors.New("invalid MT hash at index " + string(rune(i)))
		}
		
		// Validate PHT hash reference
		if mt.PHTHash != pht.Hash() {
			return errors.New("PHT hash mismatch at index " + string(rune(i)))
		}
	}
	
	// Validate timestamp
	if b.Timestamp == 0 {
		return errors.New("missing timestamp")
	}
	
	// Validate timestamp is not in the future
	if b.Timestamp > uint64(time.Now().Unix()+60) { // Allow 1 minute tolerance
		return errors.New("timestamp in the future")
	}
	
	// Validate timestamp is after B1 block
	if b.Timestamp <= b1Block.Timestamp {
		return errors.New("B2 timestamp must be after B1 timestamp")
	}
	
	return nil
}

// GetBlockType returns the block type
func (b *B1Block) GetBlockType() uint8 {
	return b.BlockType
}

// GetBlockType returns the block type
func (b *B2Block) GetBlockType() uint8 {
	return b.BlockType
}

// GetTransactionCount returns the number of transactions in the block
func (b *B1Block) GetTransactionCount() int {
	return len(b.PHTs)
}

// GetTransactionCount returns the number of transactions in the block
func (b *B2Block) GetTransactionCount() int {
	return len(b.MTs)
}

// GetMEVScore returns the MEV protection score
func (b *B1Block) GetMEVScore() float64 {
	return b.MEVScore
}

// GetDetectedAttacks returns the detected MEV attacks
func (b *B1Block) GetDetectedAttacks() []string {
	return b.DetectedAttacks
}

// GetB1BlockHash returns the B1 block hash
func (b *B2Block) GetB1BlockHash() common.Hash {
	return b.B1BlockHash
}

// GetTimestamp returns the block timestamp
func (b *B1Block) GetTimestamp() uint64 {
	return b.Timestamp
}

// GetTimestamp returns the block timestamp
func (b *B2Block) GetTimestamp() uint64 {
	return b.Timestamp
}

// GetBlockHash returns the block hash
func (b *B1Block) GetBlockHash() common.Hash {
	return b.BlockHash
}

// GetBlockHash returns the block hash
func (b *B2Block) GetBlockHash() common.Hash {
	return b.BlockHash
}

// SetBlockHash sets the block hash
func (b *B1Block) SetBlockHash(hash common.Hash) {
	b.BlockHash = hash
}

// SetBlockHash sets the block hash
func (b *B2Block) SetBlockHash(hash common.Hash) {
	b.BlockHash = hash
}

// IsValidMEVScore checks if the MEV score is valid
func (b *B1Block) IsValidMEVScore() bool {
	return b.MEVScore >= 0 && b.MEVScore <= 1
}

// HasMEVAttacks checks if the block has detected MEV attacks
func (b *B1Block) HasMEVAttacks() bool {
	return len(b.DetectedAttacks) > 0
}

// GetAttackCount returns the number of detected attacks
func (b *B1Block) GetAttackCount() int {
	return len(b.DetectedAttacks)
}

// GetAttackSeverity returns the severity of the most severe attack
func (b *B1Block) GetAttackSeverity() string {
	if len(b.DetectedAttacks) == 0 {
		return "none"
	}
	
	// This would need to be implemented based on attack severity mapping
	// For now, return "medium" if any attacks are detected
	return "medium"
}
