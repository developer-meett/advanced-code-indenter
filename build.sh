#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# 2. Install Node.js and Prettier
echo "Setting up Node.js and installing Prettier..."
export NVM_DIR="$HOME/.nvm"
# Source the nvm script and then immediately use it
. "$NVM_DIR/nvm.sh" && nvm install 18 && npm install -g prettier

# 3. Install System Dependencies
echo "Installing clang-format..."
apt-get update && apt-get install -y clang-format

echo "Build script completed successfully!"