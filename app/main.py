from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth_routes
from app.routes.expenses_routes import ExpenseRoutes
from app.routes.user_routes import UserRoutes
from app.routes.groups_routes import GroupRoutes
from app.routes.settlement_routes import SettlementRoutes
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

expenses_routes = ExpenseRoutes()
groups_routes = GroupRoutes()
user_routes = UserRoutes()
settlement_routes = SettlementRoutes()

app.include_router(auth_routes.router)
app.include_router(expenses_routes.router)
app.include_router(user_routes.router)
app.include_router(groups_routes.router)
app.include_router(settlement_routes.router)
