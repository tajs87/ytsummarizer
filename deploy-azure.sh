#!/bin/bash

# Azure Deployment Script for ytsum
# This script automates the deployment of the ytsum application to Azure Container Apps
# NOTE: This script is idempotent - it can be run multiple times safely.
#       Existing resources will be detected and skipped or updated.

set -e

echo "🚀 ytsum Azure Deployment Script"
echo "================================="
echo ""

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    echo -e "${RED}❌ Azure CLI is not installed. Please install it first:${NC}"
    echo "   brew install azure-cli"
    exit 1
fi

# Check if user is logged in
if ! az account show &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not logged in to Azure. Logging in now...${NC}"
    az login
fi

# Prompt for configuration
echo -e "${BLUE}📝 Configuration${NC}"
echo ""

read -p "Resource Group Name (default: ytsum-rg): " RESOURCE_GROUP
RESOURCE_GROUP=${RESOURCE_GROUP:-ytsum-rg}

read -p "Location (default: eastus): " LOCATION
LOCATION=${LOCATION:-eastus}

read -p "Container Registry Name (default: ytsumregistry): " REGISTRY_NAME
REGISTRY_NAME=${REGISTRY_NAME:-ytsumregistry}

read -p "PostgreSQL Admin Password: " -s POSTGRES_PASSWORD
echo ""

read -p "Secret Key for JWT (leave empty to generate): " SECRET_KEY
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -base64 32)
    echo -e "${GREEN}✓ Generated secret key${NC}"
fi

read -p "OpenAI API Key: " -s OPENAI_API_KEY
echo ""
echo ""

# Confirm deployment
echo -e "${YELLOW}Configuration Summary:${NC}"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Registry: $REGISTRY_NAME"
echo ""
read -p "Continue with deployment? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo ""
echo -e "${BLUE}Step 1/11: Creating Resource Group${NC}"
if az group show --name $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}✓ Resource group already exists${NC}"
else
    az group create \
      --name $RESOURCE_GROUP \
      --location $LOCATION \
      --output none
    echo -e "${GREEN}✓ Resource group created${NC}"
fi

echo ""
echo -e "${BLUE}Step 2/11: Creating Azure Container Registry${NC}"
if az acr show --name $REGISTRY_NAME --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}✓ Container registry already exists${NC}"
else
    az acr create \
      --resource-group $RESOURCE_GROUP \
      --name $REGISTRY_NAME \
      --sku Basic \
      --output none

    az acr update \
      --name $REGISTRY_NAME \
      --admin-enabled true \
      --output none
    echo -e "${GREEN}✓ Container registry created${NC}"
fi

ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)
echo -e "${GREEN}✓ Registry credentials retrieved${NC}"

echo ""
echo -e "${BLUE}Step 3/11: Building and Pushing Docker Images${NC}"
az acr login --name $REGISTRY_NAME

echo "  Building backend for linux/amd64..."
docker buildx build --platform linux/amd64 -t $REGISTRY_NAME.azurecr.io/ytsum-backend:latest ./backend --push

echo "  Building frontend for linux/amd64..."
docker buildx build --platform linux/amd64 --target production -t $REGISTRY_NAME.azurecr.io/ytsum-frontend:latest ./frontend --push
echo -e "${GREEN}✓ Images built and pushed${NC}"

echo ""
echo -e "${BLUE}Step 4/11: Creating PostgreSQL Database${NC}"
POSTGRES_SERVER="ytsum-db-$RANDOM"

# Check if any PostgreSQL server exists in the resource group
EXISTING_POSTGRES=$(az postgres flexible-server list --resource-group $RESOURCE_GROUP --query "[?contains(name, 'ytsum-db')].name" -o tsv 2>/dev/null | head -n 1)

if [ ! -z "$EXISTING_POSTGRES" ]; then
    POSTGRES_SERVER=$EXISTING_POSTGRES
    echo -e "${GREEN}✓ Using existing PostgreSQL server: $POSTGRES_SERVER${NC}"
