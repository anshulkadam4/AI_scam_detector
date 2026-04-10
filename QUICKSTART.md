# 🚀 QUICKSTART: Deploy in 5 Minutes

## Choose Your Path

### 🟢 Path 1: Streamlit Cloud (EASIEST - FREE)
**Time**: 2-3 minutes | **Cost**: $0 | **Effort**: ⭐

```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for production"
git push origin main

# 2. Go to https://share.streamlit.io
# 3. Click "New app" → Select your repo → Deploy
# Done! Your app is live 🎉
```

**URL**: `https://ai-scam-detector.streamlit.app` (example)

---

### 🔵 Path 2: Azure (FREE TIER - 12 months)
**Time**: 10 minutes | **Cost**: $0 (then $10/mo) | **Effort**: ⭐⭐

```bash
# 1. Install Azure CLI
# Windows: choco install azure-cli
# Mac: brew install azure-cli

# 2. Login to Azure
az login

# 3. Run deployment script
bash deploy-azure.sh
# (Update REGISTRY_USERNAME and REGISTRY_PASSWORD)

# Your app URL will be printed
```

---

### 🟠 Path 3: Docker Hub + Azure Container Instances
**Time**: 5 minutes | **Cost**: $11/month | **Effort**: ⭐⭐⭐

```bash
# 1. Build Docker image
docker build -t <your-username>/ai-scam-detector .

# 2. Push to Docker Hub
docker login
docker push <your-username>/ai-scam-detector

# 3. Deploy to Azure
az container create \
  --resource-group scam-detector-rg \
  --name ai-scam-detector \
  --image <your-username>/ai-scam-detector:latest \
  --ports 8501 \
  --dns-name-label ai-scam-detector \
  --cpu 1 --memory 1
```

---

## Recommended for Production

| Scenario | Recommendation |
|----------|---|
| Quick demo / testing | **Streamlit Cloud** ✅ |
| Learning Azure | **Azure F1 Free Tier** |
| Production with auto-scaling | **Azure App Service B1+** |
| 24/7 high-traffic app | **Azure Container Instances or Kubernetes** |

---

## After Deployment

1. **Test your app**: Visit the URL and test message detection
2. **Share with others**: Send them the app URL
3. **Monitor performance**: Check logs in your deployment platform
4. **Scale if needed**: Upgrade to a paid tier for more resources

---

## Troubleshooting

**"Container won't start"**
```bash
# Check logs
docker logs <container_id>

# Or for Azure
az container logs --resource-group scam-detector-rg --name ai-scam-detector
```

**"Port already in use"**
```bash
docker run -p 8502:8501 ai-scam-detector
```

**"Module not found errors"**
```bash
pip install -r requirements.txt
```

---

## Need Help?

- **Streamlit Cloud Issues**: https://docs.streamlit.io/
- **Azure Issues**: https://learn.microsoft.com/azure/
- **Docker Issues**: https://docs.docker.com/
