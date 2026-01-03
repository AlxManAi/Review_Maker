#!/usr/bin/env python3
import sys
import os

# Добавляем корень проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Создаём минимальное приложение
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
    site_url: str = ""
    description: str = ""

# Временное хранилище
projects = []

# Роуты
@app.get("/")
async def root():
    return {"message": "Review Generator API is running"}

@app.get("/api")
async def api_info():
    return {"message": "Review Generator API is running"}

@app.get("/api/projects")
async def get_projects():
    return projects

@app.post("/api/projects")
async def create_project(project: ProjectCreate):
    new_project = {
        "id": len(projects) + 1,
        "name": project.name,
        "site_url": project.site_url,
        "description": project.description,
        "created_at": "2024-01-01"
    }
    projects.append(new_project)
    return new_project

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
