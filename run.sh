#!/bin/bash
# =============================================================================
# APEX Engine - Startup Script (Linux/macOS)
# =============================================================================
# Usage:
#   ./run.sh          - Start the web UI (default)
#   ./run.sh --cli    - Run CLI mode
#   ./run.sh --demo   - Run demonstration mode
#   ./run.sh --help   - Show all options
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}     █████╗ ██████╗ ███████╗██╗  ██╗    ███████╗███╗   ██╗   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ██╔══██╗██╔══██╗██╔════╝╚██╗██╔╝    ██╔════╝████╗  ██║   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ███████║██████╔╝█████╗   ╚███╔╝     █████╗  ██╔██╗ ██║   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ██╔══██║██╔═══╝ ██╔══╝   ██╔██╗     ██╔══╝  ██║╚██╗██║   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ██║  ██║██║     ███████╗██╔╝ ██╗    ███████╗██║ ╚████║   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═══╝   ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}                                                              ${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}    Autonomous Aural Architectures for Algorithmic Rap        ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON=python3
    elif command -v python &> /dev/null; then
        PYTHON=python
    else
        echo -e "${RED}Error: Python not found. Please install Python 3.11+${NC}"
        exit 1
    fi
    
    VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    MAJOR=$($PYTHON -c "import sys; print(sys.version_info.major)")
    MINOR=$($PYTHON -c "import sys; print(sys.version_info.minor)")
    
    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
        echo -e "${YELLOW}Warning: Python $VERSION detected. Python 3.11+ is recommended.${NC}"
    else
        echo -e "${GREEN}Python $VERSION detected${NC}"
    fi
}

check_venv() {
    if [ -d "venv" ]; then
        echo -e "${GREEN}Virtual environment found${NC}"
        source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    elif [ -d ".venv" ]; then
        echo -e "${GREEN}Virtual environment found${NC}"
        source .venv/bin/activate 2>/dev/null || source .venv/Scripts/activate 2>/dev/null
    else
        echo -e "${YELLOW}No virtual environment found. Using system Python.${NC}"
        echo -e "${YELLOW}Tip: Create one with: python -m venv venv${NC}"
    fi
}

check_dependencies() {
    echo -e "\n${CYAN}[Checking Dependencies]${NC}"
    
    MISSING=0
    for pkg in flask openai librosa numpy soundfile pydantic pronouncing; do
        if $PYTHON -c "import $pkg" 2>/dev/null; then
            echo -e "  ${GREEN}✓${NC} $pkg"
        else
            echo -e "  ${RED}✗${NC} $pkg (missing)"
            MISSING=1
        fi
    done
    
    if [ $MISSING -eq 1 ]; then
        echo -e "\n${YELLOW}Some dependencies are missing. Install them with:${NC}"
        echo -e "  pip install -r requirements.txt"
        echo ""
        read -p "Install now? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            $PYTHON -m pip install -r requirements.txt
        else
            exit 1
        fi
    fi
}

check_env() {
    echo -e "\n${CYAN}[Environment Configuration]${NC}"
    
    if [ -f ".env" ]; then
        echo -e "  ${GREEN}✓${NC} .env file found"
        export $(grep -v '^#' .env | xargs 2>/dev/null) || true
    else
        echo -e "  ${YELLOW}!${NC} .env file not found"
        if [ -f ".env.example" ]; then
            echo -e "  ${YELLOW}Tip: Copy .env.example to .env and add your API keys${NC}"
        fi
    fi
    
    if [ -n "$SONAUTO_API_KEY" ]; then
        echo -e "  ${GREEN}✓${NC} SONAUTO_API_KEY configured"
    else
        echo -e "  ${YELLOW}!${NC} SONAUTO_API_KEY not set (audio generation disabled)"
    fi
    
    if [ -n "$OPENAI_API_KEY" ]; then
        echo -e "  ${GREEN}✓${NC} OPENAI_API_KEY configured"
    else
        echo -e "  ${YELLOW}!${NC} OPENAI_API_KEY not set (using simulation mode)"
    fi
}

start_web() {
    HOST="${HOST:-0.0.0.0}"
    PORT="${PORT:-5000}"
    
    echo -e "\n${GREEN}Starting APEX Engine Web UI...${NC}"
    echo -e "  URL: ${CYAN}http://localhost:$PORT${NC}"
    echo -e "  Press Ctrl+C to stop\n"
    
    cd apex_engine
    $PYTHON -m web.app
}

start_cli() {
    echo -e "\n${GREEN}Starting APEX Engine CLI...${NC}\n"
    $PYTHON apex_engine/main.py --interactive
}

show_help() {
    echo "APEX Engine - Startup Options"
    echo ""
    echo "Usage: ./run.sh [option]"
    echo ""
    echo "Options:"
    echo "  (default)     Start the web UI on http://localhost:5000"
    echo "  --cli, -c     Start interactive CLI mode"
    echo "  --demo, -d    Run demonstration mode"
    echo "  --check       Check environment only (don't start)"
    echo "  --help, -h    Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  FAL_KEY           Sonauto API key for audio generation"
    echo "  OPENAI_API_KEY    OpenAI API key for GPT-4o"
    echo "  PORT              Server port (default: 5000)"
    echo "  HOST              Server host (default: 0.0.0.0)"
    echo ""
}

print_banner
check_python
check_venv
check_dependencies
check_env

case "${1:-web}" in
    --help|-h)
        show_help
        ;;
    --cli|-c)
        start_cli
        ;;
    --demo|-d)
        $PYTHON apex_engine/main.py --demo
        ;;
    --check)
        echo -e "\n${GREEN}Environment check complete.${NC}\n"
        ;;
    web|--web|*)
        start_web
        ;;
esac
