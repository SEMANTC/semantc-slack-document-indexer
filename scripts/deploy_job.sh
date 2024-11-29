#!/bin/bash
# scripts/deploy_job.sh

# Build the container
gcloud builds submit --tag gcr.io/$PROJECT_ID/document-indexer

# Deploy Cloud Run Job
gcloud run jobs create document-indexer \
    --image gcr.io/$PROJECT_ID/document-indexer \
    --region $REGION \
    --service-account $SERVICE_ACCOUNT \
    --memory 2Gi \
    --cpu 2 \
    --max-retries 3 \
    --task-timeout 10m