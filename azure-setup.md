# Azure Deployment Guide for ytsum

## Prerequisites
1. Azure CLI installed: `brew install azure-cli`
2. Docker images built and pushed to a registry
3. OpenAI API key

## Option 1: Azure Container Apps (Recommended - Easiest)

### 1. Install Azure CLI and login
```bash
az login
az extension add --name containerapp --upgrade
```

### 2. Set variables
```bash
RESOURCE_GROUP="ytsum-rg"
LOCATION="eastus"
ENVIRONMENT="ytsum-env"
POSTGRES_SERVER="ytsum-db"
REDIS_NAME="ytsum-cache"
REGISTRY_NAME="ytsumregistry"
```

### 3. Create resource group
```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

### 4. Create Azure Container Registry (ACR)
```bash
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic

# Enable admin access
az acr update --name $REGISTRY_NAME --admin-enabled true

# Get credentials
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)
```

### 5. Build and push Docker images
```bash
# Login to ACR
az acr login --name $REGISTRY_NAME

# Build and push backend (targeting linux/amd64 for Azure)
docker buildx build --platform linux/amd64 -t $REGISTRY_NAME.azurecr.io/ytsum-backend:latest ./backend --push

# Build and push frontend (production build, targeting linux/amd64)
docker buildx build --platform linux/amd64 --target production -t $REGISTRY_NAME.azurecr.io/ytsum-frontend:latest ./frontend --push
```

**Note:** We use `docker buildx` with `--platform linux/amd64` to ensure compatibility with Azure Container Apps, even if building on Apple Silicon (ARM64) Macs.

### 6. Create Azure Database for PostgreSQL
```bash
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER \
  --location $LOCATION \
  --admin-user ytsumadmin \
  --admin-password "YourSecurePassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --version 15 \
  --storage-size 32 \
  --public-access 0.0.0.0

# Create database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $POSTGRES_SERVER \
  --database-name ytsum
```

### 7. Create Azure Cache for Redis
```bash
az redis create \
  --resource-group $RESOURCE_GROUP \
  --name $REDIS_NAME \
  --location $LOCATION \
  --sku Basic \
  --vm-size c0

# Get connection string
REDIS_KEY=$(az redis list-keys --resource-group $RESOURCE_GROUP --name $REDIS_NAME --query primaryKey -o tsv)
REDIS_URL="redis://:${REDIS_KEY}@${REDIS_NAME}.redis.cache.windows.net:6380?ssl=true"
```

### 8. Create Container Apps Environment
```bash
az containerapp env create \
  --name $ENVIRONMENT \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### 9. Deploy Backend Container App
```bash
DATABASE_URL="postgresql://ytsumadmin:YourSecurePassword123!@${POSTGRES_SERVER}.postgres.database.azure.com:5432/ytsum"

az containerapp create \
  --name ytsum-backend \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $REGISTRY_NAME.azurecr.io/ytsum-backend:latest \
  --registry-server $REGISTRY_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars \
    DATABASE_URL="${DATABASE_URL}" \
    REDIS_URL="${REDIS_URL}" \
    OPENAI_API_KEY="${OPENAI_API_KEY}" \
    SECRET_KEY="${SECRET_KEY}"

# Get backend URL
BACKEND_URL=$(az containerapp show \
  --name ytsum-backend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)
```

### 10. Deploy Celery Worker Container App
```bash
az containerapp create \
  --name ytsum-celery-worker \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $REGISTRY_NAME.azurecr.io/ytsum-backend:latest \
  --registry-server $REGISTRY_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --min-replicas 1 \
  --max-replicas 5 \
  --cpu 1.0 \
  --memory 2.0Gi \
  --env-vars \
    DATABASE_URL="${DATABASE_URL}" \
    REDIS_URL="${REDIS_URL}" \
    OPENAI_API_KEY="${OPENAI_API_KEY}" \
    SECRET_KEY="${SECRET_KEY}" \
  --command "/bin/sh" "-c" "celery -A src.tasks.app:celery_app worker --loglevel=info"
```

