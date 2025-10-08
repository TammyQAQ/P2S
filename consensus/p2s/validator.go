package p2s

import (
	"errors"
	"math/big"
	"math/rand"
	"sort"
	"sync"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
)

// ValidatorManager manages validators and their selection
type ValidatorManager struct {
	validators map[common.Address]*Validator
	selection  ValidatorSelection
	config     *P2SConfig
	mu         sync.RWMutex
}

// Validator represents a validator in the P2S network
type Validator struct {
	Address    common.Address `json:"address"`
	Stake      *big.Int      `json:"stake"`
	Reputation int64         `json:"reputation"`
	IsActive   bool          `json:"isActive"`
	LastBlock  uint64        `json:"lastBlock"`
	CreatedAt  uint64        `json:"createdAt"`
	UpdatedAt  uint64        `json:"updatedAt"`
}

// ValidatorSelection interface for validator selection algorithms
type ValidatorSelection interface {
	SelectProposer(validators map[common.Address]*Validator, blockNumber uint64) (common.Address, error)
	SelectValidators(validators map[common.Address]*Validator, count int) []common.Address
}

// WeightedRandomSelection implements weighted random selection
type WeightedRandomSelection struct {
	randomSource func() float64
}

// NewWeightedRandomSelection creates a new weighted random selection
func NewWeightedRandomSelection() *WeightedRandomSelection {
	return &WeightedRandomSelection{
		randomSource: rand.Float64,
	}
}

// SelectProposer selects a proposer using weighted random selection
func (w *WeightedRandomSelection) SelectProposer(validators map[common.Address]*Validator, blockNumber uint64) (common.Address, error) {
	if len(validators) == 0 {
		return common.Address{}, errors.New("no validators available")
	}
	
	// Calculate total weight
	totalWeight := big.NewInt(0)
	for _, validator := range validators {
		if validator.IsActive {
			// Weight = stake * reputation factor
			reputationFactor := big.NewInt(validator.Reputation + 100) // +100 to avoid negative
			weight := new(big.Int).Mul(validator.Stake, reputationFactor)
			totalWeight.Add(totalWeight, weight)
		}
	}
	
	if totalWeight.Cmp(big.NewInt(0)) == 0 {
		return common.Address{}, errors.New("no active validators")
	}
	
	// Select random proposer
	randomWeight := new(big.Int).Rand(rand.New(rand.NewSource(time.Now().UnixNano())), totalWeight)
	
	currentWeight := big.NewInt(0)
	for address, validator := range validators {
		if validator.IsActive {
			reputationFactor := big.NewInt(validator.Reputation + 100)
			weight := new(big.Int).Mul(validator.Stake, reputationFactor)
			currentWeight.Add(currentWeight, weight)
			
			if currentWeight.Cmp(randomWeight) >= 0 {
				return address, nil
			}
		}
	}
	
	// Fallback to first active validator
	for address, validator := range validators {
		if validator.IsActive {
			return address, nil
		}
	}
	
	return common.Address{}, errors.New("no active validators found")
}

// SelectValidators selects multiple validators
func (w *WeightedRandomSelection) SelectValidators(validators map[common.Address]*Validator, count int) []common.Address {
	if count <= 0 || len(validators) == 0 {
		return []common.Address{}
	}
	
	// Get active validators
	activeValidators := make([]common.Address, 0)
	for address, validator := range validators {
		if validator.IsActive {
			activeValidators = append(activeValidators, address)
		}
	}
	
	if len(activeValidators) == 0 {
		return []common.Address{}
	}
	
	// Limit count to available validators
	if count > len(activeValidators) {
		count = len(activeValidators)
	}
	
	// Select validators
	selected := make([]common.Address, 0, count)
	used := make(map[common.Address]bool)
	
	for len(selected) < count {
		// Select random validator
		randomIndex := rand.Intn(len(activeValidators))
		validator := activeValidators[randomIndex]
		
		if !used[validator] {
			selected = append(selected, validator)
			used[validator] = true
		}
	}
	
	return selected
}

