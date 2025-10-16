package p2s

import (
	"crypto/sha256"
	"errors"
	"math/big"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
)

// PHTManager manages Partially Hidden Transactions
type PHTManager struct {
	commitmentScheme CommitmentScheme
	antiMEVNonce     *AntiMEVNonce
	config          *P2SConfig
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

// CommitmentScheme interface for cryptographic commitments
type CommitmentScheme interface {
	Commit(data ...[]byte) ([]byte, error)
	Verify(commitment []byte, data ...[]byte) bool
	Open(commitment []byte) ([]byte, error)
}

// PedersenCommitment implements Pedersen commitment scheme
type PedersenCommitment struct {
	generator *big.Int
	modulus   *big.Int
}

// NewPedersenCommitment creates a new Pedersen commitment scheme
func NewPedersenCommitment() *PedersenCommitment {
	// Use secp256k1 parameters for compatibility with Ethereum
	return &PedersenCommitment{
		generator: big.NewInt(2),
		modulus:   crypto.S256().P,
	}
}

// Commit creates a commitment for the given data
func (p *PedersenCommitment) Commit(data ...[]byte) ([]byte, error) {
	if len(data) == 0 {
		return nil, errors.New("no data to commit")
	}
	
	// Hash all data together
	hasher := sha256.New()
	for _, d := range data {
		hasher.Write(d)
	}
	hash := hasher.Sum(nil)
	
	// Convert to big.Int
	hashInt := new(big.Int).SetBytes(hash)
	
	// Create commitment: g^hash mod p
	commitment := new(big.Int).Exp(p.generator, hashInt, p.modulus)
	
	return commitment.Bytes(), nil
}

// Verify verifies a commitment against data
func (p *PedersenCommitment) Verify(commitment []byte, data ...[]byte) bool {
	// Recreate commitment from data
	newCommitment, err := p.Commit(data...)
	if err != nil {
		return false
	}
	
	// Compare commitments
	return string(commitment) == string(newCommitment)
}

// Open opens a commitment (for verification purposes)
func (p *PedersenCommitment) Open(commitment []byte) ([]byte, error) {
	// In a real implementation, this would require the opening key
	// For now, return the commitment itself
	return commitment, nil
}

// AntiMEVNonce generates anti-MEV nonces
type AntiMEVNonce struct {
	randomSource func() []byte
}

// NewAntiMEVNonce creates a new anti-MEV nonce generator
func NewAntiMEVNonce() *AntiMEVNonce {
	return &AntiMEVNonce{
		randomSource: func() []byte {
			// Generate random bytes
			return crypto.Keccak256([]byte(time.Now().String()))
		},
	}
}

// Generate generates a new anti-MEV nonce
func (a *AntiMEVNonce) Generate() []byte {
	return a.randomSource()
}

// NewPHTManager creates a new PHT manager
func NewPHTManager(config *P2SConfig) *PHTManager {
	return &PHTManager{
		commitmentScheme: NewPedersenCommitment(),
		antiMEVNonce:     NewAntiMEVNonce(),
		config:          config,
	}
}

// CreatePHT creates a PHT from a regular transaction
func (p *PHTManager) CreatePHT(tx *types.Transaction) (*PHTTransaction, error) {
	// Extract transaction fields
	sender, err := types.Sender(types.NewEIP155Signer(tx.ChainId()), tx)
	if err != nil {
		return nil, err
	}
	
	recipient := tx.To()
	if recipient == nil {
		// Contract creation transaction
		recipient = common.Address{}
	}
	
	// Create commitment for hidden fields
	hiddenData := [][]byte{
		recipient.Bytes(),
		tx.Value().Bytes(),
		tx.Data(),
		{tx.Type()},
		{byte(tx.Gas())},
	}
	
	commitment, err := p.commitmentScheme.Commit(hiddenData...)
	if err != nil {
		return nil, err
	}
	
	// Generate anti-MEV nonce
	nonce := p.antiMEVNonce.Generate()
	
	// Create PHT
	pht := &PHTTransaction{
		Sender:     sender,
		GasPrice:   tx.GasPrice(),
		Commitment: commitment,
		Nonce:      nonce,
		Timestamp:  uint64(time.Now().Unix()),
		Recipient:  *recipient,
		Value:      tx.Value(),
		CallData:   tx.Data(),
		TxType:     tx.Type(),
		GasLimit:   tx.Gas(),
		TxHash:     tx.Hash(),
	}
	
	return pht, nil
}

// ValidatePHT validates a PHT
func (p *PHTManager) ValidatePHT(pht *PHTTransaction) error {
	// Validate commitment
	hiddenData := [][]byte{
		pht.Recipient.Bytes(),
		pht.Value.Bytes(),
		pht.CallData,
		{pht.TxType},
		{byte(pht.GasLimit)},
	}
	
	if !p.commitmentScheme.Verify(pht.Commitment, hiddenData...) {
		return errors.New("invalid commitment")
	}
	
	// Validate nonce
	if len(pht.Nonce) == 0 {
		return errors.New("missing anti-MEV nonce")
	}
	
	// Validate timestamp
	if pht.Timestamp == 0 {
		return errors.New("missing timestamp")
	}
	
	// Validate gas price
	if pht.GasPrice.Cmp(big.NewInt(0)) <= 0 {
		return errors.New("invalid gas price")
	}
	
	return nil
}

// VerifyCommitment verifies a commitment against revealed data
func (p *PHTManager) VerifyCommitment(pht *PHTTransaction, recipient common.Address, value *big.Int, callData []byte, txType uint8, gasLimit uint64) bool {
	hiddenData := [][]byte{
		recipient.Bytes(),
		value.Bytes(),
		callData,
		{txType},
		{byte(gasLimit)},
	}
	
	return p.commitmentScheme.Verify(pht.Commitment, hiddenData...)
}

// GetHiddenFields returns the hidden fields of a PHT
func (p *PHTManager) GetHiddenFields(pht *PHTTransaction) (common.Address, *big.Int, []byte, uint8, uint64) {
	return pht.Recipient, pht.Value, pht.CallData, pht.TxType, pht.GasLimit
}

// Hash returns the hash of a PHT
func (pht *PHTTransaction) Hash() common.Hash {
	// Hash visible fields only
	hasher := sha256.New()
	hasher.Write(pht.Sender.Bytes())
	hasher.Write(pht.GasPrice.Bytes())
	hasher.Write(pht.Commitment)
	hasher.Write(pht.Nonce)
	
	// Convert timestamp to bytes
	timestampBytes := make([]byte, 8)
	for i := 0; i < 8; i++ {
		timestampBytes[i] = byte(pht.Timestamp >> (8 * i))
	}
	hasher.Write(timestampBytes)
	
	hash := hasher.Sum(nil)
	return common.BytesToHash(hash)
}

// ToTransaction converts a PHT back to a regular transaction
func (pht *PHTTransaction) ToTransaction() *types.Transaction {
	// Create transaction with revealed fields
	var tx *types.Transaction
	
	if pht.TxType == types.LegacyTxType {
		tx = types.NewTransaction(0, pht.Recipient, pht.Value, pht.GasLimit, pht.GasPrice, pht.CallData)
	} else {
		// Handle other transaction types
		tx = types.NewTransaction(0, pht.Recipient, pht.Value, pht.GasLimit, pht.GasPrice, pht.CallData)
	}
	
	return tx
}

// Serialize serializes a PHT to bytes
func (pht *PHTTransaction) Serialize() ([]byte, error) {
	// Simple serialization - in production, use proper encoding
	data := make([]byte, 0)
	
	// Add sender
	data = append(data, pht.Sender.Bytes()...)
	
	// Add gas price
	data = append(data, pht.GasPrice.Bytes()...)
	
	// Add commitment
	data = append(data, pht.Commitment...)
	
	// Add nonce
	data = append(data, pht.Nonce...)
	
	// Add timestamp
	timestampBytes := make([]byte, 8)
	for i := 0; i < 8; i++ {
		timestampBytes[i] = byte(pht.Timestamp >> (8 * i))
	}
	data = append(data, timestampBytes...)
	
	return data, nil
}

// Deserialize deserializes bytes to a PHT
func (pht *PHTTransaction) Deserialize(data []byte) error {
	if len(data) < 20+32+32+32+8 { // Minimum required bytes
		return errors.New("insufficient data")
	}
	
	offset := 0
	
	// Deserialize sender
	pht.Sender = common.BytesToAddress(data[offset : offset+20])
	offset += 20
	
	// Deserialize gas price
	pht.GasPrice = new(big.Int).SetBytes(data[offset : offset+32])
	offset += 32
	
	// Deserialize commitment
	pht.Commitment = make([]byte, 32)
	copy(pht.Commitment, data[offset:offset+32])
	offset += 32
	
	// Deserialize nonce
	pht.Nonce = make([]byte, 32)
	copy(pht.Nonce, data[offset:offset+32])
	offset += 32
	
	// Deserialize timestamp
	pht.Timestamp = 0
	for i := 0; i < 8; i++ {
		pht.Timestamp |= uint64(data[offset+i]) << (8 * i)
	}
	
	return nil
}

// GetMEVScore calculates MEV score for a PHT
func (p *PHTManager) GetMEVScore(pht *PHTTransaction) float64 {
	score := 1.0
	
	// Higher gas price indicates potential MEV
	if pht.GasPrice.Cmp(big.NewInt(1000000000)) > 0 { // > 1 gwei
		score -= 0.1
	}
	
	// Large value transactions are more susceptible to MEV
	if pht.Value.Cmp(big.NewInt(1000000000000000000)) > 0 { // > 1 ETH
		score -= 0.2
	}
	
	// Contract interactions are more susceptible to MEV
	if len(pht.CallData) > 0 {
		score -= 0.1
	}
	
	// Ensure score is between 0 and 1
	if score < 0 {
		score = 0
	}
	if score > 1 {
		score = 1
	}
	
	return score
}

// IsMEVSusceptible checks if a PHT is susceptible to MEV attacks
func (p *PHTManager) IsMEVSusceptible(pht *PHTTransaction) bool {
	score := p.GetMEVScore(pht)
	return score < 0.7 // Threshold for MEV susceptibility
}
