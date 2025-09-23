#!/bin/bash

# Ethereum Fork Setup Script for P2S Implementation
# This script sets up a development environment for modifying Ethereum with P2S proposer

set -e

echo "🚀 Setting up Ethereum fork for P2S implementation..."

# Check if Go is installed
if ! command -v go &> /dev/null; then
    echo "❌ Go is not installed. Please install Go 1.21+ first."
    echo "   Visit: https://golang.org/doc/install"
    exit 1
fi

# Check Go version
GO_VERSION=$(go version | awk '{print $3}' | sed 's/go//')
echo "✅ Go version: $GO_VERSION"

# Create workspace directory
WORKSPACE_DIR="$HOME/ethereum-p2s-fork"
echo "📁 Creating workspace at: $WORKSPACE_DIR"

if [ -d "$WORKSPACE_DIR" ]; then
    echo "⚠️  Workspace already exists. Backing up..."
    mv "$WORKSPACE_DIR" "${WORKSPACE_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

mkdir -p "$WORKSPACE_DIR"
cd "$WORKSPACE_DIR"

# Clone Geth repository
echo "📥 Cloning Ethereum Go client..."
git clone https://github.com/ethereum/go-ethereum.git geth
cd geth

# Create P2S branch
echo "🌿 Creating P2S development branch..."
git checkout -b p2s-proposer-implementation

# Create P2S consensus package structure
echo "📦 Creating P2S consensus package..."
mkdir -p consensus/p2s

# Create basic P2S files
cat > consensus/p2s/proposer.go << 'EOF'
package p2s

import (
	"crypto/sha256"
	"encoding/binary"
	"math/big"
	"sync"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
)

// P2SProposer implements the two-step proposer selection mechanism
type P2SProposer struct {
	mu          sync.RWMutex
	merkleTree  *MerkleTree
	proposers   []ProposerNode
	round       uint64
	config      *P2SConfig
}

// P2SConfig holds configuration for P2S proposer
type P2SConfig struct {
	Enabled           bool
	MerkleTreeDepth   int
	ProposerCount     int
	SimulationURL     string
}

// ProposerNode represents a proposer in the network
type ProposerNode struct {
	ID        uint64
	Address   common.Address
	Available bool
	Stake     *big.Int
	Round     uint64
}

// MerkleTree for PHT (Proposer Hash Tree)
type MerkleTree struct {
	Root   common.Hash
	Leaves []common.Hash
	Depth  int
}

// NewP2SProposer creates a new P2S proposer instance
func NewP2SProposer(config *P2SConfig) *P2SProposer {
	return &P2SProposer{
		config: config,
		round:  0,
	}
}

// Step 1: User reveals MT for PHT
func (p *P2SProposer) RevealMerkleTree(userID uint64, merkleProof []common.Hash) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	// TODO: Implement merkle proof verification
	// This is where you'll integrate with your Python simulation
	
	return nil
}

// Step 2: Select proposer based on availability
func (p *P2SProposer) SelectProposer(blockNumber uint64) (*ProposerNode, error) {
	p.mu.RLock()
	defer p.mu.RUnlock()
	
	// TODO: Implement P2S proposer selection logic
	// This should integrate with your existing Python simulation
	
	// For now, return a placeholder
	if len(p.proposers) == 0 {
		return nil, ErrNoProposersAvailable
	}
	
	// Simple round-robin selection (replace with P2S logic)
	selectedIndex := blockNumber % uint64(len(p.proposers))
	return &p.proposers[selectedIndex], nil
}

// AddProposer adds a proposer to the pool
func (p *P2SProposer) AddProposer(proposer ProposerNode) {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	p.proposers = append(p.proposers, proposer)
}

// UpdateProposerAvailability updates proposer availability
func (p *P2SProposer) UpdateProposerAvailability(proposerID uint64, available bool) {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	for i := range p.proposers {
		if p.proposers[i].ID == proposerID {
			p.proposers[i].Available = available
			break
		}
	}
}

