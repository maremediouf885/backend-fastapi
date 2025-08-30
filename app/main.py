from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine
from app.routes import auth, offres, transactions, admin

# Création des tables au démarrage (dev)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Backend FastAPI - Transfert de denrées",
    version="1.0.0",
    description="API pour authentification et gestion du système de dons alimentaires."
)

# CORS (autorise l'appli Flutter pendant le dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # en prod: restreindre
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(offres.router, prefix="/offres", tags=["Offres"])
app.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
app.include_router(admin.router, prefix="/admin", tags=["Administration"])

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Bienvenue sur l'API de transfert de denrées alimentaires "}

@app.get("/status", tags=["System"])
def system_status():
    return {
        "status": "running",
        "service": "transfert-denrees-api",
        "version": "1.0.0"
    }