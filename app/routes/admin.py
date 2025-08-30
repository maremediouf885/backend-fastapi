from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.database import get_db
from app import models
from app.schemas import (
    UserOut, UserUpdate, UserWithStats, UserStats,
    OffreOut, OffreWithCreator, TransactionOut, TransactionWithDetails,
    DashboardStats
)
from app.routes.auth import get_current_user

router = APIRouter()

# Dépendance pour vérifier les droits admin
def get_admin_user(current_user: models.Utilisateur = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs."
        )
    return current_user

# === GESTION DES UTILISATEURS ===

# Lister tous les utilisateurs avec pagination et filtres
@router.get("/users", response_model=List[UserOut])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    query = db.query(models.Utilisateur)
    
    if role:
        query = query.filter(models.Utilisateur.role == role)
    if is_active is not None:
        query = query.filter(models.Utilisateur.is_active == is_active)
    
    users = query.offset(skip).limit(limit).all()
    return users

# Détails d'un utilisateur avec statistiques
@router.get("/users/{user_id}", response_model=UserWithStats)
def get_user_details(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    # Calculer les statistiques
    total_offres = db.query(models.Offre).filter(models.Offre.createur_id == user_id).count()
    total_transactions = db.query(models.Transaction).filter(models.Transaction.beneficiaire_id == user_id).count()
    transactions_actives = db.query(models.Transaction).filter(
        models.Transaction.beneficiaire_id == user_id,
        models.Transaction.statut.in_(["reserve", "recupere"])
    ).count()
    
    stats = UserStats(
        total_offres=total_offres,
        total_transactions=total_transactions,
        transactions_actives=transactions_actives
    )
    
    return UserWithStats(**user.__dict__, stats=stats)

# Modifier un utilisateur
@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    # Empêcher de se désactiver soi-même
    if user_id == admin.id and user_update.is_active is False:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas désactiver votre propre compte.")
    
    # Mettre à jour les champs
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    db.commit()
    db.refresh(user)
    return user

# Supprimer un utilisateur
@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    if user_id == admin.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas supprimer votre propre compte.")
    
    # Anonymiser plutôt que supprimer (GDPR friendly)
    user.nom = "Utilisateur supprimé"
    user.email = f"deleted_{user_id}@deleted.com"
    user.is_active = False
    
    db.commit()
    return {"message": "Utilisateur anonymisé avec succès."}

# === SUPERVISION DES OFFRES ===

# Lister toutes les offres avec détails créateur
@router.get("/offres", response_model=List[OffreWithCreator])
def list_all_offres(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    is_disponible: Optional[bool] = Query(None),
    type_offre: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    query = db.query(models.Offre)
    
    if is_disponible is not None:
        query = query.filter(models.Offre.is_disponible == is_disponible)
    if type_offre:
        query = query.filter(models.Offre.type_offre == type_offre)
    
    offres = query.offset(skip).limit(limit).all()
    return offres

# Bloquer/débloquer une offre
@router.put("/offres/{offre_id}/toggle-disponibilite", response_model=OffreOut)
def toggle_offre_disponibilite(
    offre_id: int,
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    offre = db.query(models.Offre).filter(models.Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée.")
    
    offre.is_disponible = not offre.is_disponible
    db.commit()
    db.refresh(offre)
    return offre

# Supprimer une offre
@router.delete("/offres/{offre_id}")
def delete_offre_admin(
    offre_id: int,
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    offre = db.query(models.Offre).filter(models.Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée.")
    
    db.delete(offre)
    db.commit()
    return {"message": "Offre supprimée avec succès."}

# === SUPERVISION DES TRANSACTIONS ===

# Lister toutes les transactions
@router.get("/transactions", response_model=List[TransactionWithDetails])
def list_all_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    statut: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    query = db.query(models.Transaction)
    
    if statut:
        query = query.filter(models.Transaction.statut == statut)
    
    transactions = query.order_by(models.Transaction.created_at.desc()).offset(skip).limit(limit).all()
    return transactions

# Forcer l'annulation d'une transaction
@router.put("/transactions/{transaction_id}/forcer-annulation", response_model=TransactionOut)
def forcer_annulation_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée.")
    
    if transaction.statut == "annule":
        raise HTTPException(status_code=400, detail="Cette transaction est déjà annulée.")
    
    ancien_statut = transaction.statut
    transaction.statut = "annule"
    
    # Remettre l'offre disponible si nécessaire
    if ancien_statut == "reserve":
        transaction.offre.is_disponible = True
    
    db.commit()
    db.refresh(transaction)
    return transaction

# === TABLEAU DE BORD ===

# Statistiques générales
@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: models.Utilisateur = Depends(get_admin_user)
):
    total_utilisateurs = db.query(models.Utilisateur).count()
    utilisateurs_actifs = db.query(models.Utilisateur).filter(models.Utilisateur.is_active == True).count()
    
    total_offres = db.query(models.Offre).count()
    offres_disponibles = db.query(models.Offre).filter(models.Offre.is_disponible == True).count()
    
    total_transactions = db.query(models.Transaction).count()
    transactions_en_cours = db.query(models.Transaction).filter(
        models.Transaction.statut.in_(["reserve"])
    ).count()
    
    return DashboardStats(
        total_utilisateurs=total_utilisateurs,
        utilisateurs_actifs=utilisateurs_actifs,
        total_offres=total_offres,
        offres_disponibles=offres_disponibles,
        total_transactions=total_transactions,
        transactions_en_cours=transactions_en_cours
    )