from pydantic import BaseModel
from typing import Optional, List, Dict
from enum import Enum

class MutationType(str, Enum):
    SUBSTITUTION = "substitution"
    INSERTION = "insertion"
    DELETION = "deletion"
    DUPLICATION = "duplication"
    COMPLEX = "complex"

class MutationBase(BaseModel):
    gene_name: str
    chromosome: str
    position: int
    reference: str
    alternate: str
    mutation_type: MutationType
    disease_id: Optional[str] = None  # MONDO ID
    clinical_significance: Optional[str] = None
    description: Optional[str] = None

class MutationCreate(MutationBase):
    pass

class Mutation(MutationBase):
    id: int
    
    class Config:
        from_attributes = True