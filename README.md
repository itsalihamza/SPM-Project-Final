# Ad Intelligence Agent

AI-powered competitor ad intelligence and analysis system with HTTP API.

## 🚀 Features

- **Ad Collection**: Scrape competitor ads from Meta Ad Library (no authentication required)
- **Performance Analysis**: ROI calculations, performance scoring (0-100)
- **Insights & Alerts**: Automatic identification of high/low performers
- **Multiple Report Formats**: JSON, CSV, and visual dashboards
- **RESTful API**: FastAPI with JSON contracts
- **Supervisor Integration**: Registration and health check endpoints

## 📊 API Endpoints

### Health Check
```
GET /health
```

### Collect & Analyze Ads
```
POST /api/v1/collect
{
  "keywords": ["Nike", "Adidas"],
  "platform": "metaweb",
  "max_results": 20
}
```

### Interactive Documentation
Visit `/docs` for full API documentation

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python api_server.py

# Server runs on http://localhost:8000
```

## 🧪 Testing

```bash
# Run integration tests
python test_api_integration.py

# Demo analytics features
python demo_analytics.py
```

## 📦 Deployment

Deployed on Render.com with automatic HTTPS.

## 📝 Documentation

- API Docs: `/docs`
- Deployment Guide: `DEPLOYMENT_GUIDE.md`
- Full Walkthrough: See artifacts

## 🎯 Requirements Met

✅ Working AI Agent with JSON contract  
✅ HTTP API deployment  
✅ Supervisor/Registry communication  
✅ Health check endpoint  
✅ Integration tests  
✅ ROI analysis & performance scoring  
✅ Insights & alerts  
✅ JSON/CSV/Visual reports  

## 📄 License

Academic project for SPM course.
