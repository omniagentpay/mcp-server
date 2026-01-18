#!/bin/bash
# Deployment script for Google Cloud Run

set -e

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-your-project-id}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-omniagentpay-mcp-server}"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Docker image...${NC}"
docker build -t ${IMAGE_NAME}:latest .

echo -e "${GREEN}Pushing image to Google Container Registry...${NC}"
docker push ${IMAGE_NAME}:latest

echo -e "${GREEN}Deploying to Cloud Run...${NC}"
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 300 \
  --set-env-vars ENVIRONMENT=prod

echo -e "${GREEN}Deployment complete!${NC}"
echo -e "${YELLOW}Service URL:${NC}"
gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'
