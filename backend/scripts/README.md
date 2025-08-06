# AetherFlow Backend Scripts

This directory contains utility scripts for managing the AetherFlow backend system.

## Available Scripts

### 🗄️ Database Management

#### `setup_database.py`
Sets up the database schema and optionally seeds sample data.

```bash
# Create database tables
python scripts/setup_database.py --create

# Drop existing tables and recreate (CAUTION: Data loss!)
python scripts/setup_database.py --drop --create

# Create tables and seed with sample data
python scripts/setup_database.py --create --seed
```

### 🚀 Development Server

#### `dev_server.py`
Starts the development server with hot reload and automatic configuration.

```bash
# Start development server
python scripts/dev_server.py

# Server will be available at:
# - API: http://localhost:8000
# - Docs: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

Features:
- Automatic .env file creation if missing
- Hot reload on code changes
- Comprehensive logging
- Development-friendly error messages

### 🧪 Testing

#### `run_tests.py`
Comprehensive test runner with multiple options.

```bash
# Run all tests
python scripts/run_tests.py

# Run only unit tests
python scripts/run_tests.py unit

# Run with coverage report
python scripts/run_tests.py --coverage

# Run with verbose output
python scripts/run_tests.py --verbose

# Run linting and code quality checks
python scripts/run_tests.py --lint

# Run security vulnerability checks
python scripts/run_tests.py --security

# Run all checks (tests + linting + security)
python scripts/run_tests.py --all-checks
```

### 🚀 Deployment

#### `deploy.py`
Production deployment script with comprehensive checks and rollback capabilities.

```bash
# Deploy to staging
python scripts/deploy.py staging

# Deploy to production
python scripts/deploy.py production

# Deploy with custom options
python scripts/deploy.py production --skip-checks --skip-tests
```

Deployment process includes:
- Pre-deployment checks (tests, linting)
- Database backup
- Dependency installation
- Database migrations
- Application build
- Service deployment
- Health checks
- Post-deployment tests

### 📊 Data Management

#### `migrate_data.py`
Data import/export and migration utilities.

```bash
# Import vehicle data from CSV
python scripts/migrate_data.py import --vehicle-csv data/vehicle_data.csv

# Import traffic lights from JSON
python scripts/migrate_data.py import --traffic-json data/traffic_lights.json

# Export vehicle data to CSV (last 30 days)
python scripts/migrate_data.py export --vehicle-csv output/vehicle_export.csv --days 30

# Migrate from legacy database
python scripts/migrate_data.py import --legacy-db legacy/old_database.db

# Data maintenance
python scripts/migrate_data.py maintenance --cleanup 90  # Delete data older than 90 days
python scripts/migrate_data.py maintenance --validate    # Validate data integrity
python scripts/migrate_data.py maintenance --generate-samples 1000  # Generate test data
```

### 📈 Monitoring

#### `monitor.py`
System monitoring and health checks.

```bash
# Generate single monitoring report
python scripts/monitor.py --mode report

# Save report to file
python scripts/monitor.py --mode report --output monitoring_report.json

# Run continuous monitoring (every 60 seconds)
python scripts/monitor.py --mode continuous --interval 60
```

Monitoring includes:
- API health checks
- Database connectivity
- Data freshness validation
- System resource usage
- Hedera network connectivity
- Endpoint availability

## Script Dependencies

Most scripts require the following Python packages:

```bash
# Core dependencies (from requirements.txt)
pip install -r requirements.txt

# Additional monitoring dependencies
pip install psutil requests

# Development dependencies
pip install black isort flake8 mypy safety
```

## Environment Setup

Before running scripts, ensure you have:

1. **Python Environment**: Python 3.8+ with virtual environment activated
2. **Environment Variables**: `.env` file configured (see `.env.example`)
3. **Database**: SQLite database file or connection string
4. **Dependencies**: All required packages installed

## Common Usage Patterns

### Initial Setup
```bash
# 1. Set up database
python scripts/setup_database.py --create --seed

# 2. Run tests to verify setup
python scripts/run_tests.py

# 3. Start development server
python scripts/dev_server.py
```

### Development Workflow
```bash
# Run tests before committing
python scripts/run_tests.py --all-checks

# Generate sample data for testing
python scripts/migrate_data.py maintenance --generate-samples 500

# Monitor system during development
python scripts/monitor.py --mode continuous --interval 30
```

### Production Deployment
```bash
# 1. Run comprehensive checks
python scripts/run_tests.py --all-checks

# 2. Deploy to staging first
python scripts/deploy.py staging

# 3. Run monitoring to verify
python scripts/monitor.py --mode report

# 4. Deploy to production
python scripts/deploy.py production
```

### Data Management
```bash
# Regular maintenance
python scripts/migrate_data.py maintenance --validate
python scripts/migrate_data.py maintenance --cleanup 60

# Backup data
python scripts/migrate_data.py export --vehicle-csv backups/vehicle_backup_$(date +%Y%m%d).csv

# Import new data
python scripts/migrate_data.py import --vehicle-csv new_data/vehicle_data.csv
```

## Script Configuration

### Environment Variables
Scripts use the following environment variables (from `.env`):

- `DATABASE_URL`: Database connection string
- `HEDERA_NETWORK`: Hedera network (testnet/mainnet)
- `HEDERA_ACCOUNT_ID`: Hedera account ID
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

### Configuration Files
Some scripts support configuration files:

- `deployment/staging.json`: Staging deployment config
- `deployment/production.json`: Production deployment config
- `monitoring/config.json`: Monitoring configuration

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running scripts from the backend root directory
2. **Database Errors**: Check DATABASE_URL in .env file
3. **Permission Errors**: Ensure proper file permissions for log and data directories
4. **Network Errors**: Check Hedera network configuration and connectivity

### Debug Mode
Most scripts support verbose logging:

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python scripts/script_name.py
```

### Getting Help
Each script provides help information:

```bash
python scripts/script_name.py --help
```

## Security Considerations

- **Never commit sensitive data** like private keys or passwords
- **Use environment variables** for configuration
- **Regularly update dependencies** to patch security vulnerabilities
- **Run security checks** before deployment
- **Monitor system logs** for suspicious activity

## Contributing

When adding new scripts:

1. Follow the existing naming convention
2. Include comprehensive help text and argument parsing
3. Add logging and error handling
4. Update this README with usage instructions
5. Test scripts in different environments

## Support

For issues with scripts:

1. Check the logs for detailed error messages
2. Verify environment configuration
3. Ensure all dependencies are installed
4. Consult the main project documentation
5. Open an issue with detailed error information
