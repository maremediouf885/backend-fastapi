from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, Literal
from datetime import datetime

RoleLiteral = Literal["beneficiaire","donateur","partenaire","admin"]
TypeOffreLiteral = Literal["denrees","plats","credits"]
StatutTransactionLiteral = Literal["reserve","recupere","annule"]

class UserBase(BaseModel):
    nom: Optional[str] = None
    email: EmailStr
    role: RoleLiteral

class UserCreate(UserBase):
    mot_de_passe: str

    @field_validator("mot_de_passe")
    @classmethod
    def validate_pwd(cls, v):
        if len(v) < 6:
            raise ValueError("Le mot de passe doit contenir au moins 6 caractères.")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str

class UserOut(BaseModel):
    id: int
    nom: Optional[str] = None
    email: EmailStr
    role: RoleLiteral
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Schémas pour les offres
class OffreBase(BaseModel):
    titre: str
    description: Optional[str] = None
    type_offre: TypeOffreLiteral
    quantite: int
    localisation: Optional[str] = None
    date_expiration: Optional[datetime] = None

class OffreCreate(OffreBase):
    @field_validator("quantite")
    @classmethod
    def validate_quantite(cls, v):
        if v <= 0:
            raise ValueError("La quantité doit être positive.")
        return v

class OffreUpdate(BaseModel):
    titre: Optional[str] = None
    description: Optional[str] = None
    quantite: Optional[int] = None
    localisation: Optional[str] = None
    date_expiration: Optional[datetime] = None
    is_disponible: Optional[bool] = None

class OffreOut(OffreBase):
    id: int
    is_disponible: bool
    createur_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schémas pour les transactions
class TransactionReserver(BaseModel):
    id_offre: int

class TransactionOut(BaseModel):
    id: int
    offre_id: int
    beneficiaire_id: int
    statut: StatutTransactionLiteral
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionWithDetails(TransactionOut):
    offre: OffreOut
    beneficiaire: UserOut

    class Config:
        from_attributes = True

# Schémas pour l'administration
class UserUpdate(BaseModel):
    nom: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[RoleLiteral] = None

class UserStats(BaseModel):
    total_offres: int
    total_transactions: int
    transactions_actives: int

class UserWithStats(UserOut):
    stats: UserStats

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_utilisateurs: int
    utilisateurs_actifs: int
    total_offres: int
    offres_disponibles: int
    total_transactions: int
    transactions_en_cours: int

class OffreWithCreator(OffreOut):
    createur: UserOut

    class Config:
        from_attributes = True