from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.projects import Project
from app.routes import analytics, api_keys, chat, models, providers, projects, requests, users
from app.routes.api_keys import get_current_project

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(providers.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(api_keys.router)
app.include_router(models.router)
app.include_router(chat.router)
app.include_router(requests.router)
app.include_router(analytics.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/v1/me")
def whoami(project: Project = Depends(get_current_project)):
    return {"project_id": str(project.id), "project_name": project.name}