// NewValidatorManager creates a new validator manager
func NewValidatorManager(config *P2SConfig) *ValidatorManager {
	return &ValidatorManager{
		validators: make(map[common.Address]*Validator),
		selection:  NewWeightedRandomSelection(),
		config:     config,
	}
}

// AddValidator adds a new validator
func (v *ValidatorManager) AddValidator(address common.Address, stake *big.Int) error {
	v.mu.Lock()
	defer v.mu.Unlock()
	
	if stake.Cmp(v.config.MinStake) < 0 {
		return errors.New("stake below minimum")
	}
	
	if len(v.validators) >= v.config.MaxValidators {
		return errors.New("maximum validators reached")
	}
	
	validator := &Validator{
		Address:    address,
		Stake:      new(big.Int).Set(stake),
		Reputation: 100, // Start with neutral reputation
		IsActive:   true,
		LastBlock:  0,
		CreatedAt:  uint64(time.Now().Unix()),
		UpdatedAt:  uint64(time.Now().Unix()),
	}
	
	v.validators[address] = validator
	return nil
}

// RemoveValidator removes a validator
func (v *ValidatorManager) RemoveValidator(address common.Address) error {
	v.mu.Lock()
	defer v.mu.Unlock()
	
	if _, exists := v.validators[address]; !exists {
		return errors.New("validator not found")
	}
	
	delete(v.validators, address)
	return nil
}

// UpdateStake updates a validator's stake
func (v *ValidatorManager) UpdateStake(address common.Address, stake *big.Int) error {
	v.mu.Lock()
	defer v.mu.Unlock()
	
	validator, exists := v.validators[address]
	if !exists {
		return errors.New("validator not found")
	}
	
	if stake.Cmp(v.config.MinStake) < 0 {
		validator.IsActive = false
	} else {
		validator.IsActive = true
	}
	
	validator.Stake = new(big.Int).Set(stake)
	validator.UpdatedAt = uint64(time.Now().Unix())
	
	return nil
}

// UpdateReputation updates a validator's reputation
func (v *ValidatorManager) UpdateReputation(address common.Address, score int64) {
	v.mu.Lock()
	defer v.mu.Unlock()
	
	if validator, exists := v.validators[address]; exists {
		validator.Reputation += score
		
		// Cap reputation to prevent gaming
		if validator.Reputation > 1000 {
			validator.Reputation = 1000
		}
		if validator.Reputation < -1000 {
			validator.Reputation = -1000
		}
		
		validator.UpdatedAt = uint64(time.Now().Unix())
	}
}

// SelectProposer selects a proposer for the given block number
func (v *ValidatorManager) SelectProposer(blockNumber uint64) (common.Address, error) {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	return v.selection.SelectProposer(v.validators, blockNumber)
}

// SelectValidators selects multiple validators
func (v *ValidatorManager) SelectValidators(count int) []common.Address {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	return v.selection.SelectValidators(v.validators, count)
}

// GetValidator returns a validator by address
func (v *ValidatorManager) GetValidator(address common.Address) *Validator {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	if validator, exists := v.validators[address]; exists {
		// Return a copy to prevent race conditions
		return &Validator{
			Address:    validator.Address,
			Stake:      new(big.Int).Set(validator.Stake),
			Reputation: validator.Reputation,
			IsActive:   validator.IsActive,
			LastBlock:  validator.LastBlock,
			CreatedAt:  validator.CreatedAt,
			UpdatedAt:  validator.UpdatedAt,
		}
	}
	
	return nil
}

// GetAllValidators returns all validators
func (v *ValidatorManager) GetAllValidators() map[common.Address]*Validator {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	validators := make(map[common.Address]*Validator)
	for address, validator := range v.validators {
		validators[address] = &Validator{
			Address:    validator.Address,
			Stake:      new(big.Int).Set(validator.Stake),
			Reputation: validator.Reputation,
			IsActive:   validator.IsActive,
			LastBlock:  validator.LastBlock,
			CreatedAt:  validator.CreatedAt,
			UpdatedAt:  validator.UpdatedAt,
		}
	}
	
	return validators
}

