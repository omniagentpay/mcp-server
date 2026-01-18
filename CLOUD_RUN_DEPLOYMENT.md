# Google Cloud Run Deployment Guide

This guide walks you through deploying the OmniAgentPay MCP Server to Google Cloud Run.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and configured
3. **Docker** installed (for local builds)
4. **Project ID** in Google Cloud Platform

## Setup

### 1. Install Google Cloud SDK

```bash
# Install gcloud CLI (if not already installed)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Enable Required APIs

```bash
gcloud services enable \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  containerregistry.googleapis.com
```

### 3. Configure Environment Variables

Set secrets in Google Cloud Secret Manager or as Cloud Run environment variables:

```bash
# Set secrets in Secret Manager (recommended)
gcloud secrets create circle-api-key --data-file=- <<< "your_circle_api_key"
gcloud secrets create entity-secret --data-file=- <<< "your_entity_secret"
gcloud secrets create mcp-auth-token --data-file=- <<< "your_auth_token"
gcloud secrets create mcp-jwt-secret --data-file=- <<< "your_jwt_secret"
gcloud secrets create omniagentpay-webhook-secret --data-file=- <<< "your_webhook_secret"
```

## Deployment Methods

### Method 1: Using Deployment Script (Recommended)

```bash
# Make script executable
chmod +x deploy.sh

# Set environment variables
export GCP_PROJECT_ID="your-project-id"
export GCP_REGION="us-central1"
export SERVICE_NAME="omniagentpay-mcp-server"

# Deploy
./deploy.sh
```

### Method 2: Using Cloud Build (Automated CI/CD)

```bash
# Submit build to Cloud Build
gcloud builds submit --config cloudbuild.yaml \
  --substitutions _SERVICE_NAME=omniagentpay-mcp-server,_REGION=us-central1
```

### Method 3: Manual Deployment

```bash
# Build and push image
docker build -t gcr.io/YOUR_PROJECT_ID/omniagentpay-mcp-server .
docker push gcr.io/YOUR_PROJECT_ID/omniagentpay-mcp-server

# Deploy to Cloud Run
gcloud run deploy omniagentpay-mcp-server \
  --image gcr.io/YOUR_PROJECT_ID/omniagentpay-mcp-server \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --set-env-vars ENVIRONMENT=prod
```

## Configure Secrets

After deployment, attach secrets to your Cloud Run service:

```bash
gcloud run services update omniagentpay-mcp-server \
  --region us-central1 \
  --update-secrets=CIRCLE_API_KEY=circle-api-key:latest,ENTITY_SECRET=entity-secret:latest,MCP_AUTH_TOKEN=mcp-auth-token:latest
```

Or set environment variables directly:

```bash
gcloud run services update omniagentpay-mcp-server \
  --region us-central1 \
  --set-env-vars \
    ENVIRONMENT=prod,\
    CIRCLE_API_KEY=your_key,\
    ENTITY_SECRET=your_secret,\
    MCP_AUTH_TOKEN=your_token,\
    OMNIAGENTPAY_DAILY_BUDGET=1000.0,\
    OMNIAGENTPAY_HOURLY_BUDGET=200.0,\
    OMNIAGENTPAY_TX_LIMIT=500.0
```

## Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe omniagentpay-mcp-server \
  --region us-central1 \
  --format 'value(status.url)')

# Test health endpoint
curl ${SERVICE_URL}/health

# Test MCP endpoint (with auth)
curl -X POST ${SERVICE_URL}/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}'
```

## Configuration Options

### Resource Limits

Adjust in `cloudbuild.yaml` or deployment command:

- **Memory**: `--memory 512Mi` (512Mi, 1Gi, 2Gi, 4Gi, 8Gi)
- **CPU**: `--cpu 1` (1, 2, 4, 6, 8)
- **Timeout**: `--timeout 300` (seconds, max 3600)
- **Min Instances**: `--min-instances 0` (0 for scale-to-zero, 1+ for always-on)
- **Max Instances**: `--max-instances 10` (auto-scaling limit)

### Environment Variables

Required for production:
- `ENVIRONMENT=prod`
- `CIRCLE_API_KEY`
- `ENTITY_SECRET`
- `MCP_AUTH_TOKEN` or `MCP_JWT_SECRET`
- `OMNIAGENTPAY_WEBHOOK_SECRET` (if using webhooks)
- `OMNIAGENTPAY_MERCHANT_ID` (if using webhooks)

Optional guard policies:
- `OMNIAGENTPAY_DAILY_BUDGET=1000.0`
- `OMNIAGENTPAY_HOURLY_BUDGET=200.0`
- `OMNIAGENTPAY_TX_LIMIT=500.0`
- `OMNIAGENTPAY_RATE_LIMIT_PER_MIN=5`
- `OMNIAGENTPAY_WHITELISTED_RECIPIENTS=addr1,addr2`

## Monitoring

### View Logs

```bash
gcloud run services logs read omniagentpay-mcp-server \
  --region us-central1 \
  --limit 50
```

### View Metrics

```bash
# Open Cloud Console
gcloud run services describe omniagentpay-mcp-server \
  --region us-central1
```

## Troubleshooting

### Service won't start

1. Check logs: `gcloud run services logs read omniagentpay-mcp-server --region us-central1`
2. Verify environment variables are set correctly
3. Check that secrets are accessible
4. Ensure PORT environment variable is available (Cloud Run sets this automatically)

### Authentication errors

1. Verify `MCP_AUTH_TOKEN` or `MCP_JWT_SECRET` is set
2. Check that `MCP_AUTH_ENABLED=true` (default)
3. Ensure Authorization header is included in requests

### Payment API errors

1. Verify `CIRCLE_API_KEY` and `ENTITY_SECRET` are correct
2. Check Circle API status
3. Review payment guard policies

## Cost Optimization

- Use **scale-to-zero** (`--min-instances 0`) for development
- Set **min-instances 1** only if you need always-on
- Adjust **memory** based on actual usage (start with 512Mi)
- Use **CPU throttling** for non-CPU intensive workloads
- Monitor usage in Cloud Console

## Security Best Practices

1. **Use Secret Manager** for sensitive values (API keys, tokens)
2. **Enable authentication** (`MCP_AUTH_ENABLED=true`)
3. **Use HTTPS only** (Cloud Run provides this automatically)
4. **Set guard policies** to limit payment amounts
5. **Monitor access logs** regularly
6. **Rotate secrets** periodically

## Next Steps

- Set up **Cloud Build triggers** for automatic deployments
- Configure **custom domain** mapping
- Set up **alerting** for errors and high latency
- Enable **Cloud CDN** for better performance
- Configure **VPC connector** if accessing private resources
