from fastapi import Depends, FastAPI

from app.models.projects import Project
from app.routes import api_keys, chat, models, providers, projects, users
from app.routes.api_keys import get_current_project

app = FastAPI()

app.include_router(providers.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(api_keys.router)
app.include_router(models.router)
app.include_router(chat.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/v1/me")
def whoami(project: Project = Depends(get_current_project)):
    """
    Demo endpoint proving get_current_project actually gates access --
    requires a valid X-API-Key header, returns the project it resolved to.
    """
    return {"project_id": str(project.id), "project_name": project.name}