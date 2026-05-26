#!/bin/bash

# Deploy ytsum to Oracle Cloud Free Tier ARM instance
# This script should be run ON the Oracle Cloud VM after SSH'ing in

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 ytsum Oracle Cloud Free Tier Deployment${NC}"
echo "==========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${RED}❌ Please run as regular user, not root${NC}"
    exit 1
fi

# Prompt for configuration
echo -e "${YELLOW}Configuration${NC}"
read -p "Enter your GitHub repo URL (or leave empty to clone from main): " REPO_URL
REPO_URL=${REPO_URL:-https://github.com/tajs87/ytsummarizer.git}

read -p "Enter your OpenAI API Key: " -s OPENAI_API_KEY
echo ""

read -p "Generate SECRET_KEY automatically? (Y/n): " GEN_SECRET
GEN_SECRET=${GEN_SECRET:-Y}

if [[ $GEN_SECRET =~ ^[Yy]$ ]]; then
    SECRET_KEY=$(openssl rand -base64 32)
    echo -e "${GREEN}✓ Generated SECRET_KEY${NC}"
else
    read -p "Enter your SECRET_KEY: " -s SECRET_KEY
    echo ""
fi

read -p "Enter your domain (or leave empty for IP-only): " DOMAIN

echo ""
echo -e "${BLUE}Step 1/9: Updating system packages${NC}"
sudo apt-get update -qq
sudo apt-get upgrade -y -qq
echo -e "${GREEN}✓ System updated${NC}"

echo ""
echo -e "${BLUE}Step 2/9: Installing Docker${NC}"
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo -e "${GREEN}✓ Docker installed${NC}"
else
    echo -e "${GREEN}✓ Docker already installed${NC}"
fi

echo ""
echo -e "${BLUE}Step 3/9: Installing Docker Compose${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✓ Docker Compose already installed${NC}"
fi

echo ""
echo -e "${BLUE}Step 4/9: Cloning repository${NC}"
if [ -d "ytsum" ]; then
    echo -e "${YELLOW}Directory exists, pulling latest changes...${NC}"
    cd ytsum
    git pull
else
    git clone $REPO_URL ytsum
    cd ytsum
fi
echo -e "${GREEN}✓ Repository ready${NC}"

echo ""
echo -e "${BLUE}Step 5/9: Creating environment configuration${NC}"
cat > .env << EOF
OPENAI_API_KEY=${OPENAI_API_KEY}
SECRET_KEY=${SECRET_KEY}
EOF
echo -e "${GREEN}✓ Environment configured${NC}"

echo ""
echo -e "${BLUE}Step 6/9: Configuring Oracle Cloud firewall${NC}"
# Open ports
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5173 -j ACCEPT

# Make rules persistent
sudo apt-get install -y -qq iptables-persistent
sudo netfilter-persistent save
echo -e "${GREEN}✓ Firewall configured${NC}"

echo ""
echo -e "${BLUE}Step 7/9: Starting Docker services${NC}"
# Need to use newgrp to apply docker group without logout
sg docker -c "docker-compose up -d"
echo -e "${GREEN}✓ Services started${NC}"

echo ""
echo -e "${BLUE}Step 8/9: Running database migrations${NC}"
sleep 10  # Wait for services to be ready
sg docker -c "docker-compose exec -T backend alembic upgrade head" || echo -e "${YELLOW}⚠️  Migrations may need to be run manually${NC}"
echo -e "${GREEN}✓ Migrations completed${NC}"

echo ""
echo -e "${BLUE}Step 9/9: Installing and configuring Caddy (reverse proxy)${NC}"
if [ ! -z "$DOMAIN" ]; then
    # Install Caddy
    sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
    sudo apt update
    sudo apt install -y caddy

    # Configure Caddy with domain
    sudo tee /etc/caddy/Caddyfile > /dev/null << CADDY_EOF
${DOMAIN} {
    reverse_proxy localhost:5173
}

api.${DOMAIN} {
    reverse_proxy localhost:8000
}
CADDY_EOF

    sudo systemctl restart caddy
    echo -e "${GREEN}✓ Caddy configured with domain${NC}"
else
    echo -e "${YELLOW}Skipping Caddy - using IP addresses${NC}"
fi

# Get public IP
PUBLIC_IP=$(curl -s ifconfig.me)

echo ""
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                            ║${NC}"
echo -e "${GREEN}║  🎉 Deployment Successful!                 ║${NC}"
echo -e "${GREEN}║                                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

if [ ! -z "$DOMAIN" ]; then
    echo -e "${BLUE}Application URLs (with domain):${NC}"
    echo -e "  Frontend:  ${GREEN}https://${DOMAIN}${NC}"
    echo -e "  Backend:   ${GREEN}https://api.${DOMAIN}${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Important:${NC} Point your domain DNS to: ${PUBLIC_IP}"
    echo "   Add A records:"
    echo "   - ${DOMAIN} → ${PUBLIC_IP}"
    echo "   - api.${DOMAIN} → ${PUBLIC_IP}"
else
    echo -e "${BLUE}Application URLs (IP-based):${NC}"
    echo -e "  Frontend:  ${GREEN}http://${PUBLIC_IP}:5173${NC}"
    echo -e "  Backend:   ${GREEN}http://${PUBLIC_IP}:8000${NC}"
    echo -e "  API Docs:  ${GREEN}http://${PUBLIC_IP}:8000/docs${NC}"
fi

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Check services: docker-compose ps"
echo "  2. View logs: docker-compose logs -f"
echo "  3. Update code: git pull && docker-compose up -d --build"
echo ""
echo -e "${YELLOW}Oracle Cloud Console:${NC}"
echo "  - Don't forget to add ingress rules in VCN Security Lists:"
echo "    • Allow TCP ports 80, 443, 8000, 5173"
echo ""
echo -e "${GREEN}Cost: \$0/month (Oracle Free Tier Forever!)${NC}"
echo ""
