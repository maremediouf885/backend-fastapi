from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models
from app.schemas import OffreCreate, OffreOut, OffreUpdate
from app.routes.auth import get_current_user

router = APIRouter()

# Dépendance pour vérifier que l'utilisateur peut créer des offres
def get_donateur_or_partenaire(current_user: models.Utilisateur = Depends(get_current_user)):
    if current_user.role not in ["donateur", "partenaire"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seuls les donateurs et partenaires peuvent créer des offres."
        )
    return current_user

# Créer une offre (donateur/partenaire uniquement)
@router.post("/", response_model=OffreOut, status_code=status.HTTP_201_CREATED)
def create_offre(offre: OffreCreate, db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_donateur_or_partenaire)):
    db_offre = models.Offre(
        **offre.dict(),
        createur_id=current_user.id
    )
    db.add(db_offre)
    db.commit()
    db.refresh(db_offre)
    return db_offre

# Lister toutes les offres disponibles
@router.get("/", response_model=List[OffreOut])
def list_offres(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    offres = db.query(models.Offre).filter(models.Offre.is_disponible == True).offset(skip).limit(limit).all()
    return offres

# Voir les détails d'une offre
@router.get("/{offre_id}", response_model=OffreOut)
def get_offre(offre_id: int, db: Session = Depends(get_db)):
    offre = db.query(models.Offre).filter(models.Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée.")
    return offre

# Modifier une offre (créateur ou admin seulement)
@router.put("/{offre_id}", response_model=OffreOut)
def update_offre(offre_id: int, offre_update: OffreUpdate, db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    offre = db.query(models.Offre).filter(models.Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée.")
    
    # Vérifier les permissions
    if offre.createur_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres offres."
        )
    
    # Mettre à jour les champs modifiés
    for field, value in offre_update.dict(exclude_unset=True).items():
        setattr(offre, field, value)
    
    db.commit()
    db.refresh(offre)
    return offre

# Supprimer une offre (créateur ou admin seulement)
@router.delete("/{offre_id}")
def delete_offre(offre_id: int, db: Session = Depends(get_db), current_user: models.Utilisateur = Depends(get_current_user)):
    offre = db.query(models.Offre).filter(models.Offre.id == offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée.")
    
    # Vérifier les permissions
    if offre.createur_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres offres."
        )
    
    db.delete(offre)
    db.commit()
    return {"message": "Offre supprimée avec succès."}