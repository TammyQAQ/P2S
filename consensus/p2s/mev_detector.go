package p2s

import (
	"math/big"
	"strings"
	"sync"
	"time"

	"github.com/ethereum/go-ethereum/common"
)

// MEVDetector detects and analyzes MEV attacks
type MEVDetector struct {
	attackPatterns map[string]*AttackPattern
	threshold      float64
	config        *P2SConfig
	mu            sync.RWMutex
}

// AttackPattern represents a type of MEV attack
type AttackPattern struct {
	Name        string  `json:"name"`
	Threshold   float64 `json:"threshold"`
	Description string  `json:"description"`
	Severity    string  `json:"severity"` // low, medium, high, critical
}

// MEVAnalysis contains the result of MEV analysis
type MEVAnalysis struct {
	Score           float64  `json:"score"`
	DetectedAttacks []string `json:"detectedAttacks"`
	RiskLevel       string   `json:"riskLevel"`
	Recommendations []string `json:"recommendations"`
}

// NewMEVDetector creates a new MEV detector
func NewMEVDetector(config *P2SConfig) *MEVDetector {
	detector := &MEVDetector{
		attackPatterns: make(map[string]*AttackPattern),
		threshold:      0.7,
		config:        config,
	}
	
	// Initialize attack patterns
	detector.initializeAttackPatterns()
	
	return detector
}

// initializeAttackPatterns initializes known MEV attack patterns
func (m *MEVDetector) initializeAttackPatterns() {
	m.attackPatterns["sandwich_attack"] = &AttackPattern{
		Name:        "Sandwich Attack",
		Threshold:   0.8,
		Description: "Transaction is sandwiched between two attacker transactions",
		Severity:    "high",
	}
	
	m.attackPatterns["front_running"] = &AttackPattern{
		Name:        "Front Running",
		Threshold:   0.6,
		Description: "Attacker transaction executes before target transaction",
		Severity:    "medium",
	}
	
	m.attackPatterns["back_running"] = &AttackPattern{
		Name:        "Back Running",
		Threshold:   0.5,
		Description: "Attacker transaction executes after target transaction",
		Severity:    "medium",
	}
	
	m.attackPatterns["arbitrage"] = &AttackPattern{
		Name:        "Arbitrage",
		Threshold:   0.3,
		Description: "Price difference exploitation between exchanges",
		Severity:    "low",
	}
	
	m.attackPatterns["liquidation"] = &AttackPattern{
		Name:        "Liquidation",
		Threshold:   0.7,
		Description: "Forced liquidation of undercollateralized positions",
		Severity:    "high",
	}
	
	m.attackPatterns["dai_arbitrage"] = &AttackPattern{
		Name:        "DAI Arbitrage",
		Threshold:   0.4,
		Description: "DAI price arbitrage between MakerDAO and exchanges",
		Severity:    "low",
	}
}

// DetectMEV detects MEV attacks in a set of PHTs
func (m *MEVDetector) DetectMEV(phts []*PHTTransaction) (float64, []string) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	if len(phts) == 0 {
		return 1.0, []string{}
	}
	
	var totalScore float64
	var detectedAttacks []string
	
	for _, pht := range phts {
		score, attacks := m.analyzeTransaction(pht)
		totalScore += score
		detectedAttacks = append(detectedAttacks, attacks...)
	}
	
	// Normalize score
	avgScore := totalScore / float64(len(phts))
	
	// Remove duplicates from attacks
	uniqueAttacks := m.removeDuplicateAttacks(detectedAttacks)
	
	return avgScore, uniqueAttacks
}

