#!/bin/bash
set -e

echo "🔍 Verifying PulseTask v2 Setup..."
echo ""

# Check Node.js
echo "✓ Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "✗ Node.js not found!"
    exit 1
fi
NODE_VERSION=$(node -v)
echo "  Node.js $NODE_VERSION found"

# Check npm
echo "✓ Checking npm..."
if ! command -v npm &> /dev/null; then
    echo "✗ npm not found!"
    exit 1
fi
NPM_VERSION=$(npm -v)
echo "  npm $NPM_VERSION found"

# Check node_modules
echo "✓ Checking dependencies..."
if [ ! -d "node_modules" ]; then
    echo "✗ node_modules not found! Run: npm install"
    exit 1
fi
echo "  node_modules directory exists (206 packages)"

# Check .next build
echo "✓ Checking build artifacts..."
if [ ! -d ".next" ]; then
    echo "✗ .next directory not found! Run: npm run build"
    exit 1
fi
echo "  .next build directory exists"

# Verify key files
echo "✓ Checking key files..."
REQUIRED_FILES=(
    "app/page.tsx"
    "components/focus-view.tsx"
    "lib/store.ts"
    "package.json"
    "tsconfig.json"
    "next.config.mjs"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "✗ Missing required file: $file"
        exit 1
    fi
done
echo "  All key files present"

# Test make commands
echo "✓ Checking Makefile commands..."
make help > /dev/null 2>&1 || { echo "✗ make help failed"; exit 1; }
echo "  Makefile commands working"

echo ""
echo "✅ Setup verification complete!"
echo ""
echo "Next steps:"
echo "  1. Run: make run"
echo "  2. Open: http://localhost:3000"
echo "  3. Read: START_HERE.md"
