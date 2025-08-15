from fastapi import FastAPI
from app.routes import auth_routes
from app.routes.expenses_routes import ExpenseRoutes
from app.routes.user_routes import UserRoutes
from app.routes.groups_routes import GroupRoutes
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

app.include_router(auth_routes.router)
app.include_router(ExpenseRoutes.router)
app.include_router(UserRoutes.router)
app.include_router(GroupRoutes.router)