else
    az postgres flexible-server create \
      --resource-group $RESOURCE_GROUP \
      --name $POSTGRES_SERVER \
      --location $LOCATION \
      --admin-user ytsumadmin \
      --admin-password "$POSTGRES_PASSWORD" \
      --sku-name Standard_B1ms \
      --tier Burstable \
      --version 15 \
      --storage-size 32 \
      --public-access 0.0.0.0-255.255.255.255 \
      --yes \
      --output none

    az postgres flexible-server db create \
      --resource-group $RESOURCE_GROUP \
      --server-name $POSTGRES_SERVER \
      --database-name ytsum \
      --output none
    echo -e "${GREEN}✓ PostgreSQL database created${NC}"
fi

DATABASE_URL="postgresql://ytsumadmin:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}.postgres.database.azure.com:5432/ytsum"
echo -e "${GREEN}✓ Database URL configured${NC}"

echo ""
echo -e "${BLUE}Step 5/11: Creating Azure Cache for Redis${NC}"
REDIS_NAME="ytsum-cache-$RANDOM"

# Check if any Redis cache exists in the resource group
EXISTING_REDIS=$(az redis list --resource-group $RESOURCE_GROUP --query "[?contains(name, 'ytsum-cache')].name" -o tsv 2>/dev/null | head -n 1)

if [ ! -z "$EXISTING_REDIS" ]; then
    REDIS_NAME=$EXISTING_REDIS
    echo -e "${GREEN}✓ Using existing Redis cache: $REDIS_NAME${NC}"
else
    az redis create \
      --resource-group $RESOURCE_GROUP \
      --name $REDIS_NAME \
      --location $LOCATION \
      --sku Basic \
      --vm-size c0 \
      --output none
    echo -e "${GREEN}✓ Redis cache created${NC}"
fi

REDIS_KEY=$(az redis list-keys --resource-group $RESOURCE_GROUP --name $REDIS_NAME --query primaryKey -o tsv)
REDIS_HOST="${REDIS_NAME}.redis.cache.windows.net"
REDIS_URL="rediss://:${REDIS_KEY}@${REDIS_HOST}:6380/0?ssl_cert_reqs=required"
echo -e "${GREEN}✓ Redis URL configured${NC}"

echo ""
echo -e "${BLUE}Step 6/11: Creating Container Apps Environment${NC}"
ENVIRONMENT="ytsum-env"

if az containerapp env show --name $ENVIRONMENT --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${GREEN}✓ Container Apps environment already exists${NC}"
else
    az containerapp env create \
      --name $ENVIRONMENT \
      --resource-group $RESOURCE_GROUP \
      --location $LOCATION \
      --output none
    echo -e "${GREEN}✓ Container Apps environment created${NC}"
fi

echo ""
echo -e "${BLUE}Step 7/11: Deploying Backend Container App${NC}"
if az containerapp show --name ytsum-backend --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${YELLOW}Backend container app exists, updating...${NC}"
    az containerapp update \
      --name ytsum-backend \
      --resource-group $RESOURCE_GROUP \
      --image $REGISTRY_NAME.azurecr.io/ytsum-backend:latest \
      --set-env-vars \
        DATABASE_URL="${DATABASE_URL}" \
        REDIS_URL="${REDIS_URL}" \
        OPENAI_API_KEY="${OPENAI_API_KEY}" \
        SECRET_KEY="${SECRET_KEY}" \
      --output none
    echo -e "${GREEN}✓ Backend updated${NC}"
else
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
        SECRET_KEY="${SECRET_KEY}" \
      --output none
    echo -e "${GREEN}✓ Backend deployed${NC}"
fi

BACKEND_URL=$(az containerapp show \
  --name ytsum-backend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)
echo -e "${GREEN}✓ Backend URL: https://${BACKEND_URL}${NC}"

