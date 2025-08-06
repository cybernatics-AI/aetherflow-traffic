#!/bin/bash
"""
Make all Python scripts executable
"""

echo "🔧 Making AetherFlow backend scripts executable..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make all Python scripts in the scripts directory executable
chmod +x "$SCRIPT_DIR"/*.py

# List of scripts to make executable
SCRIPTS=(
    "setup_database.py"
    "dev_server.py"
    "run_tests.py"
    "deploy.py"
    "migrate_data.py"
    "monitor.py"
)

echo "📝 Setting executable permissions for scripts:"

for script in "${SCRIPTS[@]}"; do
    if [ -f "$SCRIPT_DIR/$script" ]; then
        chmod +x "$SCRIPT_DIR/$script"
        echo "  ✅ $script"
    else
        echo "  ❌ $script (not found)"
    fi
done

# Make this script executable too
chmod +x "$SCRIPT_DIR/make_executable.sh"

echo ""
echo "🎉 Script permissions updated!"
echo ""
echo "You can now run scripts directly:"
echo "  ./scripts/dev_server.py"
echo "  ./scripts/run_tests.py"
echo "  ./scripts/setup_database.py --create --seed"
echo ""
echo "Or with python:"
echo "  python scripts/dev_server.py"
echo "  python scripts/run_tests.py"
echo "  python scripts/setup_database.py --create --seed"