// analyzeTransaction analyzes a single transaction for MEV patterns
func (m *MEVDetector) analyzeTransaction(pht *PHTTransaction) (float64, []string) {
	var score float64 = 1.0
	var attacks []string
	
	// Check for sandwich attack patterns
	if m.isSandwichPattern(pht) {
		score -= 0.3
		attacks = append(attacks, "sandwich_attack")
	}
	
	// Check for front-running patterns
	if m.isFrontRunPattern(pht) {
		score -= 0.2
		attacks = append(attacks, "front_running")
	}
	
	// Check for arbitrage patterns
	if m.isArbitragePattern(pht) {
		score -= 0.1
		attacks = append(attacks, "arbitrage")
	}
	
	// Check for liquidation patterns
	if m.isLiquidationPattern(pht) {
		score -= 0.25
		attacks = append(attacks, "liquidation")
	}
	
	// Check for high-value transactions
	if m.isHighValuePattern(pht) {
		score -= 0.15
	}
	
	// Check for contract interactions
	if m.isContractInteractionPattern(pht) {
		score -= 0.1
	}
	
	// Ensure score is between 0 and 1
	if score < 0 {
		score = 0
	}
	if score > 1 {
		score = 1
	}
	
	return score, attacks
}

// isSandwichPattern checks for sandwich attack patterns
func (m *MEVDetector) isSandwichPattern(pht *PHTTransaction) bool {
	// High gas price indicates potential sandwich attack
	if pht.GasPrice.Cmp(big.NewInt(10000000000)) > 0 { // > 10 gwei
		return true
	}
	
	// Large value transactions are more susceptible
	if pht.Value.Cmp(big.NewInt(1000000000000000000)) > 0 { // > 1 ETH
		return true
	}
	
	// Contract interactions with specific patterns
	if len(pht.CallData) > 0 {
		// Check for common DEX function signatures
		if m.hasDEXFunctionSignature(pht.CallData) {
			return true
		}
	}
	
	return false
}

// isFrontRunPattern checks for front-running patterns
func (m *MEVDetector) isFrontRunPattern(pht *PHTTransaction) bool {
	// Very high gas price indicates front-running
	if pht.GasPrice.Cmp(big.NewInt(50000000000)) > 0 { // > 50 gwei
		return true
	}
	
	// Transactions with specific call data patterns
	if len(pht.CallData) > 0 {
		// Check for common front-running patterns
		if m.hasFrontRunPattern(pht.CallData) {
			return true
		}
	}
	
	return false
}

// isArbitragePattern checks for arbitrage patterns
func (m *MEVDetector) isArbitragePattern(pht *PHTTransaction) bool {
	// Check for arbitrage-specific call data
	if len(pht.CallData) > 0 {
		// Look for arbitrage function signatures
		if m.hasArbitrageFunctionSignature(pht.CallData) {
			return true
		}
	}
	
	// Check for specific recipient addresses (known arbitrage contracts)
	if m.isKnownArbitrageContract(pht.Recipient) {
		return true
	}
	
	return false
}

// isLiquidationPattern checks for liquidation patterns
func (m *MEVDetector) isLiquidationPattern(pht *PHTTransaction) bool {
	// Check for liquidation-specific call data
	if len(pht.CallData) > 0 {
		// Look for liquidation function signatures
		if m.hasLiquidationFunctionSignature(pht.CallData) {
			return true
		}
	}
	
	// Check for specific recipient addresses (known liquidation contracts)
	if m.isKnownLiquidationContract(pht.Recipient) {
		return true
	}
	
	return false
}

// isHighValuePattern checks for high-value transaction patterns
func (m *MEVDetector) isHighValuePattern(pht *PHTTransaction) bool {
	// Very large value transactions
	return pht.Value.Cmp(big.NewInt(10000000000000000000)) > 0 // > 10 ETH
}

// isContractInteractionPattern checks for contract interaction patterns
func (m *MEVDetector) isContractInteractionPattern(pht *PHTTransaction) bool {
	// Non-zero call data indicates contract interaction
	return len(pht.CallData) > 0
}

