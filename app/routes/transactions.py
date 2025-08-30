from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models
from app.schemas import TransactionReserver, TransactionOut, TransactionWithDetails
from app.routes.auth import get_current_user

router = APIRouter()

# Réserver une offre
@router.post("/reserver", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
def reserver_offre(reservation: TransactionReserver, db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    # Vérifier que l'offre existe
    offre = db.query(models.Offre).filter(models.Offre.id == reservation.id_offre).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée.")
    
    # Vérifier que l'offre est disponible
    if not offre.is_disponible:
        raise HTTPException(status_code=400, detail="Cette offre n'est plus disponible.")
    
    # Vérifier qu'on ne réserve pas sa propre offre
    if offre.createur_id == current_user.id:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas réserver votre propre offre.")
    
    # ✅ CONTRAINTE 1: Un bénéficiaire ne peut pas réserver deux fois la même offre
    existing_transaction = db.query(models.Transaction).filter(
        models.Transaction.offre_id == reservation.id_offre,
        models.Transaction.beneficiaire_id == current_user.id
    ).first()
    
    if existing_transaction:
        if existing_transaction.statut == "reserve":
            raise HTTPException(status_code=400, detail="Vous avez déjà réservé cette offre.")
        elif existing_transaction.statut == "recupere":
            raise HTTPException(status_code=400, detail="Vous avez déjà récupéré cette offre.")
        elif existing_transaction.statut == "annule":
            raise HTTPException(status_code=400, detail="Vous avez déjà une transaction annulée pour cette offre.")
    
    # ✅ CONTRAINTE 2: Vérifier qu'aucune autre transaction active n'existe pour cette offre
    any_active_transaction = db.query(models.Transaction).filter(
        models.Transaction.offre_id == reservation.id_offre,
        models.Transaction.statut.in_(["reserve", "recupere"])
    ).first()
    
    if any_active_transaction:
        raise HTTPException(status_code=400, detail="Cette offre a déjà été réservée par un autre utilisateur.")
    
    # Créer la transaction
    transaction = models.Transaction(
        offre_id=reservation.id_offre,
        beneficiaire_id=current_user.id,
        statut="reserve"
    )
    
    # Marquer l'offre comme non disponible
    offre.is_disponible = False
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

# Marquer une transaction comme récupérée
@router.put("/{transaction_id}/recuperer", response_model=TransactionOut)
def recuperer_offre(transaction_id: int, db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée.")
    
    # ✅ CONTRAINTE 3: Seul le bénéficiaire qui a réservé peut marquer comme récupéré
    if transaction.beneficiaire_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le bénéficiaire qui a réservé peut récupérer cette offre.")
    
    if transaction.statut != "reserve":
        if transaction.statut == "recupere":
            raise HTTPException(status_code=400, detail="Cette offre a déjà été récupérée.")
        elif transaction.statut == "annule":
            raise HTTPException(status_code=400, detail="Cette transaction a été annulée.")
    
    transaction.statut = "recupere"
    db.commit()
    db.refresh(transaction)
    return transaction

# Annuler une transaction
@router.put("/{transaction_id}/annuler", response_model=TransactionOut)
def annuler_transaction(transaction_id: int, db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction non trouvée.")
    
    # ✅ CONTRAINTE 3: Seul le bénéficiaire qui a réservé peut annuler
    if transaction.beneficiaire_id != current_user.id:
        raise HTTPException(status_code=403, detail="Seul le bénéficiaire qui a réservé peut annuler cette transaction.")
    
    if transaction.statut == "recupere":
        raise HTTPException(status_code=400, detail="Une transaction récupérée ne peut pas être annulée.")
    elif transaction.statut == "annule":
        raise HTTPException(status_code=400, detail="Cette transaction est déjà annulée.")
    
    # Sauvegarder l'ancien statut pour la logique de remise en disponibilité
    ancien_statut = transaction.statut
    transaction.statut = "annule"
    
    # Remettre l'offre disponible si elle était réservée
    if ancien_statut == "reserve":
        transaction.offre.is_disponible = True
    
    db.commit()
    db.refresh(transaction)
    return transaction

# Historique des transactions d'un utilisateur
@router.get("/historique/{user_id}", response_model=List[TransactionWithDetails])
def get_historique_transactions(user_id: int, db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    # Vérifier les permissions (utilisateur lui-même ou admin)
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Vous ne pouvez voir que votre propre historique.")
    
    transactions = db.query(models.Transaction).filter(
        models.Transaction.beneficiaire_id == user_id
    ).order_by(models.Transaction.created_at.desc()).all()
    
    return transactions

# Mes transactions (raccourci)
@router.get("/mes-transactions", response_model=List[TransactionWithDetails])
def get_mes_transactions(db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    transactions = db.query(models.Transaction).filter(
        models.Transaction.beneficiaire_id == current_user.id
    ).order_by(models.Transaction.created_at.desc()).all()
    
    return transactions