### 11. Deploy Frontend Container App
```bash
az containerapp create \
  --name ytsum-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT \
  --image $REGISTRY_NAME.azurecr.io/ytsum-frontend:latest \
  --registry-server $REGISTRY_NAME.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 80 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    VITE_API_URL="https://${BACKEND_URL}"

# Get frontend URL
FRONTEND_URL=$(az containerapp show \
  --name ytsum-frontend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo "Application deployed!"
echo "Frontend: https://${FRONTEND_URL}"
echo "Backend API: https://${BACKEND_URL}"
```

### 12. Run Database Migrations
```bash
# Connect to backend container and run migrations
az containerapp exec \
  --name ytsum-backend \
  --resource-group $RESOURCE_GROUP \
  --command "alembic upgrade head"
```

## Option 2: Azure App Service (Simpler but less flexible)

### Deploy Backend
```bash
# Create App Service Plan
az appservice plan create \
  --name ytsum-plan \
  --resource-group $RESOURCE_GROUP \
  --sku B1 \
  --is-linux

# Create Web App
az webapp create \
  --resource-group $RESOURCE_GROUP \
  --plan ytsum-plan \
  --name ytsum-backend-app \
  --deployment-container-image-name $REGISTRY_NAME.azurecr.io/ytsum-backend:latest

# Configure environment variables
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name ytsum-backend-app \
  --settings \
    DATABASE_URL="${DATABASE_URL}" \
    REDIS_URL="${REDIS_URL}" \
    OPENAI_API_KEY="${OPENAI_API_KEY}" \
    SECRET_KEY="${SECRET_KEY}"
```

### Deploy Frontend to Static Web Apps
```bash
# Install Static Web Apps CLI
npm install -g @azure/static-web-apps-cli

# Deploy (from frontend directory)
cd frontend
npm run build
az staticwebapp create \
  --name ytsum-frontend \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

## Cost Estimates (Monthly)

### Container Apps Setup (Recommended)
- Container Apps Environment: ~$0
- Backend Container (1 instance, 1 vCPU, 2GB): ~$40-50
- Celery Worker (1 instance, 1 vCPU, 2GB): ~$40-50
- Frontend Container (0.5 vCPU, 1GB): ~$20-30
- PostgreSQL Flexible Server (Burstable B1ms): ~$20-30
- Azure Cache for Redis (Basic C0): ~$15-20
- Container Registry (Basic): ~$5
- **Total: ~$140-185/month**

### Cost Optimization Tips
1. Use Azure Free Tier where possible
2. Scale down to 0 instances during low traffic (Container Apps supports this)
3. Use Spot instances for Celery workers
4. Set up autoscaling based on metrics

## Monitoring & Management

### View Logs
```bash
# Backend logs
az containerapp logs show \
  --name ytsum-backend \
  --resource-group $RESOURCE_GROUP \
  --tail 100 \
  --follow

# Worker logs
az containerapp logs show \
  --name ytsum-celery-worker \
  --resource-group $RESOURCE_GROUP \
  --tail 100 \
  --follow
```

### Update Deployment
```bash
# Build new image
docker build -t $REGISTRY_NAME.azurecr.io/ytsum-backend:latest ./backend
docker push $REGISTRY_NAME.azurecr.io/ytsum-backend:latest

# Update container app
az containerapp update \
  --name ytsum-backend \
  --resource-group $RESOURCE_GROUP \
  --image $REGISTRY_NAME.azurecr.io/ytsum-backend:latest
```

### Setup CI/CD with GitHub Actions
See `azure-pipeline.yml` for automated deployments.

## Security Best Practices

1. **Use Managed Identities** instead of connection strings
2. **Enable CORS** properly on backend
3. **Use Azure Key Vault** for secrets
4. **Enable Application Insights** for monitoring
5. **Set up firewall rules** on PostgreSQL and Redis
6. **Use custom domains** with SSL certificates

## Cleanup (when done testing)
```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```
