"""
Models - SQLAlchemy ORM models
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


class Project(Base):
    """Project model - top-level container for review campaigns."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    site_url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    periods = relationship("Period", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"


class Period(Base):
    """Period model - time-bounded campaign within a project."""
    __tablename__ = "periods"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    total_reviews_count = Column(Integer, nullable=False, default=0)  # Total reviews for this period
    status = Column(String(50), default="draft")  # draft, active, completed
    is_archived = Column(Boolean, default=False)  # Archive status
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="periods")
    product_tasks = relationship("ProductTask", back_populates="period", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="period", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Period(id={self.id}, project_id={self.project_id}, {self.start_date} to {self.end_date})>"


class ProductTask(Base):
    """ProductTask model - individual product to generate reviews for."""
    __tablename__ = "product_tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False)
    product_name = Column(String(255), nullable=False)
    review_count = Column(Integer, nullable=True)  # Can be null, will be calculated
    product_url = Column(String(500), nullable=True)
    parsed_url = Column(String(500), nullable=True)  # Found URL from parsing
    parse_status = Column(String(50), default="pending")  # pending, success, failed
    parsed_at = Column(DateTime, nullable=True)  # When parsing was done
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    period = relationship("Period", back_populates="product_tasks")
    reviews = relationship("Review", back_populates="product_task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ProductTask(id={self.id}, product='{self.product_name}', count={self.review_count})>"



class Review(Base):
    """Review model for storing generated reviews."""
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=True)
    product_task_id = Column(Integer, ForeignKey("product_tasks.id"), nullable=True)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    
    # Content
    product_name = Column(String(255), nullable=True)
    product_url = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    pros = Column(Text, nullable=True)
    cons = Column(Text, nullable=True)
    
    # Metadata
    author = Column(String(100), nullable=True)  # Author name/surname
    rating = Column(Integer, nullable=True)  # 1-5 stars
    target_date = Column(DateTime, nullable=True)  # Publication date in calendar
    source = Column(String(255), nullable=True)
    placement_url = Column(String(500), nullable=True)  # URL where review was published
    
    # Workflow
    is_approved = Column(Boolean, default=False)  # User checked "OK"
    is_published = Column(Boolean, default=False)  # User checked "Published"
    
    # System
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_generated = Column(Boolean, default=True)
    generated_at = Column(DateTime, nullable=True)  # When AI generated this review
    ai_model = Column(String(50), nullable=True)  # perplexity, mistral, deepseek
    is_used = Column(Boolean, default=False)
    
    # Relationships
    period = relationship("Period", back_populates="reviews")
    product_task = relationship("ProductTask", back_populates="reviews")
    template = relationship("Template", back_populates="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, product='{self.product_name}', date='{self.target_date}')>"


class Template(Base):
    """Template model for storing review templates."""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship to reviews
    reviews = relationship("Review", back_populates="template")
    
    def __repr__(self):
        return f"<Template(id={self.id}, name='{self.name}')>"


class ApiKey(Base):
    """API Key model for storing encrypted API keys."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    provider = Column(String(50), nullable=False, unique=True)  # openai, mistral, etc.
    key_value = Column(String(500), nullable=False)  # Should be encrypted in production
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ApiKey(id={self.id}, provider='{self.provider}')>"


class ReviewExample(Base):
    """ReviewExample model - training examples for AI learning."""
    __tablename__ = "review_examples"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Content
    product_name = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    pros = Column(Text, nullable=True)
    cons = Column(Text, nullable=True)
    
    # Metadata
    author = Column(String(100), nullable=True)  # Author name/surname
    rating = Column(Integer, nullable=True)  # 1-5 stars
    review_date = Column(DateTime, nullable=True)  # Original review date
    
    # Source tracking
    source = Column(String(50), nullable=False)  # parsed, generated, manual
    source_url = Column(String(500), nullable=True)  # URL where parsed from
    
    # Quality control
    is_good_example = Column(Boolean, default=True)  # Quality flag
    
    # System
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ReviewExample(id={self.id}, source='{self.source}', product='{self.product_name}')>"

