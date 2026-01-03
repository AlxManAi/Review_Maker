import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Добавляем корневую директорию проекта в sys.path, 
# чтобы можно было импортировать модули из core
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(root_dir))

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Импортируем ваши существующие сервисы и модели
from core.database import db
from core.models import Project, Period, ProductTask, Review
from core.ai_service import ai_service
from core.parser_service import parser_service

app = FastAPI(title="Review Generator Web API")

# Настройка CORS для работы с Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # В продакшене лучше ограничить
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Обслуживание статических файлов React
app.mount("/static", StaticFiles(directory="web/frontend/static/static"), name="static")

@app.on_event("startup")
def _startup_create_tables():
    db.create_tables()

# Pydantic модели для API
class ProjectCreate(BaseModel):
    name: str
    site_url: Optional[str] = None
    description: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    site_url: Optional[str]
    description: Optional[str]
    created_at: str

class PeriodCreate(BaseModel):
    project_id: int
    start_date: str
    end_date: str
    total_reviews_count: int = 100

class PeriodResponse(BaseModel):
    id: int
    project_id: int
    start_date: str
    end_date: str
    total_reviews_count: int
    created_at: str

class ProductCreate(BaseModel):
    period_id: int
    product_name: str
    review_count: Optional[int] = None
    product_url: Optional[str] = None

class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    review_count: Optional[int] = None
    product_url: Optional[str] = None
    is_used: Optional[bool] = None

class ProductResponse(BaseModel):
    id: int
    product_name: str
    review_count: Optional[int]
    product_url: Optional[str]
    parse_status: str
    is_used: bool

class ReviewResponse(BaseModel):
    id: int
    product_name: str
    customer_name: str
    rating: int
    date: str
    content: str
    is_approved: bool
    is_published: bool
    is_used: bool
    target_date: Optional[str] = None

# Dependency для получения сессии БД
def get_db():
    with db.get_session() as session:
        yield session

@app.get("/")
async def root():
    """Отдаем React приложение"""
    return FileResponse("web/frontend/static/index.html")

@app.get("/api")
async def api_root():
    return {"message": "Review Generator API is running"}

# === PROJECTS ===
@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects():
    """Получить список всех проектов."""
    with db.get_session() as session:
        projects = session.query(Project).all()
        return [
            {
                "id": p.id, 
                "name": p.name, 
                "site_url": p.site_url, 
                "description": p.description,
                "created_at": p.created_at.isoformat() if p.created_at else ""
            } for p in projects
        ]

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    """Создать новый проект."""
    try:
        with db.get_session() as session:
            new_project = Project(
                name=project.name,
                site_url=project.site_url,
                description=project.description
            )
            session.add(new_project)
            session.commit()
            session.refresh(new_project)
            
            return {
                "id": new_project.id,
                "name": new_project.name,
                "site_url": new_project.site_url,
                "description": new_project.description,
                "created_at": new_project.created_at.isoformat()
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/projects/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int):
    """Получить один проект (для отображения имени проекта в заголовках)."""
    with db.get_session() as session:
        p = session.query(Project).get(project_id)
        if not p:
            raise HTTPException(status_code=404, detail="Project not found")
        return {
            "id": p.id,
            "name": p.name,
            "site_url": p.site_url,
            "description": p.description,
            "created_at": p.created_at.isoformat() if p.created_at else "",
        }

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int):
    """Удалить проект (каскадно удалит периоды/товары/отзывы)."""
    try:
        with db.get_session() as session:
            p = session.query(Project).get(project_id)
            if not p:
                raise HTTPException(status_code=404, detail="Project not found")
            session.delete(p)
            session.commit()
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    site_url: Optional[str] = None
    description: Optional[str] = None

