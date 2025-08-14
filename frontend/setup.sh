#!/bin/bash

echo "🚀 Setting up Mockintosh Management UI (Vue.js)"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js version 16+ is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Node.js version: $(node -v)"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🎉 Setup complete! You can now:"
echo ""
echo "  • Start development server: npm run dev"
echo "  • Build for production: npm run build"
echo "  • Preview production build: npm run preview"
echo ""
echo "📖 See README.md for more information"
echo ""
echo "⚠️  Make sure your Mockintosh server is running on http://localhost:8000"
echo "   The Vue.js app will proxy API requests to it automatically."
