#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies from requirements.txt
pip install -r requirements.txt

# Install Node.js and the Prettier code formatter
source ~/.nvm/nvm.sh
nvm install 18
npm install -g prettier

# Install the clang-format tool for C++, Java, etc.
apt-get update && apt-get install -y clang-format