@app.patch("/api/projects/{project_id}")
async def update_project(project_id: int, project: ProjectUpdate):
    """Обновить проект (inline редактирование)."""
    try:
        with db.get_session() as session:
            p = session.query(Project).get(project_id)
            if not p:
                raise HTTPException(status_code=404, detail="Project not found")
            if project.name is not None:
                p.name = project.name
            if project.site_url is not None:
                p.site_url = project.site_url
            if project.description is not None:
                p.description = project.description
            session.commit()
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === PERIODS ===
@app.get("/api/projects/{project_id}/periods", response_model=List[PeriodResponse])
async def get_periods(project_id: int):
    """Получить периоды для конкретного проекта."""
    with db.get_session() as session:
        periods = session.query(Period).filter(Period.project_id == project_id).all()
        return [
            {
                "id": p.id,
                "project_id": p.project_id,
                "start_date": p.start_date.isoformat(),
                "end_date": p.end_date.isoformat(),
                "total_reviews_count": p.total_reviews_count,
                "created_at": p.created_at.isoformat() if p.created_at else ""
            } for p in periods
        ]

@app.post("/api/projects/{project_id}/periods")
async def create_period(project_id: int, period: PeriodCreate):
    """Создать новый период."""
    try:
        with db.get_session() as session:
            new_period = Period(
                project_id=period.project_id,
                start_date=datetime.fromisoformat(period.start_date),
                end_date=datetime.fromisoformat(period.end_date),
                total_reviews_count=period.total_reviews_count
            )
            session.add(new_period)
            session.commit()
            session.refresh(new_period)
            
            return {"id": new_period.id, "message": "Period created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/periods/{period_id}")
