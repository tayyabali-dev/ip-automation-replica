#!/bin/bash

# JWHD IP Automation - Stop Development Servers

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Stopping all development servers...${NC}"

# Kill uvicorn
if pgrep -f "uvicorn app.main:app" > /dev/null 2>&1; then
    echo -e "  Stopping Backend API..."
    pkill -f "uvicorn app.main:app" || true
fi

# Kill celery
if pgrep -f "celery -A app.celery_app" > /dev/null 2>&1; then
    echo -e "  Stopping Celery Worker..."
    pkill -f "celery -A app.celery_app" || true
fi

if pgrep -f "celery.*worker" > /dev/null 2>&1; then
    pkill -f "celery.*worker" || true
fi

# Kill Next.js
if pgrep -f "next dev" > /dev/null 2>&1; then
    echo -e "  Stopping Frontend..."
    pkill -f "next dev" || true
fi

# Kill by ports
if lsof -ti:8000 > /dev/null 2>&1; then
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
fi

if lsof -ti:3000 > /dev/null 2>&1; then
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
fi

echo -e "${GREEN}All servers stopped.${NC}"
