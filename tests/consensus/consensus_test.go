package p2s

import (
	"math/big"
	"testing"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
)

func TestConsensus(t *testing.T) {
	// Create P2S consensus engine
	config := DefaultConfig()
	consensus := NewConsensus(nil, config)
	
	// Test basic functionality
	if consensus == nil {
		t.Fatal("Failed to create P2S consensus engine")
	}
	
	// Test configuration
	if consensus.GetConfig() == nil {
		t.Fatal("Configuration is nil")
	}
	
	// Test MEV score
	if consensus.GetMEVScore(nil) != 0.0 {
		t.Fatal("MEV score should be 0.0 for nil block")
	}
	
	// Test detected attacks
	attacks := consensus.GetDetectedAttacks(nil)
	if len(attacks) != 0 {
		t.Fatal("Detected attacks should be empty for nil block")
	}
}

func TestPHTManager(t *testing.T) {
	// Create PHT manager
	config := DefaultP2SConfig()
	manager := NewPHTManager(config)
	
	// Test basic functionality
	if manager == nil {
		t.Fatal("Failed to create PHT manager")
	}
	
	// Create a test transaction
	tx := types.NewTransaction(0, common.Address{}, big.NewInt(1000), 21000, big.NewInt(1000000000), []byte("test data"))
	
	// Create PHT from transaction
	pht, err := manager.CreatePHT(tx)
	if err != nil {
		t.Fatalf("Failed to create PHT: %v", err)
	}
	
	// Validate PHT
	if err := manager.ValidatePHT(pht); err != nil {
		t.Fatalf("PHT validation failed: %v", err)
	}
	
	// Test MEV score calculation
	score := manager.GetMEVScore(pht)
	if score < 0 || score > 1 {
		t.Fatalf("Invalid MEV score: %f", score)
	}
	
	// Test MEV susceptibility
	susceptible := manager.IsMEVSusceptible(pht)
	if susceptible && score >= 0.7 {
		t.Fatal("MEV susceptibility check failed")
	}
}

func TestMTManager(t *testing.T) {
	// Create MT manager
	config := DefaultP2SConfig()
	manager := NewMTManager(config)
	
	// Test basic functionality
	if manager == nil {
		t.Fatal("Failed to create MT manager")
	}
	
	// Create a test PHT
	pht := &PHTTransaction{
		Sender:     common.Address{},
		GasPrice:   big.NewInt(1000000000),
		Commitment: []byte("test commitment"),
		Nonce:      []byte("test nonce"),
		Timestamp:  uint64(time.Now().Unix()),
		Recipient:  common.Address{},
		Value:      big.NewInt(1000),
		CallData:   []byte("test data"),
		TxType:     0,
		GasLimit:   21000,
		TxHash:     common.Hash{},
	}
	
	// Create MT from PHT
	mt, err := manager.CreateMT(pht)
	if err != nil {
		t.Fatalf("Failed to create MT: %v", err)
	}
	
	// Validate MT
	if err := manager.ValidateMT(mt); err != nil {
		t.Fatalf("MT validation failed: %v", err)
	}
	
	// Verify MT against PHT
	if err := manager.VerifyMT(mt, pht); err != nil {
		t.Fatalf("MT verification failed: %v", err)
	}
}

func TestValidatorManager(t *testing.T) {
	// Create validator manager
	config := DefaultP2SConfig()
	manager := NewValidatorManager(config)
	
	// Test basic functionality
	if manager == nil {
		t.Fatal("Failed to create validator manager")
	}
	
	// Test validator count
	if manager.GetValidatorCount() != 0 {
		t.Fatal("Initial validator count should be 0")
	}
	
	// Test active validator count
	if manager.GetActiveValidatorCount() != 0 {
		t.Fatal("Initial active validator count should be 0")
	}
	
	// Generate test validator address
	address := GenerateValidatorAddress()
	
	// Test validator address validation
	if !ValidateValidatorAddress(address) {
		t.Fatal("Generated validator address should be valid")
	}
	
	// Test adding validator
	err := manager.AddValidator(address, big.NewInt(1000000000000000000)) // 1 ETH
	if err != nil {
		t.Fatalf("Failed to add validator: %v", err)
	}
	
	// Test validator count
	if manager.GetValidatorCount() != 1 {
		t.Fatal("Validator count should be 1")
	}
	
	// Test active validator count
	if manager.GetActiveValidatorCount() != 1 {
		t.Fatal("Active validator count should be 1")
	}
	
	// Test validator retrieval
	validator := manager.GetValidator(address)
	if validator == nil {
		t.Fatal("Validator should exist")
	}
	
	// Test validator selection
	proposer, err := manager.SelectProposer(1)
	if err != nil {
		t.Fatalf("Failed to select proposer: %v", err)
	}
	
	if proposer != address {
		t.Fatal("Selected proposer should match added validator")
	}
	
	// Test reputation update
	manager.UpdateReputation(address, 10)
	updatedValidator := manager.GetValidator(address)
	if updatedValidator.Reputation != 110 { // 100 + 10
		t.Fatal("Reputation update failed")
	}
}

