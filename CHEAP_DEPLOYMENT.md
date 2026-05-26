# Cheapest Deployment Options for ytsum

## 🆓 Option 1: Free Tier Combo ($0/month)

### Setup: Railway Free + Supabase Free + Vercel Free

**Components:**
- Frontend: Vercel (free, no credit card needed)
- Backend: Railway Free Tier (500 hours/month, $5 credit)
- Database: Supabase (free PostgreSQL, 500MB)
- Redis: Upstash (free Redis, 10k commands/day)
- Celery: Run on same Railway container (background threads)

**Limitations:**
- Railway free tier sleeps after inactivity
- Upstash limited to 10k commands/day
- Supabase 500MB storage limit
- Good for demos/testing, not production

### Deploy Backend to Railway

```bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login to Railway
railway login

# 3. Create new project
railway init

# 4. Add PostgreSQL
railway add --plugin postgresql

# 5. Add Redis
railway add --plugin redis

# 6. Set environment variables
railway variables set OPENAI_API_KEY="your-key"
railway variables set SECRET_KEY="your-secret"

# 7. Deploy from backend directory
cd backend
railway up
```

### Deploy Frontend to Vercel

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy from frontend directory
cd frontend
vercel

# 3. Set environment variable
vercel env add VITE_API_URL production
# Enter your Railway backend URL
```

**Total Cost: $0/month** (with usage limits)

---

## 💵 Option 2: Railway Hobby ($5/month)

### Railway Hobby Plan

**What you get:**
- $5 credit/month (renews monthly)
- No sleeping (always-on)
- Unlimited projects
- Custom domains

**Setup:**
Same as free tier above, but upgrade to Hobby plan for always-on.

```bash
# Deploy all services to Railway
railway add --plugin postgresql
railway add --plugin redis
railway up
```

**Estimated usage:**
- Backend: ~$3-4/month
- Database: ~$1-2/month
- Redis: ~$0.50/month
- Celery worker: Runs in same container (no extra cost)

**Total Cost: ~$5/month** (covered by Hobby credit)

---

## 💰 Option 3: Fly.io ($10-15/month)

### Why Fly.io?

- Native Docker support (use your existing Dockerfiles)
- Free PostgreSQL (3GB storage, shared CPU)
- Pay-as-you-go for compute
- Global edge deployment
- No credit card for free tier

### Deploy to Fly.io

```bash
# 1. Install Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Create PostgreSQL
fly postgres create ytsum-db --region iad --initial-cluster-size 1

# 4. Create Redis
fly redis create ytsum-redis --region iad

# 5. Deploy Backend
cd backend
fly launch --name ytsum-backend --region iad
fly secrets set OPENAI_API_KEY="your-key"
fly secrets set SECRET_KEY="your-secret"
fly deploy

# 6. Deploy Celery Worker (separate app)
cd backend
fly launch --name ytsum-worker --region iad
fly secrets set OPENAI_API_KEY="your-key"
fly deploy

# 7. Deploy Frontend
cd frontend
fly launch --name ytsum-frontend --region iad
fly deploy
```

**Cost Breakdown:**
- Compute (backend + worker): ~$8-10/month (shared-cpu-1x)
- PostgreSQL: Free (3GB)
- Redis: Free (256MB)
- Frontend: ~$2-3/month

**Total Cost: ~$10-15/month**

---

## 💵 Option 4: Single VPS - Digital Ocean Droplet ($6-12/month)

### Why Single VPS?

- Run everything with docker-compose
- Full control, no surprises
- Cheapest for multi-service apps
- Great for learning DevOps

### Setup Digital Ocean Droplet

```bash
# 1. Create droplet (Basic $6/month or $12/month)
# - Choose Ubuntu 22.04 LTS
# - Select $6/month (1GB RAM) or $12/month (2GB RAM)
# - Add SSH key

# 2. SSH into droplet
ssh root@your-droplet-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 4. Install Docker Compose
apt-get update
apt-get install -y docker-compose

# 5. Clone your repo
git clone https://github.com/yourusername/ytsum.git
cd ytsum

# 6. Create .env file
cat > .env << EOF
OPENAI_API_KEY=your-key
SECRET_KEY=your-secret
EOF

# 7. Start services
docker-compose up -d

# 8. Setup Caddy for HTTPS (optional)
apt install -y caddy
cat > /etc/caddy/Caddyfile << EOF
yourdomain.com {
    reverse_proxy localhost:5173
}