// Errors
var (
	ErrNoProposersAvailable = errors.New("no proposers available")
	ErrInvalidMerkleProof   = errors.New("invalid merkle proof")
)

// Import errors package
import "errors"
EOF

# Create simulation bridge
cat > consensus/p2s/simulation_bridge.go << 'EOF'
package p2s

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

// SimulationBridge connects to your Python P2S simulation
type SimulationBridge struct {
	simulationURL string
	client        *http.Client
}

// NewSimulationBridge creates a new bridge to Python simulation
func NewSimulationBridge(simulationURL string) *SimulationBridge {
	return &SimulationBridge{
		simulationURL: simulationURL,
		client: &http.Client{
			Timeout: 5 * time.Second,
		},
	}
}

// GetProposerFromSimulation calls your Python simulation to get proposer
func (sb *SimulationBridge) GetProposerFromSimulation(round uint64) (*ProposerNode, error) {
	url := fmt.Sprintf("%s/get_proposer?round=%d", sb.simulationURL, round)
	
	resp, err := sb.client.Get(url)
	if err != nil {
		return nil, fmt.Errorf("failed to call simulation: %w", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("simulation returned status %d", resp.StatusCode)
	}
	
	var proposer ProposerNode
	if err := json.NewDecoder(resp.Body).Decode(&proposer); err != nil {
		return nil, fmt.Errorf("failed to decode proposer: %w", err)
	}
	
	return &proposer, nil
}

// UpdateProposerAvailability updates proposer availability in simulation
func (sb *SimulationBridge) UpdateProposerAvailability(proposerID uint64, available bool) error {
	url := fmt.Sprintf("%s/update_proposer", sb.simulationURL)
	
	data := map[string]interface{}{
		"proposer_id": proposerID,
		"available":   available,
	}
	
	jsonData, err := json.Marshal(data)
	if err != nil {
		return fmt.Errorf("failed to marshal data: %w", err)
	}
	
	resp, err := sb.client.Post(url, "application/json", bytes.NewBuffer(jsonData))
	if err != nil {
		return fmt.Errorf("failed to update proposer: %w", err)
	}
	defer resp.Body.Close()
	
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("simulation returned status %d", resp.StatusCode)
	}
	
	return nil
}

// Import bytes package
import "bytes"
EOF

# Create P2S consensus engine
cat > consensus/p2s/consensus.go << 'EOF'
package p2s

import (
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/consensus"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/rpc"
)

// P2SConsensus implements consensus.Engine for P2S
type P2SConsensus struct {
	proposer *P2SProposer
	config   *P2SConfig
}

// NewP2SConsensus creates a new P2S consensus engine
func NewP2SConsensus(config *P2SConfig) *P2SConsensus {
	return &P2SConsensus{
		proposer: NewP2SProposer(config),
		config:   config,
	}
}

// Author implements consensus.Engine
func (p *P2SConsensus) Author(header *types.Header) (common.Address, error) {
	return header.Coinbase, nil
}

// VerifyHeader implements consensus.Engine
func (p *P2SConsensus) VerifyHeader(chain consensus.ChainHeaderReader, header *types.Header, seal bool) error {
	// TODO: Implement P2S-specific header verification
	return nil
}

// VerifyHeaders implements consensus.Engine
func (p *P2SConsensus) VerifyHeaders(chain consensus.ChainHeaderReader, headers []*types.Header, seals []bool) (chan<- struct{}, <-chan error) {
	// TODO: Implement batch header verification
	abort := make(chan struct{})
	results := make(chan error, len(headers))
	
	go func() {
		defer close(results)
		for i, header := range headers {
			select {
			case <-abort:
				return
			default:
				err := p.VerifyHeader(chain, header, seals[i])
				results <- err
			}
		}
	}()
	
	return abort, results
}

// Prepare implements consensus.Engine
func (p *P2SConsensus) Prepare(chain consensus.ChainHeaderReader, header *types.Header) error {
	// TODO: Implement P2S preparation logic
	return nil
}

