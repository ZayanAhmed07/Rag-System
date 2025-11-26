#!/bin/bash

echo "🚀 Setting up RAG System..."

# Backend setup
echo "📦 Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if not exists
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Please edit backend/.env with your API keys"
fi

# Frontend setup
echo "🎨 Setting up frontend..."
cd ../frontend
npm install

# Create data directories
echo "📁 Creating data directories..."
cd ..
mkdir -p data/{raw,processed,test_documents}
mkdir -p models
mkdir -p eval_results

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your API keys"
echo "2. Run: cd backend && python main.py"
echo "3. In another terminal: cd frontend && npm run dev"