func TestMEVDetector(t *testing.T) {
	// Create MEV detector
	config := DefaultP2SConfig()
	detector := NewMEVDetector(config)
	
	// Test basic functionality
	if detector == nil {
		t.Fatal("Failed to create MEV detector")
	}
	
	// Test threshold
	threshold := detector.GetThreshold()
	if threshold != 0.7 {
		t.Fatal("Default threshold should be 0.7")
	}
	
	// Test attack patterns
	patterns := detector.GetAllAttackPatterns()
	if len(patterns) == 0 {
		t.Fatal("Attack patterns should be initialized")
	}
	
	// Test sandwich attack pattern
	sandwichPattern := detector.GetAttackPattern("sandwich_attack")
	if sandwichPattern == nil {
		t.Fatal("Sandwich attack pattern should exist")
	}
	
	if sandwichPattern.Name != "Sandwich Attack" {
		t.Fatal("Sandwich attack pattern name mismatch")
	}
	
	// Test MEV analysis
	pht := &PHTTransaction{
		Sender:     common.Address{},
		GasPrice:   big.NewInt(10000000000), // High gas price
		Commitment: []byte("test commitment"),
		Nonce:      []byte("test nonce"),
		Timestamp:  uint64(time.Now().Unix()),
		Recipient:  common.Address{},
		Value:      big.NewInt(1000000000000000000), // 1 ETH
		CallData:   []byte("test data"),
		TxType:     0,
		GasLimit:   21000,
		TxHash:     common.Hash{},
	}
	
	analysis := detector.AnalyzeMEVRisk(pht)
	if analysis == nil {
		t.Fatal("MEV analysis should not be nil")
	}
	
	if analysis.Score < 0 || analysis.Score > 1 {
		t.Fatalf("Invalid MEV score: %f", analysis.Score)
	}
	
	// Test MEV detection with multiple PHTs
	phts := []*PHTTransaction{pht}
	score, attacks := detector.DetectMEV(phts)
	
	if score < 0 || score > 1 {
		t.Fatalf("Invalid MEV score: %f", score)
	}
	
	// High gas price and large value should trigger attacks
	if len(attacks) == 0 {
		t.Fatal("MEV attacks should be detected")
	}
}

