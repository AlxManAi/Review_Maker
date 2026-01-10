"""
Schemas - Pydantic models for data validation and API I/O
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl


class ReviewBase(BaseModel):
    """Base schema for Review."""
    product_name: str
    product_url: Optional[str] = None
    content: str
    pros: Optional[str] = None
    cons: Optional[str] = None
    author: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    target_date: Optional[datetime] = None
    is_used: bool = False


class ReviewCreate(ReviewBase):
    """Schema for creating a review."""
    pass


class ReviewUpdate(ReviewBase):
    """Schema for updating a review."""
    pass


class ReviewResponse(ReviewBase):
    """Schema for reading a review (includes DB ID)."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerationRequest(BaseModel):
    """Request schema for generating reviews."""
    product_query: str
    product_url: Optional[str] = None
    total_reviews: int
    start_date: date
    end_date: date
    # Optional manual overrides
    keywords: Optional[List[str]] = None
