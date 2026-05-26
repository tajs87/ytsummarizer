#!/bin/bash

# Deploy ytsum to Railway (easiest $5/month option)
# This script is idempotent - safe to run multiple times

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 ytsum Railway Deployment${NC}"
echo "============================="
echo ""
echo -e "${YELLOW}Note: Railway CLI v3 is interactive. This script will guide you through the process.${NC}"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo -e "${YELLOW}Railway CLI not found. Installing...${NC}"
    npm install -g @railway/cli
    echo -e "${GREEN}✓ Railway CLI installed${NC}"
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo -e "${YELLOW}Please login to Railway:${NC}"
    railway login
fi

echo ""
echo -e "${BLUE}Configuration${NC}"

# Check if .env file exists and source it
if [ -f .env ]; then
    echo -e "${GREEN}✓ Found .env file${NC}"
    source .env
fi

# Get OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    read -p "Enter your OpenAI API Key: " -s OPENAI_API_KEY
    echo ""
else
    echo -e "${GREEN}✓ Using OPENAI_API_KEY from .env${NC}"
fi

# Get or generate SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    read -p "Generate SECRET_KEY automatically? (Y/n): " GEN_SECRET
    GEN_SECRET=${GEN_SECRET:-Y}
    
    if [[ $GEN_SECRET =~ ^[Yy]$ ]]; then
        SECRET_KEY=$(openssl rand -base64 32)
        echo -e "${GREEN}✓ Generated SECRET_KEY${NC}"
    else
        read -p "Enter your SECRET_KEY: " -s SECRET_KEY
        echo ""
    fi
else
    echo -e "${GREEN}✓ Using SECRET_KEY from .env${NC}"
fi

# Check if already linked to a project
echo ""
echo -e "${BLUE}Step 1: Railway Project Setup${NC}"
if railway status &> /dev/null; then
    echo -e "${GREEN}✓ Already linked to Railway project${NC}"
    railway status
else
    echo -e "${YELLOW}Creating new Railway project...${NC}"
    railway init
    echo -e "${GREEN}✓ Project initialized${NC}"
fi

# Instructions for adding databases (if needed)
echo ""
echo -e "${BLUE}Step 2: Ensure PostgreSQL and Redis are added${NC}"
echo -e "${YELLOW}Go to Railway dashboard: https://railway.app/dashboard${NC}"
echo "1. Select your project"
echo "2. Click '+ New' to add:"
echo "   - PostgreSQL (if not already added)"
echo "   - Redis (if not already added)"
echo ""
read -p "Press Enter once PostgreSQL and Redis are added..."
echo -e "${GREEN}✓ Databases configured${NC}"

# Set environment variables for backend service
echo ""
echo -e "${BLUE}Step 3: Deploy Backend Service${NC}"

# Navigate to backend directory
cd backend

# Create railway.json for backend
cat > railway.json << EOF
{
  "\$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port \$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# Check if backend is already linked to a service
if [ -f ".railway/config.json" ] || railway status &> /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend already linked to a service${NC}"
else
    echo -e "${YELLOW}Linking backend to a new service...${NC}"
    echo "When prompted, select 'Create new service' or similar option"
    railway link
fi

# Set environment variables
echo -e "${YELLOW}Setting environment variables for backend...${NC}"
railway variables set OPENAI_API_KEY="${OPENAI_API_KEY}" || echo "Variable may already be set"
railway variables set SECRET_KEY="${SECRET_KEY}" || echo "Variable may already be set"

# Get database URLs from Railway services
echo -e "${YELLOW}Adding database connection variables...${NC}"
echo "These will be automatically populated from your PostgreSQL and Redis services"
railway variables set DATABASE_URL="\${{Postgres.DATABASE_URL}}" || echo "Variable may already be set"
railway variables set REDIS_URL="\${{Redis.REDIS_URL}}" || echo "Variable may already be set"

# Deploy backend
echo -e "${YELLOW}Deploying backend...${NC}"
railway up

cd ..
echo -e "${GREEN}✓ Backend deployed${NC}"

# Get backend URL
echo ""
echo -e "${YELLOW}Getting backend URL...${NC}"
cd backend
BACKEND_URL=$(railway domain 2>/dev/null | tail -1)
if [ -z "$BACKEND_URL" ]; then
    echo -e "${YELLOW}⚠️  Generating public domain for backend...${NC}"
    railway domain
    BACKEND_URL=$(railway domain 2>/dev/null | tail -1)
fi
cd ..

if [ -z "$BACKEND_URL" ]; then
    echo -e "${RED}⚠️  Could not get backend URL automatically${NC}"
    read -p "Enter your backend Railway URL: " BACKEND_URL
fi

echo -e "${GREEN}✓ Backend URL: https://${BACKEND_URL}${NC}"

echo ""
echo -e "${BLUE}Step 4: Deploy Frontend to Vercel${NC}"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}Vercel CLI not found. Installing...${NC}"
    npm install -g vercel
    echo -e "${GREEN}✓ Vercel CLI installed${NC}"
