# API Testing Guide

## Starting the Server Locally

### Prerequisites
- Python 3.11.9 installed
- Virtual environment activated

### Quick Start

```powershell
# Navigate to project directory
cd "C:\Users\HUAWEI\Desktop\Semester 7\SPM\SPM Project Final"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start the server
python api_server.py
```

Server will start at: `http://localhost:8000`

---

## API Endpoints

### 1. Health Check
**GET** `http://localhost:8000/health`

No body required.

---

### 2. Root Status
**GET** `http://localhost:8000/`

No body required.

---

### 3. Agent Status
**GET** `http://localhost:8000/api/v1/status`

No body required.

---

## Collect Ads Endpoint

**POST** `http://localhost:8000/api/v1/collect`

Content-Type: `application/json`

---

### Mock Data Collection (Recommended for Testing)

Ultra-realistic mock data with:
- 80+ brands across 7 industries
- Realistic ad IDs (Facebook, Google Ads, LinkedIn formats)
- Authentic engagement metrics (CPM, CTR, CPC, conversions)
- Realistic scraping delays (0.8-2.5s per ad)

**Request Body:**
```json
{
  "keywords": ["Nike", "Adidas"],
  "platform": "mock",
  "max_results": 10
}
```

**Alternative Keywords:**
```json
{
  "keywords": ["Apple", "Samsung", "Sony"],
  "platform": "mock",
  "max_results": 5
}
```

```json
{
  "keywords": ["McDonald's", "Starbucks"],
  "platform": "mock",
  "max_results": 8
}
```

```json
{
  "keywords": ["BMW", "Tesla", "Toyota"],
  "platform": "mock",
  "max_results": 15
}
```

---

### Real Web Scraping (Works Locally Only)

Uses Selenium + Chrome WebDriver to scrape Meta Ad Library.

**Request Body:**
```json
{
  "keywords": ["Nike"],
  "platform": "metaweb",
  "max_results": 5
}
```

**Note:** Real web scraping:
- ✅ Works on local machine (requires Chrome/Selenium)
- ❌ Does NOT work on Render/Railway free tiers (no Chrome available)
- Takes longer to execute (3-10s per ad)

---

## Thunder Client Collections

### Collection 1: Basic Health Checks
```json
{
  "name": "Ad Intelligence Agent - Health",
  "requests": [
    {
      "name": "Health Check",
      "method": "GET",
      "url": "http://localhost:8000/health"
    },
    {
      "name": "Root Status",
      "method": "GET",
      "url": "http://localhost:8000/"
    },
    {
      "name": "Agent Status",
      "method": "GET",
      "url": "http://localhost:8000/api/v1/status"
    }
  ]
}
```

### Collection 2: Mock Data Testing
```json
{
  "name": "Ad Intelligence Agent - Mock Collection",
  "requests": [
    {
      "name": "Collect Nike Ads (Mock)",
      "method": "POST",
      "url": "http://localhost:8000/api/v1/collect",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "keywords": ["Nike", "Adidas"],
        "platform": "mock",
        "max_results": 10
      }
    },
    {
      "name": "Collect Tech Ads (Mock)",
      "method": "POST",
      "url": "http://localhost:8000/api/v1/collect",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "keywords": ["Apple", "Samsung", "Sony"],
        "platform": "mock",
        "max_results": 8
      }
    },
    {
      "name": "Collect Food Ads (Mock)",
      "method": "POST",
      "url": "http://localhost:8000/api/v1/collect",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "keywords": ["McDonald's", "Starbucks", "Subway"],
        "platform": "mock",
        "max_results": 12
      }
    }
  ]
}
```

### Collection 3: Real Web Scraping (Local Only)
```json
{
  "name": "Ad Intelligence Agent - Real Scraping",
  "requests": [
    {
      "name": "Scrape Nike Ads (Real)",
      "method": "POST",
      "url": "http://localhost:8000/api/v1/collect",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "keywords": ["Nike"],
        "platform": "metaweb",
        "max_results": 5
      }
    },
    {
      "name": "Scrape Apple Ads (Real)",
      "method": "POST",
      "url": "http://localhost:8000/api/v1/collect",
      "headers": {
        "Content-Type": "application/json"
      },
      "body": {
        "keywords": ["Apple"],
        "platform": "metaweb",
        "max_results": 3
      }
    }
  ]
}
```

---

## Testing on Deployed Servers

### Render Deployment
Replace `http://localhost:8000` with:
```
https://spm-project-final.onrender.com
```

### Railway Deployment
Replace `http://localhost:8000` with:
```
https://spm-project-final-production.up.railway.app
```

**Note:** Only `mock` platform works on deployed servers. Real scraping (`metaweb`) requires Chrome/Selenium.

---

## Expected Response Structure

```json
{
  "success": true,
  "message": "Successfully collected and processed 10 ads",
  "total_collected": 10,
  "total_preprocessed": 10,
  "total_classified": 10,
  "ads": [
    {
      "ad_id": "419387494676223629",
      "performance_score": 0.0,
      "roi": 0.0,
      "classifications": {
        "ad_format": {
          "label": "text_only",
          "confidence": 0.85,
          "alternatives": [],
          "reasoning": "No media detected"
        }
      },
      "extracted_features": {
        "keywords": [],
        "entities": [],
        "call_to_action_type": "other",
        "has_urgency_indicators": false,
        "has_pricing": false,
        "has_social_proof": false
      }
    }
  ],
  "execution_time_seconds": 9.43,
  "timestamp": "2025-12-04T21:50:00+00:00",
  "analysis": {
    "summary": {
      "total_ads": 10,
      "average_performance_score": 0.0,
      "median_performance_score": 0.0,
      "average_roi": 0,
      "high_performers_count": 10,
      "low_performers_count": 10
    },
    "insights": {
      "alerts": [],
      "recommendations": [],
      "trends": {}
    }
  },
  "reports": {
    "json": "reports/report_20251204_215000.json",
    "csv": "reports/report_20251204_215000.csv"
  }
}
```

---

## Realistic Mock Data Features

✅ **Ad IDs**: Facebook (18-digit), Google Ads (gad_xxx_xxx), LinkedIn (13-digit)  
✅ **Brands**: 80+ real brands (Nike, Apple, BMW, Starbucks, etc.)  
✅ **Industries**: Sports, Technology, Retail, Food, Automotive, Beauty, Finance  
✅ **Metrics**: CPM-based impressions, CTR (0.5-5%), CPC, conversions (1-15%)  
✅ **Delays**: 0.8-2.5s per ad (simulates real scraping)  
✅ **Content**: 70+ realistic headlines, 25+ body texts with social proof  
✅ **Targeting**: Age ranges, gender, regions, platforms (FB, IG, Messenger)

---

## Troubleshooting

### Server won't start
```powershell
# Check if port 8000 is in use
Get-Process -Name python -ErrorAction SilentlyContinue | Stop-Process -Force

# Restart server
python api_server.py
```

### Import errors
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

### Real scraping fails
- Ensure Chrome browser is installed
- Check if ChromeDriver is accessible
- Use `mock` platform instead for testing

---

## API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
