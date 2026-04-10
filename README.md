# AI Scam Message Detector

This project classifies text messages as `spam/scam` or `safe` using machine learning and a simple Streamlit web app.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the web app
streamlit run app.py

# Or run the CLI version
python main.py
```

## Features

- Loads and trains on the `spam.csv` SMS spam dataset
- Cleans message text before vectorization
- Uses `TF-IDF` with a `Multinomial Naive Bayes` classifier
- Predicts scam probability for user-entered text
- Flags suspicious keywords such as `bank`, `otp`, `verify`, and `claim`
- Shows basic safety recommendations in the web app
- **Production-ready** with error handling, logging, and Docker support

## Files

- `app.py`: Streamlit web interface
- `main.py`: Command-line version
- `detector.py`: Shared dataset, training, and prediction logic
- `spam.csv`: Dataset used by the app
- `Dockerfile`: Container configuration for deployment
- `PRODUCTION.md`: Comprehensive production deployment guide

## Installation

```bash
pip install -r requirements.txt
```

## Run The App

```bash
streamlit run app.py
```

The web app will open at `http://localhost:8501`

## Run The CLI Version

```bash
python main.py
```

## Quick Deployment

### Streamlit Cloud (Free & Easiest)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) and deploy

### Docker (Local/Server)
```bash
docker build -t ai-scam-detector .
docker run -p 8501:8501 ai-scam-detector
```

### See [PRODUCTION.md](PRODUCTION.md) for detailed deployment options

## Workflow

1. Load the spam dataset.
2. Clean and normalize message text.
3. Convert text into numeric features using TF-IDF.
4. Train a Naive Bayes classifier.
5. Predict whether a new message is suspicious.

## Expected Outcome

Users can paste a message into the app and quickly see:

- Whether the message looks suspicious
- The estimated scam probability
- Matched suspicious keywords
- Safety recommendations for next steps

## Production Status

✅ Ready for production deployment with:
- Comprehensive error handling and logging
- Docker containerization
- GitHub Actions CI/CD pipeline
- Security configurations
- Pinned dependencies
- Configuration management

## Next Steps

1. **Deploy**: Follow [PRODUCTION.md](PRODUCTION.md) for deployment instructions
2. **Monitor**: Set up logs and monitoring for your deployment
3. **Scale**: Use Docker Compose or Kubernetes for scaling
4. **Integrate**: Add API endpoints for third-party integrations
