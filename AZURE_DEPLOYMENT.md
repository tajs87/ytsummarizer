# Quick Start: Azure Deployment

## Easiest Method: One-Command Deployment

```bash
chmod +x deploy-azure.sh
./deploy-azure.sh
```

This script will:
1. ✅ Create all Azure resources (or detect existing ones)
2. ✅ Build and push Docker images
3. ✅ Deploy backend, workers, and frontend
4. ✅ Set up PostgreSQL and Redis
5. ✅ Run database migrations
6. ✅ Provide you with live URLs

**Note:** This script is **idempotent** - you can run it multiple times safely. It will:
- Skip creating resources that already exist
- Update existing container apps with new images
- Reuse existing databases and caches

**Time:** ~15-20 minutes (first run) | ~5-10 minutes (subsequent runs)  
**Cost:** ~$140-185/month

---

## Prerequisites

1. **Azure CLI** - Install if you don't have it:
   ```bash
   brew install azure-cli
   ```

2. **Azure Account** - Sign up at [azure.com](https://azure.microsoft.com)

3. **OpenAI API Key** - Get from [platform.openai.com](https://platform.openai.com)

---

## Manual Setup (if you prefer step-by-step)

See [azure-setup.md](./azure-setup.md) for detailed instructions.

---

## Automated Deployment with GitHub Actions

### 1. Create Azure Service Principal

```bash
az ad sp create-for-rbac \
  --name "ytsum-github-actions" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/ytsum-rg \
  --sdk-auth
```

Copy the entire JSON output.

### 2. Add GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add these secrets:
- **AZURE_CREDENTIALS**: Paste the JSON from step 1
- **OPENAI_API_KEY**: Your OpenAI API key
- **SECRET_KEY**: Generate with `openssl rand -base64 32`

### 3. Push to main branch

Every push to `main` will automatically deploy to Azure! 🚀

---

## What Gets Deployed

| Service | Azure Resource | Purpose |
|---------|---------------|---------|
| Backend API | Container App | FastAPI application |
| Celery Workers | Container App | Background video processing |
| Frontend | Container App | React SPA |
| Database | PostgreSQL Flexible Server | Video/user data |
| Cache/Queue | Azure Cache for Redis | Celery task queue |
| Registry | Azure Container Registry | Docker images |

---

## Cost Optimization

### Development Environment (~$40/month)
```bash
# Use smaller instances
--sku-name Standard_B1s  # PostgreSQL
--vm-size c0             # Redis
--cpu 0.5 --memory 1.0Gi # Containers
```

### Production Environment (~$180/month)
```bash
# Full setup with autoscaling
--min-replicas 2 --max-replicas 10
--sku-name Standard_B2s  # PostgreSQL
--vm-size c1             # Redis
```

### Scale to Zero (Save costs when not in use)
```bash
az containerapp update \
  --name ytsum-backend \
  --resource-group ytsum-rg \
  --min-replicas 0 \
  --scale-rule-name http-rule \
  --scale-rule-http-concurrency 10
```

---

## Monitoring

### View Logs
```bash
# Backend logs
az containerapp logs show \
  --name ytsum-backend \
  --resource-group ytsum-rg \
  --follow

# Worker logs
az containerapp logs show \
  --name ytsum-celery-worker \
  --resource-group ytsum-rg \
  --follow
```

### Health Checks
```bash
# Check backend health
curl https://<backend-url>/health

# Check all container status
az containerapp list \
  --resource-group ytsum-rg \
  --query "[].{Name:name, Status:properties.runningStatus}" \
  --output table
```

---

## Update Deployment

### Option 1: GitHub Actions (Recommended)
Just push to main branch - automatic deployment!

### Option 2: Manual Update
```bash
# Build and push new image
docker build -t ytsumregistry.azurecr.io/ytsum-backend:latest ./backend
docker push ytsumregistry.azurecr.io/ytsum-backend:latest

# Update container app
az containerapp update \
  --name ytsum-backend \
  --resource-group ytsum-rg \
  --image ytsumregistry.azurecr.io/ytsum-backend:latest
```

---

## Custom Domain Setup

```bash
# Add custom domain
az containerapp hostname add \
  --name ytsum-frontend \
  --resource-group ytsum-rg \
  --hostname yourdomain.com

# Bind SSL certificate (automatic with Azure)
az containerapp hostname bind \
  --name ytsum-frontend \
  --resource-group ytsum-rg \
  --hostname yourdomain.com \
  --validation-method CNAME
```

---

## Troubleshooting

### Container won't start
```bash
# Check logs
az containerapp logs show --name ytsum-backend --resource-group ytsum-rg --tail 50

# Check revision status
az containerapp revision list --name ytsum-backend --resource-group ytsum-rg
```

### Platform mismatch error (Apple Silicon Macs)
**Error:** `no child with platform linux/amd64 in index`

**Solution:** The deployment scripts now use `docker buildx` to build for linux/amd64 automatically. If you still see this error:

```bash
# Ensure buildx is set up
docker buildx ls

# If needed, create a new builder
docker buildx create --name multiplatform --use
docker buildx inspect --bootstrap

# Re-run deployment
./deploy-azure.sh
```

### Database connection issues
```bash
# Check PostgreSQL firewall rules
az postgres flexible-server firewall-rule list \
  --resource-group ytsum-rg \
  --name <your-postgres-server>

# Allow Container Apps
az postgres flexible-server firewall-rule create \
  --resource-group ytsum-rg \
  --name <your-postgres-server> \
  --rule-name allow-all \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255
```

### Redis connection issues
```bash
# Test Redis connection
az redis show \
  --name <your-redis-name> \
  --resource-group ytsum-rg \
  --query "sslPort"

# Get connection string
az redis list-keys \
  --resource-group ytsum-rg \
  --name <your-redis-name>
```

---

## Cleanup

### Delete everything
```bash
az group delete --name ytsum-rg --yes --no-wait
```

### Delete only container apps (keep data)
```bash
az containerapp delete --name ytsum-backend --resource-group ytsum-rg --yes
az containerapp delete --name ytsum-celery-worker --resource-group ytsum-rg --yes
az containerapp delete --name ytsum-frontend --resource-group ytsum-rg --yes
```

---

## Alternative: Azure App Service + Static Web Apps

If you prefer a simpler setup without containers:

```bash
# Backend on App Service
az webapp up \
  --name ytsum-backend \
  --resource-group ytsum-rg \
  --runtime "PYTHON:3.11" \
  --plan ytsum-plan

# Frontend on Static Web Apps
cd frontend && npm run build
az staticwebapp create \
  --name ytsum-frontend \
  --resource-group ytsum-rg \
  --source ./dist
```

**Pros:** Simpler, less expensive (~$50-80/month)  
**Cons:** Less flexible, harder to scale workers

---

## Support

- Azure Documentation: [docs.microsoft.com/azure](https://docs.microsoft.com/azure)
- Container Apps: [aka.ms/containerapps](https://aka.ms/containerapps)
- Pricing Calculator: [azure.com/pricing/calculator](https://azure.com/pricing/calculator)

Need help? Open an issue or check [azure-setup.md](./azure-setup.md) for detailed instructions.