// GetActiveValidators returns only active validators
func (v *ValidatorManager) GetActiveValidators() map[common.Address]*Validator {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	activeValidators := make(map[common.Address]*Validator)
	for address, validator := range v.validators {
		if validator.IsActive {
			activeValidators[address] = &Validator{
				Address:    validator.Address,
				Stake:      new(big.Int).Set(validator.Stake),
				Reputation: validator.Reputation,
				IsActive:   validator.IsActive,
				LastBlock:  validator.LastBlock,
				CreatedAt:  validator.CreatedAt,
				UpdatedAt:  validator.UpdatedAt,
			}
		}
	}
	
	return activeValidators
}

// GetValidatorCount returns the total number of validators
func (v *ValidatorManager) GetValidatorCount() int {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	return len(v.validators)
}

// GetActiveValidatorCount returns the number of active validators
func (v *ValidatorManager) GetActiveValidatorCount() int {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	count := 0
	for _, validator := range v.validators {
		if validator.IsActive {
			count++
		}
	}
	
	return count
}

// GetTotalStake returns the total stake of all validators
func (v *ValidatorManager) GetTotalStake() *big.Int {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	totalStake := big.NewInt(0)
	for _, validator := range v.validators {
		if validator.IsActive {
			totalStake.Add(totalStake, validator.Stake)
		}
	}
	
	return totalStake
}

// GetTopValidators returns the top validators by stake
func (v *ValidatorManager) GetTopValidators(count int) []*Validator {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	validators := make([]*Validator, 0, len(v.validators))
	for _, validator := range v.validators {
		if validator.IsActive {
			validators = append(validators, validator)
		}
	}
	
	// Sort by stake (descending)
	sort.Slice(validators, func(i, j int) bool {
		return validators[i].Stake.Cmp(validators[j].Stake) > 0
	})
	
	// Return top N
	if count > len(validators) {
		count = len(validators)
	}
	
	return validators[:count]
}

// IsValidator checks if an address is a validator
func (v *ValidatorManager) IsValidator(address common.Address) bool {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	_, exists := v.validators[address]
	return exists
}

// IsActiveValidator checks if an address is an active validator
func (v *ValidatorManager) IsActiveValidator(address common.Address) bool {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	if validator, exists := v.validators[address]; exists {
		return validator.IsActive
	}
	
	return false
}

// UpdateLastBlock updates the last block number for a validator
func (v *ValidatorManager) UpdateLastBlock(address common.Address, blockNumber uint64) {
	v.mu.Lock()
	defer v.mu.Unlock()
	
	if validator, exists := v.validators[address]; exists {
		validator.LastBlock = blockNumber
		validator.UpdatedAt = uint64(time.Now().Unix())
	}
}

// GetValidatorStats returns statistics about validators
func (v *ValidatorManager) GetValidatorStats() map[string]interface{} {
	v.mu.RLock()
	defer v.mu.RUnlock()
	
	stats := make(map[string]interface{})
	
	totalCount := len(v.validators)
	activeCount := 0
	totalStake := big.NewInt(0)
	avgReputation := int64(0)
	
	for _, validator := range v.validators {
		if validator.IsActive {
			activeCount++
			totalStake.Add(totalStake, validator.Stake)
		}
		avgReputation += validator.Reputation
	}
	
	if totalCount > 0 {
		avgReputation /= int64(totalCount)
	}
	
	stats["total_validators"] = totalCount
	stats["active_validators"] = activeCount
	stats["total_stake"] = totalStake.String()
	stats["average_reputation"] = avgReputation
	stats["min_stake"] = v.config.MinStake.String()
	stats["max_validators"] = v.config.MaxValidators
	
	return stats
}

// GenerateValidatorAddress generates a new validator address
func GenerateValidatorAddress() common.Address {
	// Generate random private key
	privateKey, _ := crypto.GenerateKey()
	
	// Get public key
	publicKey := privateKey.Public()
	
	// Get address
	address := crypto.PubkeyToAddress(publicKey.(crypto.PublicKey))
	
	return address
}

// ValidateValidatorAddress validates a validator address
func ValidateValidatorAddress(address common.Address) bool {
	// Check if address is not zero
	return address != (common.Address{})
}