fi

cd frontend

# Check if already linked to Vercel
if [ -f ".vercel/project.json" ]; then
    echo -e "${GREEN}✓ Already linked to Vercel project${NC}"
    echo -e "${YELLOW}Updating deployment...${NC}"
else
    echo -e "${YELLOW}Linking to Vercel (first time)...${NC}"
    echo "When prompted, accept the default settings"
fi

# Set environment variable for production
echo -e "${YELLOW}Setting VITE_API_URL to https://${BACKEND_URL}${NC}"
vercel env add VITE_API_URL production <<< "https://${BACKEND_URL}" 2>/dev/null || echo "Environment variable may already exist"

# Deploy to production
echo -e "${YELLOW}Deploying frontend...${NC}"
vercel --prod --yes

cd ..
echo -e "${GREEN}✓ Frontend deployed${NC}"

# Get frontend URL
cd frontend
FRONTEND_URL=$(vercel inspect --prod 2>/dev/null | grep -E "^\s+url:" | awk '{print $2}' | head -1)
cd ..

if [ -z "$FRONTEND_URL" ]; then
    FRONTEND_URL="your-app.vercel.app (check Vercel dashboard)"
fi

echo ""
echo -e "${BLUE}Step 5: Configure CORS for Frontend${NC}"
echo -e "${YELLOW}Updating backend CORS configuration...${NC}"

cd backend

# Set ALLOWED_ORIGINS to include both localhost and production frontend
ALLOWED_ORIGINS="http://localhost:5173,http://localhost:3000,https://${FRONTEND_URL}"
railway variables set ALLOWED_ORIGINS="${ALLOWED_ORIGINS}"

# Redeploy backend to apply CORS changes
echo -e "${YELLOW}Redeploying backend with updated CORS settings...${NC}"
railway up --detach

cd ..
echo -e "${GREEN}✓ CORS configured for https://${FRONTEND_URL}${NC}"

echo ""
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                            ║${NC}"
echo -e "${GREEN}║  🎉 Deployment Successful!                 ║${NC}"
echo -e "${GREEN}║                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Application URLs:${NC}"
echo -e "  Frontend:  ${GREEN}https://${FRONTEND_URL}${NC}"
echo -e "  Backend:   ${GREEN}https://${BACKEND_URL}${NC}"
echo ""
echo -e "${YELLOW}Dashboards:${NC}"
echo -e "  Railway: https://railway.app/dashboard"
echo -e "  Vercel:  https://vercel.com/dashboard"
echo ""
echo -e "${BLUE}Estimated Cost:${NC} ~\$5/month (Railway Hobby plan)"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Visit your frontend URL to test the application"
echo "  2. View backend logs: cd backend && railway logs"
echo "  3. Monitor both dashboards for health and usage"
echo ""
echo -e "${YELLOW}To update your deployment:${NC}"
echo "  Backend:  cd backend && railway up"
echo "  Frontend: cd frontend && vercel --prod"
echo ""
echo -e "${GREEN}✓ Deployment complete!${NC}"
echo "  cd frontend && vercel --prod"
echo ""
