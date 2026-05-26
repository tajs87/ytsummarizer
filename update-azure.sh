#!/bin/bash

# Quick Update Script for Azure Container Apps
# Use this to deploy code changes without recreating infrastructure

set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick Update Deployment${NC}"
echo ""

# Configuration
RESOURCE_GROUP=${RESOURCE_GROUP:-ytsum-rg}
REGISTRY_NAME=${REGISTRY_NAME:-ytsumregistry}

# Check what to update
UPDATE_BACKEND=false
UPDATE_FRONTEND=false
UPDATE_BOTH=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --backend|-b)
      UPDATE_BACKEND=true
      shift
      ;;
    --frontend|-f)
      UPDATE_FRONTEND=true
      shift
      ;;
    --all|-a)
      UPDATE_BOTH=true
      shift
      ;;
    *)
      echo "Usage: $0 [--backend|-b] [--frontend|-f] [--all|-a]"
      echo ""
      echo "Options:"
      echo "  -b, --backend   Update backend and celery worker"
      echo "  -f, --frontend  Update frontend only"
      echo "  -a, --all       Update both backend and frontend"
      exit 1
      ;;
  esac
done

# If no flags, default to updating both
if [ "$UPDATE_BACKEND" = false ] && [ "$UPDATE_FRONTEND" = false ] && [ "$UPDATE_BOTH" = false ]; then
  UPDATE_BOTH=true
fi

if [ "$UPDATE_BOTH" = true ]; then
  UPDATE_BACKEND=true
  UPDATE_FRONTEND=true
fi

# Login to ACR
echo -e "${BLUE}Logging into Azure Container Registry...${NC}"
az acr login --name $REGISTRY_NAME

if [ "$UPDATE_BACKEND" = true ]; then
  echo ""
  echo -e "${BLUE}Building and pushing backend image...${NC}"
  docker buildx build --platform linux/amd64 -t $REGISTRY_NAME.azurecr.io/ytsum-backend:latest ./backend --push
  echo -e "${GREEN}✓ Backend image pushed${NC}"

  echo ""
  echo -e "${BLUE}Updating backend container app...${NC}"
  az containerapp update \
    --name ytsum-backend \
    --resource-group $RESOURCE_GROUP \
    --image $REGISTRY_NAME.azurecr.io/ytsum-backend:latest \
    --output none
  echo -e "${GREEN}✓ Backend updated${NC}"

  echo ""
  echo -e "${BLUE}Updating celery worker container app...${NC}"
  az containerapp update \
    --name ytsum-celery-worker \
    --resource-group $RESOURCE_GROUP \
    --image $REGISTRY_NAME.azurecr.io/ytsum-backend:latest \
    --output none
  echo -e "${GREEN}✓ Celery worker updated${NC}"

  echo ""
  echo -e "${BLUE}Running database migrations...${NC}"
  az containerapp exec \
    --name ytsum-backend \
    --resource-group $RESOURCE_GROUP \
    --command "alembic upgrade head" \
    --output none 2>/dev/null || echo -e "${YELLOW}⚠️  Migrations skipped or failed${NC}"
fi

if [ "$UPDATE_FRONTEND" = true ]; then
  echo ""
  echo -e "${BLUE}Building and pushing frontend image...${NC}"
  docker buildx build --platform linux/amd64 --target production -t $REGISTRY_NAME.azurecr.io/ytsum-frontend:latest ./frontend --push
  echo -e "${GREEN}✓ Frontend image pushed${NC}"

  echo ""
  echo -e "${BLUE}Updating frontend container app...${NC}"
  az containerapp update \
    --name ytsum-frontend \
    --resource-group $RESOURCE_GROUP \
    --image $REGISTRY_NAME.azurecr.io/ytsum-frontend:latest \
    --output none
  echo -e "${GREEN}✓ Frontend updated${NC}"
fi

echo ""
echo -e "${BLUE}Getting application URLs...${NC}"
BACKEND_URL=$(az containerapp show \
  --name ytsum-backend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

FRONTEND_URL=$(az containerapp show \
  --name ytsum-frontend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo -e "${GREEN}✅ Update complete!${NC}"
echo ""
echo -e "${BLUE}Application URLs:${NC}"
echo -e "  Frontend: ${GREEN}https://${FRONTEND_URL}${NC}"
echo -e "  Backend:  ${GREEN}https://${BACKEND_URL}${NC}"
echo ""
echo -e "${YELLOW}Tip:${NC} Wait 30-60 seconds for containers to fully restart"
echo ""
