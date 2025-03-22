#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Display current Python version and environment
echo "Using Python: $(which python)"
echo "Python version: $(python --version)"
echo "Virtual environment: $VIRTUAL_ENV"

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Error: .env file not found. Please create one with the required API keys."
  exit 1
fi

# Verify GEMINI_API_KEY is set
if ! grep -q "GEMINI_API_KEY=" .env || grep -q "GEMINI_API_KEY=$" .env || grep -q "GEMINI_API_KEY=your_" .env; then
  echo "Error: GEMINI_API_KEY is not properly set in the .env file."
  echo "Please set a valid API key in the .env file."
  exit 1
fi

# Install requirements with progress indicator
echo "Installing backend requirements..."
pip install -r backend/requirements.txt | while read -r line; do
  echo "  $line"
done

echo "Installing streamlit app requirements..."
pip install -r streamlit_app/requirements.txt | while read -r line; do
  echo "  $line"
done

# Check for AI models and resources
echo "Setting up AI models..."
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')" || echo "Sentence transformer model will be downloaded on first use"

# Create necessary directories
echo "Creating directory structure..."
mkdir -p backend/uploads
mkdir -p backend/contract_templates
mkdir -p backend/vector_db
mkdir -p backend/knowledge_base

# Copy any template documents for the knowledge base
echo "Setting up legal knowledge base..."
if [ -d "legal_templates" ]; then
  cp -r legal_templates/* backend/contract_templates/ 2>/dev/null || echo "No template files found"
fi

# Export Python path to include project root
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start the backend server in the background
echo "Starting backend server..."
cd backend
python main.py > backend_log.txt 2>&1 &
BACKEND_PID=$!
cd ..

# Give backend time to start and initialize AI models
echo "Waiting for backend to initialize (this might take a moment as AI models load)..."
sleep 7  # Increased wait time for AI model initialization

# Check if backend started correctly
echo "Checking backend health..."
if ! curl -s http://localhost:8000/healthcheck > /dev/null; then
  echo "Error: Backend failed to start properly."
  echo "Check backend/backend_log.txt for details."
  echo "Here are the last few lines of the log:"
  tail -n 20 backend/backend_log.txt
  kill $BACKEND_PID
  exit 1
else
  echo "✅ Backend started successfully!"
  echo "🤖 Advanced Legal AI Agent is now active"
fi

# Start the Streamlit app
echo "Starting Streamlit app..."
cd streamlit_app
streamlit run app.py

# When Streamlit app is closed, also close the backend server
echo "Shutting down backend server (PID: $BACKEND_PID)..."
kill $BACKEND_PID 