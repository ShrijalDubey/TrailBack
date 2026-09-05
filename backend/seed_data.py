"""
Seed script to initialize RouteAI database with:
- Standard providers (groq, openai, anthropic)
- Popular models with realistic context windows & capabilities
- Current model pricing tiers
- Model benchmark metrics (quality, latency, error_rate)
- Demo user, project, and API key
"""
import uuid
from datetime import datetime, timezone

from app.database.db import LocalSession
from app.models.api_keys import APIKey
from app.models.models import Model, ModelMetrics, ModelPrice, Provider
from app.models.projects import Project
from app.models.users import User
from app.utils.security import generate_api_key

PROVIDERS = [
    {"name": "Groq", "slug": "groq"},
    {"name": "OpenAI", "slug": "openai"},
    {"name": "Anthropic", "slug": "anthropic"},
]

MODELS = [
    # Groq models
    {
        "provider_slug": "groq",
        "name": "llama-3.1-8b-instant",
        "context_window": 131072,
        "capabilities": {"chat": True, "json": True, "vision": False},
        "prices": {"input_per_1k": 0.00005, "output_per_1k": 0.00008},
        "metrics": {"quality": 0.76, "latency": 0.22, "ttft": 0.10, "error_rate": 0.01},
    },
    {
        "provider_slug": "groq",
        "name": "llama-3.3-70b-versatile",
        "context_window": 131072,
        "capabilities": {"chat": True, "json": True, "vision": False},
        "prices": {"input_per_1k": 0.00059, "output_per_1k": 0.00079},
        "metrics": {"quality": 0.88, "latency": 0.48, "ttft": 0.15, "error_rate": 0.01},
    },
    {
        "provider_slug": "groq",
        "name": "gemma2-9b-it",
        "context_window": 8192,
        "capabilities": {"chat": True, "json": True, "vision": False},
        "prices": {"input_per_1k": 0.00020, "output_per_1k": 0.00020},
        "metrics": {"quality": 0.74, "latency": 0.32, "ttft": 0.12, "error_rate": 0.02},
    },
    # OpenAI models
    {
        "provider_slug": "openai",
        "name": "gpt-4o-mini",
        "context_window": 128000,
        "capabilities": {"chat": True, "json": True, "vision": True},
        "prices": {"input_per_1k": 0.00015, "output_per_1k": 0.00060},
        "metrics": {"quality": 0.82, "latency": 0.45, "ttft": 0.25, "error_rate": 0.01},
    },
    {
        "provider_slug": "openai",
        "name": "gpt-4o",
        "context_window": 128000,
        "capabilities": {"chat": True, "json": True, "vision": True},
        "prices": {"input_per_1k": 0.00250, "output_per_1k": 0.01000},
        "metrics": {"quality": 0.94, "latency": 0.90, "ttft": 0.40, "error_rate": 0.01},
    },
    {
        "provider_slug": "openai",
        "name": "o3-mini",
        "context_window": 200000,
        "capabilities": {"chat": True, "json": True, "reasoning": True},
        "prices": {"input_per_1k": 0.00110, "output_per_1k": 0.00440},
        "metrics": {"quality": 0.95, "latency": 1.60, "ttft": 0.60, "error_rate": 0.01},
    },
    # Anthropic models
    {
        "provider_slug": "anthropic",
        "name": "claude-3-5-haiku-20241022",
        "context_window": 200000,
        "capabilities": {"chat": True, "json": True, "vision": True},
        "prices": {"input_per_1k": 0.00080, "output_per_1k": 0.00400},
        "metrics": {"quality": 0.84, "latency": 0.55, "ttft": 0.30, "error_rate": 0.01},
    },
    {
        "provider_slug": "anthropic",
        "name": "claude-3-5-sonnet-20241022",
        "context_window": 200000,
        "capabilities": {"chat": True, "json": True, "vision": True},
        "prices": {"input_per_1k": 0.00300, "output_per_1k": 0.01500},
        "metrics": {"quality": 0.95, "latency": 1.10, "ttft": 0.45, "error_rate": 0.01},
    },
]


def seed():
    db = LocalSession()
    try:
        now = datetime.now(timezone.utc)
        print("[SEED] Seeding database...")

        # 1. Seed Providers
        provider_map = {}
        for p_data in PROVIDERS:
            p = db.query(Provider).filter(Provider.slug == p_data["slug"]).first()
            if not p:
                p = Provider(name=p_data["name"], slug=p_data["slug"])
                db.add(p)
                db.flush()
                print(f"  + Added provider: {p.name} ({p.slug})")
            else:
                print(f"  = Existing provider: {p.name}")
            provider_map[p.slug] = p

        # 2. Seed Models, Model Prices & Model Metrics
        for m_data in MODELS:
            provider = provider_map[m_data["provider_slug"]]
            m = (
                db.query(Model)
                .filter(Model.provider_id == provider.id, Model.name == m_data["name"])
                .first()
            )
            if not m:
                m = Model(
                    provider_id=provider.id,
                    name=m_data["name"],
                    context_window=m_data["context_window"],
                    capabilities=m_data["capabilities"],
                )
                db.add(m)
                db.flush()
                print(f"  + Added model: {m.name} ({m_data['provider_slug']})")
            else:
                print(f"  = Existing model: {m.name}")

            # Ensure current price exists
            price = (
                db.query(ModelPrice)
                .filter(ModelPrice.model_id == m.id, ModelPrice.effective_to.is_(None))
                .first()
            )
            if not price:
                price = ModelPrice(
                    model_id=m.id,
                    prices=m_data["prices"],
                    effective_from=now,
                    effective_to=None,
                )
                db.add(price)
                print(f"    + Added price for: {m.name}")

            # Ensure current metrics exist
            metric = db.query(ModelMetrics).filter(ModelMetrics.model_id == m.id).first()
            if not metric:
                met_data = m_data["metrics"]
                metric = ModelMetrics(
                    model_id=m.id,
                    window="24h",
                    latency=met_data["latency"],
                    ttft=met_data["ttft"],
                    error_rate=met_data["error_rate"],
                    quality=met_data["quality"],
                )
                db.add(metric)
                print(f"    + Added benchmark metrics for: {m.name} (quality={met_data['quality']})")

        # 3. Seed Demo User & Project & API Key
        user = db.query(User).filter(User.email == "demo@routeai.dev").first()
        if not user:
            user = User(email="demo@routeai.dev", sso_identity={"provider": "local"})
            db.add(user)
            db.flush()
            print(f"  + Added demo user: {user.email}")

        project = db.query(Project).filter(Project.user_id == user.id, Project.name == "Default Project").first()
        if not project:
            project = Project(
                user_id=user.id,
                name="Default Project",
                retention=30,
            )
            db.add(project)
            db.flush()
            print(f"  + Added default project: {project.name}")

        existing_key = db.query(APIKey).filter(APIKey.project_id == project.id, APIKey.revoked_at.is_(None)).first()
        if not existing_key:
            raw_key, prefix, key_hash = generate_api_key()
            api_key = APIKey(project_id=project.id, prefix=prefix, key_hash=key_hash)
            db.add(api_key)
            db.flush()
            print(f"\n[KEY] Generated Demo API Key: {raw_key}")
            print(f"      (Keep this key handy to send test requests with X-API-Key: {raw_key})")
        else:
            print(f"\n[KEY] Active API Key exists with prefix: {existing_key.prefix}")

        db.commit()
        print("\n[SUCCESS] Database seeding complete!")

    except Exception as exc:
        db.rollback()
        print(f"[ERROR] Error seeding database: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
