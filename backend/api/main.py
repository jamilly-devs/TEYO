from fastapi import FastAPI

import bootstrap  # noqa: F401  (registra os subscribers de domínio da FASE 9)
from api.routers import (
    auth,
    conversation,
    events,
    finance,
    gamification,
    goals,
    market,
    mascot,
    planner,
    tasks,
)

app = FastAPI(title="TEYO API")

app.include_router(auth.router)
app.include_router(conversation.router)
app.include_router(tasks.router)
app.include_router(events.router)
app.include_router(goals.router)
app.include_router(market.router)
app.include_router(finance.router)
app.include_router(planner.router)
app.include_router(gamification.router)
app.include_router(mascot.router)
