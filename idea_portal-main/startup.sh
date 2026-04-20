#!/bin/bash
# CCEW Portal Startup Script
# This script sets up paths and starts the Flask development server

set -e  # Exit on error

echo "🚀 Starting CCEW Idea Portal..."

# Check if virtual environment is active
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Change to backend directory (where app.py is located)
cd backend

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Ensure database directory exists
echo "💾 Preparing database..."
mkdir -p generated_reports

# Start Flask development server
echo "✅ Starting Flask on port 8000..."
echo "🌐 Access at: http://localhost:8000"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

python app.py
