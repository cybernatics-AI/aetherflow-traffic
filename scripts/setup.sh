#!/bin/bash

# AetherFlow Setup Script
# This script sets up the development environment for AetherFlow

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up AetherFlow development environment...${NC}"

# Setup backend
echo -e "${YELLOW}Setting up backend environment...${NC}"
cd "$(dirname "$0")/../backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "Installing backend dependencies..."
source venv/bin/activate
pip install -r requirements.txt
pip install -e .

# Setup frontend
echo -e "${YELLOW}Setting up frontend environment...${NC}"
cd "$(dirname "$0")/../frontend"

# Install frontend dependencies
echo "Installing frontend dependencies..."
npm install

# Setup smart contracts
echo -e "${YELLOW}Setting up smart contracts environment...${NC}"
cd "$(dirname "$0")/../backend/contracts"

# Install contract dependencies
echo "Installing smart contract dependencies..."
npm install

echo -e "${GREEN}Setup complete! You can now run the development servers:${NC}"
echo -e "  * Backend: cd backend && source venv/bin/activate && uvicorn aetherflow.main:app --reload"
echo -e "  * Frontend: cd frontend && npm run dev"
echo -e "  * Smart Contracts: cd backend/contracts && npx hardhat compile"
