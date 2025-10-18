#!/bin/bash
# Deploy to Google Cloud Run

PROJECT_ID="your-project-id"
SERVICE_NAME="tx-backend"
REGION="europe-west1"
IMAGE="jeanpaulkadusimanegaberobert1/tx-backend:v1.0.3-20251018-225528"

# Deploy to Cloud Run
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=5000 \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=10 \
  --set-env-vars="ENVIRONMENT=production" \
  --set-env-vars="PORT=5000"

echo "Deployed to Cloud Run!"
echo "URL: https://$SERVICE_NAME-<hash>-$REGION.run.app"