async def delete_period(period_id: int):
    """Удалить период (каскадно удалит товары/отзывы периода)."""
    try:
        with db.get_session() as session:
            p = session.query(Period).get(period_id)
            if not p:
                raise HTTPException(status_code=404, detail="Period not found")
            session.delete(p)
            session.commit()
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class PeriodUpdate(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_reviews_count: Optional[int] = None

@app.patch("/api/periods/{period_id}")
async def update_period(period_id: int, period: PeriodUpdate):
    """Обновить период (inline редактирование)."""
    try:
        with db.get_session() as session:
            p = session.query(Period).get(period_id)
            if not p:
                raise HTTPException(status_code=404, detail="Period not found")
            if period.start_date is not None:
                p.start_date = datetime.fromisoformat(period.start_date)
            if period.end_date is not None:
                p.end_date = datetime.fromisoformat(period.end_date)
            if period.total_reviews_count is not None:
                p.total_reviews_count = period.total_reviews_count
            session.commit()
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === PRODUCTS ===
@app.get("/api/periods/{period_id}/products", response_model=List[ProductResponse])
async def get_products(period_id: int):
    """Получить товары для периода."""
    with db.get_session() as session:
        products = session.query(ProductTask).filter(ProductTask.period_id == period_id).all()
        return [
            {
                "id": p.id,
                "product_name": p.product_name,
                "review_count": p.review_count,
                "product_url": p.product_url,
                "parse_status": p.parse_status,
                "is_used": p.is_used
            } for p in products
        ]

@app.post("/api/periods/{period_id}/products")
async def create_product(period_id: int, product: ProductCreate):
    """Создать новый товар."""
    try:
        with db.get_session() as session:
            new_product = ProductTask(
                period_id=period_id,
                product_name=product.product_name,
                review_count=product.review_count,
                product_url=product.product_url
            )
            session.add(new_product)
            session.commit()
            session.refresh(new_product)
            
            return {"id": new_product.id, "message": "Product created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/products/{product_id}")
async def update_product(product_id: int, payload: ProductUpdate):
    """Обновить поля товара (для inline-редактирования в UI)."""
    try:
        with db.get_session() as session:
            product = session.query(ProductTask).get(product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            data = payload.dict(exclude_unset=True)
            for k, v in data.items():
                setattr(product, k, v)

            session.commit()
            session.refresh(product)
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: int):
    """Удалить товар."""
    try:
        with db.get_session() as session:
            product = session.query(ProductTask).get(product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            session.delete(product)
            session.commit()
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === REVIEWS ===
class ReviewUpdate(BaseModel):
    is_approved: Optional[bool] = None
    is_published: Optional[bool] = None
    is_used: Optional[bool] = None
    target_date: Optional[str] = None

@app.get("/api/periods/{period_id}/reviews", response_model=List[ReviewResponse])
async def get_reviews(period_id: int):
    """Получить отзывы для периода."""
    with db.get_session() as session:
        reviews = session.query(Review).filter(Review.period_id == period_id).all()
        return [
            {
                "id": r.id,
                "product_name": r.product_name,
                "customer_name": r.customer_name,
                "rating": r.rating,
                "date": r.date.isoformat(),
                "content": r.content,
                "is_approved": r.is_approved,
                "is_published": getattr(r, 'is_published', False),
                "is_used": r.is_used,
                "target_date": getattr(r, 'target_date', None).isoformat() if getattr(r, 'target_date', None) else None
            } for r in reviews
        ]

@app.patch("/api/reviews/{review_id}")
async def update_review(review_id: int, review: ReviewUpdate):
    """Обновить отзыв (inline редактирование)."""
    try:
        with db.get_session() as session:
            r = session.query(Review).get(review_id)
            if not r:
                raise HTTPException(status_code=404, detail="Review not found")
            if review.is_approved is not None:
                r.is_approved = review.is_approved
            if review.is_published is not None:
                r.is_published = review.is_published
            if review.is_used is not None:
                r.is_used = review.is_used
            if review.target_date is not None:
                r.target_date = datetime.fromisoformat(review.target_date) if review.target_date else None
            session.commit()
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/reviews/{review_id}")
async def delete_review(review_id: int):
    """Удалить отзыв."""
    try:
        with db.get_session() as session:
            r = session.query(Review).get(review_id)
            if not r:
                raise HTTPException(status_code=404, detail="Review not found")
            session.delete(r)
            session.commit()
            return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === PARSING ===
@app.post("/api/products/{product_id}/parse")
async def parse_product_reviews(product_id: int):
    """Запустить парсинг отзывов для товара."""
    try:
        count, message = parser_service.parse_product_reviews(product_id)
        return {"success": True, "count": count, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products/parse")
async def batch_parse_product_reviews(request: dict):
    """Парсинг отзывов для нескольких товаров."""
    try:
        product_ids = request.get("product_ids", [])
        results = []
        for product_id in product_ids:
            count, message = parser_service.parse_product_reviews(product_id)
            results.append({"product_id": product_id, "count": count, "message": message})
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === GENERATION ===
@app.post("/api/products/{product_id}/generate")
async def generate_reviews(product_id: int, model: str = "perplexity"):
    """Запустить генерацию отзывов для продукта."""
    try:
        count, message = ai_service.generate_reviews(product_task_id=product_id, model=model)
        return {"success": True, "count": count, "message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/products/generate")
async def batch_generate_reviews(request: dict):
    """Генерация отзывов для нескольких товаров."""
    try:
        product_ids = request.get("product_ids", [])
        results = []
        for product_id in product_ids:
            count, message = ai_service.generate_reviews(product_task_id=product_id, model="perplexity")
            results.append({"product_id": product_id, "count": count, "message": message})
        return {"success": True, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === IMPORT/EXPORT ===
@app.post("/api/periods/{period_id}/products/import")
async def import_products(period_id: int, file: UploadFile = File(...)):
    """Импорт товаров из CSV/Excel."""
    try:
        # TODO: implement actual import logic
        return {"success": True, "imported": 0, "message": "Import not implemented yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/periods/{period_id}/products/export")
async def export_products(period_id: int, format: str = "csv"):
    """Экспорт товаров в CSV/Excel."""
    try:
        # TODO: implement actual export logic
        from fastapi.responses import Response
        if format == "csv":
            csv_content = "ID,Product Name,Review Count,URL,Is Used\n"
            return Response(content=csv_content, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=products.{format}"})
        else:
            # TODO: Excel export
            return Response(content="Excel not implemented", media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === DELETE REVIEWS ===
@app.delete("/api/products/reviews")
async def delete_product_reviews(request: dict):
    """Удалить отзывы для выбранных товаров."""
    try:
        product_ids = request.get("product_ids", [])
        with db.get_session() as session:
            # Get products by IDs
            products = session.query(ProductTask).filter(ProductTask.id.in_(product_ids)).all()
            product_names = [p.product_name for p in products]
            # Delete reviews where product_name matches
            deleted = session.query(Review).filter(Review.product_name.in_(product_names)).delete(synchronize_session=False)
            session.commit()
            return {"success": True, "deleted": deleted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
