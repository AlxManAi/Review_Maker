#!/usr/bin/env python3
import sys
import os
from datetime import datetime
from typing import List, Optional

# Добавляем корень проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Создаём приложение
app = FastAPI(title="Review Generator API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели
class ProjectCreate(BaseModel):
    name: str
    site_url: Optional[str] = ""
    description: Optional[str] = ""

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

# Временное хранилище
projects = []
periods = []

# Роуты
@app.get("/")
async def root():
    return {"message": "Review Generator API is running"}

@app.get("/api")
async def api_info():
    return {"message": "Review Generator API is running"}

@app.get("/debug")
async def debug():
    return {"status": "ok", "message": "Debug endpoint works"}

@app.get("/api/projects", response_model=List[ProjectResponse])
async def get_projects():
    return projects

@app.post("/api/projects", response_model=ProjectResponse)
async def create_project(project: ProjectCreate):
    new_project = ProjectResponse(
        id=len(projects) + 1,
        name=project.name,
        site_url=project.site_url,
        description=project.description,
        created_at=datetime.now().isoformat()
    )
    projects.append(new_project)
    return new_project

@app.get("/api/periods", response_model=List[PeriodResponse])
async def get_periods():
    return periods

@app.post("/api/periods", response_model=PeriodResponse)
async def create_period(period: PeriodCreate):
    # Проверяем, что проект существует
    if not any(p["id"] == period.project_id for p in projects):
        raise HTTPException(status_code=400, detail="Project not found")
    
    new_period = PeriodResponse(
        id=len(periods) + 1,
        project_id=period.project_id,
        start_date=period.start_date,
        end_date=period.end_date,
        total_reviews_count=period.total_reviews_count,
        created_at=datetime.now().isoformat()
    )
    periods.append(new_period)
    return new_period

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
