#!/usr/bin/env python3
"""
Deployment Script for AetherFlow Backend
"""

import sys
import os
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class DeploymentManager:
    """Manages deployment process"""
    
    def __init__(self, environment="staging"):
        self.environment = environment
        self.backend_dir = Path(__file__).parent.parent
        self.deployment_config = self.load_deployment_config()
        
    def load_deployment_config(self):
        """Load deployment configuration"""
        
        config_file = self.backend_dir / "deployment" / f"{self.environment}.json"
        
        if config_file.exists():
            with open(config_file) as f:
                return json.load(f)
        
        # Default configuration
        return {
            "environment": self.environment,
            "health_check_url": "http://localhost:8000/health",
            "pre_deploy_checks": True,
            "run_migrations": True,
            "backup_database": True,
            "restart_services": True,
            "post_deploy_tests": True
        }
    
    def log(self, message, level="INFO"):
        """Log deployment messages"""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def run_command(self, cmd, description="", check=True):
        """Run a command and log the result"""
        
        if description:
            self.log(f"Running: {description}")
        
        self.log(f"Command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.backend_dir,
                check=check,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                self.log(f"Output: {result.stdout.strip()}")
            
            return result
            
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {e}", "ERROR")
            if e.stdout:
                self.log(f"Stdout: {e.stdout}", "ERROR")
            if e.stderr:
                self.log(f"Stderr: {e.stderr}", "ERROR")
            raise
    
    def pre_deploy_checks(self):
        """Run pre-deployment checks"""
        
        self.log("🔍 Running pre-deployment checks...")
        
        # Check if required files exist
        required_files = [
            "src/aetherflow/main.py",
            "requirements.txt",
            ".env"
        ]
        
        for file_path in required_files:
            full_path = self.backend_dir / file_path
            if not full_path.exists():
                raise FileNotFoundError(f"Required file not found: {file_path}")
        
        # Run tests
        self.log("Running tests...")
        self.run_command([
            "python", "-m", "pytest", "tests/", "-x", "--tb=short"
        ], "Running test suite")
        
        # Check code quality
        try:
            self.run_command([
                "flake8", "src/", "--max-line-length=100", "--ignore=E203,W503"
            ], "Code quality check", check=False)
        except subprocess.CalledProcessError:
            self.log("Code quality check failed, but continuing...", "WARNING")
        
        self.log("✅ Pre-deployment checks completed")
    
    def backup_database(self):
        """Backup database before deployment"""
        
        if not self.deployment_config.get("backup_database", True):
            return
        
        self.log("💾 Creating database backup...")
        
        backup_dir = self.backend_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"aetherflow_backup_{timestamp}.db"
        
        # For SQLite, just copy the file
        db_file = self.backend_dir / "aetherflow.db"
        if db_file.exists():
            import shutil
            shutil.copy2(db_file, backup_file)
            self.log(f"Database backed up to: {backup_file}")
        else:
            self.log("No database file found to backup", "WARNING")
    
    def run_migrations(self):
        """Run database migrations"""
        
        if not self.deployment_config.get("run_migrations", True):
            return
        
        self.log("🗄️  Running database migrations...")
        
        # Run the database setup script
        self.run_command([
            "python", "scripts/setup_database.py", "--create"
        ], "Database migrations")
        
        self.log("✅ Database migrations completed")
    
    def install_dependencies(self):
        """Install/update dependencies"""
        
        self.log("📦 Installing dependencies...")
        
        self.run_command([
            "pip", "install", "-r", "requirements.txt", "--upgrade"
        ], "Installing Python dependencies")
        
        self.log("✅ Dependencies installed")
    
    def build_application(self):
        """Build the application if needed"""
        
        self.log("🔨 Building application...")
        
        # For Python applications, this might involve:
        # - Compiling assets
        # - Generating documentation
        # - Creating distribution packages
        
        # Generate API documentation
        try:
            self.run_command([
                "python", "-c",
                "import sys; sys.path.insert(0, 'src'); "
                "from aetherflow.main import app; "
                "import json; "
                "with open('api_schema.json', 'w') as f: "
                "json.dump(app.openapi(), f, indent=2)"
            ], "Generating API schema", check=False)
        except subprocess.CalledProcessError:
            self.log("Failed to generate API schema", "WARNING")
        
        self.log("✅ Application build completed")
    
    def deploy_application(self):
        """Deploy the application"""
        
        self.log("🚀 Deploying application...")
        
        if self.environment == "production":
            # Production deployment with gunicorn
            self.log("Starting production server with gunicorn...")
            
            # Create systemd service file if needed
            self.create_systemd_service()
            
            # Start/restart the service
            try:
                self.run_command([
                    "sudo", "systemctl", "restart", "aetherflow-backend"
                ], "Restarting systemd service", check=False)
            except subprocess.CalledProcessError:
                self.log("Failed to restart systemd service, trying direct start...", "WARNING")
                self.start_production_server()
        
        elif self.environment == "staging":
            # Staging deployment
            self.log("Starting staging server...")
            self.start_staging_server()
        
        else:
            # Development deployment
            self.log("Starting development server...")
            self.start_development_server()
        
        self.log("✅ Application deployed")
    
    def create_systemd_service(self):
        """Create systemd service file for production"""
        
        service_content = f"""[Unit]
Description=AetherFlow Backend API
After=network.target

[Service]
Type=exec
User=aetherflow
Group=aetherflow
WorkingDirectory={self.backend_dir}
Environment=PATH={self.backend_dir}/venv/bin
ExecStart={self.backend_dir}/venv/bin/gunicorn src.aetherflow.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = Path("/etc/systemd/system/aetherflow-backend.service")
        
        try:
            with open(service_file, "w") as f:
                f.write(service_content)
            
            self.run_command([
                "sudo", "systemctl", "daemon-reload"
            ], "Reloading systemd")
            
            self.run_command([
                "sudo", "systemctl", "enable", "aetherflow-backend"
            ], "Enabling systemd service")
            
        except PermissionError:
            self.log("Cannot create systemd service (no sudo access)", "WARNING")
    
    def start_production_server(self):
        """Start production server with gunicorn"""
        
        cmd = [
            "gunicorn",
            "src.aetherflow.main:app",
            "-w", "4",
            "-k", "uvicorn.workers.UvicornWorker",
            "-b", "0.0.0.0:8000",
            "--daemon",
            "--pid", "aetherflow.pid",
            "--access-logfile", "logs/access.log",
            "--error-logfile", "logs/error.log"
        ]
        
        # Create logs directory
        (self.backend_dir / "logs").mkdir(exist_ok=True)
        
        self.run_command(cmd, "Starting production server")
    
    def start_staging_server(self):
        """Start staging server"""
        
        cmd = [
            "uvicorn",
            "src.aetherflow.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "2"
        ]
        
        self.run_command(cmd, "Starting staging server")
    
    def start_development_server(self):
        """Start development server"""
        
        cmd = [
            "uvicorn",
            "src.aetherflow.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        self.run_command(cmd, "Starting development server")
    
    def health_check(self):
        """Perform health check after deployment"""
        
        self.log("🏥 Performing health check...")
        
        import requests
        import time
        
        health_url = self.deployment_config.get("health_check_url", "http://localhost:8000/health")
        max_attempts = 30
        
        for attempt in range(max_attempts):
            try:
                response = requests.get(health_url, timeout=5)
                if response.status_code == 200:
                    self.log("✅ Health check passed")
                    return True
                else:
                    self.log(f"Health check failed: HTTP {response.status_code}")
            
            except requests.RequestException as e:
                self.log(f"Health check attempt {attempt + 1}/{max_attempts} failed: {e}")
            
            if attempt < max_attempts - 1:
                time.sleep(2)
        
        raise Exception("Health check failed after all attempts")
    
    def post_deploy_tests(self):
        """Run post-deployment tests"""
        
        if not self.deployment_config.get("post_deploy_tests", True):
            return
        
        self.log("🧪 Running post-deployment tests...")
        
        # Run integration tests
        try:
            self.run_command([
                "python", "-m", "pytest", "tests/integration/", "-v"
            ], "Post-deployment integration tests", check=False)
        except subprocess.CalledProcessError:
            self.log("Some post-deployment tests failed", "WARNING")
        
        self.log("✅ Post-deployment tests completed")
    
    def deploy(self):
        """Main deployment process"""
        
        self.log(f"🚀 Starting deployment to {self.environment}")
        
        try:
            if self.deployment_config.get("pre_deploy_checks", True):
                self.pre_deploy_checks()
            
            self.backup_database()
            self.install_dependencies()
            self.run_migrations()
            self.build_application()
            self.deploy_application()
            
            # Give the server time to start
            time.sleep(5)
            
            self.health_check()
            self.post_deploy_tests()
            
            self.log("🎉 Deployment completed successfully!")
            
        except Exception as e:
            self.log(f"❌ Deployment failed: {e}", "ERROR")
            raise


def main():
    """Main function"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy AetherFlow Backend")
    parser.add_argument(
        "environment",
        nargs="?",
        default="staging",
        choices=["development", "staging", "production"],
        help="Deployment environment"
    )
    parser.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip pre-deployment checks"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip post-deployment tests"
    )
    
    args = parser.parse_args()
    
    # Create deployment manager
    deployment = DeploymentManager(args.environment)
    
    # Override configuration based on arguments
    if args.skip_checks:
        deployment.deployment_config["pre_deploy_checks"] = False
    
    if args.skip_tests:
        deployment.deployment_config["post_deploy_tests"] = False
    
    # Run deployment
    try:
        deployment.deploy()
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
