#!/bin/bash
# Azure Deployment Script for App Service

# Variables
RESOURCE_GROUP="scam-detector-rg"
APP_SERVICE_PLAN="scam-detector-plan"
APP_NAME="ai-scam-detector-$(date +%s)"
LOCATION="eastus"
IMAGE_NAME="ai-scam-detector"
REGISTRY_NAME="scamdetectorregistry"

echo "🚀 Starting Azure deployment..."

# 1. Create resource group
echo "📁 Creating resource group..."
az group create \
    --name $RESOURCE_GROUP \
    --location $LOCATION

# 2. Create App Service Plan (F1 = Free tier)
echo "📋 Creating App Service Plan..."
az appservice plan create \
    --name $APP_SERVICE_PLAN \
    --resource-group $RESOURCE_GROUP \
    --sku F1 \
    --is-linux

# 3. Create Web App
echo "🌐 Creating Web App..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan $APP_SERVICE_PLAN \
    --name $APP_NAME \
    --deployment-container-image-name nginx

# 4. Configure container settings
echo "⚙️  Configuring container..."
az webapp config container set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --docker-custom-image-name "$IMAGE_NAME:latest" \
    --docker-registry-server-url "https://$REGISTRY_NAME.azurecr.io" \
    --docker-registry-server-user "$REGISTRY_USERNAME" \
    --docker-registry-server-password "$REGISTRY_PASSWORD"

# 5. Configure app settings
echo "🔧 Configuring app settings..."
az webapp config appsettings set \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --settings \
        WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
        STREAMLIT_SERVER_PORT=8501 \
        STREAMLIT_SERVER_ADDRESS=0.0.0.0

echo "✅ Deployment complete!"
echo "App URL: https://${APP_NAME}.azurewebsites.net"
