"""
Ad Intelligence Agent - HTTP API Server
Provides REST API endpoints for the ad intelligence pipeline
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uvicorn
import structlog
import json
from pathlib import Path

from src.collection.collectors.meta_ad_library import MetaAdLibraryCollector
from src.collection.collectors.mock_collector import MockAdCollector
from src.collection.collectors.meta_web_scraper import MetaWebScraper
from src.collection.collectors.base_collector import CollectionConfig
from src.preprocessing.pipeline import PreprocessingPipeline
from src.classification.pipeline import ClassificationPipeline
from src.analysis.performance_analyzer import PerformanceAnalyzer
from src.analysis.report_generator import ReportGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Ad Intelligence Agent API",
    description="AI Agent for competitor ad intelligence and analysis",
    version="1.0.0"
)

logger = structlog.get_logger()

# Agent metadata
AGENT_INFO = {
    "agent_id": "ad-intelligence-agent-001",
    "name": "Ad Intelligence Agent",
    "version": "1.0.0",
    "capabilities": [
        "ad_collection",
        "ad_preprocessing",
        "ad_classification",
        "competitor_analysis"
    ],
    "supported_platforms": ["meta", "metaweb", "mock"],
    "status": "healthy"
}


# ============================================================================
# REQUEST/RESPONSE MODELS (JSON Contract)
# ============================================================================

class AdCollectionRequest(BaseModel):
    """Request model for ad collection"""
    keywords: List[str] = Field(..., description="Keywords to search for", min_items=1)
    platform: str = Field(default="metaweb", description="Platform to collect from (meta, metaweb, mock)")
    max_results: int = Field(default=10, description="Maximum number of ads to collect", ge=1, le=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "keywords": ["Nike", "Adidas"],
                "platform": "metaweb",
                "max_results": 20
            }
        }


class AdData(BaseModel):
    """Model for a single ad"""
    ad_id: str
    platform: str
    headline: Optional[str]
    body_text: Optional[str]
    brand_name: Optional[str]
    collected_at: str
    preprocessed: bool = False
    classified: bool = False
    classification_results: Optional[Dict[str, Any]] = None


class AdCollectionResponse(BaseModel):
    """Response model for ad collection"""
    success: bool
    message: str
    total_collected: int
    total_preprocessed: int
    total_classified: int
    ads: List[Dict[str, Any]]
    execution_time_seconds: float
    timestamp: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully collected and processed 10 ads",
                "total_collected": 10,
                "total_preprocessed": 10,
                "total_classified": 10,
                "ads": [],
                "execution_time_seconds": 15.5,
                "timestamp": "2024-11-23T14:30:00Z"
            }
        }


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    agent_id: str
    version: str
    timestamp: str
    uptime_seconds: float
    capabilities: List[str]


class RegistrationRequest(BaseModel):
    """Request to register with supervisor"""
    supervisor_url: str = Field(..., description="URL of the supervisor service")


# ============================================================================
# GLOBAL STATE
# ============================================================================

start_time = datetime.utcnow()
supervisor_url: Optional[str] = None


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint - returns agent information"""
    return {
        "message": "Ad Intelligence Agent API",
        "version": AGENT_INFO["version"],
        "status": "running",
        "endpoints": {
            "health": "/health",
            "collect": "/api/v1/collect",
            "register": "/api/v1/register",
            "docs": "/docs"
        }
    }


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return HealthCheckResponse(
        status="healthy",
        agent_id=AGENT_INFO["agent_id"],
        version=AGENT_INFO["version"],
        timestamp=datetime.utcnow().isoformat(),
        uptime_seconds=uptime,
        capabilities=AGENT_INFO["capabilities"]
    )


