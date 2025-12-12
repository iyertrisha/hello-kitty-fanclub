#!/bin/bash
# Shell script to start WhatsApp Bot
# Usage: ./start.sh

echo "🚀 Starting WhatsApp Debt Tracking Bot..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "Download from: https://nodejs.org/"
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f ".env.template" ]; then
        cp .env.template .env
        echo "✅ Created .env file. Please edit it with your configuration."
    else
        echo "❌ .env.template not found"
        exit 1
    fi
fi

# Start the bot
echo "✅ Starting bot..."
node index.js