api.yourdomain.com {
    reverse_proxy localhost:8000
}
EOF
systemctl restart caddy
```

**Requirements:**
- $6/month: Works but tight on memory (1GB RAM)
- $12/month: Recommended for better performance (2GB RAM)
- Domain name: ~$12/year (optional, use IP otherwise)

**Total Cost: $6-12/month** (+ $1/month for domain)

---

## 💰 Option 5: Hetzner Cloud (€4-8/month = ~$4-9/month)

### Why Hetzner?

- CHEAPEST European VPS provider
- Better specs than DO at lower price
- Same docker-compose setup as Option 4

### Setup

```bash
# 1. Create Hetzner Cloud account
# 2. Create server (CPX11 - €4.15/month)
#    - 2 vCPUs, 2GB RAM, 40GB SSD
# 3. Follow same docker-compose setup as DO above
```

**Total Cost: €4-8/month** (~$4-9/month)

---

## 🎁 Option 6: Oracle Cloud Free Tier (FREE FOREVER)

### Why Oracle Cloud Free Tier?

- Actually free forever (not trial)
- 4 ARM Ampere A1 cores + 24GB RAM (can split into 4 VMs)
- 200GB total storage
- Generous network bandwidth
- No credit card required

### What's Included (Free Forever):

- 2 AMD Compute VMs (1/8 OCPU, 1GB RAM each)
- **OR 4 ARM Ampere A1 cores + 24GB RAM** (better choice!)
- 200GB Block Volume storage
- 10TB outbound data transfer/month
- Load Balancer

### Setup

```bash
# 1. Create Oracle Cloud account (free tier)
# https://www.oracle.com/cloud/free/

# 2. Create ARM-based VM (4 OCPUs, 24GB RAM)
# - Choose Ubuntu 22.04
# - Select "Always Free Eligible" shape
# - VM.Standard.A1.Flex (4 OCPUs, 24GB RAM)

# 3. SSH into instance
ssh ubuntu@instance-ip

# 4. Follow docker-compose setup (same as DO/Hetzner)

# 5. Open firewall ports
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo netfilter-persistent save

# 6. Configure Oracle Cloud Network Security
# - Go to VCN → Security Lists
# - Add ingress rules for ports 80, 443
```

**Performance:**
ARM Ampere A1 is surprisingly fast - better than x86 VPS at this tier!

**Total Cost: $0/month FOREVER**

---

## 💎 Option 7: Render ($25-30/month)

### Why Render?

- Zero-config deployments
- Auto HTTPS, auto scaling
- GitHub integration
- Great for production

### Deploy to Render

```bash
# 1. Connect GitHub repo to Render
# 2. Create services:
#    - Web Service: Backend (Docker)
#    - Background Worker: Celery (Docker)
#    - Static Site: Frontend
#    - PostgreSQL: Database
#    - Redis: Cache

# 3. Set environment variables in dashboard
# 4. Deploy!
```

**Cost Breakdown:**
- Backend (Starter): $7/month
- Celery Worker (Starter): $7/month
- Frontend (Static): Free
- PostgreSQL (Starter): $7/month
- Redis (Starter): $7/month

**Total Cost: ~$28/month**

---

## 📊 Comparison Table

| Option | Cost/Month | Pros | Cons | Best For |
|--------|-----------|------|------|----------|
| Railway Free + Vercel | $0 | Easy setup, no credit card | Sleeps, usage limits | Testing/demos |
| Railway Hobby | $5 | Simple, always-on | Limited resources | Side projects |
| Fly.io | $10-15 | Global CDN, easy scaling | Learning curve | Small apps |
| DO Droplet ($6) | $6 | Full control, cheap | Manual setup, 1GB RAM tight | Learning DevOps |
| DO Droplet ($12) | $12 | Full control, 2GB RAM | Manual management | Production-ready |
| Hetzner Cloud | $4-9 | Cheapest VPS, good specs | EU-based only | Best bang/buck |
| **Oracle Free Tier** | **$0** | **Free forever, 24GB RAM!** | **Setup complexity** | **Best free option** |
| Render | $28 | Production-ready, managed | More expensive | Hands-off hosting |
| Azure Container Apps | $140-185 | Enterprise, autoscaling | Expensive | Large scale |

---

## 🏆 Recommended Options by Use Case

### Personal Project / Learning
**Oracle Cloud Free Tier** ($0/month)
- Best free option with generous specs
- Full control, production-ready
- Requires some DevOps knowledge

### Side Project / Portfolio
**Railway Hobby** ($5/month)
- Easiest to set up
- Always-on
- Good for resume projects

### Small Startup / MVP
**Hetzner Cloud CPX21** ($8/month)
- Best price/performance
- 3 vCPUs, 4GB RAM
- Production-ready

**OR Digital Ocean $12 Droplet**
- Better docs and community
- More payment options
- US-based (if that matters)

### Growing Startup
**Fly.io** ($10-30/month)
- Easy to scale
- Global edge deployment
- Good for international users

### Enterprise
**Azure Container Apps** ($140-185/month)
- Autoscaling
- Managed services
- Enterprise support

---

## 🚀 Quick Start Scripts

### For Oracle Cloud Free Tier (Best Value - FREE)

```bash
#!/bin/bash
# deploy-oracle-free.sh