@app.post("/api/v1/collect", response_model=AdCollectionResponse)
async def collect_ads(request: AdCollectionRequest):
    """
    Main endpoint to collect and process ads
    
    This endpoint:
    1. Collects ads from specified platform
    2. Preprocesses the ads
    3. Classifies the ads
    4. Analyzes performance and generates insights
    5. Returns structured results with reports
    """
    start = datetime.utcnow()
    
    try:
        logger.info("Received ad collection request", 
                   keywords=request.keywords,
                   platform=request.platform,
                   max_results=request.max_results)
        
        # Validate platform
        if request.platform not in AGENT_INFO["supported_platforms"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported platform: {request.platform}. Supported: {AGENT_INFO['supported_platforms']}"
            )
        
        # 1. Data Collection
        config = CollectionConfig(
            platform=request.platform,
            keywords=request.keywords,
            max_results=request.max_results,
            rate_limit_per_second=0.5
        )
        
        if request.platform == 'meta':
            collector = MetaAdLibraryCollector(config)
        elif request.platform == 'metaweb':
            collector = MetaWebScraper(config)
        elif request.platform == 'mock':
            collector = MockAdCollector(config)
        else:
            raise HTTPException(status_code=400, detail=f"Platform {request.platform} not implemented")
        
        raw_ads = collector.run()
        logger.info(f"Collected {len(raw_ads)} ads")
        
        # 2. Preprocessing
        preprocessing = PreprocessingPipeline()
        preprocessed_ads = preprocessing.preprocess_batch(raw_ads, max_workers=4)
        logger.info(f"Preprocessed {len(preprocessed_ads)} ads")
        
        # 3. Classification
        classification = ClassificationPipeline()
        classified_ads = classification.classify_batch(preprocessed_ads, max_workers=4)
        logger.info(f"Classified {len(classified_ads)} ads")
        
        # 4. Performance Analysis
        analyzer = PerformanceAnalyzer()
        analysis_results = analyzer.analyze_batch(classified_ads)
        logger.info("Performance analysis complete")
        
        # 5. Generate Reports
        report_gen = ReportGenerator()
        report_paths = report_gen.generate_all_reports(analysis_results)
        logger.info(f"Generated reports: {list(report_paths.keys())}")
        
        # Calculate execution time
        execution_time = (datetime.utcnow() - start).total_seconds()
        
        # Build response with analysis results
        response = AdCollectionResponse(
            success=True,
            message=f"Successfully collected and processed {len(classified_ads)} ads",
            total_collected=len(raw_ads),
            total_preprocessed=len(preprocessed_ads),
            total_classified=len(classified_ads),
            ads=analysis_results['analyzed_ads'],
            execution_time_seconds=execution_time,
            timestamp=datetime.utcnow().isoformat()
        )
        
        # Add analysis results to response
        response_dict = response.dict()
        response_dict['analysis'] = {
            'summary': analysis_results['summary'],
            'insights': analysis_results['insights'],
            'high_performers': analysis_results['high_performers'][:5],  # Top 5
            'low_performers': analysis_results['low_performers'][:5],    # Bottom 5
        }
        response_dict['reports'] = report_paths
        
        logger.info("Request completed successfully", 
                   total_ads=len(classified_ads),
                   execution_time=execution_time)
        
        return JSONResponse(content=response_dict)
        
    except Exception as e:
        logger.error("Error processing request", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/register")
async def register_with_supervisor(request: RegistrationRequest):
    """Register this agent with a supervisor/registry service"""
    global supervisor_url
    
    try:
        import requests
        
        # Store supervisor URL
        supervisor_url = request.supervisor_url
        
        # Send registration request to supervisor
        registration_data = {
            "agent_id": AGENT_INFO["agent_id"],
            "name": AGENT_INFO["name"],
            "version": AGENT_INFO["version"],
            "capabilities": AGENT_INFO["capabilities"],
            "health_check_url": "http://localhost:8000/health",
            "api_url": "http://localhost:8000/api/v1/collect",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = requests.post(
            f"{supervisor_url}/register",
            json=registration_data,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("Successfully registered with supervisor", supervisor_url=supervisor_url)
            return {
                "success": True,
                "message": "Successfully registered with supervisor",
                "supervisor_url": supervisor_url
            }
        else:
            logger.error("Failed to register with supervisor", 
                        status_code=response.status_code,
                        response=response.text)
            raise HTTPException(
                status_code=500,
                detail=f"Supervisor returned status {response.status_code}"
            )
            
    except requests.exceptions.RequestException as e:
        logger.error("Failed to connect to supervisor", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to supervisor: {str(e)}"
        )


@app.get("/api/v1/status")
async def get_status():
    """Get detailed agent status"""
    uptime = (datetime.utcnow() - start_time).total_seconds()
    
    return {
        "agent_info": AGENT_INFO,
        "uptime_seconds": uptime,
        "supervisor_url": supervisor_url,
        "registered": supervisor_url is not None,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Ad Intelligence Agent API starting up", 
               version=AGENT_INFO["version"],
               agent_id=AGENT_INFO["agent_id"])


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Ad Intelligence Agent API shutting down")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