func TestP2SCache(t *testing.T) {
	// Create P2S cache
	cache := NewP2SCache()
	
	// Test basic functionality
	if cache == nil {
		t.Fatal("Failed to create P2S cache")
	}
	
	// Test cache stats
	stats := cache.GetCacheStats()
	if stats == nil {
		t.Fatal("Cache stats should not be nil")
	}
	
	// Test B1 block caching
	b1Block := &B1Block{
		Header:          &types.Header{},
		PHTs:            []*PHTTransaction{},
		BlockType:       1,
		MEVScore:        0.8,
		DetectedAttacks: []string{},
		ValidatorSig:    []byte{},
		Timestamp:       uint64(time.Now().Unix()),
		BlockHash:       common.Hash{},
	}
	
	hash := common.Hash{0x01}
	cache.SetB1Block(hash, b1Block)
	
	retrievedBlock, exists := cache.GetB1Block(hash)
	if !exists {
		t.Fatal("B1 block should exist in cache")
	}
	
	if retrievedBlock != b1Block {
		t.Fatal("Retrieved B1 block should match stored block")
	}
	
	// Test B2 block caching
	b2Block := &B2Block{
		Header:       &types.Header{},
		MTs:          []*MTTransaction{},
		BlockType:    2,
		B1BlockHash:  hash,
		ValidatorSig: []byte{},
		Timestamp:    uint64(time.Now().Unix()),
		BlockHash:    common.Hash{},
	}
	
	hash2 := common.Hash{0x02}
	cache.SetB2Block(hash2, b2Block)
	
	retrievedBlock2, exists := cache.GetB2Block(hash2)
	if !exists {
		t.Fatal("B2 block should exist in cache")
	}
	
	if retrievedBlock2 != b2Block {
		t.Fatal("Retrieved B2 block should match stored block")
	}
	
	// Test PHT caching
	pht := &PHTTransaction{
		Sender:     common.Address{},
		GasPrice:   big.NewInt(1000000000),
		Commitment: []byte("test commitment"),
		Nonce:      []byte("test nonce"),
		Timestamp:  uint64(time.Now().Unix()),
		Recipient:  common.Address{},
		Value:      big.NewInt(1000),
		CallData:   []byte("test data"),
		TxType:     0,
		GasLimit:   21000,
		TxHash:     common.Hash{},
	}
	
	hash3 := common.Hash{0x03}
	cache.SetPHT(hash3, pht)
	
	retrievedPHT, exists := cache.GetPHT(hash3)
	if !exists {
		t.Fatal("PHT should exist in cache")
	}
	
	if retrievedPHT != pht {
		t.Fatal("Retrieved PHT should match stored PHT")
	}
	
	// Test MT caching
	mt := &MTTransaction{
		Recipient:  common.Address{},
		Value:      big.NewInt(1000),
		CallData:   []byte("test data"),
		TxType:     0,
		GasLimit:   21000,
		PHTHash:    hash3,
		Proof:      []byte("test proof"),
		Timestamp:  uint64(time.Now().Unix()),
		TxHash:     common.Hash{},
	}
	
	hash4 := common.Hash{0x04}
	cache.SetMT(hash4, mt)
	
	retrievedMT, exists := cache.GetMT(hash4)
	if !exists {
		t.Fatal("MT should exist in cache")
	}
	
	if retrievedMT != mt {
		t.Fatal("Retrieved MT should match stored MT")
	}
	
	// Test commitment caching
	key := "test_key"
	commitment := []byte("test commitment")
	cache.SetCommitment(key, commitment)
	
	retrievedCommitment, exists := cache.GetCommitment(key)
	if !exists {
		t.Fatal("Commitment should exist in cache")
	}
	
	if string(retrievedCommitment) != string(commitment) {
		t.Fatal("Retrieved commitment should match stored commitment")
	}
	
	// Test cache clear
	cache.Clear()
	
	_, exists = cache.GetB1Block(hash)
	if exists {
		t.Fatal("B1 block should not exist after clear")
	}
	
	_, exists = cache.GetB2Block(hash2)
	if exists {
		t.Fatal("B2 block should not exist after clear")
	}
	
	_, exists = cache.GetPHT(hash3)
	if exists {
		t.Fatal("PHT should not exist after clear")
	}
	
	_, exists = cache.GetMT(hash4)
	if exists {
		t.Fatal("MT should not exist after clear")
	}
	
	_, exists = cache.GetCommitment(key)
	if exists {
		t.Fatal("Commitment should not exist after clear")
	}
}

func TestB1BlockValidation(t *testing.T) {
	// Create valid B1 block
	b1Block := &B1Block{
		Header:          &types.Header{},
		PHTs:            []*PHTTransaction{},
		BlockType:       1,
		MEVScore:        0.8,
		DetectedAttacks: []string{},
		ValidatorSig:    []byte{},
		Timestamp:       uint64(time.Now().Unix()),
		BlockHash:       common.Hash{},
	}
	
	// Test validation
	if err := b1Block.Validate(); err != nil {
		t.Fatalf("B1 block validation failed: %v", err)
	}
	
	// Test block type
	if !b1Block.IsB1Block() {
		t.Fatal("Block should be identified as B1 block")
	}
	
	// Test MEV score validation
	if !b1Block.IsValidMEVScore() {
		t.Fatal("MEV score should be valid")
	}
	
	// Test attack detection
	if b1Block.HasMEVAttacks() {
		t.Fatal("Block should not have MEV attacks")
	}
	
	// Test attack count
	if b1Block.GetAttackCount() != 0 {
		t.Fatal("Attack count should be 0")
	}
	
	// Test attack severity
	if b1Block.GetAttackSeverity() != "none" {
		t.Fatal("Attack severity should be 'none'")
	}
}

func TestB2BlockValidation(t *testing.T) {
	// Create valid B1 block
	b1Block := &B1Block{
		Header:          &types.Header{},
		PHTs:            []*PHTTransaction{},
		BlockType:       1,
		MEVScore:        0.8,
		DetectedAttacks: []string{},
		ValidatorSig:    []byte{},
		Timestamp:       uint64(time.Now().Unix()),
		BlockHash:       common.Hash{},
	}
	
	// Create valid B2 block
	b2Block := &B2Block{
		Header:       &types.Header{},
		MTs:          []*MTTransaction{},
		BlockType:    2,
		B1BlockHash:  b1Block.BlockHash,
		ValidatorSig: []byte{},
		Timestamp:    uint64(time.Now().Unix() + 1),
		BlockHash:    common.Hash{},
	}
	
	// Test validation
	if err := b2Block.Validate(b1Block); err != nil {
		t.Fatalf("B2 block validation failed: %v", err)
	}
	
	// Test block type
	if !b2Block.IsB2Block() {
		t.Fatal("Block should be identified as B2 block")
	}
	
	// Test B1 block hash
	if b2Block.GetB1BlockHash() != b1Block.BlockHash {
		t.Fatal("B1 block hash should match")
	}
}
