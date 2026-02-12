#!/bin/bash

# JWHD IP Automation - Development Server Startup Script
# This script stops existing servers, purges Celery queue, and starts all services

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Project directories
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Store PIDs for cleanup
BACKEND_PID=""
CELERY_PID=""
FRONTEND_PID=""

# Cleanup function to kill all child processes
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down all servers...${NC}"

    # Kill child processes
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
    [ -n "$CELERY_PID" ] && kill $CELERY_PID 2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null

    # Also kill by pattern to be thorough
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "celery -A app.celery_app" 2>/dev/null || true
    pkill -f "next dev" 2>/dev/null || true

    echo -e "${GREEN}All servers stopped.${NC}"
    exit 0
}

# Set trap to cleanup on Ctrl+C or script exit
trap cleanup SIGINT SIGTERM EXIT

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  JWHD IP Automation - Dev Server Start ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# -----------------------------
# Step 1: Kill existing servers
# -----------------------------
echo -e "${YELLOW}[1/4] Stopping existing servers...${NC}"

# Kill uvicorn processes
if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then
    echo -e "  Killing uvicorn processes..."
    pkill -f "uvicorn app.main:app" || true
    sleep 1
fi

# Kill celery processes
if pgrep -f "celery -A app.celery_app" > /dev/null 2>&1; then
    echo -e "  Killing celery worker processes..."
    pkill -f "celery -A app.celery_app" || true
    sleep 1
fi

# Kill any celery workers by name
if pgrep -f "celery.*worker" > /dev/null 2>&1; then
    echo -e "  Killing remaining celery workers..."
    pkill -f "celery.*worker" || true
    sleep 1
fi

# Kill Next.js dev server
if pgrep -f "next dev" > /dev/null 2>&1; then
    echo -e "  Killing Next.js dev server..."
    pkill -f "next dev" || true
    sleep 1
fi

# Kill any process on port 8000 (backend)
if lsof -ti:8000 > /dev/null 2>&1; then
    echo -e "  Killing processes on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# Kill any process on port 3000 (frontend)
if lsof -ti:3000 > /dev/null 2>&1; then
    echo -e "  Killing processes on port 3000..."
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

echo -e "${GREEN}  All existing servers stopped.${NC}"
echo ""

# -----------------------------
# Step 2: Activate virtual environment
# -----------------------------
echo -e "${YELLOW}[2/4] Activating Python virtual environment...${NC}"

if [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
    echo -e "${GREEN}  Virtual environment activated.${NC}"
else
    echo -e "${RED}  Error: Virtual environment not found at $BACKEND_DIR/venv${NC}"
    echo -e "${RED}  Please run: cd backend && python3 -m venv venv && pip install -r requirements.txt${NC}"
    exit 1
fi
echo ""

# -----------------------------
# Step 3: Purge Celery queue
# -----------------------------
echo -e "${YELLOW}[3/4] Purging Celery queue...${NC}"

cd "$BACKEND_DIR"
celery -A app.celery_app purge -f 2>/dev/null || echo -e "  ${YELLOW}Note: Could not purge queue (may be empty or Redis unavailable)${NC}"
echo -e "${GREEN}  Celery queue purged.${NC}"
echo ""

# -----------------------------
# Step 4: Start all servers
# -----------------------------
echo -e "${YELLOW}[4/4] Starting servers...${NC}"
echo ""
echo -e "${BLUE}Access Points:${NC}"
echo -e "  Frontend:     ${GREEN}http://localhost:3000${NC}"
echo -e "  Backend API:  ${GREEN}http://localhost:8000${NC}"
echo -e "  API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}                 LOGS                   ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Start Backend API with prefixed output
cd "$BACKEND_DIR"
source venv/bin/activate
(uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | while IFS= read -r line; do
    echo -e "${GREEN}[BACKEND]${NC} $line"
done) &
BACKEND_PID=$!

# Wait a moment for backend to initialize
sleep 2

# Start Celery Worker with prefixed output
cd "$BACKEND_DIR"
source venv/bin/activate
(celery -A app.celery_app worker --loglevel=info 2>&1 | while IFS= read -r line; do
    echo -e "${MAGENTA}[CELERY]${NC} $line"
done) &
CELERY_PID=$!

# Wait a moment for celery to initialize
sleep 2

# Start Frontend with prefixed output
cd "$FRONTEND_DIR"
(npm run dev 2>&1 | while IFS= read -r line; do
    echo -e "${CYAN}[FRONTEND]${NC} $line"
done) &
FRONTEND_PID=$!

# Wait for all background processes
wait
