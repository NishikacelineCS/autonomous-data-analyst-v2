#!/usr/bin/env bash
# =============================================================================
# scripts/setup.sh — Developer Environment Setup Script
# =============================================================================
# Run this once when cloning the project for the first time.
# Usage:  chmod +x scripts/setup.sh && ./scripts/setup.sh
# =============================================================================

set -e  # Exit immediately on any error

# ── Colours for output ─────────────────────────────────────────────────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Colour

echo -e "${GREEN}============================================================${NC}"
echo -e "${GREEN}  Autonomous Multi-Agent Data Analyst — Environment Setup   ${NC}"
echo -e "${GREEN}============================================================${NC}\n"

# ── 1. Check Python Version ────────────────────────────────────────────────────
echo -e "${YELLOW}[1/6] Checking Python version...${NC}"
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"
if python3 -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'" 2>/dev/null; then
    echo -e "${GREEN}✅ Python ${PYTHON_VERSION} — OK${NC}"
else
    echo -e "${RED}❌ Python 3.11+ is required. You have ${PYTHON_VERSION}.${NC}"
    echo "   Install from: https://www.python.org/downloads/"
    exit 1
fi

# ── 2. Create Virtual Environment ─────────────────────────────────────────────
echo -e "\n${YELLOW}[2/6] Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created at ./venv${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# ── 3. Install Dependencies ────────────────────────────────────────────────────
echo -e "\n${YELLOW}[3/6] Installing Python dependencies...${NC}"
pip install --upgrade pip --quiet
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# ── 4. Configure Environment Variables ────────────────────────────────────────
echo -e "\n${YELLOW}[4/6] Configuring environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env from template${NC}"
    echo -e "${YELLOW}⚠️  ACTION REQUIRED: Open .env and add your API keys:${NC}"
    echo "   - ANTHROPIC_API_KEY (get from https://console.anthropic.com)"
    echo "   - SECRET_KEY (generate with: python -c \"import secrets; print(secrets.token_hex(32))\")"
else
    echo -e "${GREEN}✅ .env already exists${NC}"
fi

# ── 5. Create Required Data Directories ───────────────────────────────────────
echo -e "\n${YELLOW}[5/6] Creating data directories...${NC}"
mkdir -p data/uploads data/sessions data/chroma_db
echo -e "${GREEN}✅ Data directories ready${NC}"

# ── 6. Git Initialization ─────────────────────────────────────────────────────
echo -e "\n${YELLOW}[6/6] Initializing Git repository...${NC}"
if [ ! -d ".git" ]; then
    git init
    git add .
    git commit -m "chore: initial project scaffold"
    echo -e "${GREEN}✅ Git repository initialized with initial commit${NC}"
else
    echo -e "${GREEN}✅ Git repository already exists${NC}"
fi

# ── Summary ────────────────────────────────────────────────────────────────────
echo -e "\n${GREEN}============================================================${NC}"
echo -e "${GREEN}  ✅ Setup complete! Next steps:                            ${NC}"
echo -e "${GREEN}============================================================${NC}"
echo ""
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Edit your .env file with your API keys:"
echo "     nano .env  (or open in your editor)"
echo ""
echo "  3. Start the backend server:"
echo "     cd backend && uvicorn app.main:app --reload --port 8000"
echo ""
echo "  4. In a new terminal, start the frontend:"
echo "     cd frontend && streamlit run app.py"
echo ""
echo "  5. Open your browser:"
echo "     Frontend: http://localhost:8501"
echo "     API Docs: http://localhost:8000/docs"
echo ""