# After creating Oracle VM and SSHing in:

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and setup
git clone https://github.com/yourusername/ytsum.git
cd ytsum

# Create .env
cat > .env << EOF
OPENAI_API_KEY=${OPENAI_API_KEY}
SECRET_KEY=$(openssl rand -base64 32)
EOF

# Open firewall
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8000 -j ACCEPT
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 5173 -j ACCEPT
sudo netfilter-persistent save

# Start services
docker-compose up -d

# Setup reverse proxy with Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy

# Configure Caddy
sudo tee /etc/caddy/Caddyfile > /dev/null << EOF
:80 {
    reverse_proxy localhost:5173
}

:8000 {
    reverse_proxy localhost:8000
}
EOF

sudo systemctl restart caddy

echo "✅ Deployment complete!"
echo "Frontend: http://$(curl -s ifconfig.me)"
echo "Backend: http://$(curl -s ifconfig.me):8000"
```

### For Railway (Easiest - $5/month)

```bash
#!/bin/bash
# deploy-railway.sh

npm i -g @railway/cli
railway login
railway init

# Create services
railway add --plugin postgresql
railway add --plugin redis

# Set variables
railway variables set OPENAI_API_KEY="${OPENAI_API_KEY}"
railway variables set SECRET_KEY="$(openssl rand -base64 32)"

# Deploy backend
cd backend
railway up

# Get backend URL
BACKEND_URL=$(railway status --json | jq -r '.deployments[0].url')

# Deploy frontend to Vercel
cd ../frontend
npm i -g vercel
vercel --prod
vercel env add VITE_API_URL production
# Paste backend URL

echo "✅ Deployment complete!"
```

---

## 💡 Money-Saving Tips

1. **Start with Oracle Free Tier** - It's actually free forever with generous specs
2. **Use Cloudflare** - Free CDN, DDoS protection, and SSL
3. **Optimize Docker images** - Smaller images = faster deploys = lower costs
4. **Use shared databases** - Railway/Render shared DB instead of dedicated
5. **Scale gradually** - Start small, scale when needed
6. **Regional pricing** - Hetzner (EU) is cheaper than DO/AWS
7. **Combine free tiers** - Frontend on Vercel, backend on Railway, DB on Supabase

---

## ⚠️ Trade-offs to Consider

### Free Tiers
- ✅ Pros: Free!
- ❌ Cons: Cold starts, limited resources, may shut down after inactivity

### Single VPS ($6-12/month)
- ✅ Pros: Predictable cost, full control
- ❌ Cons: Manual management, no auto-scaling, single point of failure

### Managed PaaS ($25-50/month)
- ✅ Pros: Easy, auto-scaling, managed backups
- ❌ Cons: More expensive, less control

### Enterprise ($140+/month)
- ✅ Pros: Production-ready, SLA, support
- ❌ Cons: Expensive, overkill for small projects

---

## 🎯 My Recommendation

**For your use case (personal/learning project):**

### Option 1: Oracle Cloud Free Tier ($0/month)
- Deploy with docker-compose on free ARM instance
- 24GB RAM is more than enough
- Actually production-ready
- Free forever (not a trial)

**Setup time:** 30-45 minutes  
**Difficulty:** Intermediate (but good learning experience)

### Option 2: Railway Hobby ($5/month)
- Dead simple setup
- Always-on
- Perfect for side projects
- Great for portfolios

**Setup time:** 10 minutes  
**Difficulty:** Beginner

---

## 📚 Detailed Guides

Choose your preferred option:

1. **[Oracle Free Setup](./deploy-oracle-free.md)** - $0/month
2. **[Railway Setup](./deploy-railway.md)** - $5/month  
3. **[Digital Ocean Setup](./deploy-digitalocean.md)** - $12/month
4. **[Fly.io Setup](./deploy-fly.md)** - $10-15/month

All guides include:
- Step-by-step instructions
- Environment setup
- Domain configuration
- SSL/HTTPS setup
- Monitoring setup
