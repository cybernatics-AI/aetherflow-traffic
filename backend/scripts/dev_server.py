#!/usr/bin/env python3
"""
Development Server Script for AetherFlow Backend
"""

import sys
import os
import subprocess
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def run_dev_server():
    """Run the development server with hot reload"""
    
    print("🚀 Starting AetherFlow Backend Development Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔄 Hot reload enabled - server will restart on code changes")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 60)
    
    # Change to the backend directory
    backend_dir = Path(__file__).parent.parent
    os.chdir(backend_dir)
    
    # Run uvicorn with hot reload
    cmd = [
        "uvicorn",
        "src.aetherflow.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "--reload-dir", "src",
        "--log-level", "info"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ uvicorn not found. Please install it with: pip install uvicorn")
        sys.exit(1)


def main():
    """Main function"""
    
    # Check if we're in the right directory
    backend_dir = Path(__file__).parent.parent
    if not (backend_dir / "src" / "aetherflow").exists():
        print("❌ Error: This script must be run from the backend directory")
        sys.exit(1)
    
    # Check if .env file exists
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("⚠️  Warning: .env file not found. Creating a basic one...")
        
        # Create basic .env file
        env_content = """# AetherFlow Backend Configuration
# Database
DATABASE_URL=sqlite+aiosqlite:///./aetherflow.db

# Hedera Configuration
HEDERA_NETWORK=testnet
HEDERA_ACCOUNT_ID=0.0.123456
HEDERA_PRIVATE_KEY=your_private_key_here

# HCS Topics
HCS_VEHICLE_DATA_TOPIC_ID=0.0.123456
HCS_AGENT_REGISTRY_TOPIC_ID=0.0.123457

# Security
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256

# Logging
LOG_LEVEL=INFO

# Development
ENVIRONMENT=development
DEBUG=true
"""
        
        with open(env_file, "w") as f:
            f.write(env_content)
        
        print(f"✅ Created basic .env file at {env_file}")
        print("⚠️  Please update the configuration values before starting the server")
    
    run_dev_server()


if __name__ == "__main__":
    main()
