from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from app.database import get_db
from app import models
from app.schemas import UserCreate, UserOut, UserLogin, Token
from app.security import hash_password, verify_password, create_access_token, decode_token

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # pour la doc Swagger

# REGISTER
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    # email unique
    existing = db.query(models.Utilisateur).filter(models.Utilisateur.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé.")
    # rôle valide (Enum géré au modèle)
    user = models.Utilisateur(
        nom=payload.nom,
        email=payload.email,
        password_hash=hash_password(payload.mot_de_passe),
        role=payload.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# LOGIN (JSON)
@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user: Optional[models.Utilisateur] = db.query(models.Utilisateur).filter(models.Utilisateur.email == payload.email).first()
    if not user or not verify_password(payload.mot_de_passe, user.password_hash):
        raise HTTPException(status_code=401, detail="Identifiants invalides.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé.")
    access_token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}

# Dépendance pour récupérer l'utilisateur courant depuis le token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Utilisateur:
    payload = decode_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré.")
    user_id = int(payload["sub"])
    user = db.query(models.Utilisateur).get(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé ou inactif.")
    return user

@router.get("/me", response_model=UserOut)
def me(current_user: models.Utilisateur = Depends(get_current_user)):
    return current_user