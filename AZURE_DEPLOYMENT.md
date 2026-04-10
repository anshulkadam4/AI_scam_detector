# Azure Deployment Guide

## Option 1: Streamlit Cloud (Recommended - FREE, Easiest)

### Prerequisites
- GitHub account
- Streamlit account (free)

### Steps

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-scam-detector.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Select your repository and branch
   - Set main file path to `app.py`
   - Click "Deploy"

3. **Your app is live!** 🎉
   - You'll get a public URL like: `https://ai-scam-detector.streamlit.app`
   - Share it with anyone

**Cost**: FREE (always)
**Deployment time**: 2-3 minutes
**Scaling**: Automatic

---

## Option 2: Azure App Service (F1 Free Tier)

### Prerequisites
- Azure account (sign up for [free $200 credits](https://azure.microsoft.com/free/))
- Azure CLI installed ([download](https://learn.microsoft.com/cli/azure/install-azure-cli))
- Docker installed

### Steps

1. **Login to Azure:**
   ```bash
   az login
   ```

2. **Create resource group:**
   ```bash
   az group create \
     --name scam-detector-rg \
     --location eastus
   ```

3. **Create App Service Plan (Free tier):**
   ```bash
   az appservice plan create \
     --name scam-detector-plan \
     --resource-group scam-detector-rg \
     --sku F1 \
     --is-linux
   ```

4. **Create Web App:**
   ```bash
   az webapp create \
     --resource-group scam-detector-rg \
     --plan scam-detector-plan \
     --name ai-scam-detector-$RANDOM \
     --deployment-container-image-name mcr.microsoft.com/appsvc/staticsite:latest
   ```

5. **Build and push Docker image to Docker Hub:**
   ```bash
   docker build -t <your-docker-username>/ai-scam-detector .
   docker login
   docker push <your-docker-username>/ai-scam-detector
   ```

6. **Configure Web App for Docker:**
   ```bash
   az webapp config container set \
     --name <your-app-name> \
     --resource-group scam-detector-rg \
     --docker-custom-image-name <your-docker-username>/ai-scam-detector:latest \
     --docker-registry-server-url https://index.docker.io
   ```

7. **Configure app settings:**
   ```bash
   az webapp config appsettings set \
     --name <your-app-name> \
     --resource-group scam-detector-rg \
     --settings \
       WEBSITES_ENABLE_APP_SERVICE_STORAGE=false \
       STREAMLIT_SERVER_PORT=8501 \
       STREAMLIT_SERVER_ADDRESS=0.0.0.0
   ```

**Cost**: FREE for 12 months (F1 tier = 60 minutes/day, limited RAM)
**After free period**: ~$10/month
**Deployment time**: 5-10 minutes
**Note**: F1 tier has 60-minute daily compute limit - suitable for testing

---

## Option 3: Azure Container Instances (Pay-as-you-go)

### Prerequisites
- Azure account
- Azure CLI
- Docker image in Docker Hub

### Steps

1. **Create Azure Container Registry (optional but recommended):**
   ```bash
   az acr create \
     --resource-group scam-detector-rg \
     --name scamdetectorregistry \
     --sku Basic
   ```

2. **Deploy container:**
   ```bash
   az container create \
     --resource-group scam-detector-rg \
     --name ai-scam-detector \
     --image <docker-username>/ai-scam-detector:latest \
     --ports 8501 \
     --environment-variables \
       STREAMLIT_SERVER_PORT=8501 \
       STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
     --cpu 1 \
     --memory 1 \
     --dns-name-label ai-scam-detector
   ```

3. **Get the URL:**
   ```bash
   az container show \
     --resource-group scam-detector-rg \
     --name ai-scam-detector \
     --query ipAddress.fqdn \
     --output tsv
   ```

**Cost**: ~$0.0015/hour = ~$11/month (if running 24/7)
**Deployment time**: 2-3 minutes
**Scaling**: Manual or via orchestration

---

## Comparison Table

| Feature | Streamlit Cloud | Azure F1 | Azure Container |
|---------|---|---|---|
| Cost | FREE | FREE (12mo) | $~11/month |
| Setup Time | 2 min | 10 min | 5 min |
| Compute Limit | Unlimited | 60 min/day | Unlimited |
| Custom Domain | Yes | Yes | Yes |
| Auto-scaling | Yes | No | Manual |
| **Recommended** | ✅ YES | Good for testing | Production |

---

## Troubleshooting

### Azure CLI Error: "command not found"
```bash
# Install Azure CLI
# Windows: https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows
# Mac: brew install azure-cli
# Linux: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
```

### Docker push fails
```bash
docker login
# Enter your Docker Hub username and password
docker push <username>/ai-scam-detector
```

### Container won't start on Azure
```bash
# Check logs
az container logs \
  --resource-group scam-detector-rg \
  --name ai-scam-detector
```

### Port 8501 not accessible
- Azure App Service needs to listen on `0.0.0.0:8501`
- Already configured in `.streamlit/config.toml`

---

## Next Steps After Deployment

1. **Monitor:** Set up Azure alerts for your container
2. **Custom Domain:** Map your domain (cloudflare/DNS settings)
3. **HTTPS:** Azure provides free SSL/TLS certificates
4. **Logging:** Enable Application Insights for better monitoring
5. **Backup:** Enable automatic backups for data

---

## Cost Estimates (Monthly)

- **Streamlit Cloud**: $0 (FREE)
- **Azure F1**: $0-10 (12 months free, then $10)
- **Azure Container Instances**: $8-15 (depends on uptime)
- **Azure App Service B1**: $13-15 (paid tier, more reliable)

**Recommendation**: Start with **Streamlit Cloud** (free, no setup), upgrade to Azure if you need more control.
