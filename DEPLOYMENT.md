# 🚀 Deployment Guide

## Quick Deployment (5 minutes)

### Option 1: Streamlit Cloud (Recommended - Easiest)

1. **Push to GitHub**
```bash
git init
git add .
git commit -m "Initial commit: Railway Signal Failure Predictor"
git remote add origin https://github.com/yourusername/railway-signal-failure.git
git push -u origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to https://streamlit.io/cloud
   - Click "New app"
   - Select your GitHub repo
   - Deploy!
   - Your app lives at: `https://yourusername-railway.streamlit.app`

**Cost:** Free tier available (with limitations)
**Setup time:** 2 minutes

---

### Option 2: Local Deployment

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py

# Access at: http://localhost:8501
```

**Perfect for:** Testing, internal use, development

---

### Option 3: Heroku Deployment

1. **Create Procfile**
```bash
echo "web: streamlit run --logger.level=error --client.showErrorDetails=false --client.toolbarMode=minimal app.py" > Procfile
```

2. **Create setup.sh**
```bash
mkdir -p ~/.streamlit/
echo "[theme]" > ~/.streamlit/config.toml
echo "primaryColor = \"#3B82F6\"" >> ~/.streamlit/config.toml
echo "backgroundColor = \"#FFFFFF\"" >> ~/.streamlit/config.toml
```

3. **Deploy**
```bash
heroku login
heroku create your-app-name
git push heroku main
```

**Cost:** $7/month (hobby dyno)
**Setup time:** 10 minutes

---

### Option 4: Docker Deployment

1. **Create Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

2. **Build and Run**
```bash
docker build -t railway-predictor .
docker run -p 8501:8501 railway-predictor
```

**Perfect for:** Production, scalable deployment, microservices

---

## Production Integration

### API Integration (For Real Systems)

If integrating with Network Rail systems, convert to FastAPI:

```python
# api.py
from fastapi import FastAPI
import joblib
from pydantic import BaseModel

app = FastAPI()

model = joblib.load('models/repair_time_model.pkl')
scaler = joblib.load('models/scaler.pkl')

class PredictionRequest(BaseModel):
    failure_type: str
    location: str
    weather: str
    temperature: int
    hour: int
    is_peak: bool
    is_weekend: bool

@app.post("/predict")
def predict(request: PredictionRequest):
    # ... prediction logic ...
    return {"repair_time_minutes": 90, "confidence": 19}

# Run: uvicorn api:app --reload
```

---

## Deployment Checklist

- [ ] All files committed to Git
- [ ] requirements.txt updated
- [ ] Model files included
- [ ] README with instructions
- [ ] Environment variables configured (if needed)
- [ ] .gitignore properly set up
- [ ] No sensitive data in code
- [ ] Local testing complete
- [ ] Dependencies tested on clean environment
- [ ] Documentation updated

---

## Environment Variables

If deploying to production, add these:

```bash
# .env
API_KEY=your_network_rail_api_key
DATABASE_URL=postgresql://...
LOG_LEVEL=INFO
```

---

## Monitoring & Maintenance

### Logs
```bash
# View Streamlit logs
tail -f logs/streamlit.log

# View app performance
streamlit logger config show
```

### Model Updates
To retrain with new data:
```bash
python scripts/train_model.py
git add models/
git commit -m "Update model with latest data"
git push
```

### Health Check
```bash
curl https://your-app.streamlit.app  # Should return 200 OK
```

---

## Troubleshooting

### "Model file not found"
```bash
# Check file exists
ls -la models/repair_time_model.pkl

# Add to git
git add models/
git lfs install  # If files > 100MB
```

### "ModuleNotFoundError"
```bash
# Reinstall requirements
pip install -r requirements.txt --upgrade
```

### App runs slowly
- Check file size (models should be <10MB)
- Cache data with @st.cache_resource
- Reduce data size if needed

---

## Security

- [ ] Don't commit API keys (use .env)
- [ ] Validate all user inputs
- [ ] Use HTTPS for all connections
- [ ] Implement rate limiting for API
- [ ] Don't expose model internals
- [ ] Log predictions for audit trail

---

## Scaling

For high traffic (100+ predictions/hour):
1. Use FastAPI instead of Streamlit
2. Add caching layer (Redis)
3. Containerize with Docker
4. Deploy on Kubernetes
5. Monitor with Prometheus/Grafana

---

## Support

- **Documentation:** See README.md
- **Issues:** GitHub issues
- **Questions:** Open a discussion
- **Bugs:** Submit with logs and reproduction steps
