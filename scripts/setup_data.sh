#!/bin/bash
#
# Safe Companions Test Data Management Script
# 
# This script provides an easy interface to manage test data in the Safe Companions database
# running in Docker containers.
#
# Usage Examples:
#   ./scripts/setup_data.sh                           # Interactive mode
#   ./scripts/setup_data.sh --clear-all               # Clear all and recreate
#   ./scripts/setup_data.sh --production              # Production-safe mode
#   ./scripts/setup_data.sh --clear-all --force       # Force clear without confirmation
#

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[SETUP]${NC} $1"
}

# Check if Docker is running
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    print_error "Docker daemon is not running"
    exit 1
fi

# Check if the container is running
CONTAINER_NAME="safe-companions-web"
if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    print_error "Container '${CONTAINER_NAME}' is not running"
    print_info "Start the application with: docker compose up -d"
    exit 1
fi

print_header "Safe Companions Test Data Setup"
print_info "Running test data setup in container: ${CONTAINER_NAME}"

# Execute the Python script in the container with all passed arguments
docker exec -it "${CONTAINER_NAME}" python scripts/setup/setup_test_data.py "$@"

# Check exit status
if [ $? -eq 0 ]; then
    print_info "Test data setup completed successfully"
    print_warning "Remember: Test credentials are 'password123' for all users"
else
    print_error "Test data setup encountered an error"
    exit 1
fi
