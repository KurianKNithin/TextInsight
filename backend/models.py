from typing import Literal, List, Union
from pydantic import BaseModel, Field, model_validator

ClassificationCategory = Literal[
    "News",
    "Business",
    "Technology",
    "Entertainment",
    "Sports",
    "Personal",
    "Other",
]

SentimentLabel = Literal["positive", "negative", "neutral"]

class SentimentResult(BaseModel):
    label: SentimentLabel = Field(
        ...,
        description="Sentiment classification: positive, negative, or neutral"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 reflecting certainty of sentiment polarity"
    )

class ClassificationResult(BaseModel):
    category: ClassificationCategory = Field(
        ...,
        description="Best-fit category from the predefined taxonomy"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0 reflecting domain alignment strength"
    )

class AnalyzeRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        description="Text content to be analyzed"
    )

class AnalyzeResponse(BaseModel):
    summary: str = Field(
        ...,
        description="A high-density, informative 2-3 sentence executive summary of the provided text"
    )
    sentiment: SentimentResult = Field(
        ...,
        description="Sentiment classification and calibrated confidence score"
    )
    keywords: List[str] = Field(
        ...,
        min_length=1,
        max_length=15,
        description="Top keywords or key phrases extracted from the text"
    )
    classification: ClassificationResult = Field(
        ...,
        description="Best-fit category and calibrated classification confidence score"
    )
    explanation: str = Field(
        ...,
        description="Insightful paragraph explaining the linguistic rationale behind sentiment and classification"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_fields(cls, data):
        if isinstance(data, dict):
            # Normalize classification if returned as raw string
            cls_val = data.get("classification")
            if isinstance(cls_val, str):
                data["classification"] = {
                    "category": cls_val,
                    "confidence": 0.88
                }
            # Normalize sentiment confidence rounding
            sent_val = data.get("sentiment")
            if isinstance(sent_val, dict) and "confidence" in sent_val:
                sent_val["confidence"] = round(float(sent_val["confidence"]), 2)
            if isinstance(data.get("classification"), dict) and "confidence" in data["classification"]:
                data["classification"]["confidence"] = round(float(data["classification"]["confidence"]), 2)
        return data
