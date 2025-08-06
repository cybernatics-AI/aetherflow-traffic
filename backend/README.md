# AetherFlow Backend

🌐 **A comprehensive decentralized federated AI platform backend for intelligent traffic management, built on the Hedera network.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com)
[![Hedera](https://img.shields.io/badge/Hedera-HCS%2FHTS-purple.svg)](https://hedera.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 Overview

AetherFlow is a cutting-edge decentralized platform that combines federated AI, blockchain technology, and real-time traffic optimization to create intelligent transportation systems. Built on the Hedera network with HCS-10 OpenConvAI integration, it enables privacy-preserving data sharing, tokenized incentives, and autonomous traffic management.

### Key Features

- 🤖 **Federated AI Learning**: Privacy-preserving machine learning across distributed nodes
- 🚦 **Real-time Traffic Optimization**: AI-powered traffic light control and flow optimization
- 🔗 **Hedera Integration**: HCS for consensus, HTS for tokenomics, and secure data sharing
- 💰 **Tokenomics System**: AETHER tokens, Traffic NFTs, and congestion derivatives
- 🛡️ **Zero-Knowledge Proofs**: Privacy-preserving data validation and submission
- 📊 **Comprehensive Analytics**: Real-time monitoring and performance metrics
- 🌍 **Scalable Architecture**: Microservices-based design for global deployment

## 🏗️ Architecture

```
┌─────────────────┐     ┌───────────────────┐     ┌──────────────────┐
│  Data Sources   │────>│  Edge Processing  │────>│ Hedera Consensus │
│ (Vehicles/IoT)  │<────│ (ZK-Proofs + AI)  │     │ Layer (HCS/HTS)  │
└─────────────────┘     └───────────────────┘     └────────┬─────────┘
                                                           │
         ┌───────────────────────────────┐               │
         │ AI Optimization Engine        │<──────────────┘
         │ - Traffic light control       │
         │ - Route recommendations       │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │ Economic Layer                │
         │ - $AETHER rewards             │
         │ - NFT marketplace             │
         │ - Derivatives settlement      │
         └───────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)
- Hedera testnet account (for full functionality)

### Installation

1. **Clone and navigate to the backend directory:**
   ```bash
   cd /Users/a/Documents/Hedera/tangible/backend
   ```

2. **Activate virtual environment:**
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**
   ```bash
   python -m uvicorn src.aetherflow.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Access the API:**
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

### Running the Demo

```bash
python api_demo.py
```

## 📁 Project Structure

```
backend/
├── src/aetherflow/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database setup
│   │   └── logging.py         # Logging configuration
│   ├── models/
│   │   ├── vehicle_data.py    # Vehicle data model
│   │   ├── ai_agents.py       # AI agents model
│   │   ├── traffic_lights.py  # Traffic lights model
│   │   ├── traffic_nfts.py    # Traffic NFTs model
│   │   └── derivatives.py     # Derivatives model
│   ├── api/v1/
│   │   ├── router.py          # API router
│   │   └── endpoints/
│   │       ├── vehicle_data.py
│   │       ├── hcs10_communication.py
│   │       ├── traffic_optimization.py
│   │       ├── ai_agents.py
│   │       └── hedera_integration.py
│   ├── hedera/
│   │   └── client.py          # Hedera network client
│   └── hcs10/
│       └── agent_registry.py  # HCS-10 agent registry
├── tests/
│   ├── conftest.py            # Test configuration
│   ├── unit/
│   └── integration/
├── api_demo.py                # API demonstration script
├── requirements.txt
├── setup.py
├── pyproject.toml
├── pytest.ini
└── .env                       # Environment configuration
```

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=sqlite:///./aetherflow.db

# Hedera Network
HEDERA_NETWORK=testnet
HEDERA_ACCOUNT_ID=0.0.123456
HEDERA_PRIVATE_KEY=your_private_key_here

# HCS Topics
HCS_REGISTRY_TOPIC_ID=0.0.998877
HCS_INBOUND_TOPIC_ID=0.0.789102
HCS_OUTBOUND_TOPIC_ID=0.0.789103

# AI/ML
OPENAI_API_KEY=your_openai_api_key_here
FEDERATED_LEARNING_ENABLED=True

# Security
SECRET_KEY=your_secret_key_here
```

## 📚 API Endpoints

### Vehicle Data
- `POST /api/v1/vehicle-data/submit` - Submit vehicle data with ZK-proofs
- `GET /api/v1/vehicle-data/` - Retrieve vehicle data records
- `GET /api/v1/vehicle-data/{id}` - Get specific vehicle data
- `POST /api/v1/vehicle-data/{id}/validate` - Validate vehicle data

### HCS-10 Communication
- `POST /api/v1/hcs10/agents/register` - Register AI agent
- `GET /api/v1/hcs10/agents` - List registered agents
- `POST /api/v1/hcs10/connections/request` - Request agent connection
- `POST /api/v1/hcs10/messages/send` - Send message between agents
- `POST /api/v1/hcs10/transactions/request` - Request transaction approval

### Traffic Optimization
- `GET /api/v1/traffic/optimize-traffic` - Get optimized traffic settings
- `POST /api/v1/traffic/intersections` - Create intersection
- `GET /api/v1/traffic/intersections` - List intersections
- `POST /api/v1/traffic/intersections/{id}/control` - Control traffic light

### Hedera Integration
- `POST /api/v1/hedera/topics/create` - Create HCS topic
- `POST /api/v1/hedera/topics/submit-message` - Submit HCS message
- `GET /api/v1/hedera/account/balance` - Get account balance
- `POST /api/v1/hedera/transfer` - Transfer HBAR

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/aetherflow

# Run specific test file
pytest tests/unit/test_vehicle_data.py

# Run integration tests
pytest tests/integration/ -m integration
```

## 🔄 Development Workflow

1. **Code Formatting:**
   ```bash
   black src/ tests/
   ```

2. **Linting:**
   ```bash
   flake8 src/ tests/
   ```

3. **Type Checking:**
   ```bash
   mypy src/aetherflow
   ```

4. **Run Tests:**
   ```bash
   pytest
   ```

## 🌐 HCS-10 OpenConvAI Integration

The backend implements the HCS-10 OpenConvAI standard for AI agent communication:

- **Agent Registry**: Decentralized directory of AI agents
- **Topic-based Communication**: Secure message passing via HCS topics
- **Connection Management**: Peer-to-peer agent connections
- **Transaction Approval**: Safe transaction workflows with human approval

### Agent Types

- `traffic_optimizer`: Traffic flow optimization agents
- `data_validator`: Data quality and ZK-proof validation agents
- `reward_distributor`: Token reward distribution agents
- `federated_learner`: Federated learning coordination agents
- `market_maker`: NFT and derivatives market makers

## 💰 Tokenomics

- **$AETHER Token**: Utility token for data rewards and fees
- **Traffic NFTs**: Monetizable intersection ownership
- **Derivatives**: Congestion futures and traffic options
- **Revenue Sharing**: NFT owners earn from intersection fees

## 🛡️ Security Features

- **Zero-Knowledge Proofs**: Privacy-preserving data validation
- **Encrypted Data Storage**: Sensitive vehicle data encryption
- **Access Control**: Role-based permissions
- **Rate Limiting**: API abuse prevention
- **Input Validation**: Comprehensive data validation

## 📈 Performance Metrics

- **Target Throughput**: 10,000 TPS per city
- **Latency**: <200ms for HCS message finality
- **Scalability**: Multi-city deployment ready
- **Availability**: 99.9% uptime target

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: [API Docs](http://localhost:8000/docs)
- **Issues**: GitHub Issues
- **Community**: AetherFlow Discord

## 🗺️ Roadmap

### Phase 1: Core Protocol (Q4 2024)
- ✅ SQLite database and HCS topic initialization
- ✅ $AETHER token and test data submission
- ✅ Federated AI MVP with synthetic data
- ✅ HCS-10 OpenConvAI integration

### Phase 2: City Integration (Q1 2025)
- 🔄 Real vehicle data via OBD-II and Android SDK
- 🔄 Traffic NFTs for 100 intersections
- 🔄 ZK-proof validation implementation
- 🔄 Live traffic optimization in pilot city

### Phase 3: Global Scale (Q3 2025)
- 📅 Congestion derivatives with Chainlink
- 📅 Carbon credits via Verra registry
- 📅 Sharding optimization for 10,000 TPS
- 📅 Multi-city deployment

---

**Built with ❤️ for the future of urban mobility**
