from fastapi import FastAPI

from api.routers import auth, conversation, events, finance, goals, market, tasks

app = FastAPI(title="TEYO API")

app.include_router(auth.router)
app.include_router(conversation.router)
app.include_router(tasks.router)
app.include_router(events.router)
app.include_router(goals.router)
app.include_router(market.router)
app.include_router(finance.router)
