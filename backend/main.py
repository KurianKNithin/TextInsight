import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import AnalyzeRequest, AnalyzeResponse
from .analyzer import analyze_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("textinsight.api")

app = FastAPI(
    title="TextInsight API",
    description="Intelligent text analysis service providing summarization, sentiment analysis, keyword extraction, classification, and explanation via Claude API.",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "TextInsight API",
        "status": "online",
        "mock_mode": settings.is_mock_enabled,
        "docs_url": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "mock_mode": settings.is_mock_enabled
    }

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest):
    """
    Analyze user-provided text across 5 features:
    - Summary (2-3 sentences)
    - Sentiment (positive/negative/neutral + confidence score)
    - Keywords (top 10 keywords/phrases)
    - Classification (predefined categories)
    - Explanation (reasoning behind sentiment & classification)
    """
    text = payload.text.strip()
    if not text:
        raise HTTPException(
            status_code=400,
            detail="Input text cannot be empty or solely whitespace."
        )

    logger.info(f"Received analysis request (length: {len(text)} chars)")
    return await analyze_text(text)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