// Finalize implements consensus.Engine
func (p *P2SConsensus) Finalize(chain consensus.ChainHeaderReader, header *types.Header, state *state.StateDB, txs []*types.Transaction, uncles []*types.Header, withdrawals []*types.Withdrawal) {
	// TODO: Implement P2S finalization logic
}

// FinalizeAndAssemble implements consensus.Engine
func (p *P2SConsensus) FinalizeAndAssemble(chain consensus.ChainHeaderReader, header *types.Header, state *state.StateDB, txs []*types.Transaction, uncles []*types.Header, receipts []*types.Receipt, withdrawals []*types.Withdrawal) (*types.Block, error) {
	// TODO: Implement P2S block assembly
	return nil, nil
}

// Seal implements consensus.Engine
func (p *P2SConsensus) Seal(chain consensus.ChainHeaderReader, block *types.Block, results chan<- *types.Block, stop <-chan struct{}) error {
	// TODO: Implement P2S sealing logic
	return nil
}

// SealHash implements consensus.Engine
func (p *P2SConsensus) SealHash(header *types.Header) common.Hash {
	// TODO: Implement P2S seal hash
	return common.Hash{}
}

// CalcDifficulty implements consensus.Engine
func (p *P2SConsensus) CalcDifficulty(chain consensus.ChainHeaderReader, time uint64, parent *types.Header) *big.Int {
	// TODO: Implement P2S difficulty calculation
	return big.NewInt(1)
}

// APIs implements consensus.Engine
func (p *P2SConsensus) APIs(chain consensus.ChainHeaderReader) []rpc.API {
	// TODO: Implement P2S APIs
	return []rpc.API{}
}

// Close implements consensus.Engine
func (p *P2SConsensus) Close() error {
	// TODO: Implement cleanup
	return nil
}

// Import required packages
import (
	"math/big"
	"github.com/ethereum/go-ethereum/core/state"
)
EOF

# Create genesis configuration
cat > p2s-genesis.json << 'EOF'
{
  "config": {
    "chainId": 12345,
    "homesteadBlock": 0,
    "eip150Block": 0,
    "eip155Block": 0,
    "byzantiumBlock": 0,
    "constantinopleBlock": 0,
    "petersburgBlock": 0,
    "istanbulBlock": 0,
    "berlinBlock": 0,
    "londonBlock": 0,
    "arrowGlacierBlock": 0,
    "grayGlacierBlock": 0,
    "shanghaiTime": 0,
    "cancunTime": 0,
    "p2sConfig": {
      "enabled": true,
      "merkleTreeDepth": 20,
      "proposerCount": 100,
      "simulationURL": "http://localhost:8000"
    }
  },
  "alloc": {
    "0x742d35Cc6634C0532925a3b8D0C4C4C4C4C4C4C4": {
      "balance": "1000000000000000000000000"
    }
  },
  "coinbase": "0x0000000000000000000000000000000000000000",
  "difficulty": "0x0",
  "extraData": "0x",
  "gasLimit": "0x1c9c380",
  "nonce": "0x0000000000000000",
  "timestamp": "0x0",
  "mixHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
  "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000"
}
EOF

# Create Python simulation server
cat > p2s_simulation_server.py << 'EOF'
#!/usr/bin/env python3
"""
P2S Simulation Server
Provides HTTP API for the Go Ethereum client to interact with P2S simulation
"""

from flask import Flask, request, jsonify
import json
import random
from typing import Dict, List, Optional

app = Flask(__name__)

# Mock proposer data
proposers = [
    {"id": i, "address": f"0x{i:040x}", "available": True, "stake": 1000, "round": 0}
    for i in range(100)
]

@app.route('/get_proposer', methods=['GET'])
def get_proposer():
    """Get proposer for a specific round"""
    round_num = int(request.args.get('round', 0))
    
    # Simple P2S logic: select available proposer
    available_proposers = [p for p in proposers if p['available']]
    
    if not available_proposers:
        return jsonify({"error": "No proposers available"}), 400
    
    # Select proposer (implement your P2S logic here)
    selected = random.choice(available_proposers)
    selected['round'] = round_num
    
    return jsonify(selected)

