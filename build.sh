#!/usr/bin/env bash
# Exit on error
set -o errexit

# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Node.js and Prettier
#    This section is updated to be more robust.
#    It uses Render's built-in environment variables to find and set up Node.js.
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

nvm install 18
npm install -g prettier

# 3. Install System Dependencies
apt-get update && apt-get install -y clang-format