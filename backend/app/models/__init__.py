"""
Import every ORM model here so a single `import app.models` (or importing
this package) registers all tables on `Base.metadata`. Needed for
`Base.metadata.create_all(...)` and for Alembic autogenerate to see
everything -- SQLAlchemy only knows about a class once it's been imported.
"""

from app.models.users import User
from app.models.projects import Project, Budget, Alert
from app.models.api_keys import APIKey
from app.models.models import Provider, Model, ModelPrice, ModelMetrics
from app.models.requests import Request, RoutingDecision, Evaluation
from app.models.benchmarks import Benchmark, BenchmarkResult
from app.models.cache_entries import CacheEntry

__all__ = [
    "User",
    "Project",
    "Budget",
    "Alert",
    "APIKey",
    "Provider",
    "Model",
    "ModelPrice",
    "ModelMetrics",
    "Request",
    "RoutingDecision",
    "Evaluation",
    "Benchmark",
    "BenchmarkResult",
    "CacheEntry",
]