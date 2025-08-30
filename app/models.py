from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class RoleEnum(str, enum.Enum):
    beneficiaire = "beneficiaire"
    donateur = "donateur"
    partenaire = "partenaire"
    admin = "admin"

class TypeOffreEnum(str, enum.Enum):
    denrees = "denrees"
    plats = "plats"
    credits = "credits"

class StatutTransactionEnum(str, enum.Enum):
    reserve = "reserve"
    recupere = "recupere"
    annule = "annule"

class Utilisateur(Base):
    __tablename__ = "utilisateurs"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.beneficiaire)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    offres = relationship("Offre", back_populates="createur")
    transactions = relationship("Transaction", back_populates="beneficiaire")

class Offre(Base):
    __tablename__ = "offres"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    type_offre = Column(Enum(TypeOffreEnum), nullable=False)
    quantite = Column(Integer, nullable=False)
    localisation = Column(String(255), nullable=True)
    date_expiration = Column(DateTime(timezone=True), nullable=True)
    is_disponible = Column(Boolean, default=True)
    createur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    createur = relationship("Utilisateur", back_populates="offres")
    transactions = relationship("Transaction", back_populates="offre")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    offre_id = Column(Integer, ForeignKey("offres.id"), nullable=False)
    beneficiaire_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    statut = Column(Enum(StatutTransactionEnum), nullable=False, default=StatutTransactionEnum.reserve)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    offre = relationship("Offre", back_populates="transactions")
    beneficiaire = relationship("Utilisateur", back_populates="transactions")