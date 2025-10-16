package p2s

import (
	"crypto/sha256"
	"errors"
	"math/big"
	"time"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
)

// MTManager manages Matching Transactions
type MTManager struct {
	commitmentScheme CommitmentScheme
	proofSystem      ProofSystem
	config          *P2SConfig
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

// ProofSystem interface for cryptographic proofs
type ProofSystem interface {
	Prove(commitment []byte, data ...[]byte) ([]byte, error)
	Verify(proof []byte, commitment []byte, data ...[]byte) bool
}

// MerkleProofSystem implements Merkle tree-based proofs
type MerkleProofSystem struct {
	treeHeight int
}

// NewMerkleProofSystem creates a new Merkle proof system
func NewMerkleProofSystem() *MerkleProofSystem {
	return &MerkleProofSystem{
		treeHeight: 32, // 32 levels for 2^32 leaves
	}
}

// Prove creates a proof for the given commitment and data
func (m *MerkleProofSystem) Prove(commitment []byte, data ...[]byte) ([]byte, error) {
	if len(data) == 0 {
		return nil, errors.New("no data to prove")
	}
	
	// Create Merkle tree from data
	tree := m.buildMerkleTree(data)
	
	// Find the commitment in the tree
	leafIndex := m.findLeafIndex(tree, commitment)
	if leafIndex == -1 {
		return nil, errors.New("commitment not found in tree")
	}
	
	// Generate Merkle proof
	proof := m.generateMerkleProof(tree, leafIndex)
	
	return proof, nil
}

// Verify verifies a proof against commitment and data
func (m *MerkleProofSystem) Verify(proof []byte, commitment []byte, data ...[]byte) bool {
	if len(data) == 0 {
		return false
	}
	
	// Recreate Merkle tree from data
	tree := m.buildMerkleTree(data)
	
	// Verify the proof
	return m.verifyMerkleProof(proof, commitment, tree)
}

// buildMerkleTree builds a Merkle tree from data
func (m *MerkleProofSystem) buildMerkleTree(data [][]byte) [][]byte {
	if len(data) == 0 {
		return nil
	}
	
	// Pad data to power of 2
	paddedData := m.padToPowerOfTwo(data)
	
	// Build tree bottom-up
	tree := make([][]byte, len(paddedData)*2-1)
	
	// Copy leaves
	for i, d := range paddedData {
		tree[i] = d
	}
	
	// Build internal nodes
	for i := len(paddedData); i < len(tree); i++ {
		leftChild := tree[2*i-len(paddedData)]
		rightChild := tree[2*i-len(paddedData)+1]
		
		// Hash children
		hasher := sha256.New()
		hasher.Write(leftChild)
		hasher.Write(rightChild)
		tree[i] = hasher.Sum(nil)
	}
	
	return tree
}

// padToPowerOfTwo pads data to the next power of 2
func (m *MerkleProofSystem) padToPowerOfTwo(data [][]byte) [][]byte {
	n := len(data)
	if n == 0 {
		return data
	}
	
	// Find next power of 2
	nextPower := 1
	for nextPower < n {
		nextPower <<= 1
	}
	
	// Pad with empty bytes
	padded := make([][]byte, nextPower)
	copy(padded, data)
	
	for i := n; i < nextPower; i++ {
		padded[i] = make([]byte, 32) // Empty hash
	}
	
	return padded
}

// findLeafIndex finds the index of a leaf in the tree
func (m *MerkleProofSystem) findLeafIndex(tree [][]byte, commitment []byte) int {
	for i, leaf := range tree {
		if string(leaf) == string(commitment) {
			return i
		}
	}
	return -1
}

// generateMerkleProof generates a Merkle proof for a leaf
func (m *MerkleProofSystem) generateMerkleProof(tree [][]byte, leafIndex int) []byte {
	proof := make([]byte, 0)
	
	currentIndex := leafIndex
	for currentIndex < len(tree)-1 {
		// Add sibling to proof
		siblingIndex := currentIndex ^ 1
		proof = append(proof, tree[siblingIndex]...)
		
		// Move to parent
		currentIndex = (currentIndex + len(tree)) / 2
	}
	
	return proof
}

// verifyMerkleProof verifies a Merkle proof
func (m *MerkleProofSystem) verifyMerkleProof(proof []byte, commitment []byte, tree [][]byte) bool {
	if len(proof) == 0 {
		return false
	}
	
	// Reconstruct root from proof
	current := commitment
	proofIndex := 0
	
	for proofIndex < len(proof) {
		// Get sibling from proof
		sibling := proof[proofIndex : proofIndex+32]
		proofIndex += 32
		
		// Hash current and sibling
		hasher := sha256.New()
		hasher.Write(current)
		hasher.Write(sibling)
		current = hasher.Sum(nil)
	}
	
	// Compare with root
	root := tree[len(tree)-1]
	return string(current) == string(root)
}

// NewMTManager creates a new MT manager
func NewMTManager(config *P2SConfig) *MTManager {
	return &MTManager{
		commitmentScheme: NewPedersenCommitment(),
		proofSystem:      NewMerkleProofSystem(),
		config:          config,
	}
}

// CreateMT creates an MT from a PHT
func (m *MTManager) CreateMT(pht *PHTTransaction) (*MTTransaction, error) {
	// Extract hidden fields from PHT
	recipient, value, callData, txType, gasLimit := pht.Recipient, pht.Value, pht.CallData, pht.TxType, pht.GasLimit
	
	// Create proof that MT matches PHT
	proof, err := m.proofSystem.Prove(pht.Commitment, 
		recipient.Bytes(),
		value.Bytes(),
		callData,
		{txType},
		{byte(gasLimit)},
	)
	if err != nil {
		return nil, err
	}
	
	// Create MT
	mt := &MTTransaction{
		Recipient:  recipient,
		Value:      value,
		CallData:   callData,
		TxType:     txType,
		GasLimit:   gasLimit,
		PHTHash:    pht.Hash(),
		Proof:      proof,
		Timestamp:  uint64(time.Now().Unix()),
		TxHash:     pht.TxHash, // Same as original transaction
	}
	
	return mt, nil
}

// VerifyMT verifies an MT against its corresponding PHT
func (m *MTManager) VerifyMT(mt *MTTransaction, pht *PHTTransaction) error {
	// Verify proof matches commitment
	valid := m.proofSystem.Verify(mt.Proof, pht.Commitment,
		mt.Recipient.Bytes(),
		mt.Value.Bytes(),
		mt.CallData,
		{mt.TxType},
		{byte(mt.GasLimit)},
	)
	
	if !valid {
		return errors.New("invalid proof")
	}
	
	// Verify PHT hash matches
	if mt.PHTHash != pht.Hash() {
		return errors.New("PHT hash mismatch")
	}
	
	// Verify revealed data matches committed data
	if mt.Recipient != pht.Recipient {
		return errors.New("recipient mismatch")
	}
	
	if mt.Value.Cmp(pht.Value) != 0 {
		return errors.New("value mismatch")
	}
	
	if string(mt.CallData) != string(pht.CallData) {
		return errors.New("call data mismatch")
	}
	
	if mt.TxType != pht.TxType {
		return errors.New("transaction type mismatch")
	}
	
	if mt.GasLimit != pht.GasLimit {
		return errors.New("gas limit mismatch")
	}
	
	return nil
}

// ValidateMT validates an MT
func (m *MTManager) ValidateMT(mt *MTTransaction) error {
	// Validate proof
	if len(mt.Proof) == 0 {
		return errors.New("missing proof")
	}
	
	// Validate timestamp
	if mt.Timestamp == 0 {
		return errors.New("missing timestamp")
	}
	
	// Validate PHT hash
	if mt.PHTHash == (common.Hash{}) {
		return errors.New("missing PHT hash")
	}
	
	// Validate transaction hash
	if mt.TxHash == (common.Hash{}) {
		return errors.New("missing transaction hash")
	}
	
	// Validate value
	if mt.Value.Cmp(big.NewInt(0)) < 0 {
		return errors.New("negative value")
	}
	
	// Validate gas limit
	if mt.GasLimit == 0 {
		return errors.New("zero gas limit")
	}
	
	return nil
}

// Hash returns the hash of an MT
func (mt *MTTransaction) Hash() common.Hash {
	// Hash revealed fields
	hasher := sha256.New()
	hasher.Write(mt.Recipient.Bytes())
	hasher.Write(mt.Value.Bytes())
	hasher.Write(mt.CallData)
	hasher.Write([]byte{mt.TxType})
	
	// Convert gas limit to bytes
	gasLimitBytes := make([]byte, 8)
	for i := 0; i < 8; i++ {
		gasLimitBytes[i] = byte(mt.GasLimit >> (8 * i))
	}
	hasher.Write(gasLimitBytes)
	
	// Add PHT hash
	hasher.Write(mt.PHTHash.Bytes())
	
	// Add timestamp
	timestampBytes := make([]byte, 8)
	for i := 0; i < 8; i++ {
		timestampBytes[i] = byte(mt.Timestamp >> (8 * i))
	}
	hasher.Write(timestampBytes)
	
	hash := hasher.Sum(nil)
	return common.BytesToHash(hash)
}

// ToTransaction converts an MT back to a regular transaction
func (mt *MTTransaction) ToTransaction() *types.Transaction {
	// Create transaction with revealed fields
	var tx *types.Transaction
	
	if mt.TxType == types.LegacyTxType {
		tx = types.NewTransaction(0, mt.Recipient, mt.Value, mt.GasLimit, big.NewInt(0), mt.CallData)
	} else {
		// Handle other transaction types
		tx = types.NewTransaction(0, mt.Recipient, mt.Value, mt.GasLimit, big.NewInt(0), mt.CallData)
	}
	
	return tx
}

// Serialize serializes an MT to bytes
func (mt *MTTransaction) Serialize() ([]byte, error) {
	// Simple serialization - in production, use proper encoding
	data := make([]byte, 0)
	
	// Add recipient
	data = append(data, mt.Recipient.Bytes()...)
	
	// Add value
	data = append(data, mt.Value.Bytes()...)
	
	// Add call data length and data
	callDataLen := make([]byte, 4)
	for i := 0; i < 4; i++ {
		callDataLen[i] = byte(len(mt.CallData) >> (8 * i))
	}
	data = append(data, callDataLen...)
	data = append(data, mt.CallData...)
	
	// Add transaction type
	data = append(data, mt.TxType)
	
	// Add gas limit
	gasLimitBytes := make([]byte, 8)
	for i := 0; i < 8; i++ {
		gasLimitBytes[i] = byte(mt.GasLimit >> (8 * i))
	}
	data = append(data, gasLimitBytes...)
	
	// Add PHT hash
	data = append(data, mt.PHTHash.Bytes()...)
	
	// Add proof length and proof
	proofLen := make([]byte, 4)
	for i := 0; i < 4; i++ {
		proofLen[i] = byte(len(mt.Proof) >> (8 * i))
	}
	data = append(data, proofLen...)
	data = append(data, mt.Proof...)
	
	// Add timestamp
	timestampBytes := make([]byte, 8)
	for i := 0; i < 8; i++ {
		timestampBytes[i] = byte(mt.Timestamp >> (8 * i))
	}
	data = append(data, timestampBytes...)
	
	return data, nil
}

// Deserialize deserializes bytes to an MT
func (mt *MTTransaction) Deserialize(data []byte) error {
	if len(data) < 20+32+4+1+8+32+4+8 { // Minimum required bytes
		return errors.New("insufficient data")
	}
	
	offset := 0
	
	// Deserialize recipient
	mt.Recipient = common.BytesToAddress(data[offset : offset+20])
	offset += 20
	
	// Deserialize value
	mt.Value = new(big.Int).SetBytes(data[offset : offset+32])
	offset += 32
	
	// Deserialize call data length
	callDataLen := 0
	for i := 0; i < 4; i++ {
		callDataLen |= int(data[offset+i]) << (8 * i)
	}
	offset += 4
	
	// Deserialize call data
	mt.CallData = make([]byte, callDataLen)
	copy(mt.CallData, data[offset:offset+callDataLen])
	offset += callDataLen
	
	// Deserialize transaction type
	mt.TxType = data[offset]
	offset += 1
	
	// Deserialize gas limit
	mt.GasLimit = 0
	for i := 0; i < 8; i++ {
		mt.GasLimit |= uint64(data[offset+i]) << (8 * i)
	}
	offset += 8
	
	// Deserialize PHT hash
	mt.PHTHash = common.BytesToHash(data[offset : offset+32])
	offset += 32
	
	// Deserialize proof length
	proofLen := 0
	for i := 0; i < 4; i++ {
		proofLen |= int(data[offset+i]) << (8 * i)
	}
	offset += 4
	
	// Deserialize proof
	mt.Proof = make([]byte, proofLen)
	copy(mt.Proof, data[offset:offset+proofLen])
	offset += proofLen
	
	// Deserialize timestamp
	mt.Timestamp = 0
	for i := 0; i < 8; i++ {
		mt.Timestamp |= uint64(data[offset+i]) << (8 * i)
	}
	
	return nil
}

// GetRevealedFields returns the revealed fields of an MT
func (m *MTManager) GetRevealedFields(mt *MTTransaction) (common.Address, *big.Int, []byte, uint8, uint64) {
	return mt.Recipient, mt.Value, mt.CallData, mt.TxType, mt.GasLimit
}

// IsValidProof checks if a proof is valid
func (m *MTManager) IsValidProof(proof []byte) bool {
	return len(proof) > 0 && len(proof)%32 == 0
}

// GetProofSize returns the size of a proof
func (m *MTManager) GetProofSize(proof []byte) int {
	return len(proof)
}