// hasDEXFunctionSignature checks for DEX function signatures
func (m *MEVDetector) hasDEXFunctionSignature(callData []byte) bool {
	if len(callData) < 4 {
		return false
	}
	
	// Common DEX function signatures
	dexSignatures := []string{
		"0x38ed1739", // swapExactTokensForTokens
		"0x7ff36ab5", // swapExactETHForTokens
		"0x18cbafe5", // swapExactTokensForETH
		"0xfb3bdb41", // swapETHForExactTokens
		"0x8803dbee", // swapTokensForExactTokens
		"0x4a25d94a", // swapTokensForExactETH
	}
	
	signature := common.Bytes2Hex(callData[:4])
	for _, dexSig := range dexSignatures {
		if signature == dexSig {
			return true
		}
	}
	
	return false
}

// hasFrontRunPattern checks for front-running patterns
func (m *MEVDetector) hasFrontRunPattern(callData []byte) bool {
	if len(callData) < 4 {
		return false
	}
	
	// Common front-running function signatures
	frontRunSignatures := []string{
		"0xa9059cbb", // transfer
		"0x23b872dd", // transferFrom
		"0x095ea7b3", // approve
		"0x40c10f19", // mint
		"0x42966c68", // burn
	}
	
	signature := common.Bytes2Hex(callData[:4])
	for _, frSig := range frontRunSignatures {
		if signature == frSig {
			return true
		}
	}
	
	return false
}

// hasArbitrageFunctionSignature checks for arbitrage function signatures
func (m *MEVDetector) hasArbitrageFunctionSignature(callData []byte) bool {
	if len(callData) < 4 {
		return false
	}
	
	// Common arbitrage function signatures
	arbitrageSignatures := []string{
		"0x6a627842", // mint
		"0x79cc6790", // burn
		"0x18160ddd", // totalSupply
		"0x70a08231", // balanceOf
	}
	
	signature := common.Bytes2Hex(callData[:4])
	for _, arbSig := range arbitrageSignatures {
		if signature == arbSig {
			return true
		}
	}
	
	return false
}

// hasLiquidationFunctionSignature checks for liquidation function signatures
func (m *MEVDetector) hasLiquidationFunctionSignature(callData []byte) bool {
	if len(callData) < 4 {
		return false
	}
	
	// Common liquidation function signatures
	liquidationSignatures := []string{
		"0x42842e0e", // safeTransferFrom
		"0xb88d4fde", // safeTransferFrom
		"0x23b872dd", // transferFrom
		"0xa9059cbb", // transfer
	}
	
	signature := common.Bytes2Hex(callData[:4])
	for _, liqSig := range liquidationSignatures {
		if signature == liqSig {
			return true
		}
	}
	
	return false
}

// isKnownArbitrageContract checks if address is a known arbitrage contract
func (m *MEVDetector) isKnownArbitrageContract(address common.Address) bool {
	// Known arbitrage contract addresses (example)
	knownContracts := []common.Address{
		common.HexToAddress("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"), // Uniswap V2 Router
		common.HexToAddress("0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506"), // SushiSwap Router
		common.HexToAddress("0xE592427A0AEce92De3Edee1F18E0157C05861564"), // Uniswap V3 Router
	}
	
	for _, contract := range knownContracts {
		if address == contract {
			return true
		}
	}
	
	return false
}

// isKnownLiquidationContract checks if address is a known liquidation contract
func (m *MEVDetector) isKnownLiquidationContract(address common.Address) bool {
	// Known liquidation contract addresses (example)
	knownContracts := []common.Address{
		common.HexToAddress("0x3ed3B47Dd13EC9a98b44e6204A523E766B225811"), // Aave Lending Pool
		common.HexToAddress("0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9"), // Aave Lending Pool V2
		common.HexToAddress("0x398eC7346DcD622eDc5ae82352F02bE94C62d119"), // Compound cETH
	}
	
	for _, contract := range knownContracts {
		if address == contract {
			return true
		}
	}
	
	return false
}

