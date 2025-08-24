from fastapi import FastAPI
from app.routes import auth_routes
from app.routes.expenses_routes import ExpenseRoutes
from app.routes.user_routes import UserRoutes
from app.routes.groups_routes import GroupRoutes
from app.routes.settlement_routes import SettlementRoutes
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

expenses_routes = ExpenseRoutes()
groups_routes = GroupRoutes()
user_routes = UserRoutes()
settlement_routes = SettlementRoutes()

app.include_router(auth_routes.router)
app.include_router(expenses_routes.router)
app.include_router(user_routes.router)
app.include_router(groups_routes.router)
app.include_router(settlement_routes.router)
