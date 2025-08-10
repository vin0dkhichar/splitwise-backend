from fastapi import FastAPI
from app.routes import user_routes, auth_routes, groups_routes, expenses_routes
from app.core.database import Base, engine

# auto-create tables (for dev). In prod prefer alembic migrations.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

app.include_router(user_routes.router)
app.include_router(auth_routes.router)
app.include_router(groups_routes.router)
app.include_router(expenses_routes.router)