// removeDuplicateAttacks removes duplicate attack types
func (m *MEVDetector) removeDuplicateAttacks(attacks []string) []string {
	seen := make(map[string]bool)
	result := []string{}
	
	for _, attack := range attacks {
		if !seen[attack] {
			seen[attack] = true
			result = append(result, attack)
		}
	}
	
	return result
}

// AnalyzeMEVRisk analyzes MEV risk for a transaction
func (m *MEVDetector) AnalyzeMEVRisk(pht *PHTTransaction) *MEVAnalysis {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	score, attacks := m.analyzeTransaction(pht)
	
	// Determine risk level
	riskLevel := m.determineRiskLevel(score)
	
	// Generate recommendations
	recommendations := m.generateRecommendations(attacks, score)
	
	return &MEVAnalysis{
		Score:           score,
		DetectedAttacks: attacks,
		RiskLevel:       riskLevel,
		Recommendations: recommendations,
	}
}

// determineRiskLevel determines the risk level based on score
func (m *MEVDetector) determineRiskLevel(score float64) string {
	if score >= 0.8 {
		return "low"
	} else if score >= 0.6 {
		return "medium"
	} else if score >= 0.4 {
		return "high"
	} else {
		return "critical"
	}
}

// generateRecommendations generates recommendations based on detected attacks
func (m *MEVDetector) generateRecommendations(attacks []string, score float64) []string {
	recommendations := []string{}
	
	if score < 0.7 {
		recommendations = append(recommendations, "Consider using private mempool or MEV protection service")
	}
	
	for _, attack := range attacks {
		switch attack {
		case "sandwich_attack":
			recommendations = append(recommendations, "Use smaller transaction sizes or split into multiple transactions")
		case "front_running":
			recommendations = append(recommendations, "Increase gas price or use commit-reveal scheme")
		case "arbitrage":
			recommendations = append(recommendations, "Monitor price differences across exchanges")
		case "liquidation":
			recommendations = append(recommendations, "Ensure sufficient collateralization ratio")
		}
	}
	
	return recommendations
}

// GetAttackPattern returns an attack pattern by name
func (m *MEVDetector) GetAttackPattern(name string) *AttackPattern {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	return m.attackPatterns[name]
}

// GetAllAttackPatterns returns all attack patterns
func (m *MEVDetector) GetAllAttackPatterns() map[string]*AttackPattern {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	patterns := make(map[string]*AttackPattern)
	for name, pattern := range m.attackPatterns {
		patterns[name] = &AttackPattern{
			Name:        pattern.Name,
			Threshold:   pattern.Threshold,
			Description: pattern.Description,
			Severity:    pattern.Severity,
		}
	}
	
	return patterns
}

// UpdateThreshold updates the MEV detection threshold
func (m *MEVDetector) UpdateThreshold(threshold float64) {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	m.threshold = threshold
}

// GetThreshold returns the current MEV detection threshold
func (m *MEVDetector) GetThreshold() float64 {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	return m.threshold
}

// AddAttackPattern adds a new attack pattern
func (m *MEVDetector) AddAttackPattern(name string, pattern *AttackPattern) {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	m.attackPatterns[name] = pattern
}

// RemoveAttackPattern removes an attack pattern
func (m *MEVDetector) RemoveAttackPattern(name string) {
	m.mu.Lock()
	defer m.mu.Unlock()
	
	delete(m.attackPatterns, name)
}

// GetMEVStats returns MEV detection statistics
func (m *MEVDetector) GetMEVStats() map[string]interface{} {
	m.mu.RLock()
	defer m.mu.RUnlock()
	
	stats := make(map[string]interface{})
	
	stats["total_patterns"] = len(m.attackPatterns)
	stats["threshold"] = m.threshold
	
	// Count patterns by severity
	severityCount := make(map[string]int)
	for _, pattern := range m.attackPatterns {
		severityCount[pattern.Severity]++
	}
	stats["severity_distribution"] = severityCount
	
	return stats
}