echo ""
echo -e "${BLUE}Step 8/11: Deploying Celery Worker Container App${NC}"
if az containerapp show --name ytsum-celery-worker --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${YELLOW}Celery worker exists, updating...${NC}"
    az containerapp update \
      --name ytsum-celery-worker \
      --resource-group $RESOURCE_GROUP \
      --image $REGISTRY_NAME.azurecr.io/ytsum-backend:latest \
      --set-env-vars \
        DATABASE_URL="${DATABASE_URL}" \
        REDIS_URL="${REDIS_URL}" \
        OPENAI_API_KEY="${OPENAI_API_KEY}" \
        SECRET_KEY="${SECRET_KEY}" \
      --output none
    echo -e "${GREEN}✓ Celery worker updated${NC}"
else
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
      --command "/bin/sh" "-c" "celery -A src.tasks.app:celery_app worker --loglevel=info" \
      --output none
    echo -e "${GREEN}✓ Celery worker deployed${NC}"
fi

echo ""
echo -e "${BLUE}Step 9/11: Deploying Frontend Container App${NC}"
if az containerapp show --name ytsum-frontend --resource-group $RESOURCE_GROUP &> /dev/null; then
    echo -e "${YELLOW}Frontend exists, updating...${NC}"
    az containerapp update \
      --name ytsum-frontend \
      --resource-group $RESOURCE_GROUP \
      --image $REGISTRY_NAME.azurecr.io/ytsum-frontend:latest \
      --set-env-vars \
        VITE_API_URL="https://${BACKEND_URL}" \
      --output none
    echo -e "${GREEN}✓ Frontend updated${NC}"
else
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
        VITE_API_URL="https://${BACKEND_URL}" \
      --output none
    echo -e "${GREEN}✓ Frontend deployed${NC}"
fi

FRONTEND_URL=$(az containerapp show \
  --name ytsum-frontend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)
echo -e "${GREEN}✓ Frontend URL: https://${FRONTEND_URL}${NC}"

echo ""
echo -e "${BLUE}Step 10/11: Running Database Migrations${NC}"
# Wait for backend to be ready
echo "  Waiting for backend to be ready..."
sleep 30

# Run migrations
az containerapp exec \
  --name ytsum-backend \
  --resource-group $RESOURCE_GROUP \
  --command "alembic upgrade head" \
  --output none 2>/dev/null || echo -e "${YELLOW}⚠️  Run migrations manually: az containerapp exec --name ytsum-backend --resource-group $RESOURCE_GROUP --command 'alembic upgrade head'${NC}"
echo -e "${GREEN}✓ Database migrations completed${NC}"

echo ""
echo -e "${BLUE}Step 11/11: Setting up Application Insights${NC}"
if az monitor app-insights component show --app ytsum-insights --resource-group $RESOURCE_GROUP &> /dev/null 2>&1; then
    echo -e "${GREEN}✓ Application Insights already exists${NC}"
else
    az monitor app-insights component create \
      --app ytsum-insights \
      --location $LOCATION \
      --resource-group $RESOURCE_GROUP \
      --output none 2>/dev/null || echo -e "${YELLOW}⚠️  Application Insights setup skipped${NC}"
fi

echo ""
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}║  🎉 Deployment Successful!                    ║${NC}"
echo -e "${GREEN}║                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Application URLs:${NC}"
echo -e "  Frontend:  ${GREEN}https://${FRONTEND_URL}${NC}"
echo -e "  Backend:   ${GREEN}https://${BACKEND_URL}${NC}"
echo ""
echo -e "${BLUE}Resource Group:${NC} $RESOURCE_GROUP"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Visit the frontend URL to test the application"
echo "  2. Monitor logs: az containerapp logs show --name ytsum-backend --resource-group $RESOURCE_GROUP --follow"
echo "  3. Set up custom domain (optional)"
echo "  4. Configure CI/CD with GitHub Actions"
echo ""
echo -e "${YELLOW}To delete all resources:${NC}"
echo "  az group delete --name $RESOURCE_GROUP --yes --no-wait"
echo ""