@app.route('/update_proposer', methods=['POST'])
def update_proposer():
    """Update proposer availability"""
    data = request.get_json()
    proposer_id = data.get('proposer_id')
    available = data.get('available')
    
    for proposer in proposers:
        if proposer['id'] == proposer_id:
            proposer['available'] = available
            return jsonify({"status": "success"})
    
    return jsonify({"error": "Proposer not found"}), 404

@app.route('/reveal_merkle_tree', methods=['POST'])
def reveal_merkle_tree():
    """Handle merkle tree revelation (Step 1 of P2S)"""
    data = request.get_json()
    user_id = data.get('user_id')
    merkle_proof = data.get('merkle_proof')
    
    # TODO: Implement merkle tree verification
    # This is where you'll integrate your existing P2S logic
    
    return jsonify({"status": "success", "message": "Merkle tree revealed"})

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "proposers": len(proposers)})

if __name__ == '__main__':
    print("🚀 Starting P2S Simulation Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("🔗 Endpoints:")
    print("   GET  /get_proposer?round=<round>")
    print("   POST /update_proposer")
    print("   POST /reveal_merkle_tree")
    print("   GET  /health")
    
    app.run(host='0.0.0.0', port=8000, debug=True)
EOF

# Create build script
cat > build_p2s.sh << 'EOF'
#!/bin/bash

echo "🔨 Building P2S-enabled Geth..."

# Build Geth
make geth

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📦 Binary location: ./build/bin/geth"
    echo ""
    echo "🚀 To run your P2S testnet:"
    echo "   ./build/bin/geth --datadir ./p2s-testnet --networkid 12345 --port 30303 --http --http.port 8545 --http.api \"eth,net,web3,personal,admin\" --mine --miner.threads 1"
else
    echo "❌ Build failed!"
    exit 1
fi
EOF

chmod +x build_p2s.sh

# Create test script
cat > test_p2s.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing P2S Implementation..."

# Start Python simulation server in background
echo "🐍 Starting Python simulation server..."
python3 p2s_simulation_server.py &
SIMULATION_PID=$!

# Wait for server to start
sleep 3

# Test simulation server
echo "🔍 Testing simulation server..."
curl -s http://localhost:8000/health | jq .

# Initialize testnet
echo "🌐 Initializing P2S testnet..."
./build/bin/geth --datadir ./p2s-testnet init p2s-genesis.json

# Start Geth node
echo "⛓️  Starting P2S-enabled Geth node..."
./build/bin/geth --datadir ./p2s-testnet --networkid 12345 --port 30303 --http --http.port 8545 --http.api "eth,net,web3,personal,admin" --mine --miner.threads 1 &
GETH_PID=$!

# Wait for node to start
sleep 5

# Test node
echo "🔍 Testing Geth node..."
curl -s -X POST -H "Content-Type: application/json" --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' http://localhost:8545 | jq .

echo "✅ Test completed!"
echo "🛑 To stop services:"
echo "   kill $SIMULATION_PID $GETH_PID"
EOF

chmod +x test_p2s.sh

# Build Geth
echo "🔨 Building Geth with P2S support..."
make geth

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🎉 P2S Ethereum fork setup complete!"
    echo ""
    echo "📁 Workspace: $WORKSPACE_DIR"
    echo "📦 Geth binary: $WORKSPACE_DIR/geth/build/bin/geth"
    echo ""
    echo "🚀 Next steps:"
    echo "   1. cd $WORKSPACE_DIR/geth"
    echo "   2. ./build_p2s.sh  # Build P2S-enabled Geth"
    echo "   3. python3 p2s_simulation_server.py  # Start simulation server"
    echo "   4. ./test_p2s.sh   # Test the implementation"
    echo ""
    echo "📚 See ETHEREUM_FORK_SETUP.md for detailed instructions"
else
    echo "❌ Build failed! Check the error messages above."
    exit 1
fi
